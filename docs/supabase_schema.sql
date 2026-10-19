-- ============================================================
-- 不烧心 · Supabase 建表脚本
-- 在 Supabase Dashboard → SQL Editor 里整段执行
-- ============================================================

-- ---------- 用户 ----------
-- 用 Supabase Auth 的匿名登录（Anonymous Sign-in）即可，无需手机号/微信
create table if not exists profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  nickname    text not null default '匿名用户',
  avatar      text,
  created_at  timestamptz not null default now()
);

-- ---------- 消费申请 ----------
create table if not exists applications (
  id           uuid primary key default gen_random_uuid(),
  author_id    uuid references auth.users(id) on delete set null,
  goods        text not null check (char_length(goods) between 1 and 60),
  price        numeric(12,2) not null check (price > 0),
  -- ISO 4217 币种代码。多币种分开记账，不做汇率换算。
  currency_code text not null default 'CNY',
  -- 存稳定 key（dining/fashion/digital/game/sports/other），不存显示名，
  -- 否则切换语言时历史数据会变成另一种语言的乱码字符串
  category_key text not null default 'other',
  reason       text not null check (char_length(reason) between 1 and 500),
  alternative  text not null default '',
  channel      text not null default 'plaza'
                 check (channel in ('plaza','group','private_')),
  group_name   text,
  status       text not null default 'voting'
                 check (status in ('voting','passed','rejected','archived')),
  pass_count   int not null default 0 check (pass_count >= 0),
  reject_count int not null default 0 check (reject_count >= 0),
  created_at   timestamptz not null default now()
);

-- ---------- 审批票（必须带理由）----------
create table if not exists votes (
  id              uuid primary key default gen_random_uuid(),
  application_id  uuid not null references applications(id) on delete cascade,
  voter_id        uuid references auth.users(id) on delete set null,
  verdict         text not null check (verdict in ('pass','reject','skip')),
  comment         text not null check (char_length(comment) >= 1),  -- 强制写理由
  flowers         int not null default 0,
  created_at      timestamptz not null default now()
);

-- 一个用户对一条申请只能投一次（防刷票）
create unique index if not exists uniq_vote_per_user
  on votes (application_id, voter_id);

-- ---------- 索引 ----------
create index if not exists idx_apps_plaza
  on applications (channel, status, created_at desc);

create index if not exists idx_votes_app
  on votes (application_id, created_at desc);

-- ============================================================
-- 触发器：投票后自动累加计数
-- ============================================================
create or replace function bump_vote_count() returns trigger as $$
begin
  if new.verdict = 'pass' then
    update applications set pass_count = pass_count + 1 where id = new.application_id;
  elsif new.verdict = 'reject' then
    update applications set reject_count = reject_count + 1 where id = new.application_id;
  end if;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists trg_bump_vote on votes;
create trigger trg_bump_vote
  after insert on votes
  for each row execute function bump_vote_count();

-- 删票时回退（防误操作）
create or replace function revert_vote_count() returns trigger as $$
begin
  if old.verdict = 'pass' then
    update applications set pass_count = greatest(0, pass_count - 1) where id = old.application_id;
  elsif old.verdict = 'reject' then
    update applications set reject_count = greatest(0, reject_count - 1) where id = old.application_id;
  end if;
  return old;
end;
$$ language plpgsql security definer;

drop trigger if exists trg_revert_vote on votes;
create trigger trg_revert_vote
  after delete on votes
  for each row execute function revert_vote_count();

-- ============================================================
-- RLS 行级安全
-- ============================================================
alter table profiles     enable row level security;
alter table applications enable row level security;
alter table votes        enable row level security;

-- profiles：本人可读写
create policy "own profile read"   on profiles for select using (auth.uid() = id);
create policy "own profile upsert" on profiles for insert with check (auth.uid() = id);
create policy "own profile update" on profiles for update using (auth.uid() = id);

-- applications：广场内容所有人可读
create policy "plaza readable" on applications
  for select using (channel = 'plaza' or author_id = auth.uid());

-- 写入必须带上 author_id，且等于当前登录用户（anon 登录后 auth.uid() 有值）
create policy "insert own application" on applications
  for insert with check (author_id = auth.uid());

create policy "update own application" on applications
  for update using (author_id = auth.uid());

-- votes：所有人可读（投完才在客户端解锁展示）
create policy "votes readable" on votes for select using (true);

create policy "insert own vote" on votes
  for insert with check (voter_id = auth.uid());

create policy "update own vote flowers" on votes
  for update using (voter_id = auth.uid());

-- ============================================================
-- 敏感词过滤（基础版，正式上线建议再接第三方内容审核）
-- ============================================================
create or replace function contains_blocked_word(t text) returns boolean as $$
declare
  blocked text[] := array['代购','刷单','贷款','裸贷','赌博','博彩','色情','杀','枪','毒品'];
  w text;
begin
  foreach w in array blocked loop
    if position(w in t) > 0 then return true; end if;
  end loop;
  return false;
end;
$$ language plpgsql immutable;

create or replace function check_app_content() returns trigger as $$
begin
  if contains_blocked_word(new.goods) or contains_blocked_word(new.reason) then
    raise exception '内容包含敏感词，请修改后重试';
  end if;
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_check_app on applications;
create trigger trg_check_app
  before insert or update on applications
  for each row execute function check_app_content();

-- ============================================================
-- 举报与拉黑（Apple UGC 审核硬性要求，缺这两项必被拒）
-- ============================================================
create table if not exists reports (
  id          uuid primary key default gen_random_uuid(),
  target_id   text not null,          -- 客户端 Application.id
  reporter_id uuid references auth.users(id) on delete set null,
  reason      text not null
                check (reason in ('spam','fraud','abuse','adult','other')),
  detail      text not null default '',
  -- 审核处理状态：pending / reviewing / removed / dismissed
  status      text not null default 'pending'
                check (status in ('pending','reviewing','removed','dismissed')),
  created_at  timestamptz not null default now()
);

create index if not exists idx_reports_pending
  on reports (status, created_at desc);

-- 同一个人对同一条内容重复举报只算一次
create unique index if not exists uniq_report_per_user
  on reports (target_id, reporter_id);

create table if not exists blocked_authors (
  id          uuid primary key default gen_random_uuid(),
  owner_id    uuid not null references auth.users(id) on delete cascade,
  author_key  text not null,
  created_at  timestamptz not null default now()
);

create unique index if not exists uniq_block_per_user
  on blocked_authors (owner_id, author_key);

alter table reports         enable row level security;
alter table blocked_authors enable row level security;

-- 举报：本人可写，不能读别人的举报（防报复）
create policy "insert own report"   on reports for insert with check (reporter_id = auth.uid());
create policy "read own reports"    on reports for select using (reporter_id = auth.uid());

-- 同一内容被多人举报后自动下架（≥3 人即隐藏），减少人工审核压力
create or replace function auto_hide_reported() returns trigger as $$
declare
  cnt int;
begin
  select count(*) into cnt from reports
   where target_id = new.target_id and status = 'pending';
  if cnt >= 3 then
    update applications set status = 'archived' where id::text = new.target_id;
  end if;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists trg_auto_hide on reports;
create trigger trg_auto_hide
  after insert on reports
  for each row execute function auto_hide_reported();

-- 拉黑：只能操作自己的名单
create policy "read own blocks"   on blocked_authors for select using (owner_id = auth.uid());
create policy "insert own blocks" on blocked_authors for insert with check (owner_id = auth.uid());
create policy "delete own blocks" on blocked_authors for delete using (owner_id = auth.uid());
