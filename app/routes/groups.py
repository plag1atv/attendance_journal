from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Group
from app.utils import role_required


groups = Blueprint("groups", __name__, url_prefix="/groups")


@groups.route("/")
@login_required
def list_groups():
    if current_user.role == "student" and current_user.group_id:
        all_groups = Group.query.filter_by(id=current_user.group_id).all()
    elif current_user.role == "teacher" and current_user.group_id:
        all_groups = Group.query.filter_by(id=current_user.group_id).all()
    else:
        all_groups = Group.query.order_by(Group.name.asc()).all()

    return render_template("groups/list.html", groups=all_groups)


@groups.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_group():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        description = request.form.get("description", "").strip()

        if not name or not course:
            flash("Заполните обязательные поля.", "error")
            return render_template("groups/create.html")

        existing_group = Group.query.filter_by(name=name).first()
        if existing_group:
            flash("Группа с таким названием уже существует.", "error")
            return render_template("groups/create.html")

        try:
            course = int(course)
        except ValueError:
            flash("Курс должен быть числом.", "error")
            return render_template("groups/create.html")

        group = Group(
            name=name,
            course=course,
            description=description if description else None,
        )

        db.session.add(group)
        db.session.commit()

        flash("Группа успешно создана.", "success")
        return redirect(url_for("groups.list_groups"))

    return render_template("groups/create.html")


@groups.route("/edit/<int:group_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        description = request.form.get("description", "").strip()

        if not name or not course:
            flash("Заполните обязательные поля.", "error")
            return render_template("groups/edit.html", group=group)

        existing_group = Group.query.filter(
            Group.name == name,
            Group.id != group.id,
        ).first()
        if existing_group:
            flash("Группа с таким названием уже существует.", "error")
            return render_template("groups/edit.html", group=group)

        try:
            course = int(course)
        except ValueError:
            flash("Курс должен быть числом.", "error")
            return render_template("groups/edit.html", group=group)

        group.name = name
        group.course = course
        group.description = description if description else None

        db.session.commit()

        flash("Группа успешно обновлена.", "success")
        return redirect(url_for("groups.list_groups"))

    return render_template("groups/edit.html", group=group)


@groups.route("/delete/<int:group_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    db.session.delete(group)
    db.session.commit()

    flash("Группа удалена.", "success")
    return redirect(url_for("groups.list_groups"))