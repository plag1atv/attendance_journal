from flask_login import UserMixin

from app.extensions import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="student")
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=True)

    group = db.relationship("Group", backref="users", foreign_keys=[group_id])


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    students = db.relationship(
        "Student",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan",
    )

    lessons = db.relationship(
        "Lesson",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("group.id"),
        nullable=False,
    )

    attendance_records = db.relationship(
        "AttendanceRecord",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_date = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    lesson_number = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(255), nullable=True)

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("group.id"),
        nullable=False,
    )
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )

    teacher = db.relationship("User", backref="lessons", foreign_keys=[teacher_id])

    attendance_records = db.relationship(
        "AttendanceRecord",
        backref="lesson",
        lazy=True,
        cascade="all, delete-orphan",
    )


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default="present")
    comment = db.Column(db.String(255), nullable=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False,
    )
    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lesson.id"),
        nullable=False,
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))