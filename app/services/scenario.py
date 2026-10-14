"""Build an execution pack for video, carousel, story, or text content."""

from __future__ import annotations

from typing import Any

from app.services.hook_science import GOAL_AR, HookScienceEngine


class ScenarioEngine:
    def __init__(self) -> None:
        self.hooks = HookScienceEngine()

    def build(self, idea: dict, brand: Any, day: int) -> dict[str, Any]:
        name = getattr(brand, "name", "نشاطك")
        audience = getattr(brand, "audience", None) or "جمهورك"
        platform = str(idea.get("platform") or "tiktok").lower()
        content_type = idea.get("content_type") or "short_video"
        goal = idea.get("post_goal") or idea.get("goal") or "discovery"
        goal_ar = GOAL_AR.get(goal, goal)
        title = idea.get("title") or f"محتوى يوم {day}"
        problem = (
            idea.get("problem")
            or idea.get("problem_desire")
            or getattr(brand, "problem", "")
            or "مشكلة الجمهور"
        )
        points = [str(point).strip() for point in (idea.get("points") or []) if point]
        while len(points) < 3:
            points.append(f"خطوة عملية مرتبطة بـ{name}")
        visual = idea.get("visual") or f"مثال أو شاشة من {name}"
        promise = idea.get("promise") or f"خطوة عملية عن {title}"
        cta = idea.get("cta") or "اختر خطوة واحدة ونفذها اليوم"
        caption = idea.get("caption") or f"{title}\n\n{promise}\n\n{cta}"

        hook_pack = self.hooks.craft_hooks(idea, brand, day)
        provided_hooks = [
            str(hook).strip() for hook in (idea.get("hooks") or []) if str(hook).strip()
        ]
        source_hooks = (
            provided_hooks
            if len(provided_hooks) >= 5
            else [hook_pack["primary"], *hook_pack["alts"], *provided_hooks]
        )
        candidates = []
        for hook in source_hooks:
            clean = str(hook).strip()
            if clean and clean not in candidates:
                candidates.append(clean)
        hooks = self.hooks.rank_hooks(candidates, idea, brand)[:5]
        hook = hooks[0] if hooks else title
        platform_label, platform_tip = self._platform(platform)

        if content_type == "carousel":
            execution = self._carousel(hook, problem, points, visual, cta)
        elif content_type == "text_post":
            execution = self._text_post(hook, problem, points, visual, cta)
        elif content_type == "story":
            execution = self._story(hook, problem, points, cta)
        else:
            execution = self._video(hook, problem, points, visual, cta)

        hypothesis = (
            f"سنختبر ما إذا كان خطاف «{hook}» يساعد {audience} على متابعة "
            f"المحتوى واتخاذ هدف {goal_ar} على {platform_label}."
        )
        script_body = execution["body"]
        editing_notes = f"{execution['notes']} · {platform_tip} · راجع أي ادعاء قبل النشر"

        return {
            "hooks": hooks,
            "scenes": execution["scenes"],
            "script_body": script_body,
            "on_screen_text": execution["on_screen"],
            "editing_notes": editing_notes,
            "creative_concept": f"{execution['format_label']}: {title}",
            "promise": promise,
            "peak_moment": visual,
            "hypothesis": hypothesis,
            "cta": cta,
            "problem": problem,
            "beats": execution["beats"],
            "caption": caption,
            "virality_extra": {
                "hook_archetype": hook_pack["archetype"],
                "hook_archetype_ar": hook_pack["archetype_ar"],
                "platform_tip": platform_tip,
                "platform_label": platform_label,
                "goal_ar": goal_ar,
                "duration": execution["duration"],
            },
            "script": {
                "hook": hook,
                "promise": promise,
                "problem": problem,
                "body": script_body,
                "peak_moment": visual,
                "closing": execution["closing"],
                "cta": cta,
                "alt_hooks": hooks[1:5],
                "alt_narratives": [
                    f"نسخة أقصر تبدأ بالنتيجة: {promise}",
                    f"نسخة سؤال تبدأ بـ: ما أصعب جزء في {problem[:60]}؟",
                ],
                "hypothesis": hypothesis,
                "fallback_version": execution["fallback"],
            },
        }

    def _video(
        self, hook: str, problem: str, points: list[str], visual: str, cta: str
    ) -> dict:
        beats = [
            {"time": "0–3ث", "name": "الخطاف", "say": hook, "shoot": "وجه أو نص كبير فورًا"},
            {"time": "3–8ث", "name": "السياق", "say": problem, "shoot": "مثال بصري للمشكلة"},
            {"time": "8–18ث", "name": "القيمة 1", "say": points[0], "shoot": "لقطة أو تسجيل شاشة"},
            {"time": "18–28ث", "name": "القيمة 2", "say": points[1], "shoot": "غيّر الزاوية مع نص مختصر"},
            {"time": "28–38ث", "name": "القيمة 3", "say": points[2], "shoot": "اعرض التطبيق"},
            {"time": "38–43ث", "name": "الدليل", "say": visual, "shoot": "استخدم دليلًا حقيقيًا فقط"},
            {"time": "43–45ث", "name": "الختام", "say": cta, "shoot": "CTA واحد على الشاشة"},
        ]
        lines = ["حزمة فيديو قصير — قرابة 45 ثانية", ""]
        for index, beat in enumerate(beats, start=1):
            lines.extend(
                [
                    f"{index}) {beat['name']} ({beat['time']})",
                    f"تقول: {beat['say']}",
                    f"التصوير: {beat['shoot']}",
                    "",
                ]
            )
        body = "\n".join(f"{beat['time']}: {beat['say']}" for beat in beats)
        return {
            "format_label": "فيديو قصير",
            "duration": "حوالي 45 ثانية",
            "scenes": "\n".join(lines).strip(),
            "body": body,
            "on_screen": " ← ".join([hook, points[0], points[1], cta]),
            "notes": "بدون شعار في البداية · قصّ واضح دون فوضى · ترجمة كبيرة",
            "beats": beats,
            "closing": "ثبّت CTA في آخر ثانية",
            "fallback": f"نسخة 15 ثانية:\n1) {hook}\n2) {points[0]}\n3) {cta}",
        }

    def _carousel(
        self, hook: str, problem: str, points: list[str], visual: str, cta: str
    ) -> dict:
        slides = [
            (1, "الغلاف", hook),
            (2, "المشكلة", problem),
            (3, "الخطوة الأولى", points[0]),
            (4, "الخطوة الثانية", points[1]),
            (5, "الخطوة الثالثة", points[2]),
            (6, "المثال/الدليل", visual),
            (7, "الدعوة", cta),
        ]
        scenes = ["حزمة كاروسيل — 7 شرائح", ""]
        for number, role, text in slides:
            scenes.extend([f"شريحة {number} — {role}", text, ""])
        body = "\n\n".join(f"شريحة {number}: {text}" for number, _, text in slides)
        beats = [
            {"slide": number, "name": role, "copy": text} for number, role, text in slides
        ]
        return {
            "format_label": "كاروسيل",
            "duration": "7 شرائح",
            "scenes": "\n".join(scenes).strip(),
            "body": body,
            "on_screen": " ← ".join(text for _, _, text in slides),
            "notes": "فكرة واحدة لكل شريحة · تباين مرتفع · اجعل الغلاف مفهومًا وحده",
            "beats": beats,
            "closing": "اختم بشريحة CTA واحدة",
            "fallback": f"نسخة 4 شرائح: {hook} ← {points[0]} ← {visual} ← {cta}",
        }

    def _text_post(
        self, hook: str, problem: str, points: list[str], visual: str, cta: str
    ) -> dict:
        body = "\n".join(
            [
                hook,
                "",
                problem,
                "",
                f"1. {points[0]}",
                f"2. {points[1]}",
                f"3. {points[2]}",
                "",
                f"مثال: {visual}",
                "",
                cta,
            ]
        )
        beats = [
            {"name": "السطر الأول", "copy": hook},
            {"name": "السياق", "copy": problem},
            {"name": "القيمة", "copy": " | ".join(points)},
            {"name": "الدعوة", "copy": cta},
        ]
        return {
            "format_label": "منشور نصي",
            "duration": "قراءة أقل من دقيقة",
            "scenes": f"نص جاهز للمراجعة والنشر:\n\n{body}",
            "body": body,
            "on_screen": hook,
            "notes": "سطر أول مستقل · فقرات قصيرة · لا تستخدم ادعاء بلا دليل",
            "beats": beats,
            "closing": "اختم بسؤال أو فعل واحد",
            "fallback": f"نسخة قصيرة:\n{hook}\n\n{points[0]}\n\n{cta}",
        }

    def _story(self, hook: str, problem: str, points: list[str], cta: str) -> dict:
        frames = [
            (1, hook),
            (2, problem),
            (3, points[0]),
            (4, points[1]),
            (5, f"{points[2]} — {cta}"),
        ]
        body = "\n\n".join(f"إطار {number}: {text}" for number, text in frames)
        return {
            "format_label": "قصة تفاعلية",
            "duration": "5 إطارات",
            "scenes": f"حزمة قصة — 5 إطارات\n\n{body}",
            "body": body,
            "on_screen": " ← ".join(text for _, text in frames),
            "notes": "نص قليل · عنصر تفاعل واحد · اختبر سؤالًا أو تصويتًا",
            "beats": [{"frame": number, "copy": text} for number, text in frames],
            "closing": "عنصر تفاعل أو CTA واحد",
            "fallback": f"3 إطارات: {hook} ← {points[0]} ← {cta}",
        }

    def _platform(self, platform: str) -> tuple[str, str]:
        if platform == "tiktok":
            return "تيك توك", "تحقق من Creative Center ثم اختبر الاحتفاظ الفعلي"
        if platform == "instagram":
            return "إنستغرام", "راقب مدة المشاهدة والحفظ والإرسال من Insights"
        if platform == "youtube":
            return "يوتيوب", "استخدم منحنى الاحتفاظ ومصادر الزيارات في YouTube Analytics"
        if platform == "x":
            return "X", "قِس الردود والنقرات ولا تساوِ الانطباعات بالنتائج"
        if platform == "facebook":
            return "فيسبوك", "راقب المشاهدة والمشاركة والنقرات بحسب الهدف"
        return platform, "قِس الإشارة المرتبطة بهدف القطعة"
