from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.extensions import db
from app.models import Brand, ContentItem, ContentPillar, ContentScript, Strategy
from app.services.hook_science import HookScienceEngine
from app.services.playbook import SOURCE_CATALOG, build_idea_bank, build_strategy_brief
from app.services.scenario import ScenarioEngine


FORMAT_LABELS = {
    "short_video": "فيديو قصير",
    "carousel": "كاروسيل",
    "text_post": "منشور نصي",
    "story": "قصة تفاعلية",
}


class StrategyGenerator:
    def __init__(self) -> None:
        self.hooks = HookScienceEngine()
        self.scenarios = ScenarioEngine()

    def generate(self, brand: Brand) -> Strategy:
        start = brand.campaign_start_date or date.today()
        platforms = brand.platforms or ["tiktok", "instagram"]
        posts_per_week = max(2, min(7, brand.posts_per_week or 5))
        item_count = max(12, min(28, posts_per_week * 4))
        brief = build_strategy_brief(brand, item_count)
        ideas = build_idea_bank(brand, brief["pillars"], item_count)
        version = max((strategy.version or 1 for strategy in brand.strategies), default=0) + 1

        strategy = Strategy(
            brand_id=brand.id,
            title=f"استراتيجية محتوى 30 يوم — {brand.name}",
            month_start=start,
            month_end=start + timedelta(days=29),
            primary_goal=brand.monthly_goal,
            executive_summary=(
                f"مسودة تنفيذية من {item_count} قطعة محتوى موزعة على "
                f"{len(platforms)} منصة، مبنية على هدف الشركة وقدرتها الأسبوعية. "
                "الفرص الرائجة المقترحة فرضيات يجب التحقق منها قبل النشر."
            ),
            market_summary=(
                f"الجمهور: {brand.audience}. المشكلة: {brand.problem}. "
                f"النتيجة المطلوبة: {brand.audience_desire or 'تُراجع مع الفريق'}."
            ),
            positioning=(
                brand.competitive_advantage
                or f"{brand.name} يقدّم {brand.offer or brand.description} بطريقة واضحة وعملية."
            ),
            version=version,
            strategy_data=brief,
            source_snapshot=SOURCE_CATALOG,
            status="draft",
        )
        db.session.add(strategy)
        db.session.flush()

        for index, pillar in enumerate(brief["pillars"], start=1):
            db.session.add(
                ContentPillar(
                    strategy_id=strategy.id,
                    name=pillar["name"],
                    function=pillar["function"],
                    distribution_percent=pillar["percent"],
                    sort_order=index,
                )
            )

        offsets = self._schedule_offsets(item_count)
        for index, idea in enumerate(ideas):
            day = offsets[index] + 1
            idea = dict(idea)
            platform = platforms[index % len(platforms)]
            content_type = self._content_type(platform, idea["format_options"], index)
            idea.update(
                {
                    "platform": platform,
                    "content_type": content_type,
                    "post_goal": idea["goal"],
                    "day_number": day,
                    "scheduled_date": start + timedelta(days=offsets[index]),
                    "priority": "high" if index < max(4, item_count // 4) else "medium",
                }
            )

            pack = self.scenarios.build(idea, brand, day)
            score, breakdown = self._score(idea, brand, pack)
            content = ContentItem(
                strategy_id=strategy.id,
                day_number=day,
                scheduled_date=idea["scheduled_date"],
                platform=platform,
                pillar_name=idea["pillar"],
                title=idea["title"],
                problem_desire=pack["problem"],
                post_goal=idea["goal"],
                rationale=idea["rationale"],
                content_type=content_type,
                creative_concept=pack["creative_concept"],
                hooks=pack["hooks"],
                script_body=pack["script_body"],
                scenes=pack["scenes"],
                on_screen_text=pack["on_screen_text"],
                editing_notes=pack["editing_notes"],
                cta=pack["cta"],
                keywords=self._keywords(brand, idea),
                hashtags=self._hashtags(brand, idea),
                priority=idea["priority"],
                virality_score=score,
                virality_breakdown=breakdown,
                status="draft",
            )
            db.session.add(content)
            db.session.flush()

            script = pack["script"]
            db.session.add(
                ContentScript(
                    content_item_id=content.id,
                    hook=script.get("hook"),
                    promise=script.get("promise"),
                    problem=script.get("problem"),
                    body=script.get("body"),
                    peak_moment=script.get("peak_moment"),
                    closing=script.get("closing"),
                    cta=script.get("cta"),
                    alt_hooks=script.get("alt_hooks") or [],
                    alt_narratives=script.get("alt_narratives") or [],
                    hypothesis=script.get("hypothesis"),
                    fallback_version=script.get("fallback_version"),
                )
            )

        db.session.commit()
        return strategy

    def regenerate_script(
        self, item: ContentItem, brand: Brand, prompt: str = ""
    ) -> ContentScript:
        idea = self._idea_from_item(item)
        pack = self.scenarios.build(idea, brand, item.day_number or 1)
        if prompt:
            note = f"\n\nملاحظة الفريق: {prompt}"
            pack["scenes"] = (pack.get("scenes") or "") + note
            pack["script"]["body"] = (pack["script"].get("body") or "") + note
        self._apply_pack(item, pack, brand, idea)
        db.session.commit()
        return item.script

    def select_hook(self, item: ContentItem, hook_index: int) -> ContentScript | None:
        hooks = list(item.hooks or [])
        if not hooks:
            return item.script
        hook_index = max(0, min(len(hooks) - 1, hook_index))
        selected = hooks.pop(hook_index)
        item.hooks = [selected, *hooks]
        if item.script:
            item.script.hook = selected
            item.script.alt_hooks = hooks
        breakdown = dict(item.virality_breakdown or {})
        breakdown["hook_scores"] = self._evaluate_hooks(item.hooks, item.problem_desire or "")
        item.virality_breakdown = breakdown
        db.session.commit()
        return item.script

    def _apply_pack(self, item: ContentItem, pack: dict, brand: Brand, idea: dict) -> None:
        item.scenes = pack["scenes"]
        item.on_screen_text = pack["on_screen_text"]
        item.editing_notes = pack["editing_notes"]
        item.script_body = pack["script_body"]
        item.hooks = pack["hooks"]
        item.creative_concept = pack["creative_concept"]
        item.cta = pack["cta"]
        item.problem_desire = pack["problem"]
        score, breakdown = self._score(idea, brand, pack)
        item.virality_score = score
        item.virality_breakdown = breakdown
        item.status = "draft"

        script_data = pack["script"]
        if item.script:
            for key, value in script_data.items():
                setattr(item.script, key, value)
        else:
            db.session.add(ContentScript(content_item_id=item.id, **script_data))

    def _idea_from_item(self, item: ContentItem) -> dict:
        meta = item.virality_breakdown or {}
        return {
            "title": item.title,
            "problem": item.problem_desire,
            "problem_desire": item.problem_desire,
            "hooks": item.hooks or [],
            "platform": item.platform,
            "content_type": item.content_type or "short_video",
            "post_goal": item.post_goal,
            "goal": item.post_goal,
            "cta": item.cta,
            "pillar": item.pillar_name,
            "points": meta.get("idea_points") or [],
            "visual": meta.get("visual"),
            "promise": meta.get("promise"),
            "rationale": item.rationale,
            "success_metric": meta.get("success_metric"),
            "repurpose": meta.get("repurpose"),
            "effort": meta.get("effort"),
            "evidence_type": "hypothesis",
            "source_keys": meta.get("source_keys") or [],
        }

    def _score(self, idea: dict, brand: Brand, pack: dict) -> tuple[int, dict]:
        hook_score = self.hooks.score_hook_strength(
            {**idea, "hooks": pack.get("hooks"), "scenes": pack.get("scenes")}
        )
        components: dict[str, int] = {
            "audience_fit": 15 if brand.audience and brand.problem else 9,
            "hook": hook_score,
            "clarity": 12 if idea.get("promise") else 8,
            "practical_value": 15 if len(idea.get("points") or []) >= 3 else 9,
            "action": 10 if idea.get("cta") else 5,
            "credibility": 10,
            "platform_fit": 10 if idea.get("content_type") else 6,
            "feasibility": 8 if idea.get("effort") != "مرتفع" else 6,
        }
        score = min(100, sum(components.values()))
        if score >= 85:
            label = "جاهزة للاختبار"
        elif score >= 70:
            label = "جيدة وتحتاج مراجعة سريعة"
        else:
            label = "تحتاج تحسينًا قبل الإنتاج"

        breakdown: dict[str, Any] = {
            **components,
            "readiness_label": label,
            "score_note": "تقدير داخلي لجودة التحضير، وليس توقعًا للمشاهدات أو الانتشار.",
            "format_label": FORMAT_LABELS.get(
                idea.get("content_type"), idea.get("content_type", "محتوى")
            ),
            "success_metric": idea.get("success_metric"),
            "repurpose": idea.get("repurpose"),
            "effort": idea.get("effort"),
            "evidence_type": idea.get("evidence_type", "hypothesis"),
            "evidence_label": "فرضية تحتاج اختبارًا",
            "source_keys": idea.get("source_keys") or [],
            "idea_points": idea.get("points") or [],
            "visual": idea.get("visual"),
            "promise": idea.get("promise"),
            "hook_scores": self._evaluate_hooks(
                pack.get("hooks") or [], brand.audience or ""
            ),
        }
        return score, breakdown

    def _evaluate_hooks(self, hooks: list[str], audience: str) -> list[dict]:
        audience_terms = {word for word in audience.split() if len(word) > 3}
        rows = []
        for hook in hooks:
            text = str(hook).strip()
            length = len(text)
            clarity = 90 if 12 <= length <= 70 else 72
            curiosity = 86 if any(token in text for token in ("؟", "لماذا", "كيف", "قبل", "خطأ", "سر")) else 72
            relevance = 88 if any(term in text for term in audience_terms) else 78
            credibility = 92 if not any(token in text for token in ("مضمون", "أكيد", "100%", "الأفضل في العالم")) else 45
            total = round((clarity + curiosity + relevance + credibility) / 4)
            rows.append(
                {
                    "text": text,
                    "score": total,
                    "clarity": clarity,
                    "curiosity": curiosity,
                    "relevance": relevance,
                    "credibility": credibility,
                }
            )
        return rows

    def _content_type(self, platform: str, options: list[str], index: int) -> str:
        if platform in {"tiktok", "youtube"}:
            return "short_video"
        if platform == "x":
            return "text_post"
        if platform == "instagram" and "carousel" in options and index % 3 == 1:
            return "carousel"
        if platform == "facebook" and "text_post" in options and index % 2:
            return "text_post"
        return options[0] if options else "short_video"

    def _schedule_offsets(self, item_count: int) -> list[int]:
        if item_count <= 1:
            return [0]
        return [round(index * 29 / (item_count - 1)) for index in range(item_count)]

    def _keywords(self, brand: Brand, idea: dict) -> list[str]:
        values = [brand.name, brand.industry, idea.get("pillar"), idea.get("goal")]
        return [str(value) for value in values if value][:6]

    def _hashtags(self, brand: Brand, idea: dict) -> list[str]:
        def tag(value: str | None) -> str | None:
            if not value:
                return None
            clean = "_".join(value.replace("#", "").split()[:3])
            return f"#{clean}" if clean else None

        values = [tag(brand.name), tag(brand.industry), tag(idea.get("pillar"))]
        return [value for value in values if value]
