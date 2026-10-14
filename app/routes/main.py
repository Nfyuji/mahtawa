from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Optional

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Brand, ContentItem
from app.services.gpt_ideas import GPTGenerationError
from app.services.key_vault import decrypt_api_key, encrypt_api_key
from app.services.playbook import SOURCE_CATALOG
from app.services.strategy import StrategyGenerator

main_bp = Blueprint("main", __name__)

PLATFORM_KEYS = ("tiktok", "instagram", "youtube", "x", "facebook")
MARKETS = {"saudi", "gulf", "mena", "global"}
OBJECTIVES = {"awareness", "leads", "sales", "community"}


def _strategy_generator() -> StrategyGenerator:
    user_api_key = decrypt_api_key(
        current_user.openai_api_key,
        current_app.config["SECRET_KEY"],
    )
    api_key = (
        user_api_key
        or (current_app.config.get("OPENAI_API_KEY") or "").strip()
    )
    return StrategyGenerator(
        openai_api_key=api_key,
        openai_base_url=current_app.config.get(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ),
        openai_model=current_app.config.get("OPENAI_MODEL", "gpt-4o"),
    )


def _active_brand() -> Optional[Brand]:
    return (
        Brand.query.filter_by(user_id=current_user.id, status="active")
        .order_by(Brand.updated_at.desc())
        .first()
    )


def _bounded_int(value: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("landing.html", sources=SOURCE_CATALOG[:4])


@main_bp.route("/app")
@login_required
def home():
    brand = _active_brand()
    strategy = brand.strategies[0] if brand and brand.strategies else None
    items = strategy.items[:6] if strategy else []
    strategy_data = (strategy.strategy_data or {}) if strategy else {}
    return render_template(
        "home.html",
        brand=brand,
        strategy=strategy,
        strategy_data=strategy_data,
        items=items,
        sources=SOURCE_CATALOG,
    )


@main_bp.route("/app/brand", methods=["GET", "POST"])
@login_required
def brand_page():
    brand = _active_brand()
    if request.method == "POST":
        platforms = [
            key for key in request.form.getlist("platforms") if key in PLATFORM_KEYS
        ]
        values = {
            "name": (request.form.get("name") or "").strip(),
            "website": (request.form.get("website") or "").strip() or None,
            "description": (request.form.get("description") or "").strip() or None,
            "industry": (request.form.get("industry") or "").strip() or None,
            "business_model": request.form.get("business_model") or "service",
            "offer": (request.form.get("offer") or "").strip() or None,
            "market": request.form.get("market")
            if request.form.get("market") in MARKETS
            else "saudi",
            "language": "ar",
            "dialect": (request.form.get("dialect") or "عربية واضحة").strip(),
            "audience": (request.form.get("audience") or "").strip() or None,
            "problem": (request.form.get("problem") or "").strip() or None,
            "audience_desire": (request.form.get("audience_desire") or "").strip()
            or None,
            "customer_stage": request.form.get("customer_stage") or "problem_aware",
            "competitive_advantage": (
                request.form.get("competitive_advantage") or ""
            ).strip()
            or None,
            "brand_voice": (request.form.get("brand_voice") or "").strip() or None,
            "competitors": (request.form.get("competitors") or "").strip() or None,
            "resources": (request.form.get("resources") or "").strip() or None,
            "marketing_objective": request.form.get("marketing_objective")
            if request.form.get("marketing_objective") in OBJECTIVES
            else "awareness",
            "monthly_goal": (request.form.get("monthly_goal") or "").strip() or None,
            "platforms": platforms or ["tiktok", "instagram"],
            "posts_per_week": _bounded_int(
                request.form.get("posts_per_week"), 5, 2, 7
            ),
        }

        if not brand:
            brand = Brand(user_id=current_user.id, status="active")
        for field, value in values.items():
            setattr(brand, field, value)

        errors = []
        required = {
            "name": "اسم الشركة",
            "description": "وصف النشاط",
            "offer": "العرض أو الخدمة الأساسية",
            "audience": "الجمهور المستهدف",
            "problem": "المشكلة التي تحلها",
            "monthly_goal": "هدف الحملة",
        }
        for field, label in required.items():
            if not getattr(brand, field):
                errors.append(f"حقل «{label}» مطلوب لبناء خطة مخصصة.")

        start = request.form.get("campaign_start_date")
        if start:
            try:
                brand.campaign_start_date = datetime.strptime(start, "%Y-%m-%d").date()
            except ValueError:
                errors.append("تاريخ بداية الحملة غير صحيح.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            if brand.id is None:
                db.session.add(brand)
            brand.status = "active"
            brand.updated_at = datetime.utcnow()
            db.session.commit()
            flash("تم حفظ ملف الشركة. أصبح جاهزًا لبناء مسودة استراتيجية.", "success")
            return redirect(url_for("main.strategy_page"))

    return render_template(
        "brand.html",
        brand=brand,
        onboarding=request.args.get("onboarding") == "1",
    )


@main_bp.route("/app/strategy", methods=["GET", "POST"])
@login_required
def strategy_page():
    brand = _active_brand()
    if not brand:
        flash("ابدأ بملف الشركة أولًا.", "error")
        return redirect(url_for("main.brand_page", onboarding="1"))

    if request.method == "POST":
        if brand.profile_completeness < 55:
            flash("أكمل البيانات الأساسية قبل إنشاء الاستراتيجية.", "error")
            return redirect(url_for("main.brand_page"))
        try:
            generator = _strategy_generator()
            strategy = generator.generate(brand)
            if generator.generation_source == "openai":
                source = f"GPT ({current_app.config.get('OPENAI_MODEL', 'gpt-4o')})"
                flash(
                    f"تم إنشاء الإصدار {strategy.version}: {len(strategy.items)} فكرة عبر {source}.",
                    "success",
                )
            elif generator.generation_source == "local_fallback":
                flash(
                    f"تعذر إكمال GPT، فتم إنشاء خطة محلية بديلة ({len(strategy.items)} فكرة). "
                    "تحقق من المفتاح/الرصيد ثم أعد التوليد.",
                    "error",
                )
            else:
                flash(
                    f"تم إنشاء خطة محلية ({len(strategy.items)} فكرة). "
                    "أضف مفتاح OpenAI من الإعدادات لتفعيل GPT.",
                    "success",
                )
        except Exception:
            db.session.rollback()
            current_app.logger.exception("strategy_generation_failed")
            flash(
                "حدث خطأ أثناء التوليد. حدّث الصفحة وأعد المحاولة بعد قليل.",
                "error",
            )
        return redirect(url_for("main.strategy_page"))

    strategy = brand.strategies[0] if brand.strategies else None
    return render_template(
        "strategy.html",
        brand=brand,
        strategy=strategy,
        data=(strategy.strategy_data or {}) if strategy else {},
        sources=(strategy.source_snapshot or SOURCE_CATALOG) if strategy else SOURCE_CATALOG,
    )


@main_bp.route("/app/strategy/export.csv")
@login_required
def export_strategy_csv():
    brand = _active_brand()
    strategy = brand.strategies[0] if brand and brand.strategies else None
    if not strategy:
        flash("أنشئ خطة أولًا ثم صدّرها.", "error")
        return redirect(url_for("main.strategy_page"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "التاريخ",
            "اليوم",
            "المنصة",
            "الهدف",
            "المحور",
            "العنوان",
            "الخطاف الأساسي",
            "الخطافات البديلة",
            "الدعوة للإجراء",
            "مؤشر النجاح",
            "جاهزية الاختبار",
            "حالة الدليل",
        ]
    )
    for item in strategy.items:
        meta = item.virality_breakdown or {}
        writer.writerow(
            [
                item.scheduled_date.isoformat() if item.scheduled_date else "",
                item.day_number or "",
                item.platform,
                item.post_goal,
                item.pillar_name,
                item.title,
                (item.hooks or [""])[0],
                " | ".join((item.hooks or [])[1:]),
                item.cta or "",
                meta.get("success_metric", ""),
                item.virality_score,
                meta.get("evidence_label", "فرضية تحتاج اختبارًا"),
            ]
        )

    body = "\ufeff" + output.getvalue()
    return Response(
        body,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=content-plan.csv"},
    )


@main_bp.route("/app/content")
@login_required
def content_page():
    brand = _active_brand()
    strategy = brand.strategies[0] if brand and brand.strategies else None
    items = strategy.items if strategy else []
    return render_template(
        "content.html",
        brand=brand,
        strategy=strategy,
        items=items,
    )


@main_bp.route("/app/studio", methods=["GET", "POST"])
@login_required
def studio_page():
    brand = _active_brand()
    items = []
    selected = None
    if brand and brand.strategies:
        items = brand.strategies[0].items
        item_id = request.args.get("item") or request.form.get("item_id")
        try:
            parsed_item_id = int(item_id) if item_id else None
        except (TypeError, ValueError):
            parsed_item_id = None
        if parsed_item_id:
            selected = ContentItem.query.filter_by(
                id=parsed_item_id, strategy_id=brand.strategies[0].id
            ).first()
        elif items:
            selected = items[0]

    if request.method == "POST" and selected and brand:
        action = request.form.get("action") or "regenerate"
        generator = _strategy_generator()
        if action == "select_hook":
            hook_index = _bounded_int(request.form.get("hook_index"), 0, 0, 4)
            generator.select_hook(selected, hook_index)
            flash("تم اعتماد الخطاف داخل حزمة التنفيذ.", "success")
        else:
            if not generator.openai_api_key:
                flash("أضف OPENAI_API_KEY لتحديث السيناريو عبر GPT.", "error")
                return redirect(url_for("main.settings_page"))
            prompt = (request.form.get("prompt") or "").strip()
            try:
                generator.regenerate_script(selected, brand, prompt=prompt)
            except GPTGenerationError as exc:
                db.session.rollback()
                flash(f"تعذر تحديث السيناريو عبر GPT: {exc}", "error")
                return redirect(url_for("main.studio_page", item=selected.id))
            flash("تم تحديث حزمة التنفيذ مع الحفاظ على الفكرة.", "success")
        return redirect(url_for("main.studio_page", item=selected.id))

    return render_template(
        "studio.html", brand=brand, items=items, selected=selected
    )


@main_bp.route("/app/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    if request.method == "POST":
        action = request.form.get("action") or "profile"
        if action == "save_openai_key":
            api_key = (request.form.get("openai_api_key") or "").strip()
            if len(api_key) < 20:
                flash("مفتاح OpenAI قصير أو غير صالح.", "error")
            else:
                current_user.openai_api_key = encrypt_api_key(
                    api_key,
                    current_app.config["SECRET_KEY"],
                )
                db.session.commit()
                flash("تم حفظ مفتاح OpenAI مشفرًا لحسابك.", "success")
            return redirect(url_for("main.settings_page"))

        if action == "clear_openai_key":
            current_user.openai_api_key = None
            db.session.commit()
            flash("تم حذف مفتاح OpenAI الخاص بحسابك.", "success")
            return redirect(url_for("main.settings_page"))

        name = (request.form.get("name") or "").strip()
        if len(name) >= 2:
            current_user.name = name
            db.session.commit()
            flash("تم تحديث بيانات الحساب.", "success")
        else:
            flash("اكتب اسمًا واضحًا.", "error")
        return redirect(url_for("main.settings_page"))

    brand = _active_brand()
    user_openai_key = decrypt_api_key(
        current_user.openai_api_key,
        current_app.config["SECRET_KEY"],
    )
    server_openai_key = (current_app.config.get("OPENAI_API_KEY") or "").strip()
    integration_state = {
        "openai": bool(user_openai_key or server_openai_key),
        "openai_user_key": bool(user_openai_key),
        "openai_source": (
            "الحساب" if user_openai_key else "الخادم" if server_openai_key else None
        ),
        "openai_model": current_app.config.get("OPENAI_MODEL", "gpt-4o"),
        "youtube": bool(current_app.config.get("YOUTUBE_API_KEY")),
    }
    return render_template(
        "settings.html",
        brand=brand,
        integration_state=integration_state,
        sources=SOURCE_CATALOG,
    )
