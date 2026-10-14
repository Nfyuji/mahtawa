"""Build a complete filming scenario: spoken lines, on-screen text, and shots."""

from __future__ import annotations

import re
from typing import Any

from app.services.hook_science import GOAL_AR, HookScienceEngine


class ScenarioEngine:
    def __init__(self) -> None:
        self.hooks = HookScienceEngine()

    def build(self, idea: dict, brand: Any, day: int) -> dict[str, Any]:
        name = getattr(brand, "name", "نشاطك")
        audience = getattr(brand, "audience", None) or "جمهورك"
        offer = getattr(brand, "offer", None) or getattr(brand, "description", None) or name
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
        # Replace director-note points with concrete spoken beats.
        points = self._materialize_points(points, problem, name, offer, title)
        visual = idea.get("visual") or f"تسجيل شاشة أو مثال حقيقي من {name}"
        promise = idea.get("promise") or f"بنهاية المقطع تعرف خطوة عملية عن {title}"
        cta = idea.get("cta") or "احفظ الفيديو وارجع له وقت التنفيذ"
        caption = idea.get("caption") or (
            f"{title}\n\n{promise}\n\n{cta}\n#{name.replace(' ', '')}"
        )

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

        say = idea.get("say") if isinstance(idea.get("say"), dict) else {}
        screen = idea.get("screen") if isinstance(idea.get("screen"), dict) else {}
        shots = idea.get("shots") if isinstance(idea.get("shots"), dict) else {}

        spoken = self._spoken_pack(
            say=say,
            hook=hook,
            problem=problem,
            promise=promise,
            points=points,
            visual=visual,
            cta=cta,
            name=name,
            audience=audience,
            offer=offer,
            title=title,
        )
        screens = self._screen_pack(screen, spoken)
        shot_pack = self._shot_pack(shots, name, visual, points)

        if content_type == "carousel":
            execution = self._carousel(spoken, screens, points, visual, cta, title)
        elif content_type == "text_post":
            execution = self._text_post(spoken, points, visual, cta, title)
        elif content_type == "story":
            execution = self._story(spoken, cta)
        else:
            execution = self._video(
                day=day,
                title=title,
                name=name,
                platform_label=platform_label,
                goal_ar=goal_ar,
                spoken=spoken,
                screens=screens,
                shots=shot_pack,
                hook=hook,
                cta=cta,
            )

        hypothesis = (
            f"إذا بدأ المقطع بـ«{hook}» وذكر أخطاء/مشكلة «{self._short(problem, 12)}» "
            f"ثم قدّم حل {name}، يرتفع الاحتفاظ والإكمال على {platform_label}."
        )
        editing_notes = (
            f"{execution['notes']} · {platform_tip} · "
            "اقرأ عمود «تقول» حرفيًا كأنك تشرح لصديق"
        )

        return {
            "hooks": hooks,
            "scenes": execution["scenes"],
            "script_body": execution["body"],
            "on_screen_text": execution["on_screen"],
            "editing_notes": editing_notes,
            "creative_concept": f"سيناريو كامل: {title}",
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
                "format_label": execution["format_label"],
                "idea_points": points,
                "visual": visual,
                "promise": promise,
                "say": spoken,
                "screen": screens,
                "shots": shot_pack,
            },
            "script": {
                "hook": hook,
                "promise": promise,
                "problem": problem,
                "body": execution["body"],
                "peak_moment": visual,
                "closing": execution["closing"],
                "cta": cta,
                "alt_hooks": hooks[1:5],
                "alt_narratives": [
                    f"نسخة أقصر: ابدأ من «{spoken['p3']}»",
                    f"نسخة سؤال: ما أصعب جزء في {self._short(problem, 10)}؟",
                ],
                "hypothesis": hypothesis,
                "fallback_version": execution["fallback"],
            },
        }

    def _materialize_points(
        self,
        points: list[str],
        problem: str,
        name: str,
        offer: str,
        title: str,
    ) -> list[str]:
        """Turn director notes into concrete spoken beats the host can say."""
        fragments = self._problem_fragments(problem)
        mistake = fragments[0]
        impact = fragments[1] if len(fragments) > 1 else f"يومك يتقطع وكل مهمة تصير أبطأ بسبب {mistake}"
        fix = fragments[2] if len(fragments) > 2 else f"اجمع الشغل في مكان واحد مع {name}"

        concrete = [
            f"الخطأ الأول: {mistake} — وهذا اللي يصير مع أغلب الناس يوميًا",
            f"أثره على يومك: {impact}",
            f"أول تصحيح بسيط: {fix}، وبهالخطوة يصير {self._short(offer, 6)} أوضح",
        ]

        result = []
        for index, point in enumerate(points[:3]):
            if self._looks_like_instruction(point) or self._looks_like_outline(point):
                result.append(concrete[index])
            else:
                result.append(point)
        while len(result) < 3:
            result.append(concrete[len(result)])
        return result

    def _problem_fragments(self, problem: str) -> list[str]:
        text = (problem or "").strip()
        if not text:
            return [
                "تشتت الشغل بين أدوات كثيرة",
                "تضيع وقتك بين التبديل والنسخ بدون نتيجة",
                "وحّد المهام في أداة واحدة بدل التبديل",
            ]

        # "تشتت … بين A و B و C" → name the tools as the real mistake.
        between = re.search(r"بين\s+(.+)$", text)
        if between:
            tools_raw = between.group(1)
            # Split only on list connectors, never on و inside a word like المحتوى.
            tools = [
                t.strip(" .،,ـ")
                for t in re.split(r"\s+وال?|\s*،\s*|\s*/\s*|\s+\+\s*", tools_raw)
                if t and len(t.strip()) > 2
            ]
            tools = [t for t in tools if t not in ("ال", "ـ")][:4]
            if len(tools) >= 2:
                a, b = tools[0], tools[1]
                extra = f" و{tools[2]}" if len(tools) > 2 else ""
                return [
                    f"تفتح {a} و{b}{extra} كل شوي وتنسى وين وقفت",
                    f"كل يوم تضيع وقت بين التبديل والنسخ بدل ما تخلّص مهمة وحدة",
                    f"اجمع المحتوى والردود والحملات في مساحة واحدة بدل {len(tools)} أماكن متفرقة",
                ]

        parts = [
            p.strip(" .،,")
            for p in re.split(r"[،,/|]| و ", text)
            if p and len(p.strip()) > 3
        ]
        if len(parts) >= 3:
            return parts[:3]
        if len(parts) == 2:
            return [
                parts[0],
                f"وهذا يكرّر نفسه كل يوم: {parts[1]}",
                "ابدأ بتصحيح واحد اليوم بدل ما تؤجل",
            ]
        short = self._short(text, 14)
        return [
            short,
            f"كل يوم يخسر وقت وطاقة بسبب: {short}",
            "صحّح خطوة واحدة اليوم وكرّرها أسبوع",
        ]

    def _spoken_pack(
        self,
        *,
        say: dict,
        hook: str,
        problem: str,
        promise: str,
        points: list[str],
        visual: str,
        cta: str,
        name: str,
        audience: str,
        offer: str,
        title: str,
    ) -> dict[str, str]:
        """Turn short notes into full spoken Arabic lines for the camera."""
        audience_short = self._short(audience, 8)
        point_lines = [
            self._expand_point(points[0], name, offer, index=1),
            self._expand_point(points[1], name, offer, index=2),
            self._expand_point(points[2], name, offer, index=3),
        ]
        defaults = {
            "hook": hook.rstrip(" .") + ".",
            "bridge": (
                f"إذا أنت من {audience_short}، هالمشهد مألوف: "
                f"{problem.rstrip(' .')}. "
                f"بنهاية هالمقطع {promise.rstrip(' .')}."
            ),
            "p1": point_lines[0],
            "p2": point_lines[1],
            "p3": point_lines[2],
            "proof": (
                f"الحين شوف التطبيق عمليًا داخل {name}: "
                f"{visual.rstrip(' .')}. هذا الدليل مو كلام فاضي."
            ),
            "cta": (
                f"{cta.rstrip(' .')}. "
                f"وإذا تبغى نفس المسار، جرّب {name} وابدأ بخطوة واحدة اليوم."
            ),
        }
        result = {}
        for key, default in defaults.items():
            custom = str(say.get(key) or "").strip()
            if (
                custom
                and len(custom.split()) >= 8
                and not self._looks_like_instruction(custom)
                and not self._looks_like_outline(custom)
            ):
                result[key] = custom.rstrip(" .") + "."
            else:
                result[key] = default
        if hook:
            result["hook"] = hook.rstrip(" .") + "."
        return result

    def _expand_point(self, point: str, name: str, offer: str, index: int) -> str:
        clean = point.rstrip(" .")
        if clean.startswith(("أولًا", "ثانيًا", "ثالثًا", "الخطأ", "أثره", "أول تصحيح")):
            if index == 3 and name.lower() not in clean.lower():
                return f"{clean} — والخطوة دي داخل {name}."
            return clean + "."
        if name.lower() in clean.lower():
            return clean + "."
        openers = (
            f"أولًا — {clean}.",
            f"ثانيًا — {clean}.",
            f"ثالثًا — {clean}. وبهالخطوة يصير عرض {self._short(offer, 8)} أوضح مع {name}.",
        )
        return openers[index - 1]

    def _looks_like_instruction(self, text: str) -> bool:
        starters = (
            "سمِّ", "سمّي", "سمّ", "وضّح", "اختم", "اعرض", "اكتب", "حط", "اربط",
            "قدّم", "فرّق", "راجع", "حدّث", "جدول", "ضع ", "اطلب", "حوّل",
            "نفّذ", "قارن", "حدّد", "اذكر", "اشرح", "أظهر", "اكشف", "أنشئ",
            "صوّر", "شارك",
        )
        stripped = text.strip()
        return any(stripped.startswith(s) for s in starters)

    def _looks_like_outline(self, text: str) -> bool:
        """Detect teleprompter outlines that are not yet spoken lines."""
        markers = (
            "كما يحدث",
            "أثره اليومي",
            "تصحيح بسيط",
            "الطريقة القديمة",
            "بدون تزيين",
            "علامة 1",
            "الشي الأول",
        )
        short = len(text.split()) <= 8
        return short and any(m in text for m in markers)

    def _screen_pack(self, screen: dict, spoken: dict[str, str]) -> dict[str, str]:
        result = {}
        for key, spoken_line in spoken.items():
            custom = str(screen.get(key) or "").strip()
            if custom and not self._looks_like_instruction(custom):
                result[key] = custom
            else:
                result[key] = self._screen_line(spoken_line)
        return result

    def _shot_pack(
        self, shots: dict, name: str, visual: str, points: list[str]
    ) -> dict[str, str]:
        defaults = {
            "hook": "وجه قريب للكاميرا أو نص كبير يملأ الشاشة — بدون شعار",
            "bridge": "إيماءة توضيح + لقطة سريعة للمشكلة (تبويبات/تطبيقات مفتوحة)",
            "p1": f"لقطة توضيح للخطأ الأول: {self._screen_line(points[0], 5)}",
            "p2": "غيّر الزاوية أو اقترب من الشاشة وأظهر أثر المشكلة",
            "p3": f"اعرض الحل داخل {name}",
            "proof": visual,
            "cta": "ثبّت آخر فريم ثانية مع نص الدعوة كبير وواضح",
        }
        result = {}
        for key, default in defaults.items():
            custom = str(shots.get(key) or "").strip()
            result[key] = custom if custom else default
        return result

    def _video(
        self,
        *,
        day: int,
        title: str,
        name: str,
        platform_label: str,
        goal_ar: str,
        spoken: dict[str, str],
        screens: dict[str, str],
        shots: dict[str, str],
        hook: str,
        cta: str,
    ) -> dict:
        beats = [
            ("0–3 ث", "الخطاف", "hook"),
            ("3–10 ث", "المشكلة + الوعد", "bridge"),
            ("10–18 ث", "الخطأ / الخطوة 1", "p1"),
            ("18–26 ث", "الأثر / الخطوة 2", "p2"),
            ("26–34 ث", "الحل / الخطوة 3", "p3"),
            ("34–40 ث", "الإثبات على الشاشة", "proof"),
            ("40–45 ث", "الختام والدعوة", "cta"),
        ]
        lines = [
            f"سيناريو تصوير كامل — يوم {day}",
            f"العنوان: {title}",
            f"المنصة: {platform_label} · الهدف: {goal_ar} · البراند: {name}",
            "المدة: حوالي 45 ثانية",
            "",
            "كيف تستخدمه؟",
            "1) اقرأ «تقول» بصوت عالٍ حرفيًا — كأنك تشرح لصديق.",
            "2) حط «تكتب على الشاشة» كنص كبير.",
            "3) نفّذ «التصوير» كما هو.",
            "",
        ]
        for index, (time_label, name_ar, key) in enumerate(beats, start=1):
            lines.extend(
                [
                    f"── المشهد {index} | {time_label} | {name_ar} ──",
                    f"تقول: «{spoken[key]}»",
                    f"تكتب على الشاشة: {screens[key]}",
                    f"التصوير: {shots[key]}",
                    "",
                ]
            )
        lines.extend(
            [
                "── نص التلقين المتصل (للقراءة مرة واحدة) ──",
                spoken["hook"],
                spoken["bridge"],
                spoken["p1"],
                spoken["p2"],
                spoken["p3"],
                spoken["proof"],
                spoken["cta"],
            ]
        )
        body = "\n\n".join(
            f"[{time_label}] {spoken[key]}" for time_label, _, key in beats
        )
        return {
            "format_label": "فيديو قصير — سيناريو كامل",
            "duration": "حوالي 45 ثانية",
            "scenes": "\n".join(lines).strip(),
            "body": body,
            "on_screen": " ← ".join(screens[key] for _, _, key in beats),
            "notes": "بدون مقدمة قناة · نص عربي كبير · بدّل اللقطة كل 2–3 ثوانٍ",
            "beats": [
                {
                    "time": time_label,
                    "name": name_ar,
                    "say": spoken[key],
                    "write": screens[key],
                    "shoot": shots[key],
                }
                for time_label, name_ar, key in beats
            ],
            "closing": "جمّد آخر فريم بعد الـ CTA",
            "fallback": (
                f"نسخة 15 ثانية:\n"
                f"1) {spoken['hook']}\n"
                f"2) {spoken['p3']}\n"
                f"3) {spoken['cta']}"
            ),
        }

    def _carousel(
        self,
        spoken: dict[str, str],
        screens: dict[str, str],
        points: list[str],
        visual: str,
        cta: str,
        title: str,
    ) -> dict:
        slides = [
            (1, "الغلاف", spoken["hook"], screens["hook"]),
            (2, "المشكلة", spoken["bridge"], screens["bridge"]),
            (3, "الخطأ 1", spoken["p1"], screens["p1"]),
            (4, "الخطأ 2 / الأثر", spoken["p2"], screens["p2"]),
            (5, "الحل", spoken["p3"], screens["p3"]),
            (6, "الإثبات", spoken["proof"], screens["proof"]),
            (7, "الدعوة", spoken["cta"], screens["cta"]),
        ]
        scenes = [f"سيناريو كاروسيل كامل — {title}", ""]
        for number, role, say, write in slides:
            scenes.extend(
                [
                    f"شريحة {number} — {role}",
                    f"النص الرئيسي: {write}",
                    f"التعليق الصوتي/الشرح: {say}",
                    "",
                ]
            )
        body = "\n\n".join(
            f"شريحة {number} ({role}): {say}" for number, role, say, _ in slides
        )
        return {
            "format_label": "كاروسيل — سيناريو كامل",
            "duration": "7 شرائح",
            "scenes": "\n".join(scenes).strip(),
            "body": body,
            "on_screen": " ← ".join(write for _, _, _, write in slides),
            "notes": "شريحة واحدة = فكرة واحدة · غلاف يُفهم لوحده · احفظ CTA للأخير",
            "beats": [
                {"slide": n, "name": role, "copy": say, "write": write}
                for n, role, say, write in slides
            ],
            "closing": "اختم بشريحة CTA واحدة",
            "fallback": f"4 شرائح: {screens['hook']} ← {screens['p1']} ← {visual} ← {cta}",
        }

    def _text_post(
        self,
        spoken: dict[str, str],
        points: list[str],
        visual: str,
        cta: str,
        title: str,
    ) -> dict:
        body = "\n".join(
            [
                spoken["hook"],
                "",
                spoken["bridge"],
                "",
                spoken["p1"],
                spoken["p2"],
                spoken["p3"],
                "",
                spoken["proof"],
                "",
                spoken["cta"],
            ]
        )
        return {
            "format_label": "منشور نصي كامل",
            "duration": "قراءة أقل من دقيقة",
            "scenes": f"سيناريو منشور — {title}\n\n{body}",
            "body": body,
            "on_screen": spoken["hook"],
            "notes": "السطر الأول يوقف التمرير · لا وعود بلا دليل",
            "beats": [{"name": key, "copy": value} for key, value in spoken.items()],
            "closing": "اختم بفعل واحد",
            "fallback": f"{spoken['hook']}\n\n{spoken['p1']}\n\n{cta}",
        }

    def _story(self, spoken: dict[str, str], cta: str) -> dict:
        frames = [
            (1, spoken["hook"]),
            (2, spoken["bridge"]),
            (3, spoken["p1"]),
            (4, spoken["p3"]),
            (5, spoken["cta"]),
        ]
        body = "\n\n".join(f"إطار {number}: {text}" for number, text in frames)
        return {
            "format_label": "قصة — سيناريو كامل",
            "duration": "5 إطارات",
            "scenes": f"سيناريو قصة\n\n{body}",
            "body": body,
            "on_screen": " ← ".join(text for _, text in frames),
            "notes": "نص قليل لكل إطار · تفاعل واحد في النهاية",
            "beats": [{"frame": n, "copy": text} for n, text in frames],
            "closing": cta,
            "fallback": f"3 إطارات: {spoken['hook']} ← {spoken['p1']} ← {cta}",
        }

    def _platform(self, platform: str) -> tuple[str, str]:
        if platform == "tiktok":
            return "تيك توك", "ابدأ بصريًا من أول نصف ثانية"
        if platform == "instagram":
            return "إنستغرام", "اجعل أول شاشة تستحق الحفظ/الإرسال"
        if platform == "youtube":
            return "يوتيوب", "جملة منطوقة واضحة في أول ثانيتين"
        if platform == "x":
            return "X", "جملة حادة + لقطة شاشة"
        if platform == "facebook":
            return "فيسبوك", "ابدأ بالمشكلة بسرعة"
        return platform, "ابدأ بالقيمة فورًا"

    def _screen_line(self, text: str, max_words: int = 6) -> str:
        words = [w for w in (text or "").replace("—", " ").replace(":", " ").split() if w]
        return " ".join(words[:max_words]) if words else "…"

    def _short(self, text: str, words: int = 8) -> str:
        parts = (text or "").split()
        if not parts:
            return "…"
        return " ".join(parts[:words]) + ("…" if len(parts) > words else "")
