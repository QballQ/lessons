"""Read and write auditing for the safeguarding module.

Every list, view, download and export is logged, not only writes. The log never
stores narrative text; `detail` holds ids, counts, filters and field names.
"""
from __future__ import annotations

from .models import AccessLog


def client_ip(request) -> str | None:
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_access(request, action: str, *, incident=None, student_id=None, employee=None, detail=None) -> AccessLog:
    user = getattr(request, "user", None) if request is not None else None
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    return AccessLog.objects.create(
        user=user,
        username=getattr(user, "get_username", lambda: "")() if user else "",
        employee_id=getattr(employee, "pk", None),
        action=action,
        incident=incident,
        incident_reference=getattr(incident, "reference", "") or "",
        student_id=student_id if student_id is not None else getattr(incident, "student_id", None),
        detail=detail or {},
        ip=client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:255] if request is not None else ""),
    )
