from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from app.extensions import db, login_manager



def create_default_admin():
    from app.models import User

    admin = User.query.filter_by(email="admin@attendance.local").first()
    if admin is None:
        admin = User(
            full_name="Системный администратор",
            username="admin",
            email="admin@attendance.local",
            password=generate_password_hash("admin12345"),
            role="admin",
            group_id=None,
        )
        db.session.add(admin)
        db.session.commit()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app import models
    from app.routes.api import api
    from app.routes.attendance import attendance
    from app.routes.auth import auth
    from app.routes.groups import groups
    from app.routes.lessons import lessons
    from app.routes.main import main
    from app.routes.reports import reports
    from app.routes.students import students
    from app.routes.summary import summary
    from app.routes.users import users

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(groups)
    app.register_blueprint(students)
    app.register_blueprint(lessons)
    app.register_blueprint(attendance)
    app.register_blueprint(reports)
    app.register_blueprint(summary)
    app.register_blueprint(users)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        create_default_admin()

    return app