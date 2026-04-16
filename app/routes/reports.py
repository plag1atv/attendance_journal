import csv
import io

from flask import Blueprint, Response, render_template, request
from flask_login import current_user, login_required

from app.models import AttendanceRecord, Group, Student


reports = Blueprint("reports", __name__, url_prefix="/reports")


@reports.route("/statistics")
@login_required
def statistics():
    selected_group_id = request.args.get("group_id", "").strip()

    if current_user.role in ("student", "teacher") and current_user.group_id:
        all_groups = Group.query.filter_by(id=current_user.group_id).all()
        selected_group = Group.query.get(current_user.group_id)
    else:
        all_groups = Group.query.order_by(Group.name.asc()).all()
        selected_group = None

    statistics_data = []

    if current_user.role in ("student", "teacher") and current_user.group_id:
        selected_group_id = current_user.group_id
    elif selected_group_id:
        try:
            selected_group_id = int(selected_group_id)
            selected_group = Group.query.get(selected_group_id)
        except ValueError:
            selected_group = None

    if selected_group:
        students = Student.query.filter_by(
            group_id=selected_group.id
        ).order_by(Student.full_name.asc()).all()

        for student in students:
            records = AttendanceRecord.query.filter_by(student_id=student.id).all()

            total = len(records)
            present = sum(1 for record in records if record.status == "present")
            absent = sum(1 for record in records if record.status == "absent")
            late = sum(1 for record in records if record.status == "late")
            excused = sum(1 for record in records if record.status == "excused")

            attendance_percent = 0
            if total > 0:
                attendance_percent = round((present / total) * 100, 1)

            statistics_data.append(
                {
                    "student": student,
                    "total": total,
                    "present": present,
                    "absent": absent,
                    "late": late,
                    "excused": excused,
                    "attendance_percent": attendance_percent,
                }
            )

    return render_template(
        "reports/statistics.html",
        groups=all_groups,
        selected_group=selected_group,
        statistics_data=statistics_data,
    )


@reports.route("/statistics/export")
@login_required
def export_statistics_csv():
    selected_group_id = request.args.get("group_id", "").strip()
    selected_group = None

    if current_user.role in ("student", "teacher") and current_user.group_id:
        selected_group = Group.query.get(current_user.group_id)
    elif selected_group_id:
        try:
            selected_group = Group.query.get(int(selected_group_id))
        except ValueError:
            selected_group = None

    if selected_group is None:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Ошибка"])
        writer.writerow(["Группа не выбрана"])
        return Response(
            output.getvalue().encode("utf-8-sig"),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=statistics.csv"},
        )

    students = Student.query.filter_by(
        group_id=selected_group.id
    ).order_by(Student.full_name.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "Студент",
        "Всего занятий",
        "Присутствовал",
        "Отсутствовал",
        "Опоздал",
        "Уважительная причина",
        "Процент посещаемости",
    ])

    for student in students:
        records = AttendanceRecord.query.filter_by(student_id=student.id).all()

        total = len(records)
        present = sum(1 for record in records if record.status == "present")
        absent = sum(1 for record in records if record.status == "absent")
        late = sum(1 for record in records if record.status == "late")
        excused = sum(1 for record in records if record.status == "excused")

        attendance_percent = 0
        if total > 0:
            attendance_percent = round((present / total) * 100, 1)

        writer.writerow([
            student.full_name,
            total,
            present,
            absent,
            late,
            excused,
            f"{attendance_percent}%",
        ])

    filename = f"statistics_group_{selected_group.id}.csv"
    return Response(
        output.getvalue().encode("utf-8-sig"),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )