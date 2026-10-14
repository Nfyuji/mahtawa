from __future__ import annotations

import json
import time
from typing import Any

import requests


class GPTGenerationError(RuntimeError):
    """A safe, user-facing GPT generation error without secrets."""


GOALS = {"discovery", "trust", "engagement", "conversion"}
ARCHETYPES = {"curiosity", "pain", "wow", "headline", "pacing"}
FORMATS = {"short_video", "carousel", "text_post", "story"}


class GPTIdeaGenerator:
    """Generate brand-specific content ideas using OpenAI structured output.

    Keeps the GPT payload light so Render free-tier requests finish before the
    reverse-proxy timeout. Full spoken scripts are assembled locally afterwards.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 75,
    ) -> None:
        if not api_key:
            raise GPTGenerationError("مفتاح OpenAI غير موجود.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(
        self,
        brand: Any,
        brief: dict[str, Any],
        count: int,
        focus: str = "",
    ) -> list[dict[str, Any]]:
        batch_sizes = self._batch_sizes(count)
        angles = (
            "مشكلات الجمهور ولحظات الألم اليومية، مع أمثلة محددة",
            "تعليم عملي، مقارنات، اعتراضات، وإثبات خبرة",
            "قصص استخدام المنتج، تحويل، تفاعل، وتجارب قابلة للقياس",
            "أخطاء شائعة وأسئلة متكررة من الجمهور",
            "قبل/بعد ونتائج عملية قابلة للتصوير",
        )

        # Sequential batches are safer on Render free memory and avoid worker kills.
        combined: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, size in enumerate(batch_sizes):
            raw_ideas = self._generate_batch(
                brand,
                brief,
                size,
                index + 1,
                len(batch_sizes),
                angles[index % len(angles)],
                focus,
            )
            for raw in raw_ideas:
                idea = self._validate_idea(raw, brand, brief)
                key = self._normalise_title(idea["title"])
                if key in seen:
                    idea["title"] = f"{idea['title']} — زاوية مختلفة"
                    key = self._normalise_title(idea["title"])
                seen.add(key)
                combined.append(idea)

        if len(combined) != count:
            raise GPTGenerationError(
                f"أعاد GPT عددًا غير مكتمل من الأفكار ({len(combined)} من {count})."
            )
        return combined

    def _generate_batch(
        self,
        brand: Any,
        brief: dict[str, Any],
        size: int,
        batch_number: int,
        total_batches: int,
        angle: str,
        focus: str,
    ) -> list[dict[str, Any]]:
        payload = {
            "model": self.model,
            "temperature": 0.75,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "أنت استراتيجي محتوى عربي خبير في الفيديو القصير. "
                        "اكتب أفكارًا أصلية ومحددة للنشاط المرسل، لا قوالب عامة. "
                        "لا تخترع أرقام نتائج أو شهادات أو مزايا لم يذكرها المستخدم. "
                        "كل فكرة يجب أن تكون مختلفة وقابلة للتصوير. أخرج JSON فقط."
                    ),
                },
                {
                    "role": "user",
                    "content": self._prompt(
                        brand,
                        brief,
                        size,
                        batch_number,
                        total_batches,
                        angle,
                        focus,
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "content_ideas",
                    "strict": True,
                    "schema": self._schema(size),
                },
            },
        }

        response = self._post(payload)
        try:
            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            ideas = parsed["ideas"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise GPTGenerationError("رد GPT لم يكن بصيغة مفهومة.") from exc
        if not isinstance(ideas, list) or len(ideas) != size:
            raise GPTGenerationError(f"دفعة GPT رقم {batch_number} غير مكتملة.")
        return ideas

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error = ""
        for attempt in range(3):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )
            except requests.Timeout as exc:
                last_error = "انتهت مهلة الاتصال بـ OpenAI. حاول مرة أخرى."
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise GPTGenerationError(last_error) from exc
            except requests.RequestException as exc:
                last_error = "تعذر الاتصال بخدمة OpenAI."
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise GPTGenerationError(last_error) from exc

            if response.ok:
                try:
                    return response.json()
                except ValueError as exc:
                    raise GPTGenerationError("خدمة OpenAI أعادت ردًا غير صالح.") from exc

            detail = self._error_detail(response)
            if response.status_code == 401:
                raise GPTGenerationError("مفتاح OpenAI غير صحيح أو منتهي.")
            if response.status_code == 429:
                last_error = "تم تجاوز حد استخدام OpenAI أو الرصيد غير كافٍ."
            elif response.status_code >= 500:
                last_error = "خدمة OpenAI غير متاحة مؤقتًا."
            else:
                raise GPTGenerationError(f"رفض OpenAI الطلب: {detail}")

            if attempt < 2:
                time.sleep(2 * (attempt + 1))
        raise GPTGenerationError(last_error or "فشل توليد الأفكار عبر OpenAI.")

    def _prompt(
        self,
        brand: Any,
        brief: dict[str, Any],
        size: int,
        batch_number: int,
        total_batches: int,
        angle: str,
        focus: str,
    ) -> str:
        pillars = brief.get("pillars") or []
        brand_data = {
            "name": brand.name,
            "description": brand.description,
            "industry": brand.industry,
            "offer": brand.offer,
            "market": brand.market,
            "dialect": brand.dialect,
            "audience": brand.audience,
            "problem": brand.problem,
            "audience_desire": brand.audience_desire,
            "competitive_advantage": brand.competitive_advantage,
            "brand_voice": brand.brand_voice,
            "resources": brand.resources,
            "marketing_objective": brand.marketing_objective,
            "monthly_goal": brand.monthly_goal,
            "platforms": brand.platforms,
        }
        pillar_data = [
            {
                "name": p.get("name"),
                "function": p.get("function"),
                "job": p.get("job"),
            }
            for p in pillars
        ]
        focus_block = (
            f"\n\nتعليمات خاصة لهذه المهمة:\n{focus}\n" if focus.strip() else ""
        )
        return (
            f"أنشئ {size} أفكار ضمن الدفعة {batch_number} من {total_batches}.\n"
            f"ركّز هذه الدفعة على: {angle}.\n\n"
            f"بيانات النشاط:\n{json.dumps(brand_data, ensure_ascii=False)}\n\n"
            f"المحاور المسموحة:\n{json.dumps(pillar_data, ensure_ascii=False)}\n\n"
            "قواعد إلزامية:\n"
            "1) استخدم اسم محور موجود حرفيًا في pillar.\n"
            "2) لا تكرر موضوعًا أو عنوانًا داخل الدفعة.\n"
            "3) العنوان والخطافات محددة لهذا النشاط وليست نصائح تسويق عامة.\n"
            "4) hooks خمس افتتاحيات قوية ومختلفة بهذا الترتيب: "
            "(أ) ألم محدد، (ب) فجوة فضول، (ج) رأي مخالف، "
            "(د) نتيجة أو آلية محددة بلا أرقام مختلقة، (هـ) افتتاح بصري. "
            "كل خطاف جملة واحدة، 5–12 كلمة، يبدأ من أول نفس، بلا تحية.\n"
            "5) points ثلاث نقاط فعلية تكمل وعد الخطاف.\n"
            "6) لا تقل الأفضل أو مضمون أو أرقام غير موجودة في البيانات.\n"
            "7) وزّع الأهداف، ولا تجعل كل الأفكار ترويجًا مباشرًا."
            + focus_block
        )

    def _validate_idea(
        self,
        raw: dict[str, Any],
        brand: Any,
        brief: dict[str, Any],
    ) -> dict[str, Any]:
        allowed_pillars = [p["name"] for p in brief.get("pillars") or []]
        pillar = str(raw.get("pillar") or "").strip()
        if pillar not in allowed_pillars:
            pillar = allowed_pillars[0] if allowed_pillars else "قيمة وثقة"

        goal = str(raw.get("goal") or "trust").strip()
        if goal not in GOALS:
            goal = "trust"
        archetype = str(raw.get("hook_archetype") or "pain").strip()
        if archetype not in ARCHETYPES:
            archetype = "pain"

        hooks = self._clean_list(raw.get("hooks"), 5, 90)
        points = self._clean_list(raw.get("points"), 3, 180)
        formats = [
            value
            for value in self._clean_list(raw.get("format_options"), 3, 30)
            if value in FORMATS
        ]
        if not formats:
            formats = ["short_video"]
        if len(hooks) < 5 or len(points) < 3:
            raise GPTGenerationError("إحدى أفكار GPT ناقصة الخطافات أو النقاط.")

        problem = self._clean(raw.get("problem"), 280)
        promise = self._clean(raw.get("promise"), 220)
        visual = self._clean(raw.get("visual"), 240)
        cta = self._clean(raw.get("cta"), 120)
        title = self._clean(raw.get("title"), 180)
        name = getattr(brand, "name", "النشاط")

        # Build spoken/screen/shot packs locally so GPT stays fast and reliable.
        script = self._local_script(hooks[0], problem, promise, points, visual, cta, name)

        return {
            "title": title,
            "pillar": pillar,
            "goal": goal,
            "hook_archetype": archetype,
            "hooks": hooks,
            "problem": problem,
            "points": points,
            "visual": visual,
            "promise": promise,
            "cta": cta,
            "rationale": self._clean(raw.get("rationale"), 260),
            "format_options": formats,
            "success_metric": self._clean(raw.get("success_metric"), 120),
            "repurpose": self._clean(raw.get("repurpose"), 180),
            "effort": self._clean(raw.get("effort"), 30) or "متوسط",
            "evidence_type": "hypothesis",
            "source_keys": [],
            **script,
        }

    def _local_script(
        self,
        hook: str,
        problem: str,
        promise: str,
        points: list[str],
        visual: str,
        cta: str,
        name: str,
    ) -> dict[str, dict[str, str]]:
        say = {
            "hook": hook.rstrip(".") + ".",
            "bridge": f"{problem}. والوعد: {promise}.",
            "p1": points[0].rstrip(".") + ".",
            "p2": points[1].rstrip(".") + ".",
            "p3": points[2].rstrip(".") + ".",
            "proof": f"شوف هنا: {visual}.",
            "cta": cta.rstrip(".") + ".",
        }
        screen = {
            "hook": self._screen_line(hook),
            "bridge": self._screen_line(problem),
            "p1": self._screen_line(points[0]),
            "p2": self._screen_line(points[1]),
            "p3": self._screen_line(points[2]),
            "proof": self._screen_line(visual),
            "cta": self._screen_line(cta),
        }
        shots = {
            "hook": "وجه للكاميرا أو نص كبير فورًا — بدون شعار",
            "bridge": "مثال بصري سريع للمشكلة",
            "p1": f"لقطة أو شاشة توضّح: {self._screen_line(points[0], 4)}",
            "p2": "غيّر الزاوية مع نص مختصر",
            "p3": f"اعرض التطبيق داخل {name}",
            "proof": visual,
            "cta": "ثبّت آخر صورة مع نص الدعوة",
        }
        return {"say": say, "screen": screen, "shots": shots}

    def _screen_line(self, text: str, max_words: int = 6) -> str:
        words = [w for w in (text or "").replace("—", " ").split() if w]
        return " ".join(words[:max_words]) if words else "…"

    def _clean_list(self, value: Any, count: int, limit: int) -> list[str]:
        if not isinstance(value, list):
            return []
        result = []
        for item in value:
            clean = self._clean(item, limit)
            if clean and clean not in result:
                result.append(clean)
            if len(result) == count:
                break
        return result

    def _clean(self, value: Any, limit: int) -> str:
        text = " ".join(str(value or "").split()).strip(" \"'")
        return text[:limit].strip()

    def _normalise_title(self, title: str) -> str:
        return "".join(char for char in title.lower() if char.isalnum())

    def _error_detail(self, response: requests.Response) -> str:
        try:
            detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            detail = response.text
        return self._clean(detail, 180) or f"HTTP {response.status_code}"

    def _batch_sizes(self, count: int) -> list[int]:
        # Prefer 1–2 larger light batches so Render finishes before proxy timeout.
        if count <= 15:
            return [count]
        if count <= 30:
            first = (count + 1) // 2
            return [first, count - first]
        batch_count = min(3, max(1, (count + 14) // 15))
        base, remainder = divmod(count, batch_count)
        return [base + (1 if index < remainder else 0) for index in range(batch_count)]

    def _schema(self, size: int) -> dict[str, Any]:
        idea_properties = {
            "title": {"type": "string"},
            "pillar": {"type": "string"},
            "goal": {"type": "string", "enum": sorted(GOALS)},
            "hook_archetype": {"type": "string", "enum": sorted(ARCHETYPES)},
            "hooks": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 5,
                "maxItems": 5,
            },
            "problem": {"type": "string"},
            "points": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 3,
            },
            "visual": {"type": "string"},
            "promise": {"type": "string"},
            "cta": {"type": "string"},
            "rationale": {"type": "string"},
            "format_options": {
                "type": "array",
                "items": {"type": "string", "enum": sorted(FORMATS)},
                "minItems": 1,
                "maxItems": 3,
            },
            "success_metric": {"type": "string"},
            "repurpose": {"type": "string"},
            "effort": {"type": "string", "enum": ["خفيف", "متوسط", "مرتفع"]},
        }
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ideas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": idea_properties,
                        "required": list(idea_properties),
                    },
                    "minItems": size,
                    "maxItems": size,
                }
            },
            "required": ["ideas"],
        }
