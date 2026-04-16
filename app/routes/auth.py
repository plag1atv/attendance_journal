from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from app.models import User


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Заполните все поля.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password, password):
            flash("Неверная почта или пароль.", "error")
            return render_template("auth/login.html")

        login_user(user)
        flash("Вы успешно вошли в систему.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("main.index"))