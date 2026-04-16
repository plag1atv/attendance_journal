from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.models import AttendanceRecord, Group, Lesson, Student


api = Blueprint("api", __name__, url_prefix="/api")


def forbidden_response():
    return jsonify({"error": "forbidden"}), 403


@api.route("/groups", methods=["GET"])
@login_required
def api_groups():
    if current_user.role in ("student", "teacher") and current_user.group_id:
        groups = Group.query.filter_by(id=current_user.group_id).all()
    else:
        groups = Group.query.order_by(Group.name.asc()).all()

    data = [
        {
            "id": group.id,
            "name": group.name,
            "course": group.course,
            "description": group.description,
        }
        for group in groups
    ]
    return jsonify(data)


@api.route("/students", methods=["GET"])
@login_required
def api_students():
    query = Student.query

    group_id = request.args.get("group_id", "").strip()
    search = request.args.get("search", "").strip().lower()

    if current_user.role in ("student", "teacher") and current_user.group_id:
        query = query.filter_by(group_id=current_user.group_id)
    elif group_id:
        try:
            query = query.filter_by(group_id=int(group_id))
        except ValueError:
            return jsonify({"error": "invalid group_id"}), 400

    students = query.order_by(Student.full_name.asc()).all()

    if search:
        students = [
            student for student in students
            if search in student.full_name.lower()
            or (student.email and search in student.email.lower())
        ]

    data = [
        {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "group": {
                "id": student.group.id,
                "name": student.group.name,
            },
        }
        for student in students
    ]
    return jsonify(data)


@api.route("/lessons", methods=["GET"])
@login_required
def api_lessons():
    query = Lesson.query

    group_id = request.args.get("group_id", "").strip()
    subject = request.args.get("subject", "").strip().lower()
    lesson_date = request.args.get("lesson_date", "").strip()
    teacher_id = request.args.get("teacher_id", "").strip()

    if current_user.role == "teacher":
        query = query.filter_by(teacher_id=current_user.id)
    elif current_user.role == "student" and current_user.group_id:
        query = query.filter_by(group_id=current_user.group_id)
    else:
        if group_id:
            try:
                query = query.filter_by(group_id=int(group_id))
            except ValueError:
                return jsonify({"error": "invalid group_id"}), 400

        if teacher_id:
            try:
                query = query.filter_by(teacher_id=int(teacher_id))
            except ValueError:
                return jsonify({"error": "invalid teacher_id"}), 400

    lessons = query.order_by(Lesson.lesson_date.desc(), Lesson.id.desc()).all()

    if subject:
        lessons = [
            lesson for lesson in lessons
            if subject in lesson.subject.lower()
        ]

    if lesson_date:
        lessons = [
            lesson for lesson in lessons
            if lesson.lesson_date == lesson_date
        ]

    data = [
        {
            "id": lesson.id,
            "lesson_date": lesson.lesson_date,
            "subject": lesson.subject,
            "lesson_number": lesson.lesson_number,
            "topic": lesson.topic,
            "group": {
                "id": lesson.group.id,
                "name": lesson.group.name,
            },
            "teacher": {
                "id": lesson.teacher.id,
                "full_name": lesson.teacher.full_name,
                "email": lesson.teacher.email,
            },
        }
        for lesson in lessons
    ]
    return jsonify(data)


@api.route("/attendance/lesson/<int:lesson_id>", methods=["GET"])
@login_required
def api_attendance_by_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if current_user.role == "student" and current_user.group_id != lesson.group_id:
        return forbidden_response()

    if current_user.role == "teacher" and lesson.teacher_id != current_user.id:
        return forbidden_response()

    records = AttendanceRecord.query.filter_by(lesson_id=lesson.id).all()

    data = {
        "lesson": {
            "id": lesson.id,
            "lesson_date": lesson.lesson_date,
            "subject": lesson.subject,
            "lesson_number": lesson.lesson_number,
            "topic": lesson.topic,
            "group": lesson.group.name,
            "teacher": lesson.teacher.full_name,
        },
        "records": [
            {
                "student_id": record.student.id,
                "student_name": record.student.full_name,
                "status": record.status,
                "comment": record.comment,
            }
            for record in records
        ],
    }
    return jsonify(data)