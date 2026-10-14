from datetime import date
from hmac import compare_digest
from pathlib import Path
from secrets import token_urlsafe

from dotenv import load_dotenv
from flask import Flask, abort, request, session
from sqlalchemy import inspect, text

from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class: type = Config) -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.before_request
    def protect_forms():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        expected = session.get("_csrf_token")
        supplied = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        if not expected or not supplied or not compare_digest(expected, supplied):
            abort(400, description="انتهت صلاحية النموذج. حدّث الصفحة وحاول مرة أخرى.")
        return None

    @app.context_processor
    def inject_globals():
        from flask_login import current_user

        def csrf_token() -> str:
            token = session.get("_csrf_token")
            if not token:
                token = token_urlsafe(32)
                session["_csrf_token"] = token
            return token

        if not getattr(current_user, "is_authenticated", False):
            return {"brand": None, "csrf_token": csrf_token, "current_year": date.today().year}
        from app.models import Brand

        brand = (
            Brand.query.filter_by(user_id=current_user.id, status="active")
            .order_by(Brand.updated_at.desc())
            .first()
        )
        return {
            "brand": brand,
            "csrf_token": csrf_token,
            "current_year": date.today().year,
        }

    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()
        _ensure_schema_compatibility()
        _seed_demo_user()

    return app


def _seed_demo_user() -> None:
    from app.models import Brand, User

    user = User.query.filter_by(email="ahmed@contentforge.ai").first()
    if not user:
        user = User(name="Ahmed Al-Rashid", email="ahmed@contentforge.ai")
        user.set_password("password")
        db.session.add(user)
        db.session.flush()

    brand = Brand.query.filter_by(user_id=user.id, status="active").first()
    if not brand:
        brand = Brand(
            user_id=user.id,
            name="SMAGUIDE",
            website="https://smaguide.ai/",
            description=(
                "SMAGUIDE (سماجايد) منصة SaaS سحابية من الرياض تجمع إدارة المحتوى "
                "والمحادثات والإعلانات ووكلاء الذكاء الاصطناعي."
            ),
            industry="تقنية التسويق والبرمجيات",
            business_model="b2b_saas",
            offer="منصة موحدة لإدارة المحتوى والمحادثات والحملات ووكلاء الذكاء الاصطناعي",
            market="saudi",
            language="ar",
            dialect="saudi",
            audience="أصحاب المتاجر والشركات الصغيرة ووكالات التسويق في السعودية",
            problem="تشتت العمل بين أدوات المحتوى والـ CRM والإعلانات والرد الآلي",
            audience_desire="إدارة التسويق والمبيعات من مكان واحد مع وقت أقل ووضوح أكبر",
            customer_stage="problem_aware",
            competitive_advantage="تجميع المحتوى + واتساب + حملات + وكلاء AI بواجهة عربية",
            brand_voice="خبير، عملي، واضح، سعودي دون مبالغة",
            competitors="Hootsuite، Sprout Social، أدوات إدارة المحادثات المنفصلة",
            resources="فريق صغير، تصوير بالجوال، تسجيل شاشة المنتج",
            marketing_objective="leads",
            monthly_goal="زيادة الوعي المؤهل واجتذاب تجريب الباقة المجانية",
            platforms=["tiktok", "instagram", "youtube", "x", "facebook"],
            posts_per_week=5,
            campaign_start_date=date.today().replace(day=1),
            status="active",
        )
        db.session.add(brand)
    else:
        demo_defaults = {
            "industry": "تقنية التسويق والبرمجيات",
            "business_model": "b2b_saas",
            "offer": "منصة موحدة لإدارة المحتوى والمحادثات والحملات ووكلاء الذكاء الاصطناعي",
            "audience_desire": "إدارة التسويق والمبيعات من مكان واحد مع وقت أقل ووضوح أكبر",
            "customer_stage": "problem_aware",
            "brand_voice": "خبير، عملي، واضح، سعودي دون مبالغة",
            "competitors": "Hootsuite، Sprout Social، أدوات إدارة المحادثات المنفصلة",
            "resources": "فريق صغير، تصوير بالجوال، تسجيل شاشة المنتج",
            "marketing_objective": "leads",
        }
        for field, value in demo_defaults.items():
            if not getattr(brand, field, None):
                setattr(brand, field, value)

    db.session.commit()


def _ensure_schema_compatibility() -> None:
    """Add the small set of columns introduced before migrations are adopted.

    Existing local SQLite databases are kept intact. New databases already contain
    these fields through ``db.create_all`` and therefore skip every ALTER statement.
    """

    additions = {
        "brands": {
            "industry": "VARCHAR(120)",
            "business_model": "VARCHAR(60)",
            "offer": "TEXT",
            "audience_desire": "TEXT",
            "customer_stage": "VARCHAR(60)",
            "brand_voice": "VARCHAR(180)",
            "competitors": "TEXT",
            "resources": "TEXT",
            "marketing_objective": "VARCHAR(60) DEFAULT 'awareness'",
        },
        "strategies": {
            "version": "INTEGER DEFAULT 1",
            "strategy_data": "JSON",
            "source_snapshot": "JSON",
        },
    }

    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    for table_name, columns in additions.items():
        if table_name not in tables:
            continue
        existing = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name, ddl in columns.items():
            if column_name in existing:
                continue
            db.session.execute(
                text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {ddl}')
            )
    db.session.commit()
