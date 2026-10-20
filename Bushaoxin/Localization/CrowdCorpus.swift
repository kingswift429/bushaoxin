import Foundation

/// 模拟网友语料（多语言）。
///
/// 冷启动阶段广场的"人气"全靠这批语料，如果海外用户看到的是中文理由，
/// 产品的本地化感会立刻穿帮。所以语料必须跟着语言走。
enum CrowdCorpus {

    /// 简体中文
    static let zhHans: (reject: [String], pass: [String]) = (
        reject: [
            "先冷静 24 小时，睡一觉大概就不想了。",
            "这个价格能买三顿正经饭了，不值。",
            "同类平替很多，搜一下能省一半。",
            "你上个月是不是也买过差不多的？",
            "先加入购物车放三天，还想要再说。",
            "不是刚需，是情绪在花钱。",
            "这个钱省下来，年底能心疼自己一次。",
            "看评论说质量一般，别踩雷。",
            "有更便宜质量也好的，去看博主的测评。",
            "你这理由说服不了我，重写。"
        ],
        pass: [
            "确实需要，买吧。",
            "这个价格合理，不算冲动。",
            "支持你，人生苦短。",
            "刚需就买，别内耗。",
            "看得出你真的很想要，值。",
            "用得久就是划算，通过。",
            "替你想了一圈，没有更好的替代，过。",
            "这钱花得踏实，不烧心。"
        ]
    )

    /// English
    static let en: (reject: [String], pass: [String]) = (
        reject: [
            "Sleep on it for 24 hours. You'll probably forget about it.",
            "That price buys three proper meals. Not worth it.",
            "There are plenty of cheaper equivalents. Search first.",
            "Didn't you buy something like this last month?",
            "Add to cart, wait three days, then ask again.",
            "Not a need — your mood is spending.",
            "Skip it and you'll thank yourself at year end.",
            "Reviews say the quality is mediocre. Don't risk it.",
            "There's a cheaper one with better reviews. Go read up.",
            "Your reason doesn't convince me. Try again."
        ],
        pass: [
            "You actually need it. Buy.",
            "Fair price, not an impulse.",
            "Go for it — life is short.",
            "If it's a real need, just buy it.",
            "You clearly want it. Worth it.",
            "You'll use it for years. Approved.",
            "I looked for alternatives. Nothing better.",
            "This is money well spent. Sleep fine."
        ]
    )

    /// 日本語
    static let ja: (reject: [String], pass: [String]) = (
        reject: [
            "24時間寝かせましょう。たぶん忘れます。",
            "その値段ならちゃんとした食事が3回できます。",
            "似たもので安いものがあります。まず検索を。",
            "先月も似たようなもの買いませんでした？",
            "カートに入れて3日待ってから決めましょう。",
            "必要じゃなくて、気分がお金を使っています。",
            "今は我慢すると、年末に自分を褒められます。",
            "レビューで品質が今ひとつと言われています。",
            "安くて評価の高いものがあります。調べてみては。",
            "その理由では納得できません。書き直してください。"
        ],
        pass: [
            "本当に必要ですね。買ってよし。",
            "妥当な価格で、衝動買いではありません。",
            "応援します。人生は短い。",
            "必要なものなら買いましょう。",
            "本当に欲しそうですね。価値あり。",
            "長く使えるならお得です。承認。",
            "代替案を探しましたが、これ以上のものはありません。",
            "後悔しない買い物です。"
        ]
    )

    /// 한국어
    static let ko: (reject: [String], pass: [String]) = (
        reject: [
            "24시간 두고 보세요. 아마 잊을 거예요.",
            "그 돈이면 제대로 된 밥을 세 끼 먹을 수 있어요.",
            "비슷한데 더 싼 게 많아요. 검색부터 해 보세요.",
            "지난달에도 비슷한 걸 사지 않았나요?",
            "장바구니에 넣고 3일 뒤에 다시 생각해 보세요.",
            "필요해서가 아니라 기분이 돈을 쓰고 있어요.",
            "지금 참으면 연말에 스스로를 칭찬하게 될 거예요.",
            "리뷰에서 품질이 별로라고 하네요. 걸러요.",
            "더 싸고 평가 좋은 게 있어요. 찾아보세요.",
            "이유가 납득이 안 돼요. 다시 써 주세요."
        ],
        pass: [
            "정말 필요하네요. 사세요.",
            "가격이 적당하고 충동적이지 않아요.",
            "응원합니다. 인생은 짧아요.",
            "필수품이면 그냥 사세요.",
            "간절해 보여요. 살 만해요.",
            "오래 쓰면 오히려 이득입니다. 승인.",
            "대안을 찾아봤는데 더 나은 게 없네요.",
            "후회 없는 지출이에요."
        ]
    )

    /// Français
    static let fr: (reject: [String], pass: [String]) = (
        reject: [
            "Attends 24 h. Dans 9 cas sur 10, l'envie passe.",
            "Ce prix, c'est trois vrais repas. Non.",
            "Il existe des équivalents bien moins chers. Cherche avant.",
            "Tu n'as pas déjà acheté un truc pareil le mois dernier ?",
            "Mets-le dans le panier, attends trois jours, on en reparle.",
            "Ce n'est pas un besoin, c'est une humeur qui dépense.",
            "Économise-le et tu te remercieras en fin d'année.",
            "Les avis disent que la qualité est moyenne. Prends pas le risque.",
            "Une alternative moins chère existe. Va voir les tests.",
            "Ta raison ne me convainc pas. Rédige encore."
        ],
        pass: [
            "C'est vraiment nécessaire. Vas-y.",
            "Le prix est raisonnable, ce n'est pas un coup de tête.",
            "Je te soutiens. La vie est courte.",
            "Si c'est indispensable, achète, arrête de te torturer.",
            "On sent que tu le veux vraiment. Ça vaut le coup.",
            "Si tu le gardes longtemps, c'est rentable. Validé.",
            "J'ai cherché : pas de meilleure alternative. Feu vert.",
            "Un achat sans regret."
        ]
    )

    /// Deutsch
    static let de: (reject: [String], pass: [String]) = (
        reject: [
            "Warte 24 Stunden. In neun von zehn Fällen vergeht die Lust.",
            "Für den Preis gibt es drei anständige Mahlzeiten. Nein.",
            "Es gibt viel günstigere Alternativen. Such erst.",
            "Hast du nicht letzten Monat schon sowas gekauft?",
            "In den Warenkorb, drei Tage warten, dann nochmal fragen.",
            "Kein Bedarf, sondern die Laune gibt Geld aus.",
            "Sparen und du dankst dir am Jahresende.",
            "Laut Rezensionen ist die Qualität mittelmäßig. Lass es.",
            "Es gibt etwas Günstigeres mit guter Qualität. Schau die Tests.",
            "Deine Begründung überzeugt mich nicht. Nochmal."
        ],
        pass: [
            "Wirklich nötig. Kauf es.",
            "Der Preis ist fair, kein Kurzschluss.",
            "Ich unterstütze dich. Das Leben ist kurz.",
            "Wenn du es brauchst, kaufe. Grübeln hilft nicht.",
            "Man merkt, dass du es wirklich willst. Lohnt sich.",
            "Lange Nutzung = günstig. Genehmigt.",
            "Ich habe nachgedacht: keine bessere Alternative. Durch.",
            "Ein Kauf ohne Reue."
        ]
    )

    /// Español
    static let es: (reject: [String], pass: [String]) = (
        reject: [
            "Espera 24 h. En nueve de cada diez, se te pasa.",
            "Con ese precio comes tres veces bien. No.",
            "Hay equivalentes mucho más baratos. Busca primero.",
            "¿No compraste algo parecido el mes pasado?",
            "Añádelo al carrito, espera tres días y volvemos a hablar.",
            "No es una necesidad, es el ánimo gastando.",
            "Ahorra esto y te lo agradecerás a fin de año.",
            "Las reseñas dicen que la calidad es regular. No arriesgues.",
            "Hay algo más barato y bueno. Mira los análisis.",
            "Tu razón no me convence. Reescríbela."
        ],
        pass: [
            "Lo necesitas de verdad. Cómpralo.",
            "El precio es razonable, no es un impulso.",
            "Te apoyo. La vida es corta.",
            "Si es imprescindible, compra y deja de darle vueltas.",
            "Se nota que lo quieres mucho. Vale la pena.",
            "Si lo usas mucho tiempo, sale rentable. Aprobado.",
            "Le di una vuelta: no hay mejor alternativa. Adelante.",
            "Un gasto sin remordimientos."
        ]
    )

    /// Português (Brasil)
    static let ptBR: (reject: [String], pass: [String]) = (
        reject: [
            "Espera 24 h. Em nove de dez vezes, a vontade passa.",
            "Com esse preço dá pra comer bem três vezes. Não.",
            "Tem equivalente bem mais barato. Pesquisa antes.",
            "Você não comprou algo parecido mês passado?",
            "Bota no carrinho, espera três dias e a gente conversa.",
            "Não é necessidade, é o humor gastando.",
            "Guarda isso e você vai se agradecer no fim do ano.",
            "As avaliações dizem que a qualidade é mediana. Não arrisca.",
            "Tem opção mais barata e boa. Olha os reviews.",
            "Sua justificativa não me convenceu. Escreve de novo."
        ],
        pass: [
            "É realmente necessário. Compra.",
            "O preço é justo, não é impulso.",
            "Tô contigo. A vida é curta.",
            "Se é essencial, compra e para de sofrer.",
            "Dá pra ver que você quer muito. Vale a pena.",
            "Se usar por muito tempo, compensa. Aprovado.",
            "Pensei aqui: não tem alternativa melhor. Passa.",
            "Um gasto sem arrependimento."
        ]
    )

    /// Русский
    static let ru: (reject: [String], pass: [String]) = (
        reject: [
            "Подожди 24 часа. В девяти случаях из десяти желание пройдёт.",
            "На эти деньги можно три раза нормально поесть. Нет.",
            "Есть куда более дешёвые аналоги. Поищи сначала.",
            "Ты же покупал что-то похожее в прошлом месяце?",
            "Положи в корзину, подожди три дня, потом поговорим.",
            "Это не потребность, это настроение тратит.",
            "Отложи — и в конце года спасибо себе скажешь.",
            "В отзывах пишут, что качество среднее. Не рискуй.",
            "Есть дешевле и не хуже. Посмотри обзоры.",
            "Твой довод меня не убедил. Перепиши."
        ],
        pass: [
            "Действительно нужно. Бери.",
            "Цена разумная, это не импульс.",
            "Поддерживаю. Жизнь коротка.",
            "Если необходимо — покупай, не мучай себя.",
            "Видно, что очень хочешь. Стоит того.",
            "Если надолго — выгодно. Одобряю.",
            "Подумал: лучшей альтернативы нет. Проходит.",
            "Покупка без сожалений."
        ]
    )

    /// العربية
    static let ar: (reject: [String], pass: [String]) = (
        reject: [
            "انتظر ٢٤ ساعة. في تسع حالات من عشر، تزول الرغبة.",
            "بهذا السعر تأكل ثلاث وجبات محترمة. لا.",
            "هناك بدائل أرخص بكثير. ابحث أولًا.",
            "ألم تشترِ شيئًا مشابهًا الشهر الماضي؟",
            "ضعه في السلة، انتظر ثلاثة أيام، ثم نتحدث.",
            "ليست حاجة، بل المزاج هو من ينفق.",
            "وفّرها وستشكر نفسك في نهاية العام.",
            "التقييمات تقول إن الجودة متوسطة. لا تخاطر.",
            "يوجد أرخص وبجودة جيدة. شاهد المراجعات.",
            "سببك لم يقنعني. أعد كتابته."
        ],
        pass: [
            "أنت تحتاجه فعلًا. اشترِه.",
            "السعر معقول، ليس اندفاعًا.",
            "أدعمك. الحياة قصيرة.",
            "إن كان ضروريًا فاشترِ ولا تُرهق نفسك.",
            "واضح أنك تريده بشدة. يستحق.",
            "إن استخدمته طويلًا فهو مجدٍ. موافقة.",
            "فكرت معك: لا يوجد بديل أفضل. اجتز.",
            "مصروف بلا ندم."
        ]
    )

    /// Italiano
    static let it: (reject: [String], pass: [String]) = (
        reject: [
            "Aspetta 24 ore. Nove volte su dieci la voglia passa.",
            "Con quel prezzo ci mangi bene tre volte. No.",
            "Ci sono equivalenti molto più economici. Cerca prima.",
            "Non hai comprato una cosa simile il mese scorso?",
            "Mettilo nel carrello, aspetta tre giorni, poi ne parliamo.",
            "Non è un bisogno, è l'umore che spende.",
            "Risparmialo e a fine anno ti ringrazierai.",
            "Le recensioni dicono che la qualità è media. Non rischiare.",
            "C'è di meglio a meno. Guarda le prove.",
            "La tua motivazione non mi convince. Riscrivila."
        ],
        pass: [
            "Ti serve davvero. Compra.",
            "Il prezzo è giusto, non è un impulso.",
            "Ti sostengo. La vita è breve.",
            "Se è indispensabile, compra e smetti di tormentarti.",
            "Si vede che lo vuoi molto. Vale.",
            "Se lo usi a lungo conviene. Approvato.",
            "Ci ho pensato: nessuna alternativa migliore. Passa.",
            "Una spesa senza rimpianti."
        ]
    )

    /// Nederlands
    static let nl: (reject: [String], pass: [String]) = (
        reject: [
            "Wacht 24 uur. In negen van de tien gevallen gaat het over.",
            "Voor dat geld eet je drie keer fatsoenlijk. Nee.",
            "Er zijn veel goedkopere alternatieven. Zoek eerst.",
            "Had je vorige maand niet zoiets gekocht?",
            "In je winkelwagen, drie dagen wachten, dan praten we verder.",
            "Geen behoefte, maar je humeur geeft geld uit.",
            "Sla het over en je bedankt jezelf eind dit jaar.",
            "Uit reviews blijkt de kwaliteit matig. Neem geen risico.",
            "Er is goedkopers met goede kwaliteit. Bekijk de tests.",
            "Je reden overtuigt me niet. Schrijf opnieuw."
        ],
        pass: [
            "Je hebt het echt nodig. Kopen.",
            "De prijs is redelijk, geen impuls.",
            "Ik steun je. Het leven is kort.",
            "Als het noodzakelijk is, koop en tob niet verder.",
            "Je ziet er echt naar uit. De moeite waard.",
            "Lang gebruiken is voordelig. Goedgekeurd.",
            "Ik heb nagedacht: geen beter alternatief. Door.",
            "Een aankoop zonder spijt."
        ]
    )

    /// 按当前语言取语料；不支持的语言回落到英文
    static func current() -> (reject: [String], pass: [String]) {
        let code = Locale.current.language.languageCode?.identifier ?? "en"
        switch code {
        case "zh": return zhHans
        case "ja": return ja
        case "ko": return ko
        case "fr": return fr
        case "de": return de
        case "es": return es
        case "pt": return ptBR
        case "ru": return ru
        case "ar": return ar
        case "it": return it
        case "nl": return nl
        default: return en
        }
    }
}
