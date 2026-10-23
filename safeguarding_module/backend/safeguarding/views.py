from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.core.exceptions import FieldError
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import integration, services
from .audit import log_access
from .export import incident_html
from .models import (
    AccessGrant,
    Action,
    Alert,
    AlertGroup,
    Attachment,
    BodyMapMark,
    Category,
    Incident,
    Location,
    Ring,
    RoleAssignment,
    Status,
    TimeBand,
    widest_ring,
)
from .permissions import IsActiveStaff, IsDSL, IsDSLOrReadOnly, IsSafeguardingTeam
from .serializers import (
    AccessGrantSerializer,
    ActionCreateSerializer,
    ActionSerializer,
    AlertCreateSerializer,
    AlertGroupSerializer,
    AlertSerializer,
    AttachmentSerializer,
    BodyMapMarkSerializer,
    CategorySerializer,
    IncidentCreateSerializer,
    IncidentDetailSerializer,
    IncidentListSerializer,
    IncidentReporterSerializer,
    IncidentUpdateSerializer,
    LocationSerializer,
    MyAlertSerializer,
    RingChangeSerializer,
    RoleAssignmentSerializer,
    SoftDeleteSerializer,
    StatusChangeSerializer,
    TimeBandSerializer,
)

MAX_UPLOAD = getattr(settings, "SG_MAX_UPLOAD_BYTES", 20 * 1024 * 1024)
ALLOWED_TYPES = set(getattr(settings, "SG_ALLOWED_UPLOAD_TYPES", [
    "image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf", "audio/mpeg", "audio/mp4", "audio/x-m4a",
    "video/mp4", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
]))


class ConfigViewSetMixin:
    permission_classes = [IsDSLOrReadOnly]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # no DELETE: deactivate instead

    def perform_create(self, serializer):
        obj = serializer.save()
        log_access(self.request, "CONFIG", employee=services.context_for_request(self.request).employee,
                   detail={"model": obj.__class__.__name__, "id": obj.pk, "op": "create"})

    def perform_update(self, serializer):
        obj = serializer.save()
        log_access(self.request, "CONFIG", employee=services.context_for_request(self.request).employee,
                   detail={"model": obj.__class__.__name__, "id": obj.pk, "op": "update"})


class CategoryViewSet(ConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LocationViewSet(ConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = Location.objects.select_related("room")
    serializer_class = LocationSerializer


class TimeBandViewSet(ConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = TimeBand.objects.all()
    serializer_class = TimeBandSerializer


class AlertGroupViewSet(ConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = AlertGroup.objects.prefetch_related("members")
    serializer_class = AlertGroupSerializer


class RoleAssignmentViewSet(viewsets.ModelViewSet):
    """Who holds safeguarding access. DSL only. Every change is logged and all DSLs are told."""

    permission_classes = [IsDSL]
    queryset = RoleAssignment.objects.select_related("employee")
    serializer_class = RoleAssignmentSerializer

    def _log(self, obj, op):
        ctx = services.context_for_request(self.request)
        detail = {"assignment_id": obj.pk, "employee_id": obj.employee_id, "role": obj.role, "section": obj.section, "op": op}
        log_access(self.request, "ROLE_CHANGE", employee=ctx.employee, detail=detail)
        services.notify_dsls("role_change", detail)

    def perform_create(self, serializer):
        obj = serializer.save(granted_by=self.request.user)
        self._log(obj, "create")

    def perform_update(self, serializer):
        obj = serializer.save()
        self._log(obj, "update")
        self._ensure_a_dsl_remains()

    def perform_destroy(self, instance):
        self._log(instance, "delete")
        instance.delete()
        self._ensure_a_dsl_remains()

    def _ensure_a_dsl_remains(self):
        if not services.current_dsl_employees():
            raise ValidationError("At least one active DSL must remain.")


class IncidentViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsActiveStaff]
    http_method_names = ["get", "post", "patch", "head", "options"]

    # ---------------------------------------------------------------- plumbing
    @property
    def ctx(self):
        return services.context_for_request(self.request)

    def get_queryset(self):
        return (services.visible_incidents(self.request.user, self.ctx)
                .select_related("student", "reporter", "assigned_to", "location", "time_band", "subject")
                .prefetch_related("categories"))

    def get_serializer_context(self):
        c = super().get_serializer_context()
        c["sg"] = self.ctx
        return c

    def get_serializer_class(self):
        if self.action == "create":
            return IncidentCreateSerializer
        if self.action in {"partial_update", "update"}:
            return IncidentUpdateSerializer
        if self.action in {"list", "by_student", "mine"}:
            return IncidentListSerializer
        return IncidentDetailSerializer

    def _level(self, incident) -> str:
        level = services.access_level(self.ctx, incident)
        if level == services.LEVEL_NONE:
            log_access(self.request, "DENIED", incident=incident, employee=self.ctx.employee)
            raise PermissionDenied("You do not have access to this record.")
        return level

    def _require(self, incident, perm: str) -> str:
        level = self._level(incident)
        if not services.permissions_for(level, self.ctx)[perm]:
            log_access(self.request, "DENIED", incident=incident, employee=self.ctx.employee, detail={"perm": perm})
            raise PermissionDenied("Your safeguarding role does not allow this.")
        return level

    # ------------------------------------------------------------------ CRUD
    def filter_queryset(self, queryset):
        p = self.request.query_params
        if p.get("student"):
            queryset = queryset.filter(student_id=p["student"])
        if p.get("status"):
            queryset = queryset.filter(status__in=p["status"].split(","))
        if p.get("open") in {"1", "true"}:
            queryset = queryset.filter(status__in=[Status.ACTIVE, Status.MONITORING, Status.REFERRED])
        if p.get("category"):
            queryset = queryset.filter(categories__code__in=p["category"].split(","))
        if p.get("ring"):
            queryset = queryset.filter(ring=p["ring"])
        if p.get("section"):
            queryset = queryset.filter(section=p["section"])
        if p.get("severity"):
            queryset = queryset.filter(severity__in=p["severity"].split(","))
        if p.get("assigned_to"):
            queryset = queryset.filter(assigned_to_id=p["assigned_to"])
        if p.get("location"):
            queryset = queryset.filter(location_id=p["location"])
        if p.get("time_band"):
            queryset = queryset.filter(time_band_id=p["time_band"])
        if p.get("date_from"):
            queryset = queryset.filter(occurred_at__date__gte=p["date_from"])
        if p.get("date_to"):
            queryset = queryset.filter(occurred_at__date__lte=p["date_to"])
        if p.get("q"):
            term = p["q"].strip()
            q = Q(reference__icontains=term) | Q(class_name_at_time__icontains=term)
            try:
                ids = list(integration.active_students_qs().filter(integration.student_search_q(term)).values_list("pk", flat=True)[:200])
                q |= Q(student_id__in=ids)
            except FieldError:
                pass
            queryset = queryset.filter(q)
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        log_access(request, "LIST", employee=self.ctx.employee, detail={"filters": dict(request.query_params.items())})
        return response

    def retrieve(self, request, *args, **kwargs):
        incident = self.get_object()
        level = self._level(incident)
        log_access(request, "VIEW", incident=incident, employee=self.ctx.employee, detail={"level": level})
        if level == services.LEVEL_REPORTER:
            ser = IncidentReporterSerializer(incident, context=self.get_serializer_context())
        else:
            ctx = self.get_serializer_context()
            ctx["level"] = level
            ser = IncidentDetailSerializer(incident, context=ctx)
        return Response(ser.data)

    def create(self, request, *args, **kwargs):
        ser = IncidentCreateSerializer(data=request.data, context=self.get_serializer_context())
        ser.is_valid(raise_exception=True)
        incident = ser.save()
        level = services.access_level(self.ctx, incident)
        ctx = self.get_serializer_context()
        ctx["level"] = level
        out = IncidentReporterSerializer if level == services.LEVEL_REPORTER else IncidentDetailSerializer
        return Response(out(incident, context=ctx).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        incident = self.get_object()
        self._require(incident, "can_edit")
        ser = IncidentUpdateSerializer(incident, data=request.data, partial=True, context=self.get_serializer_context())
        ser.is_valid(raise_exception=True)
        ser.save()
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # --------------------------------------------------------------- listings
    @action(detail=False, methods=["get"])
    def mine(self, request):
        """Concerns I logged (reporter view)."""
        qs = Incident.objects.live().filter(reporter=self.ctx.employee).select_related("student").prefetch_related("categories")
        page = self.paginate_queryset(qs)
        ser = IncidentListSerializer(page if page is not None else qs, many=True, context=self.get_serializer_context())
        log_access(request, "LIST", employee=self.ctx.employee, detail={"scope": "mine"})
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=False, methods=["get"], url_path="by-student")
    def by_student(self, request):
        """The safeguarding tab on the student profile: only what this viewer may see."""
        sid = request.query_params.get("student")
        if not sid:
            raise ValidationError({"student": "required"})
        qs = self.get_queryset()
        primary = qs.filter(student_id=sid)
        linked = qs.filter(linked_students__id=sid).exclude(student_id=sid)
        log_access(request, "STUDENT_TAB", student_id=int(sid), employee=self.ctx.employee,
                   detail={"primary": primary.count(), "linked": linked.count()})
        c = self.get_serializer_context()
        return Response({
            "student": integration.student_summary(integration.student_model().objects.filter(pk=sid).first()),
            "incidents": IncidentListSerializer(primary, many=True, context=c).data,
            "linked": IncidentListSerializer(linked, many=True, context=c).data,
            "can_add": True,
            "has_role": self.ctx.has_any_role,
        })

    # ------------------------------------------------------------- chronology
    @action(detail=True, methods=["get", "post"])
    def actions(self, request, pk=None):
        incident = self.get_object()
        if request.method == "GET":
            level = self._level(incident)
            return Response(ActionSerializer(services.visible_actions(incident, level, request.user), many=True).data)
        level = self._require(incident, "can_add_action")
        ser = ActionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ring = ser.validated_data["ring"]
        if ring == Ring.DSL and level != services.LEVEL_DSL:
            raise PermissionDenied("Only a DSL can write DSL-only notes.")
        a = services.record_action(incident, ser.validated_data["kind"], request.user, self.ctx.employee,
                                   body=ser.validated_data["body"], ring=ring)
        log_access(request, "ACTION", incident=incident, employee=self.ctx.employee, detail={"kind": a.kind, "ring": ring})
        return Response(ActionSerializer(a).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="status")
    def set_status(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_change_status")
        ser = StatusChangeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new = ser.validated_data["status"]
        old = incident.status
        if new == old:
            return self.retrieve(request, pk=pk)
        with transaction.atomic():
            incident.status = new
            if new in {Status.NFA, Status.CLOSED}:
                incident.closed_at = timezone.now()
                incident.closed_by = request.user
            else:
                incident.closed_at = None
                incident.closed_by = None
            incident.save(update_fields=["status", "closed_at", "closed_by", "updated_at"])
            services.record_action(incident, Action.Kind.STATUS, request.user, self.ctx.employee,
                                   body=ser.validated_data["note"], meta={"from": old, "to": new})
            log_access(request, "UPDATE", incident=incident, employee=self.ctx.employee, detail={"status": [old, new]})
        return self.retrieve(request, pk=pk)

    @action(detail=True, methods=["post"], url_path="ring")
    def set_ring(self, request, pk=None):
        incident = self.get_object()
        level = self._level(incident)
        ser = RingChangeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new = ser.validated_data["ring"]
        old = incident.ring
        raising = widest_ring([old, new]) == new and new != old
        if level == services.LEVEL_DSL or (level == services.LEVEL_TEAM and raising):
            pass
        else:
            raise PermissionDenied("Only a DSL can widen who sees a record.")
        if new != old:
            with transaction.atomic():
                incident.ring = new
                incident.save(update_fields=["ring", "updated_at"])
                services.record_action(incident, Action.Kind.RING, request.user, self.ctx.employee,
                                       body=ser.validated_data["note"], meta={"from": old, "to": new})
                log_access(request, "UPDATE", incident=incident, employee=self.ctx.employee, detail={"ring": [old, new]})
        if services.access_level(self.ctx, incident) == services.LEVEL_NONE:
            # A deputy who marks a record DSL-only can no longer open it: say so instead of a 404.
            return Response({"id": incident.pk, "reference": incident.reference, "ring": incident.ring, "visible_to_you": False})
        return self.retrieve(request, pk=pk)

    # ----------------------------------------------------------- alerts/grants
    @action(detail=True, methods=["post"])
    def alerts(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_alert")
        ser = AlertCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        created = services.send_alerts(incident, employees=integration.employees_in_ids(d["employees"]), group_ids=d["groups"],
                                       user=request.user, employee=self.ctx.employee, message=d["message"],
                                       grants_access=d["grants_access"])
        log_access(request, "ALERT", incident=incident, employee=self.ctx.employee,
                   detail={"employees": [a.employee_id for a in created], "groups": d["groups"]})
        return Response(AlertSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="grants")
    def grant(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_grant")
        ser = AccessGrantSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        g = ser.save(incident=incident, granted_by=request.user)
        services.record_action(incident, Action.Kind.ACCESS, request.user, self.ctx.employee,
                               meta={"employee_id": g.employee_id, "op": "grant", "expires_at": str(g.expires_at or "")})
        log_access(request, "GRANT", incident=incident, employee=self.ctx.employee, detail={"employee_id": g.employee_id})
        services.notify("access_granted", employees=[g.employee], incident=incident, message=g.reason)
        return Response(AccessGrantSerializer(g).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"grants/(?P<grant_id>\d+)/revoke")
    def revoke(self, request, pk=None, grant_id=None):
        incident = self.get_object()
        self._require(incident, "can_grant")
        g = incident.access_grants.filter(pk=grant_id, revoked_at__isnull=True).first()
        if g is None:
            raise ValidationError("No such active grant.")
        g.revoked_at = timezone.now()
        g.revoked_by = request.user
        g.save(update_fields=["revoked_at", "revoked_by"])
        services.record_action(incident, Action.Kind.ACCESS, request.user, self.ctx.employee,
                               meta={"employee_id": g.employee_id, "op": "revoke"})
        log_access(request, "REVOKE", incident=incident, employee=self.ctx.employee, detail={"employee_id": g.employee_id})
        return Response(AccessGrantSerializer(g).data)

    # ---------------------------------------------------------------- body map
    @action(detail=True, methods=["post"], url_path="body-map")
    def add_mark(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_edit_body_map")
        ser = BodyMapMarkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        m = ser.save(incident=incident, created_by=request.user)
        services.record_action(incident, Action.Kind.BODY_MAP, request.user, self.ctx.employee,
                               meta={"op": "add", "mark_id": m.pk, "view": m.view, "region": m.region})
        return Response(BodyMapMarkSerializer(m).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"body-map/(?P<mark_id>\d+)/remove")
    def remove_mark(self, request, pk=None, mark_id=None):
        incident = self.get_object()
        level = self._require(incident, "can_edit_body_map")
        m = incident.body_map_marks.filter(pk=mark_id).first()
        if m is None:
            raise ValidationError("No such mark.")
        if level not in {services.LEVEL_DSL, services.LEVEL_TEAM} and m.created_by_id != request.user.pk:
            raise PermissionDenied("You can only remove marks you added.")
        m.delete()
        services.record_action(incident, Action.Kind.BODY_MAP, request.user, self.ctx.employee,
                               meta={"op": "remove", "mark_id": int(mark_id)})
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------- attachments
    @action(detail=True, methods=["post"], url_path="attachments")
    def upload(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_upload")
        f = request.FILES.get("file")
        if f is None:
            raise ValidationError({"file": "required"})
        if f.size > MAX_UPLOAD:
            raise ValidationError({"file": f"larger than {MAX_UPLOAD} bytes"})
        ctype = (f.content_type or "").split(";")[0].strip()
        if ALLOWED_TYPES and ctype not in ALLOWED_TYPES:
            raise ValidationError({"file": f"type {ctype} not allowed"})
        att = Attachment(incident=incident, original_name=f.name[:255], content_type=ctype, size=f.size,
                         sha256=Attachment.digest(f), uploaded_by=request.user)
        att.file.save(f.name, f, save=True)
        services.record_action(incident, Action.Kind.ATTACHMENT, request.user, self.ctx.employee,
                               meta={"attachment_id": att.pk, "name": att.original_name, "size": att.size})
        log_access(request, "UPLOAD", incident=incident, employee=self.ctx.employee, detail={"attachment_id": att.pk, "size": att.size})
        return Response(AttachmentSerializer(att).data, status=status.HTTP_201_CREATED)

    # -------------------------------------------------------------- DSL tools
    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        incident = self.get_object()
        level = self._require(incident, "can_export")
        who = getattr(self.ctx.employee, "name", None) or request.user.get_username()
        html = incident_html(incident, services.visible_actions(incident, level, request.user), who)
        services.record_action(incident, Action.Kind.EXPORT, request.user, self.ctx.employee, meta={"format": "html"})
        log_access(request, "EXPORT", incident=incident, employee=self.ctx.employee)
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = f'inline; filename="{incident.reference}.html"'
        return resp

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        incident = self.get_object()
        self._require(incident, "can_soft_delete")
        ser = SoftDeleteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        incident.is_deleted = True
        incident.deleted_at = timezone.now()
        incident.deleted_by = request.user
        incident.delete_reason = ser.validated_data["reason"]
        incident.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "delete_reason", "updated_at"])
        log_access(request, "SOFT_DELETE", incident=incident, employee=self.ctx.employee, detail={"reason": incident.delete_reason})
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttachmentDownloadView(APIView):
    """Files are never served from MEDIA_URL. This view checks visibility first."""

    permission_classes = [IsActiveStaff]

    def get(self, request, pk):
        ctx = services.context_for_request(request)
        att = Attachment.objects.select_related("incident").filter(pk=pk).first()
        if att is None or services.access_level(ctx, att.incident) == services.LEVEL_NONE:
            log_access(request, "DENIED", employee=ctx.employee, detail={"attachment_id": pk})
            raise PermissionDenied("You do not have access to this file.")
        if services.access_level(ctx, att.incident) == services.LEVEL_REPORTER and att.uploaded_by_id != request.user.pk:
            raise PermissionDenied("You do not have access to this file.")
        log_access(request, "DOWNLOAD", incident=att.incident, employee=ctx.employee, detail={"attachment_id": att.pk})
        return FileResponse(att.file.open("rb"), as_attachment=True, filename=att.original_name,
                            content_type=att.content_type or "application/octet-stream")


class StudentLookupView(APIView):
    """Typeahead for the form: any active staff member may find any active student."""

    permission_classes = [IsActiveStaff]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response([])
        limit = min(int(request.query_params.get("limit", 15)), 50)
        qs = integration.active_students_qs()
        try:
            qs = qs.filter(integration.student_search_q(q))
        except FieldError:
            qs = qs.filter(pk__in=[int(q)] if q.isdigit() else [])
        results = [integration.student_summary(s) for s in qs[:limit]]
        log_access(request, "LOOKUP", employee=services.context_for_request(request).employee, detail={"q": q[:60], "n": len(results)})
        return Response(results)


class ContextView(APIView):
    """Pre-fill helper: section, time band, period and the timetabled lesson(s) for a student at a moment."""

    permission_classes = [IsActiveStaff]

    def get(self, request):
        sid = request.query_params.get("student")
        at = request.query_params.get("at")
        if not sid or not at:
            raise ValidationError("student and at are required")
        when = parse_datetime(at)
        if when is None:
            raise ValidationError({"at": "ISO 8601 datetime expected"})
        if timezone.is_naive(when):
            when = timezone.make_aware(when)
        student = integration.student_model().objects.filter(pk=sid).first()
        if student is None:
            raise ValidationError({"student": "not found"})
        period = request.query_params.get("period")
        return Response(services.lesson_context(student, when, int(period) if period else None))


class MeView(APIView):
    """What the frontend needs to decide menus, tabs and buttons."""

    permission_classes = [IsActiveStaff]

    def get(self, request):
        ctx = services.context_for_request(request)
        data = ctx.as_dict()
        data["unread_alerts"] = Alert.objects.filter(employee=ctx.employee, read_at__isnull=True, incident__is_deleted=False).count()
        data["settings"] = {
            "reporter_sees_own": services.reporter_sees_own(),
            "idle_timeout_minutes": getattr(settings, "SG_IDLE_TIMEOUT_MINUTES", 10),
            "overdue_days": getattr(settings, "SG_OVERDUE_DAYS", 5),
        }
        return Response(data)


class MyAlertsView(APIView):
    permission_classes = [IsActiveStaff]

    def get(self, request):
        ctx = services.context_for_request(request)
        qs = Alert.objects.filter(employee=ctx.employee, incident__is_deleted=False).select_related("incident", "incident__student")
        if request.query_params.get("unread") in {"1", "true"}:
            qs = qs.filter(read_at__isnull=True)
        return Response(MyAlertSerializer(qs[:100], many=True).data)

    def post(self, request):
        ctx = services.context_for_request(request)
        ids = request.data.get("ids") or []
        n = Alert.objects.filter(employee=ctx.employee, pk__in=ids, read_at__isnull=True).update(read_at=timezone.now())
        return Response({"marked": n})


class DashboardView(APIView):
    permission_classes = [IsSafeguardingTeam]

    def get(self, request):
        ctx = services.context_for_request(request)
        qs = services.visible_incidents(request.user, ctx)
        open_qs = qs.filter(status__in=[Status.ACTIVE, Status.MONITORING, Status.REFERRED])
        overdue_days = getattr(settings, "SG_OVERDUE_DAYS", 5)
        cutoff = timezone.now() - dt.timedelta(days=overdue_days)
        today = timezone.localdate()
        return Response({
            "open": open_qs.count(),
            "by_status": {r["status"]: r["n"] for r in qs.values("status").annotate(n=Count("id"))},
            "by_severity": {r["severity"]: r["n"] for r in open_qs.values("severity").annotate(n=Count("id"))},
            "by_category": [{"code": r["categories__code"], "name_en": r["categories__name_en"], "name_zh": r["categories__name_zh"], "n": r["n"]}
                            for r in open_qs.values("categories__code", "categories__name_en", "categories__name_zh").annotate(n=Count("id")).order_by("-n")[:12]],
            "by_location": [{"id": r["location_id"], "name_en": r["location__name_en"], "name_zh": r["location__name_zh"], "n": r["n"]}
                            for r in qs.filter(occurred_at__date__gte=today - dt.timedelta(days=90)).values("location_id", "location__name_en", "location__name_zh").annotate(n=Count("id")).order_by("-n")[:12]],
            "by_time_band": [{"id": r["time_band_id"], "label_en": r["time_band__label_en"], "label_zh": r["time_band__label_zh"], "n": r["n"]}
                             for r in qs.filter(occurred_at__date__gte=today - dt.timedelta(days=90)).values("time_band_id", "time_band__label_en", "time_band__label_zh").annotate(n=Count("id")).order_by("-n")[:12]],
            "overdue": open_qs.filter(Q(last_action_at__lt=cutoff) | Q(last_action_at__isnull=True, logged_at__lt=cutoff)).count(),
            "my_assigned": open_qs.filter(assigned_to=ctx.employee).count(),
            "logged_last_7_days": qs.filter(logged_at__gte=timezone.now() - dt.timedelta(days=7)).count(),
            "unread_alerts": Alert.objects.filter(employee=ctx.employee, read_at__isnull=True).count(),
            "overdue_days": overdue_days,
        })
