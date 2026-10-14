from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.home"))
        flash("بيانات الدخول غير صحيحة.", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        errors = []
        if len(name) < 2:
            errors.append("اكتب اسمًا واضحًا.")
        if "@" not in email or len(email) > 190:
            errors.append("اكتب بريدًا إلكترونيًا صحيحًا.")
        if len(password) < 8:
            errors.append("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
        if User.query.filter_by(email=email).first():
            errors.append("هذا البريد مسجّل بالفعل. جرّب تسجيل الدخول.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("أهلًا بك. لنبدأ ببناء ملف شركتك.", "success")
            return redirect(url_for("main.brand_page", onboarding="1"))

    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
