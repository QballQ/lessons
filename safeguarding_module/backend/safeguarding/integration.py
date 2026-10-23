"""Every SIMS-specific lookup lives in this one file.

The safeguarding app never reaches into other apps directly from views or
serializers; it calls these adapters. When a SIMS model or field name differs
from the guesses below, fix it HERE and nowhere else.

What the frontend bundle told us about SIMS (October 2026):
  * users.Student: student_id (学号), first_name_en, last_name_en, first_name_zh,
    last_name_zh, gender, class (FK), enrollment_status (active/suspended/...),
    graduating_year, photo, guardian, guardian_phone
  * users.Employee: employee_no, name, position_type (Teacher/Admin/Medical/Logistics),
    user (OneToOne to auth user), status
  * academic.Class: name, grade (FK), room, homeroom_teacher
  * academic.Room: name
  * courses.Subject, courses.Course (subject FK), courses.Schedule: term, day_of_week,
    period, room, week_type, class FK, course FK, teacher FK, duration_minutes
Field names marked TODO are guesses to confirm against the models.
"""
from __future__ import annotations

import datetime as dt
from typing import Iterable

from django.apps import apps
from django.conf import settings
from django.db.models import Q

STUDENT_MODEL = getattr(settings, "SG_STUDENT_MODEL", "users.Student")
EMPLOYEE_MODEL = getattr(settings, "SG_EMPLOYEE_MODEL", "users.Employee")
SCHEDULE_MODEL = getattr(settings, "SG_SCHEDULE_MODEL", "courses.Schedule")

# Grade names (as stored on academic.Grade.name) that belong to the Lower School.
# Everything else is treated as Upper School. Boarding is chosen on the form.
LOWER_SCHOOL_GRADES = set(getattr(settings, "SG_LOWER_SCHOOL_GRADES", []))

# TODO confirm: attribute path from a Student to its regular class and from a
# Schedule to its class. The names below are the most likely guesses.
STUDENT_CLASS_ATTR = getattr(settings, "SG_STUDENT_CLASS_ATTR", "class_obj")
SCHEDULE_CLASS_FIELD = getattr(settings, "SG_SCHEDULE_CLASS_FIELD", "class_obj")
SCHEDULE_LAYER_CLASS_FIELD = getattr(settings, "SG_SCHEDULE_LAYER_CLASS_FIELD", "layer_class")
STUDENT_LAYER_CLASSES_ATTR = getattr(settings, "SG_STUDENT_LAYER_CLASSES_ATTR", "layer_classes")


def student_model():
    return apps.get_model(STUDENT_MODEL)


def employee_model():
    return apps.get_model(EMPLOYEE_MODEL)


def _get(obj, *path, default=None):
    """Safe attribute chain: _get(student, 'class_obj', 'grade', 'name')."""
    cur = obj
    for p in path:
        if cur is None:
            return default
        cur = getattr(cur, p, None)
    return default if cur is None else cur


# ---------------------------------------------------------------- employees

def employee_for_user(user):
    """The Employee record behind a logged-in user, or None for non-staff accounts."""
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    emp = getattr(user, "employee", None)  # TODO confirm related_name on Employee.user
    if emp is not None:
        return emp
    Employee = employee_model()
    try:
        return Employee.objects.filter(user=user).first()
    except Exception:  # field name differs; fix STUDENT/EMPLOYEE adapters above
        return None


def employee_is_active(employee) -> bool:
    status = _get(employee, "status", default=None)
    if status is None:
        return bool(_get(employee, "is_active", default=True))
    return str(status).lower() in {"active", "在职", "1", "true"}


def employee_summary(employee) -> dict | None:
    if employee is None:
        return None
    return {
        "id": employee.pk,
        "employee_no": _get(employee, "employee_no", default=""),
        "name": _get(employee, "name", default=str(employee)),
        "position_type": _get(employee, "position_type", default=""),
    }


# ----------------------------------------------------------------- students

def student_name_en(student) -> str:
    first = _get(student, "first_name_en", default="") or ""
    last = _get(student, "last_name_en", default="") or ""
    return (f"{first} {last}").strip() or _get(student, "name_en", default="") or ""


def student_name_zh(student) -> str:
    first = _get(student, "first_name_zh", default="") or ""
    last = _get(student, "last_name_zh", default="") or ""
    return (f"{last}{first}").strip() or _get(student, "name_cn", default="") or ""


def student_class(student):
    return _get(student, STUDENT_CLASS_ATTR)


def student_class_name(student) -> str:
    return str(_get(student_class(student), "name", default="") or "")


def student_grade(student):
    return _get(student_class(student), "grade")


def student_grade_name(student) -> str:
    return str(_get(student_grade(student), "name", default="") or "")


def student_house_id(student):
    return _get(student, "house_id") or _get(student, "house", "pk")


def student_class_ids(student) -> list[int]:
    ids = []
    cls = student_class(student)
    if cls is not None:
        ids.append(cls.pk)
    layer = _get(student, STUDENT_LAYER_CLASSES_ATTR)
    if layer is not None and hasattr(layer, "all"):
        ids.extend(c.pk for c in layer.all())
    return ids


def student_section(student) -> str:
    """LOWER or UPPER from the grade name; the form can override."""
    grade = student_grade_name(student)
    if grade and grade in LOWER_SCHOOL_GRADES:
        return "LOWER"
    return "UPPER"


def student_summary(student) -> dict | None:
    if student is None:
        return None
    return {
        "id": student.pk,
        "student_id": _get(student, "student_id", default=""),
        "name_en": student_name_en(student),
        "name_zh": student_name_zh(student),
        "class_name": student_class_name(student),
        "grade_name": student_grade_name(student),
        "gender": _get(student, "gender", default=""),
        "enrollment_status": _get(student, "enrollment_status", default=""),
    }


def student_search_q(term: str) -> Q:
    """Q object for the typeahead. Any active staff member may look a student up;
    the result carries names and class only, never safeguarding data."""
    term = term.strip()
    return (
        Q(student_id__icontains=term)
        | Q(first_name_en__icontains=term)
        | Q(last_name_en__icontains=term)
        | Q(first_name_zh__icontains=term)
        | Q(last_name_zh__icontains=term)
    )


def active_students_qs():
    Student = student_model()
    qs = Student.objects.all()
    try:
        return qs.filter(enrollment_status="active")  # TODO confirm status value
    except Exception:
        return qs


# ---------------------------------------------------------------- timetable

def week_type_for(date: dt.date) -> str:
    """'odd' or 'even' ISO week; SIMS schedules use week_type all/odd/even."""
    return "odd" if date.isocalendar()[1] % 2 else "even"


def lessons_at(student, when: dt.datetime, period_number: int | None) -> list[dict]:
    """Lessons on the student's timetable at that day and period.

    Returns a list because streamed (layer) classes can overlap with the
    regular class entry. The form shows them for confirmation and stores the
    chosen schedule id on the incident.
    """
    if period_number is None:
        return []
    try:
        Schedule = apps.get_model(SCHEDULE_MODEL)
    except LookupError:
        return []
    class_ids = student_class_ids(student)
    if not class_ids:
        return []
    q = Q(**{f"{SCHEDULE_CLASS_FIELD}_id__in": class_ids})
    try:
        Schedule._meta.get_field(SCHEDULE_LAYER_CLASS_FIELD)
        q |= Q(**{f"{SCHEDULE_LAYER_CLASS_FIELD}_id__in": class_ids})
    except Exception:
        pass
    qs = Schedule.objects.filter(q, day_of_week=when.isoweekday(), period=period_number)
    wk = week_type_for(when.date())
    try:
        qs = qs.filter(Q(week_type="all") | Q(week_type=wk) | Q(week_type="") | Q(week_type__isnull=True))
    except Exception:
        pass
    out = []
    for s in qs.select_related():
        subject = _get(s, "course", "subject") or _get(s, "subject")
        out.append(
            {
                "schedule_id": s.pk,
                "subject_id": _get(subject, "pk"),
                "subject_name": str(subject) if subject is not None else "",
                "course_name": str(_get(s, "course", "name", default="") or ""),
                "teacher": employee_summary(_get(s, "teacher")),
                "room_id": _get(s, "room", "pk"),
                "room_name": str(_get(s, "room", "name", default="") or _get(s, "room", default="") or ""),
                "period": _get(s, "period"),
                "day_of_week": _get(s, "day_of_week"),
            }
        )
    return out


def employees_in_ids(ids: Iterable[int]):
    Employee = employee_model()
    return Employee.objects.filter(pk__in=list(ids))
