from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    openai_api_key = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    brands = db.relationship(
        "Brand",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    industry = db.Column(db.String(120))
    business_model = db.Column(db.String(60))
    offer = db.Column(db.Text)
    market = db.Column(db.String(80), default="saudi")
    language = db.Column(db.String(20), default="ar")
    dialect = db.Column(db.String(40), default="saudi")
    audience = db.Column(db.Text)
    problem = db.Column(db.Text)
    audience_desire = db.Column(db.Text)
    customer_stage = db.Column(db.String(60))
    competitive_advantage = db.Column(db.Text)
    brand_voice = db.Column(db.String(180))
    competitors = db.Column(db.Text)
    resources = db.Column(db.Text)
    marketing_objective = db.Column(db.String(60), default="awareness")
    monthly_goal = db.Column(db.Text)
    platforms = db.Column(db.JSON, default=list)
    posts_per_week = db.Column(db.Integer, default=5)
    campaign_start_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(30), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="brands")
    strategies = db.relationship(
        "Strategy",
        back_populates="brand",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(Strategy.id)",
    )

    @property
    def profile_completeness(self) -> int:
        """A transparent completion indicator, not a quality or accuracy score."""
        weighted_fields = (
            (self.name, 12),
            (self.description, 12),
            (self.industry, 7),
            (self.offer, 10),
            (self.audience, 12),
            (self.problem, 10),
            (self.audience_desire, 7),
            (self.competitive_advantage, 8),
            (self.brand_voice, 5),
            (self.marketing_objective, 7),
            (self.monthly_goal, 5),
            (self.platforms, 5),
        )
        return min(100, sum(weight for value, weight in weighted_fields if value))


class Strategy(db.Model):
    __tablename__ = "strategies"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    month_start = db.Column(db.Date)
    month_end = db.Column(db.Date)
    primary_goal = db.Column(db.Text)
    executive_summary = db.Column(db.Text)
    market_summary = db.Column(db.Text)
    positioning = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    strategy_data = db.Column(db.JSON, default=dict)
    source_snapshot = db.Column(db.JSON, default=list)
    status = db.Column(db.String(40), default="ready")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    brand = db.relationship("Brand", back_populates="strategies")
    pillars = db.relationship(
        "ContentPillar",
        back_populates="strategy",
        cascade="all, delete-orphan",
        order_by="ContentPillar.sort_order",
    )
    items = db.relationship(
        "ContentItem",
        back_populates="strategy",
        cascade="all, delete-orphan",
        order_by="ContentItem.day_number",
    )


class ContentPillar(db.Model):
    __tablename__ = "content_pillars"

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    function = db.Column(db.String(80))
    distribution_percent = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=1)

    strategy = db.relationship("Strategy", back_populates="pillars")


class ContentItem(db.Model):
    __tablename__ = "content_items"

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id"), nullable=False)
    day_number = db.Column(db.Integer)
    scheduled_date = db.Column(db.Date)
    platform = db.Column(db.String(40), default="tiktok")
    pillar_name = db.Column(db.String(120))
    title = db.Column(db.String(255), nullable=False)
    problem_desire = db.Column(db.Text)
    post_goal = db.Column(db.String(40), default="discovery")
    rationale = db.Column(db.Text)
    content_type = db.Column(db.String(40), default="short_video")
    creative_concept = db.Column(db.Text)
    hooks = db.Column(db.JSON, default=list)
    script_body = db.Column(db.Text)
    scenes = db.Column(db.Text)
    on_screen_text = db.Column(db.Text)
    editing_notes = db.Column(db.Text)
    cta = db.Column(db.String(255))
    keywords = db.Column(db.JSON, default=list)
    hashtags = db.Column(db.JSON, default=list)
    priority = db.Column(db.String(20), default="medium")
    virality_score = db.Column(db.Integer, default=0)
    virality_breakdown = db.Column(db.JSON, default=dict)
    status = db.Column(db.String(40), default="scripted")

    strategy = db.relationship("Strategy", back_populates="items")
    script = db.relationship(
        "ContentScript",
        back_populates="content_item",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ContentScript(db.Model):
    __tablename__ = "content_scripts"

    id = db.Column(db.Integer, primary_key=True)
    content_item_id = db.Column(
        db.Integer, db.ForeignKey("content_items.id"), nullable=False, unique=True
    )
    hook = db.Column(db.Text)
    promise = db.Column(db.Text)
    problem = db.Column(db.Text)
    body = db.Column(db.Text)
    peak_moment = db.Column(db.Text)
    closing = db.Column(db.Text)
    cta = db.Column(db.Text)
    alt_hooks = db.Column(db.JSON, default=list)
    alt_narratives = db.Column(db.JSON, default=list)
    hypothesis = db.Column(db.Text)
    fallback_version = db.Column(db.Text)

    content_item = db.relationship("ContentItem", back_populates="script")
