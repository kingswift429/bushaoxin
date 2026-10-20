# -*- coding: utf-8 -*-
"""
为「不烧心」补充 8 种语言的翻译。

设计原则：
1. 不直译中文，按各语言母语者的习惯表达
2. 保留产品的"降温/不焦虑"语气，不用说教口吻
3. 保留 %@ %lld 等格式占位符（顺序可调整，这是 iOS 本地化允许的）
4. App 名称在各语言保持品牌一致性

语言：fr / de / es / pt-BR / ru / ar / it / nl
"""
import json

PATH = r"F:\Administrator\deepseek-harness\default-workspace\bushaoxin\Bushaoxin\Localization\Localizable.xcstrings"

# ═══════════════════════════════════════════════════════════════
# 翻译表：key -> {locale: text}
# ═══════════════════════════════════════════════════════════════

T = {}

def add(key, **kw):
    T[key] = kw

# ───────────── 品牌 ─────────────
add("app.name",
    fr="Cool Head", de="Cool Head", es="Cool Head", **{"pt-BR": "Cool Head"},
    ru="Cool Head", ar="Cool Head", it="Cool Head", nl="Cool Head")

add("app.tagline",
    fr="Bien dépenser, l'esprit tranquille",
    de="Gut kaufen, ruhig schlafen",
    es="Gasta bien, duerme tranquilo",
    **{"pt-BR": "Gaste bem, durma tranquilo"},
    ru="Тратьте с умом, спите спокойно",
    ar="أنفق بذكاء، ونم مرتاحًا",
    it="Spendi bene, dormi sereno",
    nl="Goed besteden, rustig slapen")

# ───────────── 通用动作 ─────────────
add("action.post",
    fr="Publier", de="Posten", es="Publicar", **{"pt-BR": "Publicar"},
    ru="Опубликовать", ar="نشر", it="Pubblica", nl="Plaatsen")

add("more.action",
    fr="Plus", de="Mehr", es="Más", **{"pt-BR": "Mais"},
    ru="Ещё", ar="المزيد", it="Altro", nl="Meer")

add("share.action",
    fr="Partager", de="Teilen", es="Compartir", **{"pt-BR": "Compartilhar"},
    ru="Поделиться", ar="مشاركة", it="Condividi", nl="Delen")

add("sheet.close",
    fr="Fermer", de="Schließen", es="Cerrar", **{"pt-BR": "Fechar"},
    ru="Закрыть", ar="إغلاق", it="Chiudi", nl="Sluiten")

# ───────────── 标签页 ─────────────
add("tab.plaza",
    fr="Place", de="Platz", es="Plaza", **{"pt-BR": "Praça"},
    ru="Площадь", ar="الساحة", it="Piazza", nl="Plein")

add("tab.mine",
    fr="Moi", de="Ich", es="Yo", **{"pt-BR": "Eu"},
    ru="Моё", ar="خاصتي", it="Mio", nl="Mijn")

# ───────────── 拉黑 ─────────────
add("block.action",
    fr="Bloquer cet utilisateur", de="Diesen Nutzer blockieren",
    es="Bloquear a este usuario", **{"pt-BR": "Bloquear este usuário"},
    ru="Заблокировать пользователя", ar="حظر هذا المستخدم",
    it="Blocca questo utente", nl="Deze gebruiker blokkeren")

add("block.confirm",
    fr="Vous ne verrez plus ses publications.",
    de="Du siehst keine Beiträge mehr von dieser Person.",
    es="Ya no verás sus publicaciones.",
    **{"pt-BR": "Você não verá mais as publicações dele."},
    ru="Вы больше не увидите его публикации.",
    ar="لن ترى منشوراته بعد الآن.",
    it="Non vedrai più i suoi contenuti.",
    nl="Je ziet geen berichten meer van deze persoon.")

add("block.done",
    fr="Bloqué", de="Blockiert", es="Bloqueado", **{"pt-BR": "Bloqueado"},
    ru="Заблокировано", ar="تم الحظر", it="Bloccato", nl="Geblokkeerd")

add("block.empty",
    fr="Aucun utilisateur bloqué", de="Keine blockierten Nutzer",
    es="No has bloqueado a nadie", **{"pt-BR": "Nenhum usuário bloqueado"},
    ru="Нет заблокированных", ar="لا يوجد مستخدمون محظورون",
    it="Nessun utente bloccato", nl="Geen geblokkeerde gebruikers")

add("block.manage",
    fr="Utilisateurs bloqués", de="Blockierte Nutzer",
    es="Usuarios bloqueados", **{"pt-BR": "Usuários bloqueados"},
    ru="Заблокированные", ar="المستخدمون المحظورون",
    it="Utenti bloccati", nl="Geblokkeerde gebruikers")

add("block.title",
    fr="Bloquer cet utilisateur ?", de="Diesen Nutzer blockieren?",
    es="¿Bloquear a este usuario?", **{"pt-BR": "Bloquear este usuário?"},
    ru="Заблокировать пользователя?", ar="حظر هذا المستخدم؟",
    it="Bloccare questo utente?", nl="Deze gebruiker blokkeren?")

add("block.unblock",
    fr="Débloquer", de="Entsperren", es="Desbloquear", **{"pt-BR": "Desbloquear"},
    ru="Разблокировать", ar="إلغاء الحظر", it="Sblocca", nl="Deblokkeren")

# ───────────── 卡片 ─────────────
add("card.alternative",
    fr="Alternative", de="Alternative", es="Alternativa", **{"pt-BR": "Alternativa"},
    ru="Альтернатива", ar="بديل", it="Alternativa", nl="Alternatief")

add("card.passCount %lld",
    fr="Approuvé %lld fois", de="%lld-mal genehmigt",
    es="Aprobado %lld veces", **{"pt-BR": "Aprovado %lld vezes"},
    ru="Одобрено %lld раз", ar="تمت الموافقة %lld مرة",
    it="Approvato %lld volte", nl="%lld keer goedgekeurd")

add("card.reason",
    fr="Raison", de="Begründung", es="Razón", **{"pt-BR": "Motivo"},
    ru="Причина", ar="السبب", it="Motivo", nl="Reden")

add("card.rejectCount %lld",
    fr="Refusé %lld fois", de="%lld-mal abgelehnt",
    es="Rechazado %lld veces", **{"pt-BR": "Recusado %lld vezes"},
    ru="Отклонено %lld раз", ar="تم الرفض %lld مرة",
    it="Respinto %lld volte", nl="%lld keer afgekeurd")

add("card.saved %@",
    fr="Économisé %@", de="Gespart: %@", es="Ahorrado %@", **{"pt-BR": "Economizado %@"},
    ru="Сэкономлено %@", ar="تم توفير %@", it="Risparmiato %@", nl="Bespaard %@")

add("card.viewAllReasons %lld",
    fr="Voir les %lld raisons", de="Alle %lld Begründungen ansehen",
    es="Ver las %lld razones", **{"pt-BR": "Ver os %lld motivos"},
    ru="Все причины (%lld)", ar="عرض كل الأسباب (%lld)",
    it="Vedi tutti i %lld motivi", nl="Alle %lld redenen bekijken")

add("card.voteCount %lld",
    fr="%lld avis", de="%lld Bewertungen", es="%lld valoraciones",
    **{"pt-BR": "%lld avaliações"},
    ru="Оценок: %lld", ar="%lld تقييم", it="%lld valutazioni", nl="%lld beoordelingen")

add("card.voteNow",
    fr="Donner mon avis", de="Jetzt abstimmen", es="Opinar ahora",
    **{"pt-BR": "Opinar agora"},
    ru="Оценить", ar="صوّت الآن", it="Vota ora", nl="Nu stemmen")

add("card.youPassed",
    fr="Vous avez approuvé cet achat", de="Du hast diesen Kauf genehmigt",
    es="Aprobaste este gasto", **{"pt-BR": "Você aprovou este gasto"},
    ru="Вы одобрили эту покупку", ar="لقد وافقت على هذا الشراء",
    it="Hai approvato questa spesa", nl="Je hebt deze aankoop goedgekeurd")

add("card.youRejected",
    fr="Vous avez refusé cet achat", de="Du hast diesen Kauf abgelehnt",
    es="Rechazaste este gasto", **{"pt-BR": "Você recusou este gasto"},
    ru="Вы отклонили эту покупку", ar="لقد رفضت هذا الشراء",
    it="Hai respinto questa spesa", nl="Je hebt deze aankoop afgekeurd")

add("card.youWatched",
    fr="Vous suivez, sans avis pour l'instant",
    de="Du beobachtest, noch keine Meinung",
    es="Estás observando, aún sin opinión",
    **{"pt-BR": "Você está observando, sem opinião ainda"},
    ru="Вы наблюдаете, решения пока нет",
    ar="أنت تتابع، دون رأي بعد",
    it="Stai osservando, nessun parere ancora",
    nl="Je volgt het, nog geen oordeel")

# ───────────── 分类 ─────────────
add("category.digital",
    fr="Tech", de="Technik", es="Tecnología", **{"pt-BR": "Tecnologia"},
    ru="Техника", ar="تقنية", it="Tecnologia", nl="Techniek")

add("category.dining",
    fr="Restos", de="Essen", es="Comida", **{"pt-BR": "Comida"},
    ru="Еда", ar="طعام", it="Cibo", nl="Eten")

add("category.fashion",
    fr="Mode", de="Mode", es="Moda", **{"pt-BR": "Moda"},
    ru="Мода", ar="أزياء", it="Moda", nl="Mode")

add("category.game",
    fr="Jeux", de="Spiele", es="Juegos", **{"pt-BR": "Jogos"},
    ru="Игры", ar="ألعاب", it="Giochi", nl="Games")

add("category.other",
    fr="Autre", de="Sonstiges", es="Otros", **{"pt-BR": "Outros"},
    ru="Другое", ar="أخرى", it="Altro", nl="Overig")

add("category.sports",
    fr="Sport", de="Sport", es="Deporte", **{"pt-BR": "Esporte"},
    ru="Спорт", ar="رياضة", it="Sport", nl="Sport")

# ───────────── 审批渠道 ─────────────
add("channel.group",
    fr="Groupe", de="Gruppe", es="Grupo", **{"pt-BR": "Grupo"},
    ru="Группа", ar="مجموعة", it="Gruppo", nl="Groep")

add("channel.groupPlaceholder",
    fr="Nom du groupe, ex. « J'achète ou pas ? »",
    de="Gruppenname, z. B. „Soll ich das kaufen?“",
    es="Nombre del grupo, p. ej. «¿Me lo compro?»",
    **{"pt-BR": "Nome do grupo, ex.: “Será que compro?”"},
    ru="Название группы, напр. «Брать или нет?»",
    ar="اسم المجموعة، مثل «هل أشتريه؟»",
    it="Nome del gruppo, es. «Lo compro?»",
    nl="Groepsnaam, bijv. “Zal ik het kopen?”")

add("channel.plaza",
    fr="La place", de="Der Platz", es="La plaza", **{"pt-BR": "A praça"},
    ru="Площадь", ar="الساحة", it="La piazza", nl="Het plein")

add("channel.private",
    fr="Moi seul", de="Nur ich", es="Solo yo", **{"pt-BR": "Só eu"},
    ru="Только я", ar="أنا فقط", it="Solo io", nl="Alleen ik")

add("channel.title",
    fr="Qui décide ?", de="Wer entscheidet?", es="¿Quién decide?",
    **{"pt-BR": "Quem decide?"},
    ru="Кто решает?", ar="من يقرر؟", it="Chi decide?", nl="Wie beslist?")

# ───────────── 发起审批 ─────────────
add("compose.cancel",
    fr="Annuler", de="Abbrechen", es="Cancelar", **{"pt-BR": "Cancelar"},
    ru="Отмена", ar="إلغاء", it="Annulla", nl="Annuleren")

add("compose.submit",
    fr="Envoyer", de="Einreichen", es="Enviar", **{"pt-BR": "Enviar"},
    ru="Отправить", ar="إرسال", it="Invia", nl="Versturen")

add("compose.submitDisabled",
    fr="Renseignez l'article, le prix et la raison",
    de="Artikel, Preis und Begründung ausfüllen",
    es="Completa artículo, precio y razón",
    **{"pt-BR": "Preencha item, preço e motivo"},
    ru="Укажите товар, цену и причину",
    ar="املأ المنتج والسعر والسبب",
    it="Compila articolo, prezzo e motivo",
    nl="Vul artikel, prijs en reden in")

add("compose.title",
    fr="Nouvelle demande", de="Neue Anfrage", es="Nueva solicitud",
    **{"pt-BR": "Nova solicitação"},
    ru="Новая заявка", ar="طلب جديد", it="Nuova richiesta", nl="Nieuw verzoek")

# ───────────── 冷静期 ─────────────
add("cooldown.12h",
    fr="12 h", de="12 Std.", es="12 h", **{"pt-BR": "12 h"},
    ru="12 ч", ar="١٢ ساعة", it="12 h", nl="12 uur")

add("cooldown.24h",
    fr="24 h", de="24 Std.", es="24 h", **{"pt-BR": "24 h"},
    ru="24 ч", ar="٢٤ ساعة", it="24 h", nl="24 uur")

add("cooldown.2h",
    fr="2 h", de="2 Std.", es="2 h", **{"pt-BR": "2 h"},
    ru="2 ч", ar="ساعتان", it="2 h", nl="2 uur")

add("cooldown.3d",
    fr="3 jours", de="3 Tage", es="3 días", **{"pt-BR": "3 dias"},
    ru="3 дня", ar="٣ أيام", it="3 giorni", nl="3 dagen")

add("cooldown.flash",
    fr="Coup de tête · sprint", de="Kurzschluss · Sprint",
    es="Impulso · sprint", **{"pt-BR": "Impulso · sprint"},
    ru="Импульс · спринт", ar="اندفاع · سريع",
    it="Impulso · sprint", nl="Impuls · sprint")

add("cooldown.golden",
    fr="24 h en or", de="Goldene 24 Std.", es="24 h de oro",
    **{"pt-BR": "24 h de ouro"},
    ru="Золотые 24 ч", ar="٢٤ ساعة ذهبية", it="24 h d'oro", nl="Gouden 24 uur")

add("cooldown.hint",
    fr="On vous redemandera : toujours envie ?",
    de="Wir fragen nach: noch immer wollen?",
    es="Te preguntaremos: ¿lo sigues queriendo?",
    **{"pt-BR": "Vamos perguntar: ainda quer?"},
    ru="Мы спросим: всё ещё хотите?",
    ar="سنسألك: هل ما زلت تريده؟",
    it="Ti chiederemo: lo vuoi ancora?",
    nl="We vragen je: nog steeds nodig?")

add("cooldown.long",
    fr="Gros achat · marathon", de="Große Ausgabe · Marathon",
    es="Gasto grande · maratón", **{"pt-BR": "Gasto alto · maratona"},
    ru="Крупная покупка · марафон", ar="مصروف كبير · طويل",
    it="Spesa grossa · maratona", nl="Grote uitgave · marathon")

add("cooldown.normal",
    fr="Une demi-journée", de="Ein halber Tag", es="Medio día",
    **{"pt-BR": "Meio dia"},
    ru="Полдня", ar="نصف يوم", it="Mezza giornata", nl="Een halve dag")

add("cooldown.title",
    fr="Délai de réflexion", de="Bedenkzeit", es="Periodo de espera",
    **{"pt-BR": "Período de espera"},
    ru="Период ожидания", ar="فترة التأمل", it="Periodo di attesa", nl="Bedenktijd")

# ───────────── 表单字段 ─────────────
add("field.alternative",
    fr="Alternative", de="Alternative", es="Alternativa", **{"pt-BR": "Alternativa"},
    ru="Альтернатива", ar="بديل", it="Alternativa", nl="Alternatief")

add("field.alternativePlaceholder",
    fr="Une solution moins chère ? Ex. : boire de l'eau",
    de="Günstigere Lösung? Z. B. Leitungswasser trinken",
    es="¿Algo más barato? P. ej.: beber agua",
    **{"pt-BR": "Algo mais barato? Ex.: beber água"},
    ru="Есть дешевле? Например: просто выпить воды",
    ar="بديل أرخص؟ مثل: شرب الماء",
    it="Qualcosa di più economico? Es.: bere acqua",
    nl="Iets goedkopers? Bijv. gewoon water drinken")

add("field.category",
    fr="Catégorie", de="Kategorie", es="Categoría", **{"pt-BR": "Categoria"},
    ru="Категория", ar="الفئة", it="Categoria", nl="Categorie")

add("field.goods",
    fr="Ce que vous voulez acheter", de="Was du kaufen willst",
    es="Qué quieres comprar", **{"pt-BR": "O que você quer comprar"},
    ru="Что хотите купить", ar="ماذا تريد أن تشتري",
    it="Cosa vuoi comprare", nl="Wat je wilt kopen")

add("field.goodsPlaceholder",
    fr="Ex. : un bubble tea", de="Z. B. ein Bubble Tea",
    es="P. ej.: un té de burbujas", **{"pt-BR": "Ex.: um chá de bolhas"},
    ru="Напр.: бабл-ти", ar="مثل: كوب شاي فقاعات",
    it="Es.: un bubble tea", nl="Bijv. een bubble tea")

add("field.price",
    fr="Prix", de="Preis", es="Precio", **{"pt-BR": "Preço"},
    ru="Цена", ar="السعر", it="Prezzo", nl="Prijs")

add("field.pricePlaceholder",
    fr="0", de="0", es="0", **{"pt-BR": "0"},
    ru="0", ar="٠", it="0", nl="0")

add("field.reason",
    fr="Pourquoi l'acheter", de="Warum kaufen", es="Por qué comprarlo",
    **{"pt-BR": "Por que comprar"},
    ru="Зачем это нужно", ar="لماذا تشتريه", it="Perché comprarlo", nl="Waarom kopen")

add("field.reasonHint",
    fr="Chaque avis doit être justifié — vous verrez toutes les raisons.",
    de="Jede Bewertung braucht eine Begründung — du siehst alle.",
    es="Cada opinión lleva su razón, y tú las verás todas.",
    **{"pt-BR": "Cada opinião precisa de um motivo, e você verá todos."},
    ru="Каждое мнение должно быть обосновано — вы всё увидите.",
    ar="كل رأي يحتاج إلى سبب، وسترى جميعها.",
    it="Ogni parere deve essere motivato — li vedrai tutti.",
    nl="Elk oordeel moet onderbouwd zijn — je ziet ze allemaal.")

# 中文原文："说说你为什么想买它……审批员会认真看"
# 这里"审批员"在个人使用场景其实是"你自己"或"群里的人"，翻译用中性表达
add("field.reasonPlaceholder",
    fr="Dites pourquoi vous le voulez… ce sera lu attentivement",
    de="Sag, warum du es willst … es wird genau gelesen",
    es="Cuenta por qué lo quieres… se leerá con atención",
    **{"pt-BR": "Conte por que quer… vai ser lido com atenção"},
    ru="Расскажите, зачем это нужно… это прочтут внимательно",
    ar="قل لماذا تريده… سيُقرأ بعناية",
    it="Racconta perché lo vuoi… sarà letto con attenzione",
    nl="Vertel waarom je het wilt… het wordt goed gelezen")

# ───────────── 截图识别 ─────────────
add("import.failed",
    fr="Aucun texte détecté. Essayez une capture plus nette.",
    de="Kein Text erkannt. Versuch es mit einem schärferen Screenshot.",
    es="No se encontró texto. Prueba con una captura más nítida.",
    **{"pt-BR": "Nenhum texto encontrado. Tente uma captura mais nítida."},
    ru="Текст не распознан. Попробуйте более чёткий скриншот.",
    ar="لم يتم العثور على نص. جرّب لقطة أوضح.",
    it="Nessun testo trovato. Prova uno screenshot più nitido.",
    nl="Geen tekst gevonden. Probeer een scherpere schermafbeelding.")

add("import.highConfidence",
    fr="C'est bon, il ne reste qu'à envoyer.",
    de="Passt. Du kannst direkt einreichen.",
    es="Todo listo. Solo falta enviar.",
    **{"pt-BR": "Tudo pronto. Basta enviar."},
    ru="Готово. Можно отправлять.",
    ar="كل شيء جاهز. أرسله مباشرة.",
    it="Tutto pronto. Devi solo inviare.",
    nl="Helemaal klaar. Je hoeft alleen nog te versturen.")

add("import.lowConfidence",
    fr="Je ne suis pas très sûr — vérifiez, s'il vous plaît.",
    de="Nicht ganz sicher — bitte kurz prüfen.",
    es="No estoy muy seguro, revísalo por favor.",
    **{"pt-BR": "Não tenho certeza, confira por favor."},
    ru="Не очень уверен — пожалуйста, проверьте.",
    ar="لست متأكدًا تمامًا، يرجى التحقق.",
    it="Non sono molto sicuro, controlla per favore.",
    nl="Niet helemaal zeker — controleer het even.")

add("import.mediumConfidence",
    fr="Rempli. Vérifiez le montant avant d'envoyer.",
    de="Ausgefüllt. Prüfe den Betrag vor dem Senden.",
    es="Rellenado. Revisa el importe antes de enviar.",
    **{"pt-BR": "Preenchido. Confira o valor antes de enviar."},
    ru="Заполнено. Проверьте сумму перед отправкой.",
    ar="تم الملء. تحقق من المبلغ قبل الإرسال.",
    it="Compilato. Controlla l'importo prima di inviare.",
    nl="Ingevuld. Controleer het bedrag voor je verstuurt.")

add("import.pick",
    fr="Choisir", de="Auswählen", es="Elegir", **{"pt-BR": "Escolher"},
    ru="Выбрать", ar="اختيار", it="Scegli", nl="Kiezen")

add("import.subtitle",
    fr="Article et prix, sans rien taper",
    de="Artikel und Preis, ohne Tippen",
    es="Artículo y precio, sin teclear",
    **{"pt-BR": "Item e preço, sem digitar"},
    ru="Товар и цена — без набора текста",
    ar="المنتج والسعر دون كتابة",
    it="Articolo e prezzo, senza digitare",
    nl="Artikel en prijs, zonder typen")

add("import.title",
    fr="Remplir depuis une capture", de="Aus Screenshot ausfüllen",
    es="Rellenar desde una captura", **{"pt-BR": "Preencher pela captura"},
    ru="Заполнить по скриншоту", ar="التعبئة من لقطة الشاشة",
    it="Compila da screenshot", nl="Invullen vanaf schermafbeelding")

# ───────────── 「我的」页 ─────────────
add("mine.coolingEnded",
    fr="Délai de réflexion terminé", de="Bedenkzeit vorbei",
    es="Periodo de espera terminado", **{"pt-BR": "Período de espera encerrado"},
    ru="Время ожидания истекло", ar="انتهت فترة التأمل",
    it="Periodo di attesa finito", nl="Bedenktijd voorbij")

add("mine.coolingLeftHM %lld %lld",
    fr="Encore %lld h %lld min", de="Noch %lld Std. %lld Min.",
    es"Qu": "", **{"pt-BR": ""},
    ru="", ar="", it="", nl="")

add("mine.coolingLeftM %lld",
    fr="Encore %lld min", de="Noch %lld Min.", es="Quedan %lld min",
    **{"pt-BR": "Faltam %lld min"},
    ru="Осталось %lld мин", ar="متبقي %lld دقيقة",
    it="Mancano %lld min", nl="Nog %lld min")

add("mine.coolingSection",
    fr="Compte à rebours", de="Countdown", es="Cuenta atrás",
    **{"pt-BR": "Contagem regressiva"},
    ru="Обратный отсчёт", ar="العد التنازلي",
    it="Conto alla rovescia", nl="Aftellen")

add("mine.dayUnit",
    fr="jours", de="Tage", es="días", **{"pt-BR": "dias"},
    ru="дн.", ar="يوم", it="giorni", nl="dagen")

add("mine.history",
    fr="Mes avis", de="Meine Bewertungen", es="Mis opiniones",
    **{"pt-BR": "Minhas opiniões"},
    ru="Мои оценки", ar="تقييماتي", it="I miei pareri", nl="Mijn oordelen")

add("mine.historyEmpty",
    fr="Aucun avis pour l'instant", de="Noch keine Bewertungen",
    es="Aún no hay opiniones", **{"pt-BR": "Nenhuma opinião ainda"},
    ru="Оценок пока нет", ar="لا توجد تقييمات بعد",
    it="Nessun parere ancora", nl="Nog geen oordelen")

add("mine.neverMind",
    fr="Laisse tomber", de="Lass es", es="Déjalo", **{"pt-BR": "Deixa pra lá"},
    ru="Передумал, не буду", ar="لا داعي، لن أشترِ",
    it="Lascia stare", nl="Laat maar")

add("mine.savedTotal",
    fr="Refusé · économisé", de="Abgelehnt · gespart",
    es="Rechazado · ahorrado", **{"pt-BR": "Recusado · economizado"},
    ru="Отклонено · сэкономлено", ar="مرفوض · موفّر",
    it="Respinto · risparmiato", nl="Afgekeurd · bespaard")

add("mine.stillWant",
    fr="Toujours envie", de="Immer noch", es="Lo sigo queriendo",
    **{"pt-BR": "Ainda quero"},
    ru="Всё ещё хочу", ar="ما زلت أريده", it="Lo voglio ancora", nl="Nog steeds nodig")

add("mine.streak",
    fr="Série", de="Serie", es="Racha", **{"pt-BR": "Sequência"},
    ru="Серия", ar="سلسلة", it="Serie", nl="Reeks")

add("mine.streakHint",
    fr="Un jour d'arrêt et ça repart de zéro",
    de="Ein Tag Pause setzt zurück",
    es="Un día sin racha y vuelve a cero",
    **{"pt-BR": "Um dia sem e volta a zero"},
    ru="Пропустите день — начнётся заново",
    ar="يوم واحد بدون سلسلة يعيدها إلى الصفر",
    it="Un giorno di pausa e riparte da zero",
    nl="Eén dag overslaan en je begint opnieuw")

add("mine.streakStart",
    fr="Refusez-en un aujourd'hui pour commencer",
    de="Lehn heute einen Kauf ab, um zu starten",
    es="Rechaza uno hoy para empezar",
    **{"pt-BR": "Recuse um hoje para começar"},
    ru="Отклоните одну покупку сегодня — и начнёте",
    ar="ارفض عملية شراء اليوم لتبدأ",
    it="Rifiuta un acquisto oggi per iniziare",
    nl="Keur er vandaag één af om te beginnen")

add("mine.whereSaved",
    fr="Où vous avez économisé", de="Wo du gespart hast",
    es="Dónde ahorraste", **{"pt-BR": "Onde você economizou"},
    ru="Где сэкономлено", ar="أين وفّرت",
    it="Dove hai risparmiato", nl="Waar je hebt bespaard")

# ───────────── 通知 ─────────────
add("notify.cooldownBody %@ %@",
    fr="« %@ » %@ — toujours envie ?",
    de="„%@“ %@ — noch immer wollen?",
    es="«%@» %@ — ¿lo sigues queriendo?",
    **{"pt-BR": "“%@” %@ — ainda quer?"},
    ru="«%@» %@ — всё ещё хотите?",
    ar="«%@» %@ — هل ما زلت تريده؟",
    it="«%@» %@ — lo vuoi ancora?",
    nl="“%@” %@ — nog steeds nodig?")

add("notify.cooldownTitle",
    fr="Le délai est écoulé", de="Bedenkzeit vorbei",
    es="El plazo terminó", **{"pt-BR": "O prazo terminou"},
    ru="Время ожидания прошло", ar="انتهت فترة التأمل",
    it="Il tempo è scaduto", nl="De tijd is om")

add("notify.savedBody",
    fr="Cet argent est resté dans votre poche.",
    de="Dieses Geld bleibt in deiner Tasche.",
    es="Ese dinero se quedó en tu bolsillo.",
    **{"pt-BR": "Esse dinheiro ficou no seu bolso."},
    ru="Эти деньги остались у вас в кармане.",
    ar="هذا المال بقي في جيبك.",
    it="Quei soldi sono rimasti in tasca tua.",
    nl="Dat geld bleef in je zak.")

add("notify.savedTitle %@",
    fr="Économisé %@", de="Gespart: %@", es="Ahorrado %@", **{"pt-BR": "Economizado %@"},
    ru="Сэкономлено %@", ar="تم توفير %@", it="Risparmiato %@", nl="Bespaard %@")
