"""Hook Science Engine — 12 archetypes × platform-tuned hooks.

Each archetype maps to a proven psychological trigger. The engine generates
multiple hook variants per idea and scores them on clarity, curiosity,
specificity, emotional pull, and credibility to help the team pick the
strongest opener for a controlled A/B test.

IMPORTANT: Scores are internal preparation estimates, NOT predictions of
reach or virality. A high score means the idea is well-prepared and worth
testing, not that it will guarantee views.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
#  12 Hook Archetypes
# ---------------------------------------------------------------------------

ARCHETYPES: dict[str, dict[str, Any]] = {
    "curiosity": {
        "ar": "فجوة فضول",
        "mechanism": "سؤال يفتح فجوة معلومات لا تُغلق إلا بالمشاهدة",
        "trigger": "الدماغ يكره ترك سؤال بلا جواب",
        "power": 9,
    },
    "pain": {
        "ar": "ألم المشكلة",
        "mechanism": "ضرب الوجع الحقيقي فورًا بلغة الجمهور",
        "trigger": "التعرّف الفوري يوقف التمرير",
        "power": 9,
    },
    "wow": {
        "ar": "مفاجأة بصرية",
        "mechanism": "قبل/بعد أو لقطة صادمة خلال ثانية",
        "trigger": "كسر التوقع يوقظ الانتباه",
        "power": 10,
    },
    "headline": {
        "ar": "عنوان نصي صادم",
        "mechanism": "نص كبير واضح يتحدى المعتقد السائد",
        "trigger": "الخلاف يستفز الرد أو المشاركة",
        "power": 8,
    },
    "pacing": {
        "ar": "إيقاع سريع",
        "mechanism": "قصّات قصيرة بدون مقدمة — مباشرة في القيمة",
        "trigger": "السرعة تمنع الملل وتكافئ الانتباه",
        "power": 7,
    },
    "controversy": {
        "ar": "رأي مخالف",
        "mechanism": "ادعاء يعاكس المعتقد الشائع بدليل",
        "trigger": "المعارضة تنتج ردود فعل قوية ومشاركات",
        "power": 10,
    },
    "transformation": {
        "ar": "تحوّل مثبت",
        "mechanism": "نتيجة ملموسة واضحة: من حالة A إلى حالة B",
        "trigger": "الناس تريد نفس التحول لنفسها",
        "power": 9,
    },
    "urgency": {
        "ar": "إلحاح وتوقيت",
        "mechanism": "سبب واضح لماذا الآن وليس لاحقًا",
        "trigger": "الخوف من الفوات يسرّع القرار",
        "power": 8,
    },
    "social_proof": {
        "ar": "دليل اجتماعي",
        "mechanism": "أرقام حقيقية أو قصة عميل",
        "trigger": "ما يفعله الآخرون يشجع التجربة",
        "power": 8,
    },
    "storytelling": {
        "ar": "قصة شخصية",
        "mechanism": "حكاية قصيرة بها صراع ونتيجة",
        "trigger": "القصص تُفرز أوكسيتوسين وتبني ثقة",
        "power": 9,
    },
    "challenge": {
        "ar": "تحدّي أو اختبار",
        "mechanism": "اطلب من المشاهد أن يفعل شيئًا الآن",
        "trigger": "المشاركة تصنع استثمارًا شخصيًا",
        "power": 8,
    },
    "secret": {
        "ar": "السر المخفي",
        "mechanism": "معلومة لا يعرفها أغلب الناس",
        "trigger": "الحصرية تجعل المعلومة تستحق المشاركة",
        "power": 9,
    },
}

GOAL_AR = {
    "discovery": "وصول واكتشاف",
    "trust": "بناء ثقة",
    "engagement": "تفاعل ومشاركة",
    "conversion": "تحويل وبيع",
}


# ---------------------------------------------------------------------------
#  Viral Hook Formulas — proven patterns
# ---------------------------------------------------------------------------

VIRAL_HOOK_FORMULAS: list[dict[str, str]] = [
    {"pattern": "problem_direct", "ar": "مشكلة مباشرة", "template": "{problem}… وأنت تكرر نفس الشي كل يوم"},
    {"pattern": "result_specific", "ar": "نتيجة محددة", "template": "من {before} إلى {after} في {timeframe}"},
    {"pattern": "curiosity_gap", "ar": "فجوة فضول", "template": "الشي اللي ما أحد يقوله عن {topic}"},
    {"pattern": "contrarian", "ar": "رأي مخالف", "template": "توقف عن {common_belief}… والسبب بسيط"},
    {"pattern": "before_after", "ar": "قبل وبعد", "template": "قبل ما أعرف هالشي كنت {pain}… الحين {result}"},
    {"pattern": "common_mistake", "ar": "خطأ شائع", "template": "أكبر خطأ في {topic} — وأغلب الناس تسويه"},
    {"pattern": "number_list", "ar": "قائمة مرقمة", "template": "{number} أشياء تغيّر {topic} من أساسه"},
    {"pattern": "question_hook", "ar": "سؤال مفتوح", "template": "ليش {audience} مازالوا يعانون من {problem}؟"},
    {"pattern": "secret_reveal", "ar": "كشف سر", "template": "السر اللي ما يقولونه: {secret}"},
    {"pattern": "challenge_hook", "ar": "تحدي", "template": "جرّب هذا لمدة {timeframe} وشوف الفرق"},
    {"pattern": "story_hook", "ar": "بداية قصة", "template": "كنت أقول مستحيل… لين صار هالشي"},
    {"pattern": "urgency_hook", "ar": "إلحاح", "template": "آخر فرصة تصلح {problem} قبل {deadline}"},
]


class HookScienceEngine:
    """Generates, scores, and evaluates hooks for maximum audience retention."""

    def archetype_for_day(self, day: int) -> str:
        keys = list(ARCHETYPES.keys())
        return keys[(day - 1) % len(keys)]

    def archetype_meta(self, key: str) -> dict[str, Any]:
        meta = ARCHETYPES.get(key, ARCHETYPES["pain"])
        return {
            "key": key if key in ARCHETYPES else "pain",
            "ar": meta["ar"],
            "mechanism": meta["mechanism"],
            "trigger": meta["trigger"],
            "power": meta["power"],
        }

    def craft_hooks(self, idea: dict, brand: Any, day: int) -> dict[str, Any]:
        """Generate 5+ hook variants using multiple archetypes and viral formulas."""
        archetype = idea.get("hook_archetype") or self.archetype_for_day(day)
        meta = self.archetype_meta(archetype)
        title = (idea.get("title") or "فكرتك").strip()
        problem = (
            idea.get("problem")
            or idea.get("problem_desire")
            or getattr(brand, "problem", None)
            or "هالمشكلة اليومية"
        )
        name = getattr(brand, "name", "نشاطك")
        audience = getattr(brand, "audience", "") or ""
        offer = getattr(brand, "offer", "") or getattr(brand, "description", "") or ""
        existing = [str(h).strip() for h in (idea.get("hooks") or []) if h]

        short_title = title if len(title) <= 42 else title[:40] + "…"
        short_problem = problem if len(problem) <= 60 else problem[:58] + "…"
        short_audience = audience.split()[0] if audience else "الناس"

        # Archetype-specific hooks — each designed to STOP the scroll
        archetype_generated: dict[str, list[str]] = {
            "curiosity": [
                f"ليش {short_audience} مازالوا يعانون من {short_problem}؟",
                f"الشي اللي ما أحد يقوله عن {short_title.rstrip('؟')}",
                f"سؤال واحد يكشف إذا {short_problem}",
            ],
            "pain": [
                f"{short_problem}… وأنت تكرر نفس الشي كل يوم",
                f"تضيع وقتك على الشي الغلط — وهذا السبب",
                f"إذا {short_problem} فأنت لازم تشوف هذا",
            ],
            "wow": [
                "شوف الفرق خلال 3 ثوانٍ — قبل وبعد",
                f"ما توقعت إن {short_title.rstrip('؟')} يسوي هالشي",
                f"هذا اللي يصير لما تستخدم {name} بالطريقة الصح",
            ],
            "headline": [
                f"توقف عن {short_title.rstrip('؟')} — أغلبكم يسويها غلط",
                "الحقيقة اللي ما أحد يبغى يسمعها",
                f"قاعدة واحدة غيّرت كل شي في {name}",
            ],
            "pacing": [
                "لا تطوّل — القيمة تبدأ الحين",
                "3 لقطات… والنتيجة واضحة",
                "مقطع سريع — القيمة أولًا والباقي بالتعليقات",
            ],
            "controversy": [
                f"كل اللي يقولون عن {short_title.rstrip('؟')} غلط",
                f"رأي ما بتحبه: {short_title.rstrip('؟')} مضيعة وقت إذا…",
                f"انسَ كل نصيحة سمعتها عن {short_title.rstrip('؟')}",
            ],
            "transformation": [
                f"من {short_problem} إلى نتيجة ما توقعتها — هذا اللي صار",
                f"قبل شهر كنت أعاني من {short_problem}… الحين شوف",
                f"تحوّل كامل — بس غيّرت شي واحد في {short_title.rstrip('؟')}",
            ],
            "urgency": [
                f"آخر فرصة تصلح {short_problem} قبل فوات الأوان",
                f"إذا ما بدأت اليوم في {short_title.rstrip('؟')} بتندم",
                f"الوقت ينتهي — {short_title.rstrip('؟')} يتغير الآن",
            ],
            "social_proof": [
                f"قبل ما تصدق أي نتيجة عن {short_title.rstrip('؟')} اطلب هذا الدليل",
                "شهادة العميل وحدها ما تكفي — شوف التطبيق",
                f"كيف تثبت قيمة {name} بدون أرقام مختلقة؟",
            ],
            "storytelling": [
                f"السبب الحقيقي اللي خلاني أبدأ {name}",
                f"كنت أقول مستحيل… لين جرّبت هالشي مع {short_problem}",
                f"هذا الموقف يشرح ليش {short_problem}",
            ],
            "challenge": [
                f"تحدّي: جرّب هذا لمدة أسبوع واحد",
                f"اختبر نفسك: هل فعلاً تعاني من {short_problem}؟",
                f"30 ثانية تكفي — جرّب قبل ما تحكم",
            ],
            "secret": [
                f"السر اللي ما يقولونه عن {short_title.rstrip('؟')}",
                f"معلومة مخفية تغيّر نظرتك لـ{short_title.rstrip('؟')}",
                f"{name} يكشف السر: ليش {short_problem}",
            ],
        }

        # Cross-archetype viral formulas
        viral_generated = [
            f"أكبر خطأ في {short_title.rstrip('؟')} — وأغلب الناس تسويه",
            f"إذا كانت مشكلتك «{short_problem}» ابدأ من هنا",
            f"3 أشياء تمنيت أعرفها قبل ما أبدأ {short_title.rstrip('؟')}",
            f"الخطأ اللي يكلفك كل شي في {short_title.rstrip('؟')}",
            f"قبل ما تقرر في {short_title.rstrip('؟')}، اسأل هذا السؤال",
            f"ليش {short_audience} الأذكياء يتجنبون {short_title.rstrip('؟')} التقليدي",
        ]

        # Build final hooks list: existing > archetype > cross-archetype > viral
        hooks: list[str] = []
        for h in existing + archetype_generated.get(meta["key"], []) + viral_generated:
            h = str(h).strip()
            if h and h not in hooks and len(h) >= 6:
                hooks.append(h)
            if len(hooks) >= 7:  # Give more options for A/B testing
                break

        return {
            "primary": hooks[0] if hooks else short_title,
            "alts": hooks[1:7],
            "archetype": meta["key"],
            "archetype_ar": meta["ar"],
            "mechanism": meta["mechanism"],
            "trigger": meta["trigger"],
            "power": meta["power"],
        }

    def rank_hooks(
        self,
        hooks: list[str],
        idea: dict,
        brand: Any,
    ) -> list[str]:
        """Rank candidates by preparation quality, never by promised views."""
        unique: list[str] = []
        for hook in hooks:
            clean = " ".join(str(hook).split()).strip()
            if clean and clean not in unique:
                unique.append(clean)
        scored = [
            (self.evaluate_hook(hook, idea, brand)["score"], index, hook)
            for index, hook in enumerate(unique)
        ]
        scored.sort(key=lambda row: (-row[0], row[1]))
        return [hook for _, _, hook in scored]

    def evaluate_hook(self, hook: str, idea: dict, brand: Any) -> dict[str, int]:
        """Transparent 100-point estimate for choosing what to A/B test."""
        text = " ".join(str(hook).split()).strip()
        words = text.split()
        problem = str(idea.get("problem") or idea.get("problem_desire") or "")
        title = str(idea.get("title") or "")
        audience = str(getattr(brand, "audience", "") or "")
        context_terms = {
            word.strip("،.:؟!?«»")
            for word in f"{problem} {title} {audience}".split()
            if len(word.strip("،.:؟!?«»")) >= 4
        }

        clarity = 20 if 5 <= len(words) <= 12 else 14 if 3 <= len(words) <= 16 else 7
        relevance_hits = sum(1 for term in context_terms if term in text)
        relevance = min(20, 10 + relevance_hits * 3)

        curiosity_markers = (
            "؟", "ليش", "كيف", "السبب", "قبل", "خطأ", "لكن",
            "الحقيقة", "الفرق", "وش", "متى",
        )
        curiosity = min(15, 7 + sum(2 for marker in curiosity_markers if marker in text))

        specificity_markers = (
            "3", "5", "7", "دقيقة", "ثانية", "أسبوع", "خطوة",
            "طريقة", "قالب", "واتساب", "تيك توك", "إنستغرام",
        )
        specificity = min(
            15, 6 + sum(3 for marker in specificity_markers if marker in text)
        )

        spoken = 15
        if len(text) > 90 or len(words) > 16:
            spoken = 7
        elif len(text) < 10:
            spoken = 9

        credibility = 15
        overpromise = (
            "مضمون", "أكيد", "100%", "الأفضل في العالم", "مليون مشاهدة",
            "سر لا يعرفه أحد", "بتندم", "آخر فرصة",
        )
        if any(marker in text for marker in overpromise):
            credibility = 4
        elif any(marker in text for marker in ("الكل", "مستحيل", "ما تصدق")):
            credibility = 9

        score = clarity + relevance + curiosity + specificity + spoken + credibility
        return {
            "score": min(100, score),
            "clarity": clarity * 5,
            "curiosity": round(curiosity / 15 * 100),
            "relevance": relevance * 5,
            "specificity": round(specificity / 15 * 100),
            "credibility": round(credibility / 15 * 100),
        }

    def build_scene_pack(
        self, idea: dict, brand: Any, day: int, hook_pack: dict
    ) -> dict[str, Any]:
        hook = hook_pack["primary"]
        archetype_ar = hook_pack["archetype_ar"]
        title = idea.get("title") or f"يوم {day}"
        name = getattr(brand, "name", "نشاطك")
        problem = (
            idea.get("problem")
            or idea.get("problem_desire")
            or getattr(brand, "problem", None)
            or "مشكلة الجمهور"
        )
        points = idea.get("points") or []
        if isinstance(points, str):
            points = [p.strip() for p in points.split("|") if p.strip()]
        if len(points) < 3:
            points = (points + [
                f"اعرض الحل داخل {name}",
                "وضّح الفائدة بجملة واحدة",
                "اربطها بخطوة عملية اليوم",
            ])[:3]
        visual = idea.get("visual") or f"شاشة داخل {name} توضّح الفكرة"
        promise = idea.get("promise") or f"بنهاية المقطع تعرف خطوة عملية عن: {title}"
        cta = idea.get("cta") or "الرابط في البايو"
        platform = str(idea.get("platform") or "tiktok").lower()
        goal = idea.get("post_goal") or "discovery"
        goal_ar = GOAL_AR.get(goal, goal)

        platform_label, platform_tip = self._platform_tips(platform)

        # Enhanced scenes for maximum retention
        scenes = "\n".join([
            f"1) الخطاف (0–3 ث) — نوع: {archetype_ar} [قوة: {hook_pack.get('power', 8)}/10]",
            f"   قل/اكتب على الشاشة: «{hook}»",
            "   التصوير: وجه للكاميرا أو نص كبير. ممنوع شعار أو مقدمة بطيئة.",
            f"   المحفز: {hook_pack.get('trigger', 'وقف التمرير فورًا')}",
            "",
            "2) المشكلة والوعد (3–8 ث) — Pattern Interrupt",
            f"   «{problem}»",
            f"   الوعد: {promise}",
            "   أضف حركة بصرية/قطع سريع لمنع التمرير",
            "",
            f"3) القيمة الأساسية (8–25 ث) — داخل {name}",
            f"   • {points[0]}",
            f"   • {points[1]}",
            f"   • {points[2]}",
            "   إيقاع: بدّل اللقطة كل 1–2 ث مع نص مختصر على الشاشة",
            "",
            "4) الذروة والإثبات (25–38 ث) — Peak Moment",
            f"   اعرض: {visual}",
            "   هذه اللحظة التي تصنع المشاركة والحفظ",
            "",
            "5) الإغلاق والـ Loop (38–45 ث)",
            f"   CTA: «{cta}»",
            "   اترك سؤالاً مفتوحاً أو إشارة للجزء القادم لتشجيع إعادة المشاهدة",
        ])

        on_screen = " → ".join([hook, points[0][:36], points[1][:36], cta])

        script_body = "\n".join([
            f"يوم {day} | {platform_label} | هدف: {goal_ar}",
            f"العنوان: {title}",
            f"النوع: {archetype_ar} — {hook_pack.get('mechanism', '')}",
            f"0–3ث: {hook}",
            f"3–8ث: {problem}",
            f"8–25ث:",
            f"  • {points[0]}",
            f"  • {points[1]}",
            f"  • {points[2]}",
            f"25–38ث: {visual}",
            f"38–45ث: {cta}",
        ])

        return {
            "scenes": scenes,
            "on_screen_text": on_screen,
            "script_body": script_body,
            "editing_notes": " | ".join([
                "بدون براندنج أول 3 ثوانٍ",
                "كابشن عربي كبير وواضح",
                "موسيقى خفيفة تحت الصوت",
                "قطع سريع كل 2 ثانية",
                platform_tip,
            ]),
            "creative_concept": f"{archetype_ar}: {hook} — ثم حل عملي داخل {name}.",
            "promise": promise,
            "peak_moment": visual,
            "hypothesis": f"خطاف {archetype_ar} قوي (قوة {hook_pack.get('power', 8)}/10) في أول 3 ثوانٍ يرفع الإكمال على {platform_label}.",
            "virality_extra": {
                "hook_archetype": hook_pack["archetype"],
                "hook_archetype_ar": archetype_ar,
                "platform_tip": platform_tip,
                "platform_label": platform_label,
                "goal_ar": goal_ar,
                "trigger": hook_pack.get("trigger", ""),
                "power": hook_pack.get("power", 8),
            },
        }

    def score_hook_strength(self, item: dict) -> int:
        """Score hook strength on 0–20 scale with nuanced criteria."""
        hooks = [h for h in (item.get("hooks") or []) if h]
        primary = str(hooks[0]) if hooks else ""
        score = 5

        # Length optimization (best hooks are 12–55 chars)
        length = len(primary)
        if 12 <= length <= 55:
            score += 4
        elif 8 <= length <= 70:
            score += 2
        elif primary:
            score += 1

        # Curiosity markers (questions, mystery, gaps)
        curiosity_markers = ("؟", "?", "ليش", "هل ", "لا ", "قبل", "خطأ", "تضيع",
                            "نفس", "متى", "كيف", "ليه", "وش", "السر", "مخفي",
                            "ما أحد", "أكبر", "أول", "آخر")
        curiosity_count = sum(1 for m in curiosity_markers if m in primary)
        score += min(4, curiosity_count * 2)

        # Specificity markers (numbers, time, comparisons)
        specificity_markers = ("3", "5", "7", "10", "دقيقة", "ثانية", "أسبوع",
                               "شهر", "يوم", "ريال", "%", "ثوانٍ")
        if any(m in primary for m in specificity_markers):
            score += 2

        # Multiple hooks available for A/B testing
        if len(hooks) >= 5:
            score += 2
        elif len(hooks) >= 3:
            score += 1

        # Has supporting content
        if item.get("points") or (item.get("scenes") and "1) الخطاف" in str(item.get("scenes"))):
            score += 1

        # Credibility check — penalize overpromising
        overpromise_markers = ("مضمون", "أكيد", "100%", "الأفضل في العالم", "مليون مشاهدة")
        if any(m in primary for m in overpromise_markers):
            score -= 3

        return max(0, min(20, score))

    def _platform_tips(self, platform: str) -> tuple[str, str]:
        """Platform-specific label and production tip."""
        tips = {
            "tiktok": ("تيك توك", "أول نصف ثانية صورة/نص — مو كلام طويل"),
            "instagram": ("إنستغرام ريلز", "خطاف قوي + لقطة تستحق الإرسال والحفظ"),
            "youtube": ("يوتيوب Shorts", "جملة منطوقة واضحة في أول ثانيتين"),
            "x": ("X", "جملة واحدة حادة + لقطة شاشة"),
            "facebook": ("فيسبوك", "ابدأ بالمشكلة ثم الحل بسرعة"),
        }
        return tips.get(platform, (platform, "ابدأ بالقيمة فورًا — بدون مقدمة قناة"))
