from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import AttendanceRecord, Lesson, Student


attendance = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance.route("/lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def lesson_attendance(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if current_user.role == "student":
        if current_user.group_id != lesson.group_id:
            flash("У вас нет доступа к этому журналу.", "error")
            return redirect(url_for("main.dashboard"))

    if current_user.role == "teacher":
        if lesson.teacher_id != current_user.id:
            flash("У вас нет доступа к этому журналу.", "error")
            return redirect(url_for("main.dashboard"))

    students = Student.query.filter_by(group_id=lesson.group_id).order_by(
        Student.full_name.asc()
    ).all()

    can_edit = current_user.role in ("admin", "teacher")

    if request.method == "POST":
        if not can_edit:
            flash("У вас нет прав для редактирования посещаемости.", "error")
            return redirect(url_for("attendance.lesson_attendance", lesson_id=lesson.id))

        AttendanceRecord.query.filter_by(lesson_id=lesson.id).delete()

        for student in students:
            status = request.form.get(f"status_{student.id}", "present").strip()
            comment = request.form.get(f"comment_{student.id}", "").strip()

            record = AttendanceRecord(
                status=status,
                comment=comment if comment else None,
                student_id=student.id,
                lesson_id=lesson.id,
            )
            db.session.add(record)

        db.session.commit()

        flash("Посещаемость успешно сохранена.", "success")
        return redirect(url_for("attendance.lesson_attendance", lesson_id=lesson.id))

    existing_records = AttendanceRecord.query.filter_by(lesson_id=lesson.id).all()
    records_map = {record.student_id: record for record in existing_records}

    return render_template(
        "attendance/lesson.html",
        lesson=lesson,
        students=students,
        records_map=records_map,
        can_edit=can_edit,
    )