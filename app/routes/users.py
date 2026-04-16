from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Group, Student, User
from app.utils import role_required


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/")
@login_required
@role_required("admin")
def list_users():
    all_users = User.query.order_by(User.role.asc(), User.email.asc()).all()
    return render_template("users/list.html", users=all_users)


@users.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_user():
    groups = Group.query.order_by(Group.name.asc()).all()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()
        group_id = request.form.get("group_id", "").strip()

        if not full_name or not email or not password or not role:
            flash("Заполните обязательные поля.", "error")
            return render_template("users/create.html", groups=groups)

        if role not in ("teacher", "student"):
            flash("Можно создавать только преподавателя или студента.", "error")
            return render_template("users/create.html", groups=groups)

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash("Пользователь с такой почтой уже существует.", "error")
            return render_template("users/create.html", groups=groups)

        selected_group = None
        if group_id:
            try:
                group_id = int(group_id)
                selected_group = Group.query.get(group_id)
            except ValueError:
                selected_group = None

        if role == "student" and selected_group is None:
            flash("Для студента нужно выбрать группу.", "error")
            return render_template("users/create.html", groups=groups)

        user = User(
            full_name=full_name,
            username=email,
            email=email,
            password=generate_password_hash(password),
            role=role,
            group_id=selected_group.id if selected_group else None,
        )

        db.session.add(user)
        db.session.commit()

        if role == "student":
            student = Student(
                full_name=full_name,
                email=email,
                phone=None,
                group_id=selected_group.id,
            )
            db.session.add(student)
            db.session.commit()

        flash("Пользователь успешно создан.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/create.html", groups=groups)


@users.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Администратора удалять нельзя.", "error")
        return redirect(url_for("users.list_users"))

    if user.role == "student":
        student = Student.query.filter_by(email=user.email).first()
        if student:
            db.session.delete(student)

    db.session.delete(user)
    db.session.commit()

    flash("Пользователь удален.", "success")
    return redirect(url_for("users.list_users"))