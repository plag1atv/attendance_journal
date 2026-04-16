from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models import Group, Student


students = Blueprint("students", __name__, url_prefix="/students")


@students.route("/")
@login_required
def list_students():
    selected_group_id = request.args.get("group_id", "").strip()

    if current_user.role in ("student", "teacher") and current_user.group_id:
        available_groups = Group.query.filter_by(id=current_user.group_id).all()
        students_query = Student.query.filter_by(group_id=current_user.group_id)
        selected_group_id = str(current_user.group_id)
    else:
        available_groups = Group.query.order_by(Group.name.asc()).all()
        students_query = Student.query

        if selected_group_id:
            try:
                selected_group_id = int(selected_group_id)
                students_query = students_query.filter_by(group_id=selected_group_id)
            except ValueError:
                selected_group_id = ""

    all_students = students_query.order_by(Student.full_name.asc()).all()

    return render_template(
        "students/list.html",
        students=all_students,
        groups=available_groups,
        selected_group_id=str(selected_group_id) if selected_group_id else "",
    )