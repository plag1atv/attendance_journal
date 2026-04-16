from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            if current_user.role not in allowed_roles:
                abort(403)

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


def can_manage_groups():
    return current_user.is_authenticated and current_user.role == "admin"


def can_manage_students():
    return current_user.is_authenticated and current_user.role == "admin"


def can_manage_lessons():
    return current_user.is_authenticated and current_user.role == "admin"


def can_edit_attendance():
    return current_user.is_authenticated and current_user.role in ("admin", "teacher")