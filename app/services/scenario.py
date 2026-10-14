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
        points = self._materialize_points(points, problem, name, offer)
        visual = idea.get("visual") or f"مثال حقيقي من داخل {name}"
        promise = idea.get("promise") or f"تعرف أول خطوة عملية تجاه حل المشكلة"
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
        # Prefer a short provided hook over a title-echo template.
        preferred = next(
            (h for h in provided_hooks if self._is_strong_hook(h, title)),
            None,
        )
        hook = self._clean_hook(
            preferred or (hooks[0] if hooks else ""),
            problem,
            title,
        )
        if hooks and hook not in hooks:
            hooks = [hook, *[h for h in hooks if h != hook]][:5]
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
        )
        screens = self._screen_pack(screen, spoken, points, problem, name, cta)
        shot_pack = self._shot_pack(shots, name, visual)

        if content_type == "carousel":
            execution = self._carousel(spoken, screens, visual, cta, title)
        elif content_type == "text_post":
            execution = self._text_post(spoken, cta, title)
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
            )

        hypothesis = (
            f"إذا بدأ المقطع بـ«{hook}» وذكر مشكلة «{self._short(problem, 10)}» "
            f"ثم قدّم حل {name}، يرتفع الاحتفاظ على {platform_label}."
        )
        editing_notes = (
            f"{execution['notes']} · {platform_tip} · "
            "اقرأ «تقول» حرفيًا · نص الشاشة قصير وكبير"
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
                    f"نسخة 15ث: {spoken['hook']} ← {spoken['p3']} ← {spoken['cta']}",
                    f"نسخة سؤال: ما أصعب جزء في {self._short(problem, 8)}؟",
                ],
                "hypothesis": hypothesis,
                "fallback_version": execution["fallback"],
            },
        }

    # ------------------------------------------------------------------
    #  Content: points → spoken lines
    # ------------------------------------------------------------------

    def _materialize_points(
        self,
        points: list[str],
        problem: str,
        name: str,
        offer: str,
    ) -> list[str]:
        mistake, impact, fix = self._problem_beats(problem, name)
        concrete = [mistake, impact, fix]
        result = []
        for index, point in enumerate(points[:3]):
            if self._looks_like_instruction(point) or self._looks_like_outline(point):
                result.append(concrete[index])
            else:
                result.append(self._strip_labels(point))
        while len(result) < 3:
            result.append(concrete[len(result)])
        return result

    def _problem_beats(self, problem: str, name: str) -> tuple[str, str, str]:
        text = (problem or "").strip()
        tools = self._extract_tools(text)
        if len(tools) >= 2:
            listed = " و".join(tools[:3])
            return (
                f"تفتح {listed} كل شوي… وتنسى وين وقفت",
                "كل يوم يضيع وقتك بين التبديل والنسخ بدل ما تخلّص مهمة وحدة",
                f"اجمع المحتوى والردود في مساحة واحدة داخل {name}",
            )
        short = self._short(text, 12) if text else "تشتت الشغل بين أدوات كثيرة"
        return (
            f"تتعامل مع «{short}» كأنه شيء طبيعي",
            "يومك يتقطع… وكل مهمة تصير أبطأ بدون ما تحس",
            f"ابدأ بخطوة واحدة داخل {name} ووقف التبديل بين الأدوات",
        )

    def _extract_tools(self, text: str) -> list[str]:
        between = re.search(r"بين\s+(.+)$", text)
        if not between:
            return []
        tools = [
            t.strip(" .،,ـ")
            for t in re.split(r"\s+وال?|\s*،\s*|\s*/\s*", between.group(1))
            if t and len(t.strip()) > 2
        ]
        return [t for t in tools if t not in ("ال", "ـ")][:4]

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
    ) -> dict[str, str]:
        aud = self._short(audience, 6)
        defaults = {
            "hook": hook,
            "bridge": (
                f"إذا أنت من {aud} — هالمشهد مألوف: "
                f"{problem.rstrip(' .')}. "
                f"بنهاية المقطع {promise.rstrip(' .')}."
            ),
            "p1": f"الخطأ الأول: {points[0].rstrip(' .')}.",
            "p2": f"أثره: {points[1].rstrip(' .')}.",
            "p3": f"التصحيح: {points[2].rstrip(' .')}.",
            "proof": f"شوفها عمليًا داخل {name}.",
            "cta": f"{cta.rstrip(' .')}. وابدأ بخطوة واحدة داخل {name} اليوم.",
        }
        # Avoid double labels if point already starts with الخطأ/أثره/أول
        for key, prefixes in (
            ("p1", ("الخطأ", "أولًا")),
            ("p2", ("أثره", "ثانيًا")),
            ("p3", ("أول تصحيح", "ثالثًا", "التصحيح")),
        ):
            raw = points[{"p1": 0, "p2": 1, "p3": 2}[key]].rstrip(" .")
            if raw.startswith(prefixes):
                defaults[key] = raw + "."

        result = {}
        for key, default in defaults.items():
            custom = str(say.get(key) or "").strip()
            if (
                custom
                and len(custom.split()) >= 8
                and not self._looks_like_instruction(custom)
                and not self._looks_like_outline(custom)
            ):
                result[key] = self._end(custom)
            else:
                result[key] = self._end(default)
        result["hook"] = self._end(hook)
        # Proof: if visual is useful and short, append it; else keep clean.
        if visual and len(visual.split()) <= 10 and "قائمة" not in visual:
            result["proof"] = self._end(f"شوفها عمليًا داخل {name}: {visual}")
        return result

    def _screen_pack(
        self,
        screen: dict,
        spoken: dict[str, str],
        points: list[str],
        problem: str,
        name: str,
        cta: str,
    ) -> dict[str, str]:
        """Punchy on-screen labels — not truncated spoken lines."""
        crafted = {
            "hook": self._screen_hook(spoken["hook"]),
            "bridge": self._punch(problem, 4) or "المشكلة",
            "p1": "خطأ 1 · " + (self._punch(points[0], 4) or "سمِّه"),
            "p2": "الأثر · " + (self._punch(points[1], 4) or "وقت ضائع"),
            "p3": f"التصحيح · {name}",
            "proof": f"داخل {name}",
            "cta": self._punch(cta, 3) or "احفظ وشارك",
        }
        result = {}
        for key, default in crafted.items():
            custom = str(screen.get(key) or "").strip()
            if custom and not self._looks_like_instruction(custom) and len(custom.split()) <= 8:
                result[key] = custom
            else:
                result[key] = default
        return result

    def _shot_pack(self, shots: dict, name: str, visual: str) -> dict[str, str]:
        defaults = {
            "hook": "وجه قريب أو نص كبير يملأ الشاشة — بدون شعار",
            "bridge": "إيماءة سريعة + لمحة لتبويبات/تطبيقات مفتوحة",
            "p1": "لقطة واحدة توضّح الخطأ (شاشة/إيماءة)",
            "p2": "غيّر الزاوية — أظهر أثر المشكلة على اليوم",
            "p3": f"اعرض الحل داخل واجهة {name}",
            "proof": visual,
            "cta": "ثبّت آخر فريم مع نص الدعوة كبير",
        }
        result = {}
        for key, default in defaults.items():
            custom = str(shots.get(key) or "").strip()
            result[key] = custom if custom else default
        return result

    # ------------------------------------------------------------------
    #  Formatters
    # ------------------------------------------------------------------

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
    ) -> dict:
        beats = [
            ("0–3ث", "الخطاف", "hook"),
            ("3–8ث", "المشكلة", "bridge"),
            ("8–16ث", "الخطأ 1", "p1"),
            ("16–24ث", "الأثر", "p2"),
            ("24–32ث", "التصحيح", "p3"),
            ("32–40ث", "الإثبات", "proof"),
            ("40–45ث", "الدعوة", "cta"),
        ]

        lines = [
            f"سيناريو تصوير | يوم {day} | {platform_label} | ~45 ثانية",
            f"العنوان: {title}",
            f"البراند: {name} · الهدف: {goal_ar}",
            "",
            "طريقة الاستخدام: اقرأ «تقول» حرفيًا · حط «الشاشة» كنص كبير · نفّذ «التصوير»",
            "",
        ]
        for time_label, role, key in beats:
            lines.extend(
                [
                    f"── {time_label} · {role} ──",
                    f"تقول: {spoken[key]}",
                    f"الشاشة: {screens[key]}",
                    f"التصوير: {shots[key]}",
                    "",
                ]
            )
        lines.extend(
            [
                "── تلقين متصل ──",
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
            "duration": "~45 ثانية",
            "scenes": "\n".join(lines).strip(),
            "body": body,
            "on_screen": " ← ".join(screens[key] for _, _, key in beats),
            "notes": "بدون مقدمة · قص كل 2–3ث · نص عربي كبير",
            "beats": [
                {
                    "time": time_label,
                    "name": role,
                    "say": spoken[key],
                    "write": screens[key],
                    "shoot": shots[key],
                }
                for time_label, role, key in beats
            ],
            "closing": "جمّد آخر فريم بعد الدعوة",
            "fallback": (
                f"نسخة 15ث:\n"
                f"1) {spoken['hook']}\n"
                f"2) {spoken['p3']}\n"
                f"3) {spoken['cta']}"
            ),
        }

    def _carousel(
        self,
        spoken: dict[str, str],
        screens: dict[str, str],
        visual: str,
        cta: str,
        title: str,
    ) -> dict:
        slides = [
            (1, "الغلاف", spoken["hook"], screens["hook"]),
            (2, "المشكلة", spoken["bridge"], screens["bridge"]),
            (3, "الخطأ 1", spoken["p1"], screens["p1"]),
            (4, "الأثر", spoken["p2"], screens["p2"]),
            (5, "التصحيح", spoken["p3"], screens["p3"]),
            (6, "الإثبات", spoken["proof"], screens["proof"]),
            (7, "الدعوة", spoken["cta"], screens["cta"]),
        ]
        lines = [f"سيناريو كاروسيل | {title}", ""]
        for number, role, say, write in slides:
            lines.extend(
                [
                    f"شريحة {number} · {role}",
                    f"النص: {write}",
                    f"الشرح: {say}",
                    "",
                ]
            )
        body = "\n\n".join(
            f"شريحة {n} ({role}): {say}" for n, role, say, _ in slides
        )
        return {
            "format_label": "كاروسيل — سيناريو كامل",
            "duration": "7 شرائح",
            "scenes": "\n".join(lines).strip(),
            "body": body,
            "on_screen": " ← ".join(w for _, _, _, w in slides),
            "notes": "شريحة = فكرة واحدة · غلاف يُفهم لوحده · CTA في الأخير",
            "beats": [
                {"slide": n, "name": role, "copy": say, "write": write}
                for n, role, say, write in slides
            ],
            "closing": "اختم بشريحة دعوة واحدة",
            "fallback": f"4 شرائح: {screens['hook']} ← {screens['p1']} ← {visual} ← {cta}",
        }

    def _text_post(self, spoken: dict[str, str], cta: str, title: str) -> dict:
        body = "\n\n".join(
            [
                spoken["hook"],
                spoken["bridge"],
                spoken["p1"],
                spoken["p2"],
                spoken["p3"],
                spoken["proof"],
                spoken["cta"],
            ]
        )
        return {
            "format_label": "منشور نصي كامل",
            "duration": "قراءة أقل من دقيقة",
            "scenes": f"سيناريو منشور | {title}\n\n{body}",
            "body": body,
            "on_screen": spoken["hook"],
            "notes": "السطر الأول يوقف التمرير",
            "beats": [{"name": k, "copy": v} for k, v in spoken.items()],
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
        body = "\n\n".join(f"إطار {n}: {text}" for n, text in frames)
        return {
            "format_label": "قصة — سيناريو كامل",
            "duration": "5 إطارات",
            "scenes": f"سيناريو قصة\n\n{body}",
            "body": body,
            "on_screen": " ← ".join(t for _, t in frames),
            "notes": "نص قليل لكل إطار · تفاعل واحد في النهاية",
            "beats": [{"frame": n, "copy": t} for n, t in frames],
            "closing": cta,
            "fallback": f"3 إطارات: {spoken['hook']} ← {spoken['p1']} ← {cta}",
        }

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _is_strong_hook(self, hook: str, title: str) -> bool:
        text = (hook or "").strip()
        if not text or "…" in text:
            return False
        words = text.split()
        if len(words) < 4 or len(words) > 12:
            return False
        # Reject hooks that mostly paste the title.
        title_words = set((title or "").split())
        overlap = sum(1 for w in words if w in title_words)
        if title_words and overlap >= max(4, len(words) // 2):
            return False
        return True

    def _clean_hook(self, hook: str, problem: str, title: str = "") -> str:
        text = (hook or "").strip()
        if self._is_strong_hook(text, title):
            return text
        tools = self._extract_tools(problem)
        if tools:
            return f"أكبر خطأ في {tools[0]} — وأغلب الناس تسويه"
        short_problem = self._short(problem, 5)
        return f"أكبر خطأ في {short_problem} — وأغلب الناس تسويه"

    def _strip_labels(self, point: str) -> str:
        clean = point.strip()
        for prefix in (
            "الخطأ الأول:",
            "الخطأ الأول：",
            "أثره على يومك:",
            "أثره اليومي:",
            "أول تصحيح بسيط:",
            "أول تصحيح:",
            "أولًا:",
            "ثانيًا:",
            "ثالثًا:",
        ):
            if clean.startswith(prefix):
                return clean[len(prefix) :].strip()
        return clean

    def _looks_like_instruction(self, text: str) -> bool:
        starters = (
            "سمِّ", "سمّي", "سمّ", "وضّح", "اختم", "اعرض", "اكتب", "حط", "اربط",
            "قدّم", "فرّق", "راجع", "حدّث", "جدول", "ضع ", "اطلب", "حوّل",
            "نفّذ", "قارن", "حدّد", "اذكر", "اشرح", "أظهر", "اكشف", "أنشئ",
            "صوّر", "شارك",
        )
        return any(text.strip().startswith(s) for s in starters)

    def _looks_like_outline(self, text: str) -> bool:
        markers = (
            "كما يحدث",
            "أثره اليومي",
            "تصحيح بسيط",
            "الطريقة القديمة",
            "بدون تزيين",
            "علامة 1",
            "الشي الأول",
        )
        return len(text.split()) <= 8 and any(m in text for m in markers)

    def _platform(self, platform: str) -> tuple[str, str]:
        tips = {
            "tiktok": ("تيك توك", "ابدأ بصريًا من أول نصف ثانية"),
            "instagram": ("إنستغرام", "أول شاشة تستحق الحفظ"),
            "youtube": ("يوتيوب", "جملة واضحة في أول ثانيتين"),
            "x": ("X", "جملة حادة + لقطة شاشة"),
            "facebook": ("فيسبوك", "ابدأ بالمشكلة بسرعة"),
        }
        return tips.get(platform, (platform, "ابدأ بالقيمة فورًا"))

    def _screen_hook(self, hook: str) -> str:
        text = (hook or "").strip().rstrip(".")
        for sep in ("—", "–", " - "):
            if sep in text:
                left, _, right = text.partition(sep)
                head = " ".join(left.split()[:2])
                # Normalize "وأغلب الناس تسويه" → "أغلب الناس تسويه"
                tail = right.strip()
                for prefix in ("وأغلب", "واغلب", "و أغلب"):
                    if tail.startswith(prefix):
                        tail = "أغلب" + tail[len(prefix) :]
                        break
                tail = " ".join(tail.split()[:3])
                return f"{head} · {tail}".strip(" ·")
        words = text.split()
        return " ".join(words[:6]) if words else text

    def _punch(self, text: str, max_words: int = 5) -> str:
        skip = {
            "الخطأ", "الأول", "أثره", "على", "يومك", "أول", "تصحيح",
            "إذا", "أنت", "من", "هذا", "اللي", "كل", "شوي",
        }
        words = [
            w.strip(".:،")
            for w in (text or "").replace("—", " ").replace(":", " ").split()
            if w.strip(".:،")
        ]
        # Prefer concrete words; if filtering empties, fall back to raw head.
        filtered = [w for w in words if w not in skip]
        use = filtered if len(filtered) >= 2 else words
        return " ".join(use[:max_words]) if use else ""

    def _short(self, text: str, words: int = 8) -> str:
        parts = (text or "").split()
        if not parts:
            return "…"
        return " ".join(parts[:words]) + ("…" if len(parts) > words else "")

    def _end(self, text: str) -> str:
        clean = (text or "").strip().rstrip(" .")
        return clean + "." if clean else ""
