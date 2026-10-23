"""Ring-fence logic. Every read of safeguarding data goes through visible_incidents().

Access model (most to least):
  DSL       sees everything, including DSL-only records; manages roles and config.
  DEPUTY    sees TEAM and PASTORAL rings for the sections they cover.
  PASTORAL  sees PASTORAL-ring records for the classes / grades / houses in scope.
  GRANTED   per-incident access through an alert, an assignment or an access grant.
  REPORTER  the staff member who logged it sees their own submission only
            (toggle SG_REPORTER_SEES_OWN, default True).
  NONE      everyone else, including SIMS super admins.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from . import integration
from .models import (
    Action,
    Alert,
    AlertGroup,
    Incident,
    Ring,
    Role,
    RoleAssignment,
    Section,
    TimeBand,
    widest_ring,
)

LEVEL_NONE = "NONE"
LEVEL_REPORTER = "REPORTER"
LEVEL_PASTORAL = "PASTORAL"
LEVEL_GRANTED = "GRANTED"
LEVEL_TEAM = "TEAM"
LEVEL_DSL = "DSL"


def reporter_sees_own() -> bool:
    return bool(getattr(settings, "SG_REPORTER_SEES_OWN", True))


@dataclass
class SGContext:
    user: object
    employee: object = None
    roles: set = field(default_factory=set)
    deputy_sections: set = field(default_factory=set)
    pastoral_sections: set = field(default_factory=set)
    pastoral_class_ids: set = field(default_factory=set)
    pastoral_grade_ids: set = field(default_factory=set)
    pastoral_house_ids: set = field(default_factory=set)

    @property
    def is_staff(self) -> bool:
        return self.employee is not None and integration.employee_is_active(self.employee)

    @property
    def is_dsl(self) -> bool:
        return Role.DSL in self.roles

    @property
    def is_team(self) -> bool:
        return self.is_dsl or Role.DEPUTY in self.roles

    @property
    def is_pastoral(self) -> bool:
        return Role.PASTORAL in self.roles

    @property
    def has_any_role(self) -> bool:
        return bool(self.roles)

    def deputy_covers(self, section: str) -> bool:
        return self.is_dsl or Section.WHOLE in self.deputy_sections or section in self.deputy_sections

    def pastoral_covers(self, incident: Incident) -> bool:
        if incident.class_id_at_time in self.pastoral_class_ids:
            return True
        if incident.grade_id_at_time in self.pastoral_grade_ids:
            return True
        if incident.house_id_at_time in self.pastoral_house_ids:
            return True
        return incident.section in self.pastoral_sections

    def as_dict(self) -> dict:
        return {
            "employee": integration.employee_summary(self.employee),
            "roles": sorted(self.roles),
            "is_dsl": self.is_dsl,
            "is_team": self.is_team,
            "is_pastoral": self.is_pastoral,
            "deputy_sections": sorted(self.deputy_sections),
            "pastoral_scope": {
                "sections": sorted(self.pastoral_sections),
                "class_ids": sorted(self.pastoral_class_ids),
                "grade_ids": sorted(self.pastoral_grade_ids),
                "house_ids": sorted(self.pastoral_house_ids),
            },
        }


def get_context(user) -> SGContext:
    ctx = SGContext(user=user)
    ctx.employee = integration.employee_for_user(user)
    if ctx.employee is None:
        return ctx
    today = timezone.localdate()
    for a in RoleAssignment.objects.filter(employee=ctx.employee, is_active=True):
        if not a.is_current(today):
            continue
        ctx.roles.add(a.role)
        if a.role == Role.DEPUTY:
            ctx.deputy_sections.add(a.section)
        elif a.role == Role.PASTORAL:
            ids = set(a.class_ids or []) | set(a.grade_ids or []) | set(a.house_ids or [])
            ctx.pastoral_class_ids.update(a.class_ids or [])
            ctx.pastoral_grade_ids.update(a.grade_ids or [])
            ctx.pastoral_house_ids.update(a.house_ids or [])
            if not ids and a.section != Section.WHOLE:
                ctx.pastoral_sections.add(a.section)
    return ctx


def context_for_request(request) -> SGContext:
    ctx = getattr(request, "_sg_ctx", None)
    if ctx is None:
        ctx = get_context(getattr(request, "user", None))
        request._sg_ctx = ctx
    return ctx


# ----------------------------------------------------------------- queries

def _explicit_access_q(employee, now) -> Q:
    q = Q(assigned_to=employee)
    q |= Q(alerts__employee=employee, alerts__grants_access=True)
    q |= Q(access_grants__employee=employee, access_grants__revoked_at__isnull=True) & (
        Q(access_grants__expires_at__isnull=True) | Q(access_grants__expires_at__gt=now)
    )
    return q


def visible_incidents(user, ctx: SGContext | None = None):
    """The one queryset every view must start from."""
    ctx = ctx or get_context(user)
    qs = Incident.objects.live()
    if not ctx.is_staff:
        return qs.none()
    if ctx.is_dsl:
        return qs
    emp = ctx.employee
    now = timezone.now()
    q = _explicit_access_q(emp, now)
    if reporter_sees_own():
        q |= Q(reporter=emp)
    if Role.DEPUTY in ctx.roles:
        team_q = Q(ring__in=[Ring.PASTORAL, Ring.TEAM])
        if Section.WHOLE not in ctx.deputy_sections:
            team_q &= Q(section__in=list(ctx.deputy_sections))
        q |= team_q
    if Role.PASTORAL in ctx.roles:
        scope = Q(pk__in=[])
        if ctx.pastoral_class_ids:
            scope |= Q(class_id_at_time__in=list(ctx.pastoral_class_ids))
        if ctx.pastoral_grade_ids:
            scope |= Q(grade_id_at_time__in=list(ctx.pastoral_grade_ids))
        if ctx.pastoral_house_ids:
            scope |= Q(house_id_at_time__in=list(ctx.pastoral_house_ids))
        if ctx.pastoral_sections:
            scope |= Q(section__in=list(ctx.pastoral_sections))
        q |= Q(ring=Ring.PASTORAL) & scope
    return qs.filter(q).distinct()


def has_explicit_access(employee, incident: Incident) -> bool:
    now = timezone.now()
    if incident.assigned_to_id == employee.pk:
        return True
    if incident.alerts.filter(employee=employee, grants_access=True).exists():
        return True
    return incident.access_grants.filter(
        Q(employee=employee, revoked_at__isnull=True) & (Q(expires_at__isnull=True) | Q(expires_at__gt=now))
    ).exists()


def access_level(ctx: SGContext, incident: Incident) -> str:
    """How much of one incident this person may see and do."""
    if not ctx.is_staff or incident.is_deleted:
        return LEVEL_NONE
    if ctx.is_dsl:
        return LEVEL_DSL
    emp = ctx.employee
    if Role.DEPUTY in ctx.roles and incident.ring != Ring.DSL and ctx.deputy_covers(incident.section):
        return LEVEL_TEAM
    if has_explicit_access(emp, incident):
        return LEVEL_GRANTED
    if Role.PASTORAL in ctx.roles and incident.ring == Ring.PASTORAL and ctx.pastoral_covers(incident):
        return LEVEL_PASTORAL
    if reporter_sees_own() and incident.reporter_id == emp.pk:
        return LEVEL_REPORTER
    return LEVEL_NONE


def permissions_for(level: str, ctx: SGContext) -> dict:
    return {
        "level": level,
        "can_view": level != LEVEL_NONE,
        "can_edit": level in {LEVEL_DSL, LEVEL_TEAM},
        "can_change_status": level in {LEVEL_DSL, LEVEL_TEAM},
        "can_change_ring": level == LEVEL_DSL,
        "can_lower_ring": level == LEVEL_DSL,
        "can_alert": level in {LEVEL_DSL, LEVEL_TEAM, LEVEL_GRANTED},
        "can_grant": level in {LEVEL_DSL, LEVEL_TEAM},
        "can_add_action": level != LEVEL_NONE,
        "can_add_dsl_note": level == LEVEL_DSL,
        "can_upload": level != LEVEL_NONE,
        "can_edit_body_map": level in {LEVEL_DSL, LEVEL_TEAM, LEVEL_GRANTED, LEVEL_REPORTER},
        "can_export": level == LEVEL_DSL,
        "can_soft_delete": level == LEVEL_DSL,
        "sees_chronology": level != LEVEL_REPORTER,
        "sees_dsl_notes": level == LEVEL_DSL,
    }


def visible_actions(incident: Incident, level: str, user):
    qs = incident.actions.all()
    if level == LEVEL_DSL:
        return qs
    if level == LEVEL_REPORTER:
        return qs.filter(author=user)
    return qs.exclude(ring=Ring.DSL)


# ----------------------------------------------------------------- writes

def ring_for_categories(categories) -> str:
    return widest_ring([c.ring for c in categories])


def snapshot_student(incident: Incident, student) -> None:
    cls = integration.student_class(student)
    incident.class_id_at_time = getattr(cls, "pk", None)
    incident.class_name_at_time = integration.student_class_name(student)[:60]
    grade = integration.student_grade(student)
    incident.grade_id_at_time = getattr(grade, "pk", None)
    incident.house_id_at_time = integration.student_house_id(student)
    if not incident.section or incident.section == Section.WHOLE:
        incident.section = integration.student_section(student)


def record_action(incident: Incident, kind: str, user, employee=None, *, body: str = "", ring: str = Ring.TEAM, meta=None) -> Action:
    action = Action.objects.create(
        incident=incident, kind=kind, body=body or "", ring=ring, meta=meta or {},
        author=user if getattr(user, "is_authenticated", False) else None, author_employee=employee,
    )
    Incident.objects.filter(pk=incident.pk).update(last_action_at=action.created_at)
    incident.last_action_at = action.created_at
    return action


def _notify_hook():
    path = getattr(settings, "SG_NOTIFY_HOOK", None)
    if not path:
        return None
    mod, _, name = path.rpartition(".")
    return getattr(import_module(mod), name)


def notify(kind: str, *, employees, incident=None, message: str = "", detail=None) -> None:
    """Optional outbound notification (email, WeCom, SMS). Default: in-app alerts only.

    settings.SG_NOTIFY_HOOK = "myapp.notify.safeguarding"  with signature
        def safeguarding(kind, employees, incident, message, detail): ...
    Never put narrative text in the message; the alert is a pointer, not the record.
    """
    hook = _notify_hook()
    if hook is None:
        return
    try:
        hook(kind=kind, employees=list(employees), incident=incident, message=message, detail=detail or {})
    except Exception:  # a failed email must never block logging a concern
        import logging

        logging.getLogger(__name__).exception("safeguarding notify hook failed")


def send_alerts(incident: Incident, *, employees=(), group_ids=(), user, employee=None, message: str = "", grants_access: bool = True) -> list:
    targets = {e.pk: e for e in employees}
    group_codes = []
    for g in AlertGroup.objects.filter(pk__in=list(group_ids), is_active=True).prefetch_related("members"):
        group_codes.append(g.code)
        for m in g.members.all():
            targets[m.pk] = m
    created = []
    for emp in targets.values():
        alert, was_created = Alert.objects.get_or_create(
            incident=incident, employee=emp,
            defaults={"alerted_by": user if getattr(user, "is_authenticated", False) else None,
                      "message": message[:255], "grants_access": grants_access},
        )
        if was_created:
            created.append(alert)
    if created:
        record_action(incident, Action.Kind.ALERT, user, employee,
                      meta={"employee_ids": [a.employee_id for a in created], "groups": group_codes, "grants_access": grants_access})
        notify("alert", employees=[a.employee for a in created], incident=incident, message=message)
    return created


def current_dsl_employees():
    today = timezone.localdate()
    out = []
    for a in RoleAssignment.objects.filter(role=Role.DSL, is_active=True).select_related("employee"):
        if a.is_current(today):
            out.append(a.employee)
    return out


def notify_dsls(event: str, detail: dict) -> None:
    notify(event, employees=current_dsl_employees(), detail=detail)


def lesson_context(student, when, period_number=None) -> dict:
    band = TimeBand.for_moment(when)
    if period_number is None and band is not None:
        period_number = band.period_number
    return {
        "student": integration.student_summary(student),
        "section": integration.student_section(student),
        "class_ids": integration.student_class_ids(student),
        "time_band": {"id": band.pk, "code": band.code, "label_en": band.label_en, "label_zh": band.label_zh,
                      "period_number": band.period_number} if band else None,
        "period_number": period_number,
        "lessons": integration.lessons_at(student, when, period_number),
    }
