"""Minimal object builders for the tests.

These create SIMS students and employees through the adapter model labels. The
field names in STUDENT_DEFAULTS / EMPLOYEE_DEFAULTS must match the real SIMS
models; adjust them once and every test follows.
"""
from django.contrib.auth import get_user_model

from safeguarding import integration
from safeguarding.models import Category, Role, RoleAssignment, Section

STUDENT_DEFAULTS = {"first_name_en": "Test", "last_name_en": "Student", "first_name_zh": "测", "last_name_zh": "试",
                    "gender": "M", "enrollment_status": "active"}
EMPLOYEE_DEFAULTS = {"name": "Staff Member", "position_type": "Teacher", "status": "active"}

_n = {"i": 0}


def _next():
    _n["i"] += 1
    return _n["i"]


def make_user(username=None):
    User = get_user_model()
    username = username or f"user{_next()}"
    return User.objects.create_user(username=username, password="x")


def make_employee(name=None, **extra):
    Employee = integration.employee_model()
    user = make_user()
    data = dict(EMPLOYEE_DEFAULTS)
    data.update(extra)
    data["name"] = name or f"Employee {user.username}"
    data.setdefault("employee_no", f"E{_next():04d}")
    return Employee.objects.create(user=user, **data)


def make_student(class_obj=None, **extra):
    Student = integration.student_model()
    data = dict(STUDENT_DEFAULTS)
    data.update(extra)
    data.setdefault("student_id", f"S{_next():05d}")
    if class_obj is not None:
        data[integration.STUDENT_CLASS_ATTR] = class_obj
    return Student.objects.create(**data)


def give_role(employee, role, section=Section.WHOLE, **scope):
    return RoleAssignment.objects.create(employee=employee, role=role, section=section, **scope)


def category(code="welfare", ring="PASTORAL", **extra):
    obj, _ = Category.objects.get_or_create(code=code, defaults={"name_en": code, "name_zh": code, "ring": ring, **extra})
    return obj
