from __future__ import annotations

from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from . import integration, services
from .audit import log_access
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
    Section,
    Status,
    TimeBand,
    widest_ring,
)


class StudentSummaryField(serializers.ReadOnlyField):
    def to_representation(self, value):
        return integration.student_summary(value)


class EmployeeSummaryField(serializers.ReadOnlyField):
    def to_representation(self, value):
        return integration.employee_summary(value)


def _user_name(user) -> str:
    if user is None:
        return ""
    full = getattr(user, "get_full_name", lambda: "")()
    return full or user.get_username()


# ------------------------------------------------------------ configuration

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "code", "name_en", "name_zh", "ring", "uses_body_map", "colour", "sort_order", "is_active"]


class LocationSerializer(serializers.ModelSerializer):
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ["id", "name_en", "name_zh", "kind", "room", "room_name", "section", "sort_order", "is_active"]

    def get_room_name(self, obj):
        return str(obj.room) if obj.room_id else ""


class TimeBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBand
        fields = ["id", "code", "label_en", "label_zh", "start_time", "end_time", "period_number", "applies_to", "sort_order", "is_active"]


class AlertGroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=integration.employee_model().objects.all(), required=False)
    member_summaries = serializers.SerializerMethodField()

    class Meta:
        model = AlertGroup
        fields = ["id", "code", "name_en", "name_zh", "members", "member_summaries", "sort_order", "is_active"]

    def get_member_summaries(self, obj):
        return [integration.employee_summary(m) for m in obj.members.all()]


class RoleAssignmentSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=integration.employee_model().objects.all())
    employee_summary = EmployeeSummaryField(source="employee")
    granted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RoleAssignment
        fields = ["id", "employee", "employee_summary", "role", "section", "class_ids", "grade_ids", "house_ids",
                  "is_active", "starts_on", "ends_on", "note", "granted_by_name", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def get_granted_by_name(self, obj):
        return _user_name(obj.granted_by)

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        section = attrs.get("section", getattr(self.instance, "section", Section.WHOLE))
        ids = (attrs.get("class_ids", getattr(self.instance, "class_ids", [])) or []) + \
              (attrs.get("grade_ids", getattr(self.instance, "grade_ids", [])) or []) + \
              (attrs.get("house_ids", getattr(self.instance, "house_ids", [])) or [])
        if role == "PASTORAL" and section == Section.WHOLE and not ids:
            raise serializers.ValidationError("A pastoral viewer needs a section or a list of classes, grades or houses.")
        return attrs


# ---------------------------------------------------------------- children

class BodyMapMarkSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BodyMapMark
        fields = ["id", "view", "x", "y", "region", "note", "created_at", "created_by_name"]
        read_only_fields = ["created_at"]

    def get_created_by_name(self, obj):
        return _user_name(obj.created_by)

    def validate(self, attrs):
        for k in ("x", "y"):
            v = attrs.get(k)
            if v is not None and not (0 <= v <= 100):
                raise serializers.ValidationError({k: "must be between 0 and 100"})
        return attrs


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ["id", "original_name", "content_type", "size", "sha256", "created_at", "uploaded_by_name", "download_url"]

    def get_uploaded_by_name(self, obj):
        return _user_name(obj.uploaded_by)

    def get_download_url(self, obj):
        return reverse("safeguarding:attachment-download", args=[obj.pk])


class ActionSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = ["id", "kind", "body", "ring", "meta", "author_name", "created_at"]

    def get_author_name(self, obj):
        emp = obj.author_employee
        return getattr(emp, "name", None) or _user_name(obj.author)


class ActionCreateSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=[Action.Kind.NOTE, Action.Kind.ACTION, Action.Kind.PARENT_CONTACT,
                                            Action.Kind.AGENCY, Action.Kind.REFERRAL])
    body = serializers.CharField(max_length=20000)
    ring = serializers.ChoiceField(choices=[Ring.TEAM, Ring.DSL], default=Ring.TEAM)


class AlertSerializer(serializers.ModelSerializer):
    employee = EmployeeSummaryField()
    alerted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = ["id", "employee", "message", "grants_access", "created_at", "read_at", "alerted_by_name"]

    def get_alerted_by_name(self, obj):
        return _user_name(obj.alerted_by)


class MyAlertSerializer(serializers.ModelSerializer):
    incident_reference = serializers.CharField(source="incident.reference", read_only=True)
    incident_id = serializers.IntegerField(read_only=True)
    student = StudentSummaryField(source="incident.student")
    alerted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = ["id", "incident_id", "incident_reference", "student", "message", "created_at", "read_at", "alerted_by_name"]

    def get_alerted_by_name(self, obj):
        return _user_name(obj.alerted_by)


class AlertCreateSerializer(serializers.Serializer):
    employees = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    groups = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    message = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    grants_access = serializers.BooleanField(default=True)

    def validate(self, attrs):
        if not attrs.get("employees") and not attrs.get("groups"):
            raise serializers.ValidationError("Choose at least one colleague or group.")
        return attrs


class AccessGrantSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=integration.employee_model().objects.all())
    employee_summary = EmployeeSummaryField(source="employee")
    granted_by_name = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = AccessGrant
        fields = ["id", "employee", "employee_summary", "reason", "created_at", "expires_at", "revoked_at", "granted_by_name", "is_current"]
        read_only_fields = ["created_at", "revoked_at"]

    def get_granted_by_name(self, obj):
        return _user_name(obj.granted_by)

    def get_is_current(self, obj):
        return obj.is_current()


class StatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Status.choices)
    note = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")


class RingChangeSerializer(serializers.Serializer):
    ring = serializers.ChoiceField(choices=Ring.choices)
    note = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")


class SoftDeleteSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)


# ----------------------------------------------------------------- incident

class IncidentListSerializer(serializers.ModelSerializer):
    student = StudentSummaryField()
    categories = CategorySerializer(many=True, read_only=True)
    assigned_to = EmployeeSummaryField()
    reporter = EmployeeSummaryField()
    location_name = serializers.SerializerMethodField()
    time_band_label = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = ["id", "reference", "student", "class_name_at_time", "section", "categories", "status", "ring", "severity",
                  "occurred_at", "logged_at", "last_action_at", "assigned_to", "reporter", "location_name", "time_band_label",
                  "period_number", "alert_count"]

    def get_location_name(self, obj):
        return f"{obj.location.name_en} {obj.location.name_zh}" if obj.location_id else obj.location_detail

    def get_time_band_label(self, obj):
        return f"{obj.time_band.label_en} {obj.time_band.label_zh}" if obj.time_band_id else ""

    def get_alert_count(self, obj):
        return obj.alerts.count()


class IncidentDetailSerializer(IncidentListSerializer):
    linked_students = serializers.SerializerMethodField()
    staff_present = serializers.SerializerMethodField()
    body_map_marks = BodyMapMarkSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    actions = serializers.SerializerMethodField()
    alerts = AlertSerializer(many=True, read_only=True)
    access_grants = AccessGrantSerializer(many=True, read_only=True)
    subject_name = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    closed_by_name = serializers.SerializerMethodField()

    class Meta(IncidentListSerializer.Meta):
        fields = IncidentListSerializer.Meta.fields + [
            "body", "source", "linked_students", "staff_present", "time_band", "location", "location_detail", "subject",
            "subject_name", "schedule", "lesson", "agency_involved", "agency_reference", "body_map_marks", "attachments",
            "actions", "alerts", "access_grants", "closed_at", "closed_by_name", "updated_at", "permissions",
        ]

    def get_linked_students(self, obj):
        return [integration.student_summary(s) for s in obj.linked_students.all()]

    def get_staff_present(self, obj):
        return [integration.employee_summary(e) for e in obj.staff_present.all()]

    def get_subject_name(self, obj):
        return str(obj.subject) if obj.subject_id else ""

    def get_lesson(self, obj):
        if not obj.schedule_id:
            return None
        s = obj.schedule
        subject = integration._get(s, "course", "subject") or integration._get(s, "subject")
        return {
            "schedule_id": s.pk,
            "subject_name": str(subject) if subject is not None else "",
            "course_name": str(integration._get(s, "course", "name", default="") or ""),
            "teacher": integration.employee_summary(integration._get(s, "teacher")),
            "room_name": str(integration._get(s, "room", "name", default="") or ""),
            "period": integration._get(s, "period"),
        }

    def get_actions(self, obj):
        level = self.context.get("level", services.LEVEL_NONE)
        user = self.context["request"].user
        return ActionSerializer(services.visible_actions(obj, level, user), many=True).data

    def get_permissions(self, obj):
        return services.permissions_for(self.context.get("level", services.LEVEL_NONE), self.context["sg"])

    def get_closed_by_name(self, obj):
        return _user_name(obj.closed_by)


class IncidentReporterSerializer(serializers.ModelSerializer):
    """What the person who logged a concern sees afterwards: their own words, the
    categories, and the status. Not the chronology, alerts or DSL notes."""

    student = StudentSummaryField()
    categories = CategorySerializer(many=True, read_only=True)
    body_map_marks = BodyMapMarkSerializer(many=True, read_only=True)
    attachments = serializers.SerializerMethodField()
    my_notes = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = ["id", "reference", "student", "class_name_at_time", "categories", "status", "severity", "occurred_at",
                  "logged_at", "body", "location", "location_detail", "time_band", "period_number", "body_map_marks",
                  "attachments", "my_notes", "permissions"]

    def get_attachments(self, obj):
        user = self.context["request"].user
        return AttachmentSerializer(obj.attachments.filter(uploaded_by=user), many=True).data

    def get_my_notes(self, obj):
        user = self.context["request"].user
        return ActionSerializer(obj.actions.filter(author=user).exclude(kind=Action.Kind.CREATED), many=True).data

    def get_permissions(self, obj):
        return services.permissions_for(services.LEVEL_REPORTER, self.context["sg"])


class IncidentCreateSerializer(serializers.ModelSerializer):
    """The CPOMS-style 'Add incident' form. Any active staff member may submit."""

    student = serializers.PrimaryKeyRelatedField(queryset=integration.student_model().objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.filter(is_active=True))
    linked_students = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=integration.student_model().objects.all())
    staff_present = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=integration.employee_model().objects.all())
    body_map_marks = BodyMapMarkSerializer(many=True, required=False, write_only=True)
    alert_employees = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True, default=list)
    alert_groups = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True, default=list)
    alert_message = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True, default="")
    ring = serializers.ChoiceField(choices=Ring.choices, required=False)
    section = serializers.ChoiceField(choices=Section.choices, required=False)

    class Meta:
        model = Incident
        fields = ["student", "body", "categories", "linked_students", "occurred_at", "time_band", "period_number", "location",
                  "location_detail", "subject", "schedule", "staff_present", "severity", "source", "status", "assigned_to",
                  "agency_involved", "agency_reference", "section", "ring", "body_map_marks", "alert_employees", "alert_groups",
                  "alert_message"]

    def validate_categories(self, value):
        if not value:
            raise serializers.ValidationError("Choose at least one category.")
        return value

    def validate_body(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Describe what happened (at least 10 characters).")
        return value

    def validate_status(self, value):
        if value not in {Status.ACTIVE, Status.NFA}:
            raise serializers.ValidationError("A new concern is logged as Active or No further action.")
        return value

    def create(self, validated):
        request = self.context["request"]
        ctx = self.context["sg"]
        alert_employees = validated.pop("alert_employees", [])
        alert_groups = validated.pop("alert_groups", [])
        alert_message = validated.pop("alert_message", "")
        marks = validated.pop("body_map_marks", [])
        categories = validated.pop("categories")
        linked = validated.pop("linked_students", [])
        staff_present = validated.pop("staff_present", [])
        requested_ring = validated.pop("ring", None)

        with transaction.atomic():
            incident = Incident(**validated)
            incident.reporter = ctx.employee
            incident.created_by = request.user
            services.snapshot_student(incident, incident.student)
            rings = [services.ring_for_categories(categories)]
            if requested_ring and ctx.is_team:
                rings.append(requested_ring)  # team members may raise the ring, never lower it
            incident.ring = widest_ring(rings)
            if incident.time_band_id is None:
                band = TimeBand.for_moment(incident.occurred_at)
                if band is not None:
                    incident.time_band = band
                    if incident.period_number is None:
                        incident.period_number = band.period_number
            if incident.status == Status.NFA:
                incident.closed_at = incident.logged_at
            incident.save()
            incident.categories.set(categories)
            if linked:
                incident.linked_students.set(linked)
            if staff_present:
                incident.staff_present.set(staff_present)
            for m in marks:
                BodyMapMark.objects.create(incident=incident, created_by=request.user, **m)
            services.record_action(
                incident, Action.Kind.CREATED, request.user, ctx.employee,
                meta={"categories": [c.code for c in categories], "severity": incident.severity, "status": incident.status,
                      "ring": incident.ring, "marks": len(marks)},
            )
            if alert_employees or alert_groups:
                services.send_alerts(
                    incident, employees=integration.employees_in_ids(alert_employees), group_ids=alert_groups,
                    user=request.user, employee=ctx.employee, message=alert_message,
                )
            log_access(request, "CREATE", incident=incident, employee=ctx.employee,
                       detail={"categories": [c.code for c in categories], "ring": incident.ring, "alerts": len(alert_employees),
                               "groups": list(alert_groups), "marks": len(marks)})
        return incident


class IncidentUpdateSerializer(serializers.ModelSerializer):
    """Team edits of the facts of a record. Status and ring have their own endpoints
    so that every change leaves a chronology entry."""

    categories = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Category.objects.filter(is_active=True))
    linked_students = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=integration.student_model().objects.all())
    staff_present = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=integration.employee_model().objects.all())

    class Meta:
        model = Incident
        fields = ["categories", "linked_students", "occurred_at", "time_band", "period_number", "location", "location_detail",
                  "subject", "schedule", "staff_present", "severity", "source", "assigned_to", "agency_involved",
                  "agency_reference", "section"]

    def update(self, instance, validated):
        request = self.context["request"]
        ctx = self.context["sg"]
        changed = sorted(validated.keys())
        categories = validated.pop("categories", None)
        linked = validated.pop("linked_students", None)
        staff = validated.pop("staff_present", None)
        old_assignee = instance.assigned_to_id
        with transaction.atomic():
            for k, v in validated.items():
                setattr(instance, k, v)
            if categories is not None:
                new_ring = widest_ring([instance.ring, services.ring_for_categories(categories)])
                if new_ring != instance.ring:
                    services.record_action(instance, Action.Kind.RING, request.user, ctx.employee,
                                           meta={"from": instance.ring, "to": new_ring, "cause": "category"})
                    instance.ring = new_ring
            instance.save()
            if categories is not None:
                instance.categories.set(categories)
                services.record_action(instance, Action.Kind.CATEGORY, request.user, ctx.employee,
                                       meta={"categories": [c.code for c in categories]})
            if linked is not None:
                instance.linked_students.set(linked)
            if staff is not None:
                instance.staff_present.set(staff)
            if "assigned_to" in changed and instance.assigned_to_id != old_assignee:
                services.record_action(instance, Action.Kind.ASSIGN, request.user, ctx.employee,
                                       meta={"from": old_assignee, "to": instance.assigned_to_id})
                if instance.assigned_to_id:
                    services.notify("assigned", employees=[instance.assigned_to], incident=instance)
            log_access(request, "UPDATE", incident=instance, employee=ctx.employee, detail={"fields": changed})
        return instance
