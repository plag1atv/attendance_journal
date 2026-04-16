from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Group, Lesson, User
from app.utils import role_required


lessons = Blueprint("lessons", __name__, url_prefix="/lessons")


@lessons.route("/")
@login_required
def list_lessons():
    selected_group_id = request.args.get("group_id", "").strip()
    subject = request.args.get("subject", "").strip().lower()
    lesson_date = request.args.get("lesson_date", "").strip()
    teacher_id = request.args.get("teacher_id", "").strip()

    teachers = User.query.filter_by(role="teacher").order_by(User.full_name.asc()).all()

    if current_user.role == "teacher":
        available_groups = Group.query.order_by(Group.name.asc()).all()
        lessons_query = Lesson.query.filter_by(teacher_id=current_user.id)
        teacher_id = str(current_user.id)
    elif current_user.role == "student" and current_user.group_id:
        available_groups = Group.query.filter_by(id=current_user.group_id).all()
        lessons_query = Lesson.query.filter_by(group_id=current_user.group_id)
        selected_group_id = str(current_user.group_id)
    else:
        available_groups = Group.query.order_by(Group.name.asc()).all()
        lessons_query = Lesson.query

        if selected_group_id:
            try:
                lessons_query = lessons_query.filter_by(group_id=int(selected_group_id))
            except ValueError:
                selected_group_id = ""

        if teacher_id:
            try:
                lessons_query = lessons_query.filter_by(teacher_id=int(teacher_id))
            except ValueError:
                teacher_id = ""

    all_lessons = lessons_query.order_by(
        Lesson.lesson_date.desc(),
        Lesson.subject.asc(),
    ).all()

    if subject:
        all_lessons = [
            lesson for lesson in all_lessons
            if subject in lesson.subject.lower()
        ]

    if lesson_date:
        all_lessons = [
            lesson for lesson in all_lessons
            if lesson.lesson_date == lesson_date
        ]

    return render_template(
        "lessons/list.html",
        lessons=all_lessons,
        groups=available_groups,
        teachers=teachers,
        selected_group_id=str(selected_group_id) if selected_group_id else "",
        selected_teacher_id=str(teacher_id) if teacher_id else "",
        subject=subject,
        lesson_date=lesson_date,
    )


@lessons.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_lesson():
    all_groups = Group.query.order_by(Group.name.asc()).all()
    teachers = User.query.filter_by(role="teacher").order_by(User.full_name.asc()).all()

    if not all_groups:
        flash("Сначала создайте хотя бы одну группу.", "error")
        return redirect(url_for("groups.create_group"))

    if not teachers:
        flash("Сначала создайте хотя бы одного преподавателя.", "error")
        return redirect(url_for("users.create_user"))

    if request.method == "POST":
        lesson_date = request.form.get("lesson_date", "").strip()
        subject = request.form.get("subject", "").strip()
        lesson_number = request.form.get("lesson_number", "").strip()
        topic = request.form.get("topic", "").strip()
        group_id = request.form.get("group_id", "").strip()
        teacher_id = request.form.get("teacher_id", "").strip()

        if (
            not lesson_date
            or not subject
            or not lesson_number
            or not group_id
            or not teacher_id
        ):
            flash("Заполните обязательные поля.", "error")
            return render_template(
                "lessons/create.html",
                groups=all_groups,
                teachers=teachers,
            )

        try:
            group_id = int(group_id)
            teacher_id = int(teacher_id)
        except ValueError:
            flash("Некорректные данные группы или преподавателя.", "error")
            return render_template(
                "lessons/create.html",
                groups=all_groups,
                teachers=teachers,
            )

        group = Group.query.get(group_id)
        teacher = User.query.filter_by(id=teacher_id, role="teacher").first()

        if group is None:
            flash("Выбранная группа не существует.", "error")
            return render_template(
                "lessons/create.html",
                groups=all_groups,
                teachers=teachers,
            )

        if teacher is None:
            flash("Выбранный преподаватель не существует.", "error")
            return render_template(
                "lessons/create.html",
                groups=all_groups,
                teachers=teachers,
            )

        lesson = Lesson(
            lesson_date=lesson_date,
            subject=subject,
            lesson_number=lesson_number,
            topic=topic if topic else None,
            group_id=group_id,
            teacher_id=teacher_id,
        )

        db.session.add(lesson)
        db.session.commit()

        flash("Занятие успешно создано.", "success")
        return redirect(url_for("lessons.list_lessons"))

    return render_template("lessons/create.html", groups=all_groups, teachers=teachers)


@lessons.route("/edit/<int:lesson_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    all_groups = Group.query.order_by(Group.name.asc()).all()
    teachers = User.query.filter_by(role="teacher").order_by(User.full_name.asc()).all()

    if request.method == "POST":
        lesson_date = request.form.get("lesson_date", "").strip()
        subject = request.form.get("subject", "").strip()
        lesson_number = request.form.get("lesson_number", "").strip()
        topic = request.form.get("topic", "").strip()
        group_id = request.form.get("group_id", "").strip()
        teacher_id = request.form.get("teacher_id", "").strip()

        if (
            not lesson_date
            or not subject
            or not lesson_number
            or not group_id
            or not teacher_id
        ):
            flash("Заполните обязательные поля.", "error")
            return render_template(
                "lessons/edit.html",
                lesson=lesson,
                groups=all_groups,
                teachers=teachers,
            )

        try:
            group_id = int(group_id)
            teacher_id = int(teacher_id)
        except ValueError:
            flash("Некорректные данные группы или преподавателя.", "error")
            return render_template(
                "lessons/edit.html",
                lesson=lesson,
                groups=all_groups,
                teachers=teachers,
            )

        group = Group.query.get(group_id)
        teacher = User.query.filter_by(id=teacher_id, role="teacher").first()

        if group is None:
            flash("Выбранная группа не существует.", "error")
            return render_template(
                "lessons/edit.html",
                lesson=lesson,
                groups=all_groups,
                teachers=teachers,
            )

        if teacher is None:
            flash("Выбранный преподаватель не существует.", "error")
            return render_template(
                "lessons/edit.html",
                lesson=lesson,
                groups=all_groups,
                teachers=teachers,
            )

        lesson.lesson_date = lesson_date
        lesson.subject = subject
        lesson.lesson_number = lesson_number
        lesson.topic = topic if topic else None
        lesson.group_id = group_id
        lesson.teacher_id = teacher_id

        db.session.commit()

        flash("Занятие успешно обновлено.", "success")
        return redirect(url_for("lessons.list_lessons"))

    return render_template(
        "lessons/edit.html",
        lesson=lesson,
        groups=all_groups,
        teachers=teachers,
    )


@lessons.route("/delete/<int:lesson_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    db.session.delete(lesson)
    db.session.commit()

    flash("Занятие удалено.", "success")
    return redirect(url_for("lessons.list_lessons"))