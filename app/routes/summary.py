from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models import AttendanceRecord, Group, Lesson, Student


summary = Blueprint("summary", __name__, url_prefix="/attendance")


@summary.route("/summary")
@login_required
def attendance_summary():
    selected_group_id = request.args.get("group_id", "").strip()

    if current_user.role in ("student", "teacher") and current_user.group_id:
        all_groups = Group.query.filter_by(id=current_user.group_id).all()
        selected_group = Group.query.get(current_user.group_id)
    else:
        all_groups = Group.query.order_by(Group.name.asc()).all()
        selected_group = None

    lessons = []
    students = []
    attendance_map = {}

    if current_user.role in ("student", "teacher") and current_user.group_id:
        selected_group_id = current_user.group_id
    elif selected_group_id:
        try:
            selected_group_id = int(selected_group_id)
            selected_group = Group.query.get(selected_group_id)
        except ValueError:
            selected_group = None

    if selected_group:
        lessons = Lesson.query.filter_by(group_id=selected_group.id).order_by(
            Lesson.lesson_date.asc(),
            Lesson.id.asc(),
        ).all()

        students = Student.query.filter_by(group_id=selected_group.id).order_by(
            Student.full_name.asc()
        ).all()

        records = AttendanceRecord.query.join(Lesson).filter(
            Lesson.group_id == selected_group.id
        ).all()

        for record in records:
            attendance_map[(record.student_id, record.lesson_id)] = record.status

    return render_template(
        "attendance/summary.html",
        groups=all_groups,
        selected_group=selected_group,
        lessons=lessons,
        students=students,
        attendance_map=attendance_map,
    )