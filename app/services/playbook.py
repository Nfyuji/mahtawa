"""Research-grounded strategy primitives.

This module deliberately separates official methodology sources from live trend
observations. The generated opportunities are labelled as hypotheses until a user
checks them in the linked tools or connects a supported data source.
"""

from __future__ import annotations

from datetime import date
from urllib.parse import quote_plus


SOURCE_CATALOG = [
    {
        "key": "tiktok_creative_center",
        "publisher": "TikTok for Business",
        "title": "Creative Center — Trends & creative inspiration",
        "url": "https://ads.tiktok.com/business/creativecenter/",
        "used_for": "التحقق اليدوي من الهاشتاقات والأغاني والمبدعين والإعلانات الرائجة بحسب السوق.",
        "evidence_type": "مصدر رسمي للتحقق اليدوي",
        "last_reviewed": "2026-10-14",
    },
    {
        "key": "tiktok_trends_help",
        "publisher": "TikTok for Business",
        "title": "How to use Trends in Creative Center",
        "url": "https://ads.tiktok.com/help/article/how-to-use-trends",
        "used_for": "منهجية قراءة الاتجاهات والبحث عنها داخل Creative Center.",
        "evidence_type": "إرشاد رسمي",
        "last_reviewed": "2026-10-14",
    },
    {
        "key": "youtube_analytics",
        "publisher": "YouTube Help",
        "title": "Measure key moments for audience retention",
        "url": "https://support.google.com/youtube/answer/9314415",
        "used_for": "ربط اختبار الخطاف بالاحتفاظ الفعلي ومقارنة أداء أجزاء الفيديو.",
        "evidence_type": "إرشاد رسمي للقياس",
        "last_reviewed": "2026-10-14",
    },
    {
        "key": "youtube_discovery",
        "publisher": "YouTube Help",
        "title": "Search and discovery tips",
        "url": "https://support.google.com/youtube/answer/11914225",
        "used_for": "بناء محتوى يخدم اهتمام المشاهد ورضاه بدل محاولة خداع الخوارزمية.",
        "evidence_type": "إرشاد رسمي",
        "last_reviewed": "2026-10-14",
    },
    {
        "key": "instagram_best_practices",
        "publisher": "Instagram",
        "title": "Best Practices education hub for creators",
        "url": "https://about.instagram.com/blog/announcements/best-practices-education-hub-creators-instagram",
        "used_for": "إطار التحسين عبر الإنشاء والتفاعل والوصول والقياس مع توصيات الحساب نفسه.",
        "evidence_type": "إعلان وإرشاد رسمي",
        "last_reviewed": "2026-10-14",
    },
    {
        "key": "google_trends_help",
        "publisher": "Google Trends",
        "title": "Google Trends Help",
        "url": "https://support.google.com/trends/",
        "used_for": "مقارنة اهتمام البحث النسبي والتحقق من الموسمية والمناطق، لا قياس حجم بحث مطلق.",
        "evidence_type": "مركز مساعدة رسمي",
        "last_reviewed": "2026-10-14",
    },
]


PLATFORM_LABELS = {
    "tiktok": "تيك توك",
    "instagram": "إنستغرام",
    "youtube": "يوتيوب",
    "x": "X",
    "facebook": "فيسبوك",
}


PLATFORM_PLAYBOOKS = {
    "tiktok": {
        "role": "اكتشاف سريع واختبار زوايا جديدة",
        "formats": ["فيديو قصير", "رد بالفيديو", "سلسلة من 3 أجزاء"],
        "signal": "الاحتفاظ، الإكمال، إعادة المشاهدة والمشاركة",
        "source_key": "tiktok_creative_center",
    },
    "instagram": {
        "role": "بناء الثقة وتحويل الفكرة إلى حفظ أو إرسال",
        "formats": ["Reel", "كاروسيل", "قصة تفاعلية"],
        "signal": "مدة المشاهدة، الحفظ، الإرسال وزيارات الملف",
        "source_key": "instagram_best_practices",
    },
    "youtube": {
        "role": "التقاط نية البحث وبناء مكتبة طويلة العمر",
        "formats": ["Short", "شرح مركز", "إجابة على سؤال بحثي"],
        "signal": "الاحتفاظ، متوسط المشاهدة ورضا الجمهور",
        "source_key": "youtube_analytics",
    },
    "x": {
        "role": "اختبار الرسائل والآراء والمحادثة المباشرة",
        "formats": ["منشور رأي", "سلسلة", "لقطة مع تعليق"],
        "signal": "الردود، إعادة النشر، النقرات وزيارات الملف",
        "source_key": "google_trends_help",
    },
    "facebook": {
        "role": "توزيع قصص عملية وبناء تفاعل مجتمعي",
        "formats": ["فيديو", "منشور قصة", "كاروسيل"],
        "signal": "المشاهدة، المشاركة، التعليقات والنقرات",
        "source_key": "instagram_best_practices",
    },
}


OBJECTIVES = {
    "awareness": {
        "label": "توسيع الوعي المؤهل",
        "north_star": "الوصول إلى جمهور مناسب مع احتفاظ ومشاركة، لا مجرد ظهور خام.",
        "primary_kpi": "الوصول المؤهل + الاحتفاظ بالمشاهدة",
        "supporting": ["معدل الإكمال", "المشاركات/الإرسال", "زيارات الملف"],
        "cta": "احفظ أو شارك المحتوى",
        "mix": {"discovery": 40, "trust": 25, "engagement": 25, "conversion": 10},
    },
    "leads": {
        "label": "توليد عملاء محتملين",
        "north_star": "تحويل الاهتمام إلى محادثة أو تسجيل يمكن تتبعه.",
        "primary_kpi": "العملاء المحتملون المؤهلون",
        "supporting": ["نقرات الرابط", "بدء المحادثات", "تحويل صفحة العرض"],
        "cta": "اطلب الخطوة التالية بوضوح",
        "mix": {"discovery": 25, "trust": 30, "engagement": 15, "conversion": 30},
    },
    "sales": {
        "label": "دعم المبيعات",
        "north_star": "تقليل غموض القرار وتحويل الجمهور الجاهز إلى إجراء تجاري.",
        "primary_kpi": "التحويلات المنسوبة للمحتوى",
        "supporting": ["طلبات العرض", "بدء الشراء", "الاعتراضات المحلولة"],
        "cta": "ابدأ الشراء أو احجز الآن",
        "mix": {"discovery": 20, "trust": 30, "engagement": 10, "conversion": 40},
    },
    "community": {
        "label": "تنمية المجتمع والتفاعل",
        "north_star": "زيادة المحادثات المفيدة والعودة المتكررة للجمهور.",
        "primary_kpi": "المشاركات ذات المعنى وعودة الجمهور",
        "supporting": ["التعليقات النوعية", "الحفظ", "المتابعون العائدون"],
        "cta": "شارك خبرتك أو أجب عن السؤال",
        "mix": {"discovery": 25, "trust": 20, "engagement": 45, "conversion": 10},
    },
}


def _short(value: str | None, words: int = 7, fallback: str = "جمهورك") -> str:
    clean = " ".join((value or "").split())
    if not clean:
        return fallback
    parts = clean.split()
    return " ".join(parts[:words]) + ("…" if len(parts) > words else "")


def build_strategy_brief(brand, item_count: int) -> dict:
    objective = OBJECTIVES.get(brand.marketing_objective, OBJECTIVES["awareness"])
    audience = _short(brand.audience, 11)
    industry = _short(brand.industry, 6, "مجالك")
    offer = _short(brand.offer or brand.description, 11, "عرضك الأساسي")
    posts_per_week = max(2, min(7, brand.posts_per_week or 5))
    platforms = brand.platforms or ["tiktok", "instagram"]

    mix = objective["mix"]
    pillars = [
        {
            "name": f"أسئلة ومشكلات {audience}",
            "function": "discovery",
            "label": "اكتشاف",
            "percent": mix["discovery"],
            "job": "تسمية المشكلة بلغة الجمهور وفتح باب الاكتشاف.",
            "example": f"أخطاء شائعة مرتبطة بـ{_short(brand.problem, 7, 'المشكلة الأساسية')}",
        },
        {
            "name": f"خبرة عملية في {industry}",
            "function": "trust",
            "label": "ثقة",
            "percent": mix["trust"],
            "job": "إثبات الفهم عبر خطوات وقوالب قابلة للتطبيق.",
            "example": "شرح، قائمة تحقق، تفكيك قرار أو اعتراض.",
        },
        {
            "name": f"دليل وتجربة {brand.name}",
            "function": "conversion",
            "label": "تحويل",
            "percent": mix["conversion"],
            "job": "ربط القيمة بالعرض ودعوة واحدة قابلة للقياس.",
            "example": f"قبل/بعد أو عرض استخدام واضح لـ{offer}",
        },
        {
            "name": "رأي ومجتمع",
            "function": "engagement",
            "label": "تفاعل",
            "percent": mix["engagement"],
            "job": "فتح نقاش يكشف لغة الجمهور واعتراضاته الحقيقية.",
            "example": "سؤال ثنائي، رأي مهني، رد على تعليق أو قصة عميل.",
        },
    ]

    platform_plans = []
    per_platform = max(1, round(posts_per_week / max(1, len(platforms))))
    for key in platforms:
        meta = PLATFORM_PLAYBOOKS.get(key, PLATFORM_PLAYBOOKS["instagram"])
        platform_plans.append(
            {
                "key": key,
                "label": PLATFORM_LABELS.get(key, key),
                "role": meta["role"],
                "formats": meta["formats"],
                "signal": meta["signal"],
                "cadence": f"نقطة بداية: {per_platform}–{per_platform + 1} منشور أسبوعيًا ثم التعديل حسب الأداء والقدرة.",
                "source_key": meta["source_key"],
            }
        )

    assumptions = []
    for value, message in (
        (brand.audience_desire, "رغبة الجمهور غير مفصلة؛ صيغناها من العرض والمشكلة."),
        (brand.competitors, "لم تُضف منافسين؛ فرص الفجوات التنافسية تحتاج بحثًا يدويًا."),
        (brand.resources, "قدرة الإنتاج غير محددة؛ افترضنا تصويرًا خفيفًا بالجوال."),
        (brand.competitive_advantage, "الميزة التنافسية غير مكتملة؛ راجع رسائل التحويل."),
    ):
        if not value:
            assumptions.append(message)

    return {
        "objective": {
            "key": brand.marketing_objective or "awareness",
            "label": objective["label"],
            "north_star": objective["north_star"],
            "primary_kpi": objective["primary_kpi"],
            "supporting_kpis": objective["supporting"],
            "goal_text": brand.monthly_goal or objective["label"],
        },
        "positioning": {
            "audience": brand.audience,
            "problem": brand.problem,
            "desire": brand.audience_desire or "نتيجة أوضح بوقت وجهد أقل",
            "offer": brand.offer or brand.description,
            "promise": brand.competitive_advantage or f"حل عملي من {brand.name} للمشكلة الأساسية.",
            "voice": brand.brand_voice or "واضح، عملي، موثوق، دون مبالغة",
        },
        "pillars": pillars,
        "funnel_mix": [
            {"key": p["function"], "label": p["label"], "percent": p["percent"]}
            for p in pillars
        ],
        "platforms": platform_plans,
        "weekly_sprints": [
            {
                "week": 1,
                "title": "افهم المشكلة",
                "focus": "أسئلة الجمهور، الأخطاء، اللغة التي يستخدمونها.",
                "experiment": "اختبر خطاف ألم مقابل سؤال مباشر.",
            },
            {
                "week": 2,
                "title": "ابنِ الثقة",
                "focus": "خطوات عملية، قوائم تحقق، رأي خبير قابل للتطبيق.",
                "experiment": "اختبر فيديو سريع مقابل كاروسيل محفوظ.",
            },
            {
                "week": 3,
                "title": "قدّم الدليل",
                "focus": "استخدام، مقارنة عادلة، اعتراضات ونتائج يمكن إثباتها.",
                "experiment": "اختبر عرض المنتج مقابل قصة عميل موثقة.",
            },
            {
                "week": 4,
                "title": "حوّل وتعلّم",
                "focus": "CTA واضح، إعادة توزيع الأفضل، وتسجيل النتائج.",
                "experiment": "ثبّت الفكرة وغيّر الخطاف فقط لاختبار A/B.",
            },
        ],
        "measurement": {
            "primary": objective["primary_kpi"],
            "supporting": objective["supporting"],
            "baseline": "استخدم أول 7 أيام لبناء خط أساس لكل منصة وصيغة.",
            "decision_rule": "لا تعلن فائزًا من منشور واحد؛ قارِن نسخًا متقاربة وسجّل الحجم والسياق.",
        },
        "guardrails": [
            "لا تستخدم رقمًا أو نتيجة عميل بلا مصدر يمكن مراجعته.",
            "لا تسمِّ فكرةً ترندًا قبل التحقق من مصدر حديث وسوق مناسب.",
            "اجعل لكل قطعة وعدًا واحدًا وCTA واحدًا.",
            "طابق متن المحتوى مع وعد الخطاف وتجنب العنوان المضلل.",
        ],
        "assumptions": assumptions,
        "plan": {
            "days": 30,
            "items": item_count,
            "posts_per_week": posts_per_week,
            "status": "مسودة قابلة للمراجعة",
        },
        "trend_opportunities": build_trend_opportunities(brand),
    }


def build_trend_opportunities(brand) -> list[dict]:
    industry = _short(brand.industry, 5, "مجالك")
    problem = _short(brand.problem, 7, "مشكلة الجمهور")
    offer = _short(brand.offer or brand.description, 6, brand.name)
    audience = _short(brand.audience, 6)
    geo = "SA" if brand.market == "saudi" else ""
    year = date.today().year
    raw = [
        (
            "سؤال يتكرر الآن",
            f"لماذا {problem}؟",
            f"حوّل السؤال إلى إجابة مختصرة موجهة إلى {audience}.",
            f"{problem} {industry}",
        ),
        (
            "مقارنة قرار",
            f"{offer} أم الطريقة التقليدية؟",
            "اعرض متى يناسب كل خيار بصدق ثم وضّح زاوية علامتك.",
            f"{offer} مقارنة",
        ),
        (
            "خطأ أو معتقد يحتاج اختبارًا",
            f"أكثر اعتقاد يربك الناس في {industry}",
            "استخدم تعليقات العملاء أو أسئلة المبيعات لتحديد المعتقد الحقيقي.",
            f"أخطاء {industry}",
        ),
        (
            "زاوية موسمية",
            f"ما الذي تغيّر في {industry} خلال {year}؟",
            "تحقق من حداثة الإشارة ثم اربطها بقرار عملي، لا بتنبؤ غير موثق.",
            f"{industry} {year}",
        ),
    ]

    opportunities = []
    for index, (label, title, why, query) in enumerate(raw, start=1):
        encoded = quote_plus(query)
        opportunities.append(
            {
                "id": index,
                "label": label,
                "title": title,
                "why": why,
                "query": query,
                "status": "تحتاج تحققًا قبل الاستخدام",
                "evidence_type": "فرضية مولّدة من بيانات الشركة",
                "momentum": "غير متوفر",
                "checks": [
                    {
                        "label": "افتح Google Trends",
                        "source_key": "google_trends_help",
                        "url": f"https://trends.google.com/trends/explore?geo={geo}&q={encoded}",
                    },
                    {
                        "label": "تحقق في TikTok Creative Center",
                        "source_key": "tiktok_creative_center",
                        "url": "https://ads.tiktok.com/business/creativecenter/",
                    },
                    {
                        "label": "ابحث في YouTube",
                        "source_key": "youtube_discovery",
                        "url": f"https://www.youtube.com/results?search_query={encoded}",
                    },
                ],
            }
        )
    return opportunities


def build_idea_bank(brand, pillars: list[dict], count: int) -> list[dict]:
    audience = _short(brand.audience, 7)
    problem = _short(brand.problem, 9, "المشكلة الأساسية")
    desire = _short(brand.audience_desire, 8, "نتيجة أفضل بوقت أقل")
    industry = _short(brand.industry, 5, "المجال")
    offer = _short(brand.offer or brand.description, 8, brand.name)
    advantage = _short(brand.competitive_advantage, 8, f"طريقة {brand.name}")
    context = {
        "name": brand.name,
        "audience": audience,
        "problem": problem,
        "desire": desire,
        "industry": industry,
        "offer": offer,
        "advantage": advantage,
    }

    templates = [
        {
            "title": "3 أخطاء تجعل {problem} أسوأ",
            "goal": "discovery",
            "archetype": "pain",
            "points": [
                "الخطأ الأول: تتعامل مع {problem} كأنّه طبيعي وما توقف عنده",
                "أثره اليومي: وقتك يتقطع وكل مهمة تصير أبطأ بدون ما تحس",
                "أول تصحيح: ابدأ بخطوة واحدة داخل {name} واترك التبديل بين الأدوات",
            ],
            "visual": "قائمة الأخطاء مع علامة تصحيح أمام البديل",
            "promise": "سيعرف المشاهد أول خطوة تمنع تكرار المشكلة",
            "format_options": ["short_video", "carousel"],
            "metric": "الاحتفاظ + المشاركات",
            "repurpose": "كاروسيل: خطأ في كل شريحة",
            "effort": "خفيف",
        },
        {
            "title": "قبل أن تختار حلًا لـ{problem} اسأل هذه الأسئلة",
            "goal": "trust",
            "archetype": "curiosity",
            "points": ["هل يناسب وضعك الحالي؟", "ما التكلفة الخفية؟", "كيف ستقيس النتيجة؟"],
            "visual": "ثلاثة أسئلة تظهر واحدًا تلو الآخر",
            "promise": "قائمة تحقق تمنع قرارًا متسرعًا",
            "format_options": ["carousel", "short_video", "text_post"],
            "metric": "الحفظ + متوسط المشاهدة",
            "repurpose": "قائمة PDF صغيرة أو منشور مثبت",
            "effort": "خفيف",
        },
        {
            "title": "الطريقة القديمة مقابل {advantage}",
            "goal": "conversion",
            "archetype": "wow",
            "points": [
                "الطريقة القديمة: تسوي نفس المهمة يدويًا وبأدوات متفرقة",
                "بنفس المهمة داخل {name}: خطوات أقل ومسار أوضح",
                "الفرق اللي تشوفه: وقت أقل وتشتيت أقل بدون أرقام مختلقة",
            ],
            "visual": "شاشة منقسمة قبل/بعد دون أرقام مختلقة",
            "promise": "مقارنة واضحة تساعد على اتخاذ القرار",
            "format_options": ["short_video", "carousel"],
            "metric": "زيارات صفحة العرض + بدء المحادثات",
            "repurpose": "صورة مقارنة + قصة قصيرة",
            "effort": "متوسط",
        },
        {
            "title": "سؤال واحد لـ{audience}: ما أصعب جزء في {problem}؟",
            "goal": "engagement",
            "archetype": "headline",
            "points": [
                "خيارات واضحة: أ) الوقت ب) التكلفة ج) جودة النتيجة",
                "اطلب من المشاهد يكتب مثاله الحقيقي في التعليق",
                "حوّل أكثر إجابة تتكرر إلى محتوى الأسبوع الجاي",
            ],
            "visual": "السؤال على الشاشة مع خيارين أو ثلاثة",
            "promise": "محادثة تكشف لغة الجمهور الحقيقية",
            "format_options": ["text_post", "short_video", "story"],
            "metric": "التعليقات النوعية + الردود",
            "repurpose": "استفتاء قصة ثم فيديو رد",
            "effort": "خفيف",
        },
        {
            "title": "شرح {offer} كأنك تشرحه لصديق",
            "goal": "trust",
            "archetype": "pacing",
            "points": ["ابدأ بالموقف لا بالمزايا", "اربط ميزة بنتيجة", "اعرض الخطوة التالية فقط"],
            "visual": "تسجيل شاشة أو نموذج بسيط مع تعليق مباشر",
            "promise": "فهم العرض خلال أقل من دقيقة",
            "format_options": ["short_video", "carousel"],
            "metric": "الإكمال + الحفظ",
            "repurpose": "FAQ للموقع أو رسالة مبيعات",
            "effort": "خفيف",
        },
        {
            "title": "متى لا يكون {offer} مناسبًا لك؟",
            "goal": "trust",
            "archetype": "curiosity",
            "points": ["حدّد حالة عدم الملاءمة", "اشرح السبب بوضوح", "اذكر من يستفيد فعلًا"],
            "visual": "عمود مناسب / غير مناسب",
            "promise": "شفافية تبني ثقة وتصفّي العملاء المحتملين",
            "format_options": ["short_video", "text_post", "carousel"],
            "metric": "التعليقات + جودة العملاء المحتملين",
            "repurpose": "قسم «هل يناسبني؟» في صفحة العرض",
            "effort": "خفيف",
        },
        {
            "title": "اعتراض نسمعه دائمًا: هل {offer} يستحق؟",
            "goal": "conversion",
            "archetype": "headline",
            "points": ["اذكر الاعتراض حرفيًا", "اعترف بما هو صحيح فيه", "قدّم معيار قرار قابل للتحقق"],
            "visual": "تعليق عميل مجهول الهوية ثم رد منظم",
            "promise": "إجابة صادقة على اعتراض قبل الشراء",
            "format_options": ["short_video", "carousel", "text_post"],
            "metric": "بدء المحادثات + نقرات العرض",
            "repurpose": "رد جاهز لفريق المبيعات",
            "effort": "خفيف",
        },
        {
            "title": "من الكواليس: كيف نبني {desire}",
            "goal": "trust",
            "archetype": "wow",
            "points": ["أظهر الخطوة الأولى", "اشرح قرارًا مهمًا", "اكشف فحص الجودة"],
            "visual": "لقطات عملية حقيقية من الفريق أو المنتج",
            "promise": "رؤية العملية بدل الاكتفاء بالوعود",
            "format_options": ["short_video", "story"],
            "metric": "متوسط المشاهدة + الحفظ",
            "repurpose": "سلسلة كواليس أسبوعية",
            "effort": "متوسط",
        },
        {
            "title": "قائمة تحقق لـ{audience} قبل بدء الأسبوع",
            "goal": "trust",
            "archetype": "headline",
            "points": ["مهمة تمنع الخطأ", "مهمة تحسّن الوضوح", "مهمة تقيس النتيجة"],
            "visual": "Checklist قابلة للحفظ",
            "promise": "ثلاث مهام عملية يمكن تنفيذها اليوم",
            "format_options": ["carousel", "text_post", "short_video"],
            "metric": "الحفظ + المشاركة",
            "repurpose": "قالب قابل للتحميل",
            "effort": "خفيف",
        },
        {
            "title": "لو بدأنا من الصفر في {industry} هذه أول 3 خطوات",
            "goal": "discovery",
            "archetype": "curiosity",
            "points": ["حدد النتيجة أولًا", "اختر أصغر اختبار", "قِس قبل أن توسّع"],
            "visual": "طريق من ثلاث محطات",
            "promise": "مسار بداية بسيط بعيد عن التشتيت",
            "format_options": ["short_video", "carousel"],
            "metric": "الإكمال + المشاركات",
            "repurpose": "سلسلة من ثلاثة منشورات",
            "effort": "خفيف",
        },
        {
            "title": "تفكيك قرار: لماذا اخترنا {advantage}؟",
            "goal": "trust",
            "archetype": "curiosity",
            "points": ["المشكلة التي بدأنا منها", "البدائل التي درسناها", "المعيار الذي حسم القرار"],
            "visual": "مخطط قرار بثلاثة فروع",
            "promise": "منطق القرار، لا مجرد نتيجة نهائية",
            "format_options": ["text_post", "carousel", "short_video"],
            "metric": "مدة القراءة + الحفظ",
            "repurpose": "مقال قصير أو رسالة مؤسس",
            "effort": "متوسط",
        },
        {
            "title": "اختبار 30 ثانية: هل تعاني فعلًا من {problem}؟",
            "goal": "engagement",
            "archetype": "pacing",
            "points": ["سؤال تشخيص أول", "علامة تحذير ثانية", "نتيجة توجه للخطوة التالية"],
            "visual": "عداد 3 أسئلة مع نتيجة في النهاية",
            "promise": "تشخيص أولي بلا ادعاء طبي أو مهني",
            "format_options": ["short_video", "story", "carousel"],
            "metric": "الإكمال + التعليقات",
            "repurpose": "استفتاء تفاعلي في القصص",
            "effort": "خفيف",
        },
        {
            "title": "مصطلح في {industry} يربك الناس — بشرح بسيط",
            "goal": "discovery",
            "archetype": "headline",
            "points": ["قل التعريف البسيط", "اعط مثالًا يوميًا", "اشرح متى يهم"],
            "visual": "المصطلح كبير ثم مثال بصري",
            "promise": "فهم مصطلح واحد دون تعقيد",
            "format_options": ["short_video", "carousel", "text_post"],
            "metric": "الوصول من البحث + الحفظ",
            "repurpose": "قاموس أسبوعي للمجال",
            "effort": "خفيف",
        },
        {
            "title": "قصة قرار خاطئ علّمنا شيئًا عن {problem}",
            "goal": "trust",
            "archetype": "pain",
            "points": ["السياق دون تزيين", "القرار ولماذا بدا منطقيًا", "ما تغيّر بعدها"],
            "visual": "خط زمني: قبل / القرار / الدرس",
            "promise": "درس قابل للتطبيق من تجربة حقيقية",
            "format_options": ["short_video", "text_post"],
            "metric": "متوسط المشاهدة + الردود",
            "repurpose": "منشور مؤسس أو بريد تعليمي",
            "effort": "متوسط",
        },
        {
            "title": "5 إشارات تقول إن وقت {offer} قد حان",
            "goal": "conversion",
            "archetype": "pacing",
            "points": ["إشارة في الوقت", "إشارة في التكلفة", "إشارة في جودة النتيجة"],
            "visual": "عداد إشارات مع مثال لكل واحدة",
            "promise": "معيار يحدد توقيت القرار",
            "format_options": ["carousel", "short_video"],
            "metric": "الحفظ + نقرات صفحة العرض",
            "repurpose": "Quiz تأهيل أو FAQ",
            "effort": "خفيف",
        },
        {
            "title": "اطلب من خبير: سؤال من تعليقات {audience}",
            "goal": "engagement",
            "archetype": "headline",
            "points": ["اعرض السؤال", "أجب بجملة مباشرة", "أضف حالة استثناء"],
            "visual": "لقطة للتعليق بعد إخفاء أي بيانات شخصية",
            "promise": "جواب مباشر مبني على سؤال حقيقي",
            "format_options": ["short_video", "text_post"],
            "metric": "التعليقات + أسئلة جديدة",
            "repurpose": "سلسلة أسبوعية من الأسئلة",
            "effort": "خفيف",
        },
        {
            "title": "حالة استخدام: من {problem} إلى {desire}",
            "goal": "conversion",
            "archetype": "wow",
            "points": ["صف نقطة البداية", "اعرض الخطوات المستخدمة", "شارك نتيجة قابلة للإثبات فقط"],
            "visual": "رحلة مختصرة مع دليل أو لقطة حقيقية",
            "promise": "فهم كيف يعمل العرض في حالة واقعية",
            "format_options": ["short_video", "carousel", "text_post"],
            "metric": "طلبات التفاصيل + نقرات العرض",
            "repurpose": "دراسة حالة مطولة",
            "effort": "مرتفع",
        },
        {
            "title": "رأي غير مريح في {industry}: المزيد ليس دائمًا أفضل",
            "goal": "engagement",
            "archetype": "headline",
            "points": ["اذكر الرأي بوضوح", "اشرح متى يكون صحيحًا", "اطلب مثالًا مضادًا"],
            "visual": "جملة الرأي مع مقياس أكثر/أقل",
            "promise": "نقاش مهني يبتعد عن الكلام العام",
            "format_options": ["text_post", "short_video"],
            "metric": "الردود النوعية + إعادة النشر",
            "repurpose": "مناظرة قصيرة أو مساحة أسئلة",
            "effort": "خفيف",
        },
        {
            "title": "شيء واحد توقف عن فعله إذا أردت {desire}",
            "goal": "discovery",
            "archetype": "pain",
            "points": [
                "السلوك: تأجيل ترتيب الأدوات لأن «بكرة أصير منظم»",
                "ليش يعطّل: كل يوم تضيف طبقة فوضى فوق الثانية",
                "البديل الصغير: اغلق أداة واحدة اليوم ووحّد مهمتين في {name}",
            ],
            "visual": "علامة توقف ثم البديل",
            "promise": "تغيير واحد يمكن تجربته اليوم",
            "format_options": ["short_video", "text_post"],
            "metric": "الإكمال + المشاركة",
            "repurpose": "سطر افتتاحي لبريد أو إعلان",
            "effort": "خفيف",
        },
        {
            "title": "تجربة أسبوع: نثبت فكرة ونغيّر الخطاف فقط",
            "goal": "trust",
            "archetype": "pacing",
            "points": ["أنشئ نسختين متقاربتين", "غيّر الخطاف فقط", "قارن الاحتفاظ والسياق"],
            "visual": "A/B مع متغير واحد واضح",
            "promise": "طريقة اختبار تقلل التخمين",
            "format_options": ["short_video", "carousel"],
            "metric": "فرق الاحتفاظ بين النسختين",
            "repurpose": "قالب تجربة للفريق",
            "effort": "متوسط",
        },
        # --- 10 Viral-Focused Templates (new archetypes) ---
        {
            "title": "كل اللي يقولونه عن {industry} غلط — وهذا الدليل",
            "goal": "discovery",
            "archetype": "controversy",
            "points": ["اذكر المعتقد السائد", "اعرض لماذا هو خاطئ بدليل", "قدّم البديل الصحيح"],
            "visual": "نص المعتقد مشطوب + الحقيقة بجانبه",
            "promise": "كسر اعتقاد خاطئ يمنع {audience} من التقدّم",
            "format_options": ["short_video", "text_post"],
            "metric": "المشاركات + الردود + إعادة النشر",
            "repurpose": "سلسلة أسبوعية: خرافات المجال",
            "effort": "خفيف",
        },
        {
            "title": "من {problem} إلى {desire} — التحوّل الكامل خطوة بخطوة",
            "goal": "conversion",
            "archetype": "transformation",
            "points": ["صوّر نقطة البداية الحقيقية", "اعرض كل خطوة بالتفصيل", "أثبت النتيجة بدليل مرئي"],
            "visual": "فيديو قبل/بعد مع خط زمني واضح",
            "promise": "تحوّل حقيقي موثّق يمكن تكراره",
            "format_options": ["short_video", "carousel"],
            "metric": "الحفظ + نقرات صفحة العرض + المشاركات",
            "repurpose": "دراسة حالة تفصيلية أو ثريد",
            "effort": "مرتفع",
        },
        {
            "title": "السر اللي ما يقولونه عن {industry} — ولماذا يخفونه",
            "goal": "discovery",
            "archetype": "secret",
            "points": ["اكشف المعلومة المخفية", "اشرح لماذا تُخفى عادةً", "قدّم الفائدة العملية"],
            "visual": "نص مموّه يظهر تدريجيًا مع موسيقى تشويق",
            "promise": "معلومة حصرية تستحق المشاركة فورًا",
            "format_options": ["short_video", "text_post"],
            "metric": "المشاركات + الحفظ + إعادة المشاهدة",
            "repurpose": "سلسلة أسرار الصناعة",
            "effort": "خفيف",
        },
        {
            "title": "تحدّي 7 أيام: غيّر هذا الشي الواحد وشوف {desire}",
            "goal": "engagement",
            "archetype": "challenge",
            "points": ["حدّد التحدي بوضوح", "اشرح القواعد البسيطة", "اطلب مشاركة النتائج"],
            "visual": "عداد أيام 1-7 مع هدف واضح",
            "promise": "تجربة عملية يشارك فيها الجمهور ويرجع بالنتائج",
            "format_options": ["short_video", "story"],
            "metric": "التعليقات + المشاركات + المحتوى المُنشأ من الجمهور",
            "repurpose": "فيديو نتائج التحدي + سلسلة متابعة",
            "effort": "متوسط",
        },
        {
            "title": "قصة عميل: كان يعاني من {problem} — شوف وش صار",
            "goal": "conversion",
            "archetype": "storytelling",
            "points": ["ابدأ بالمعاناة الحقيقية", "اعرض لحظة التحوّل", "أنهِ بالنتيجة والدليل"],
            "visual": "مقابلة قصيرة أو تسجيل صوتي مع نص على الشاشة",
            "promise": "قصة حقيقية تثبت أن التحوّل ممكن",
            "format_options": ["short_video", "carousel", "text_post"],
            "metric": "وقت المشاهدة + بدء المحادثات + الحفظ",
            "repurpose": "شهادة للموقع + إعلان مدفوع",
            "effort": "مرتفع",
        },
        {
            "title": "آخر فرصة: {industry} يتغيّر الآن — وهذا اللي لازم تسويه",
            "goal": "discovery",
            "archetype": "urgency",
            "points": ["اشرح التغيير الحاصل", "وضّح تأثيره على {audience}", "قدّم خطوة فورية"],
            "visual": "عداد تنازلي أو رسم بياني للتغيّر",
            "promise": "فهم التغيير قبل المنافسين واتخاذ إجراء فوري",
            "format_options": ["short_video", "text_post"],
            "metric": "المشاركات + النقرات + سرعة التفاعل",
            "repurpose": "نشرة بريدية عاجلة أو بوست مثبّت",
            "effort": "خفيف",
        },
        {
            "title": "أرقام حقيقية: نتائج {name} مع {audience} هذا الشهر",
            "goal": "trust",
            "archetype": "social_proof",
            "points": ["اعرض الأرقام الفعلية فقط", "قارن بالشهر السابق", "اشرح ماذا تعني للعميل"],
            "visual": "لوحة أرقام حقيقية بتصميم نظيف",
            "promise": "شفافية بالأرقام تبني ثقة أعمق من أي وعد",
            "format_options": ["carousel", "short_video", "text_post"],
            "metric": "الحفظ + التعليقات النوعية + المتابعة",
            "repurpose": "تقرير شهري + محتوى LinkedIn",
            "effort": "متوسط",
        },
        {
            "title": "3 أشياء تمنيت أعرفها قبل ما أبدأ في {industry}",
            "goal": "trust",
            "archetype": "storytelling",
            "points": ["الشي الأول: ما كنت أتوقعه", "الشي الثاني: الخطأ اللي كلّفني", "الشي الثالث: القاعدة اللي غيّرت كل شي"],
            "visual": "وجه للكاميرا مع أرقام تظهر تباعًا",
            "promise": "اختصار سنوات خبرة في دقيقة",
            "format_options": ["short_video", "text_post"],
            "metric": "الإكمال + الحفظ + المشاركة مع الأصدقاء",
            "repurpose": "ثريد تويتر أو كاروسيل",
            "effort": "خفيف",
        },
        {
            "title": "اختبر نفسك: 5 علامات إنك تحتاج {offer} الآن",
            "goal": "conversion",
            "archetype": "challenge",
            "points": ["علامة 1: الوقت", "علامة 2: التكلفة", "علامة 3–5: الجودة والنتائج"],
            "visual": "اختبار تفاعلي مع عداد نتيجة",
            "promise": "اكتشف خلال 30 ثانية إذا كان الوقت مناسب للبدء",
            "format_options": ["short_video", "story", "carousel"],
            "metric": "الإكمال + بدء المحادثات + الحفظ",
            "repurpose": "Quiz على الموقع + إعلان ريتارقتنق",
            "effort": "خفيف",
        },
        {
            "title": "توقف عن هذا الشي الآن — يكلّفك أكثر مما تتخيل في {industry}",
            "goal": "discovery",
            "archetype": "controversy",
            "points": [
                "الفعل المكلف: تنقّل بين التطبيقات عشان مهمة وحدة",
                "التكلفة الخفية: دقائق تضيع كل يوم وتصير ساعات بالأسبوع",
                "البديل الأذكى: مسار واحد داخل {name} من الفكرة للتنفيذ",
            ],
            "visual": "حاسبة تكلفة بصرية: الطريقة الخاطئة vs الصحيحة",
            "promise": "وعي بتكلفة خفية تدفعها كل يوم دون أن تدري",
            "format_options": ["short_video", "carousel", "text_post"],
            "metric": "المشاركات + الردود الجدلية + الوصول",
            "repurpose": "إنفوجرافيك للحفظ + إعلان",
            "effort": "خفيف",
        },
    ]

    pillar_by_goal = {pillar["function"]: pillar["name"] for pillar in pillars}
    default_ctas = {
        "discovery": "احفظها وشاركها مع شخص يواجه نفس المشكلة",
        "trust": "اكتب سؤالك وسنحوّله إلى شرح عملي",
        "engagement": "اكتب تجربتك أو اختر رأيك في التعليقات",
        "conversion": f"اكتشف إن كان {brand.name} مناسبًا لك من الرابط",
    }

    # Always generate exactly 30 ideas
    target_count = max(count, 30)

    ideas = []
    for index in range(target_count):
        template = templates[index % len(templates)]
        cycle = index // len(templates)
        title = template["title"].format(**context)
        if cycle:
            title = f"{title} — زاوية {cycle + 1}"
        goal = template["goal"]
        rationale_parts = [
            f"يخدم محور {pillar_by_goal.get(goal, pillars[0]['name'])}",
            f"هدف: {goal}",
            f"نوع الخطاف: {template['archetype']}",
            f"المقياس: {template['metric']}",
        ]
        ideas.append(
            {
                "title": title,
                "pillar": pillar_by_goal.get(goal, pillars[0]["name"]),
                "goal": goal,
                "hook_archetype": template["archetype"],
                "problem": brand.problem,
                "points": [point.format(**context) for point in template["points"]],
                "visual": template["visual"].format(**context),
                "promise": template["promise"].format(**context),
                "cta": default_ctas[goal],
                "rationale": " · ".join(rationale_parts),
                "format_options": template["format_options"],
                "success_metric": template["metric"],
                "repurpose": template["repurpose"],
                "effort": template["effort"],
                "evidence_type": "hypothesis",
                "source_keys": [
                    "youtube_analytics",
                    "instagram_best_practices",
                    "tiktok_creative_center",
                ],
                "caption": f"{title}\n\n{template['promise'].format(**context)}\n\n{default_ctas[goal]}",
            }
        )
    return ideas
