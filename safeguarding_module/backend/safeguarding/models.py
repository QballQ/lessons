from __future__ import annotations

import hashlib
import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.utils import timezone

from .fields import EncryptedTextField

STUDENT_MODEL = getattr(settings, "SG_STUDENT_MODEL", "users.Student")
EMPLOYEE_MODEL = getattr(settings, "SG_EMPLOYEE_MODEL", "users.Employee")
ROOM_MODEL = getattr(settings, "SG_ROOM_MODEL", "academic.Room")
SUBJECT_MODEL = getattr(settings, "SG_SUBJECT_MODEL", "courses.Subject")
SCHEDULE_MODEL = getattr(settings, "SG_SCHEDULE_MODEL", "courses.Schedule")


# ------------------------------------------------------------------ choices

class Ring(models.TextChoices):
    """Who may see a record. Rings nest: DSL sees TEAM and PASTORAL; TEAM sees PASTORAL."""

    PASTORAL = "PASTORAL", "Pastoral ring 教牧层"
    TEAM = "TEAM", "Safeguarding team ring 安全保障团队层"
    DSL = "DSL", "DSL only 仅限DSL"


RING_ORDER = {Ring.PASTORAL: 0, Ring.TEAM: 1, Ring.DSL: 2}


def widest_ring(rings) -> str:
    """The most restrictive ring in a collection. Empty input defaults to TEAM."""
    rings = [r for r in rings if r in RING_ORDER]
    if not rings:
        return Ring.TEAM
    return max(rings, key=lambda r: RING_ORDER[r])


class Section(models.TextChoices):
    WHOLE = "WHOLE", "Whole school 全校"
    LOWER = "LOWER", "Lower School 小学部"
    UPPER = "UPPER", "Upper School 中学部"
    BOARDING = "BOARDING", "Boarding 寄宿"


class Role(models.TextChoices):
    DSL = "DSL", "Designated Safeguarding Lead 安全保障负责人"
    DEPUTY = "DEPUTY", "Deputy DSL / safeguarding team 副负责人/团队"
    PASTORAL = "PASTORAL", "Pastoral viewer (scoped) 教牧查看（限范围）"


class Status(models.TextChoices):
    ACTIVE = "ACTIVE", "Active 处理中"
    MONITORING = "MONITORING", "Monitoring 持续关注"
    REFERRED = "REFERRED", "Referred to agency 已转介"
    NFA = "NFA", "No further action 无需进一步行动"
    CLOSED = "CLOSED", "Closed 已关闭"


class Severity(models.TextChoices):
    LOW = "LOW", "Low 低"
    MEDIUM = "MEDIUM", "Medium 中"
    HIGH = "HIGH", "High 高"
    CRITICAL = "CRITICAL", "Critical 紧急"


class Source(models.TextChoices):
    STAFF_OBSERVED = "STAFF_OBSERVED", "Observed by staff 教职工观察"
    STUDENT_DISCLOSURE = "STUDENT_DISCLOSURE", "Student disclosure 学生披露"
    PEER_REPORT = "PEER_REPORT", "Reported by another student 同学报告"
    PARENT = "PARENT", "Parent or guardian 家长/监护人"
    EXTERNAL = "EXTERNAL", "External agency 外部机构"
    OTHER = "OTHER", "Other 其他"


# ---------------------------------------------------------- configuration

class RoleAssignment(models.Model):
    """Safeguarding access is granted here and only here.

    The SIMS admin flag and position matrix do NOT grant safeguarding access.
    Every change is written to AccessLog and all current DSLs are notified.
    """

    employee = models.ForeignKey(EMPLOYEE_MODEL, on_delete=models.CASCADE, related_name="safeguarding_roles")
    role = models.CharField(max_length=16, choices=Role.choices)
    section = models.CharField(max_length=16, choices=Section.choices, default=Section.WHOLE)
    class_ids = models.JSONField(default=list, blank=True, help_text="PASTORAL scope: class ids")
    grade_ids = models.JSONField(default=list, blank=True, help_text="PASTORAL scope: grade ids")
    house_ids = models.JSONField(default=list, blank=True, help_text="PASTORAL scope: house ids")
    is_active = models.BooleanField(default=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id", "role"]

    def is_current(self, today=None) -> bool:
        today = today or timezone.localdate()
        if not self.is_active:
            return False
        if self.starts_on and today < self.starts_on:
            return False
        if self.ends_on and today > self.ends_on:
            return False
        return True

    def __str__(self):
        return f"{self.employee_id}:{self.role}:{self.section}"


class Category(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name_en = models.CharField(max_length=80)
    name_zh = models.CharField(max_length=80)
    ring = models.CharField(max_length=16, choices=Ring.choices, default=Ring.TEAM,
                            help_text="Minimum ring needed to see incidents carrying this category")
    uses_body_map = models.BooleanField(default=False)
    colour = models.CharField(max_length=7, default="#8a8f98")
    sort_order = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "code"]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name_en} {self.name_zh}"


class Location(models.Model):
    class Kind(models.TextChoices):
        CLASSROOM = "CLASSROOM", "Classroom 教室"
        CORRIDOR = "CORRIDOR", "Corridor / stairs 走廊/楼梯"
        TOILET = "TOILET", "Toilets / changing rooms 卫生间/更衣室"
        DINING = "DINING", "Dining 餐厅"
        OUTDOOR = "OUTDOOR", "Outdoor / playground 户外/操场"
        SPORTS = "SPORTS", "Sports facility 体育场馆"
        BOARDING = "BOARDING", "Boarding house 宿舍"
        MEDICAL = "MEDICAL", "Medical room 医务室"
        TRANSPORT = "TRANSPORT", "School transport 校车"
        OFFSITE = "OFFSITE", "Off site / trip 校外"
        ONLINE = "ONLINE", "Online 线上"
        HOME = "HOME", "Home 家中"
        OTHER = "OTHER", "Other 其他"

    name_en = models.CharField(max_length=80)
    name_zh = models.CharField(max_length=80)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.OTHER)
    room = models.ForeignKey(ROOM_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             help_text="Link to a SIMS room so the timetable can pre-fill it")
    section = models.CharField(max_length=16, choices=Section.choices, default=Section.WHOLE)
    sort_order = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name_en"]

    def __str__(self):
        return f"{self.name_en} {self.name_zh}"


class TimeBand(models.Model):
    """Time of day. Lesson periods map to SIMS schedule period numbers; boarding
    and weekend bands do not."""

    class Applies(models.TextChoices):
        WEEKDAY = "WEEKDAY", "Weekday 工作日"
        WEEKEND = "WEEKEND", "Weekend 周末"
        ALL = "ALL", "Every day 每天"

    code = models.SlugField(max_length=30, unique=True)
    label_en = models.CharField(max_length=60)
    label_zh = models.CharField(max_length=60)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_number = models.PositiveSmallIntegerField(null=True, blank=True,
                                                     help_text="SIMS schedule period this band is")
    applies_to = models.CharField(max_length=8, choices=Applies.choices, default=Applies.WEEKDAY)
    sort_order = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "start_time"]

    def __str__(self):
        return f"{self.label_en} {self.label_zh}"

    @classmethod
    def for_moment(cls, when):
        local = timezone.localtime(when)
        applies = cls.Applies.WEEKEND if local.isoweekday() >= 6 else cls.Applies.WEEKDAY
        t = local.time()
        return (
            cls.objects.filter(is_active=True, applies_to__in=[applies, cls.Applies.ALL],
                               start_time__lte=t, end_time__gt=t)
            .order_by("sort_order")
            .first()
        )


class AlertGroup(models.Model):
    """Named groups for the 'Alert staff members' buttons (Safeguarding Team, SLT-US ...)."""

    code = models.SlugField(max_length=30, unique=True)
    name_en = models.CharField(max_length=60)
    name_zh = models.CharField(max_length=60)
    members = models.ManyToManyField(EMPLOYEE_MODEL, blank=True, related_name="safeguarding_alert_groups")
    sort_order = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "code"]

    def __str__(self):
        return f"{self.name_en} {self.name_zh}"


class ReferenceSequence(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    last = models.PositiveIntegerField(default=0)

    @classmethod
    def next_reference(cls) -> str:
        year = timezone.localdate().year
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(year=year)
            seq.last += 1
            seq.save(update_fields=["last"])
        return f"SG-{year}-{seq.last:06d}"


# ----------------------------------------------------------------- incident

class IncidentQuerySet(models.QuerySet):
    def live(self):
        return self.filter(is_deleted=False)


class Incident(models.Model):
    """One safeguarding concern about one student. Never hard-deleted."""

    reference = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(STUDENT_MODEL, on_delete=models.PROTECT, related_name="safeguarding_incidents")
    linked_students = models.ManyToManyField(STUDENT_MODEL, blank=True, related_name="safeguarding_linked_incidents")

    # Snapshots taken at creation so ring-fence filters do not depend on later class moves
    section = models.CharField(max_length=16, choices=Section.choices, default=Section.WHOLE)
    class_id_at_time = models.IntegerField(null=True, blank=True)
    class_name_at_time = models.CharField(max_length=60, blank=True)
    grade_id_at_time = models.IntegerField(null=True, blank=True)
    house_id_at_time = models.IntegerField(null=True, blank=True)

    reporter = models.ForeignKey(EMPLOYEE_MODEL, null=True, blank=True, on_delete=models.PROTECT,
                                 related_name="safeguarding_reported")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    source = models.CharField(max_length=24, choices=Source.choices, default=Source.STAFF_OBSERVED)

    body = EncryptedTextField(help_text="What happened, in the reporter's words. Encrypted at rest.")
    categories = models.ManyToManyField(Category, related_name="incidents")

    occurred_at = models.DateTimeField()
    time_band = models.ForeignKey(TimeBand, null=True, blank=True, on_delete=models.SET_NULL)
    period_number = models.PositiveSmallIntegerField(null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    location_detail = models.CharField(max_length=120, blank=True)
    subject = models.ForeignKey(SUBJECT_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    schedule = models.ForeignKey(SCHEDULE_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                                 help_text="The timetabled lesson matched to the time and class")
    staff_present = models.ManyToManyField(EMPLOYEE_MODEL, blank=True, related_name="+")

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    ring = models.CharField(max_length=16, choices=Ring.choices, default=Ring.TEAM)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    assigned_to = models.ForeignKey(EMPLOYEE_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="safeguarding_assigned")
    agency_involved = models.CharField(max_length=120, blank=True)
    agency_reference = models.CharField(max_length=60, blank=True)

    logged_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_action_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    delete_reason = models.CharField(max_length=255, blank=True)

    objects = IncidentQuerySet.as_manager()

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=["student", "occurred_at"]),
            models.Index(fields=["status", "ring"]),
            models.Index(fields=["section", "ring"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = ReferenceSequence.next_reference()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

    @property
    def is_open(self) -> bool:
        return self.status in {Status.ACTIVE, Status.MONITORING, Status.REFERRED}


class BodyMapMark(models.Model):
    class View(models.TextChoices):
        FRONT = "FRONT", "Front 正面"
        BACK = "BACK", "Back 背面"

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="body_map_marks")
    view = models.CharField(max_length=5, choices=View.choices)
    x = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100 percent of figure width")
    y = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100 percent of figure height")
    region = models.CharField(max_length=40, blank=True, help_text="Hit-test region code, e.g. left_forearm")
    note = EncryptedTextField(blank=True, help_text="Size, colour, description of the mark")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]


def _private_storage():
    root = getattr(settings, "SG_PRIVATE_MEDIA_ROOT", None) or os.path.join(str(settings.BASE_DIR), "private_media")
    # base_url=None: the file has no public URL. It is served only by AttachmentDownloadView.
    return FileSystemStorage(location=root, base_url=None)


def _attachment_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()[:10]
    return f"safeguarding/{instance.incident_id}/{uuid.uuid4().hex}{ext}"


class Attachment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=_attachment_path, storage=_private_storage)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    @staticmethod
    def digest(fileobj) -> str:
        h = hashlib.sha256()
        for chunk in fileobj.chunks():
            h.update(chunk)
        fileobj.seek(0)
        return h.hexdigest()


class Action(models.Model):
    """The chronology under an incident: notes, actions taken, status changes, alerts."""

    class Kind(models.TextChoices):
        CREATED = "CREATED", "Logged 已记录"
        NOTE = "NOTE", "Note 备注"
        ACTION = "ACTION", "Action taken 已采取措施"
        STATUS = "STATUS", "Status change 状态变更"
        CATEGORY = "CATEGORY", "Category change 类别变更"
        RING = "RING", "Visibility change 可见范围变更"
        ASSIGN = "ASSIGN", "Assignment 指派"
        ALERT = "ALERT", "Alert sent 已提醒"
        ACCESS = "ACCESS", "Access granted or revoked 访问授权"
        PARENT_CONTACT = "PARENT_CONTACT", "Parent contact 联系家长"
        AGENCY = "AGENCY", "Agency contact 联系机构"
        REFERRAL = "REFERRAL", "Referral 转介"
        ATTACHMENT = "ATTACHMENT", "File added 已添加文件"
        BODY_MAP = "BODY_MAP", "Body map updated 身体图已更新"
        EXPORT = "EXPORT", "Exported 已导出"

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="actions")
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.NOTE)
    body = EncryptedTextField(blank=True)
    ring = models.CharField(max_length=16, choices=Ring.choices, default=Ring.TEAM,
                            help_text="DSL-only notes are hidden from the team ring")
    meta = models.JSONField(default=dict, blank=True, help_text="Structured detail, never narrative")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    author_employee = models.ForeignKey(EMPLOYEE_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class Alert(models.Model):
    """'Alert staff members': tells a colleague about the incident and, by default,
    lets them see it (the CPOMS red-highlight rule)."""

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="alerts")
    employee = models.ForeignKey(EMPLOYEE_MODEL, on_delete=models.CASCADE, related_name="safeguarding_alerts")
    alerted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    message = models.CharField(max_length=255, blank=True)
    grants_access = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["incident", "employee"], name="sg_alert_once_per_incident")]


class AccessGrant(models.Model):
    """Explicit, time-limited per-incident access for someone outside the rings."""

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="access_grants")
    employee = models.ForeignKey(EMPLOYEE_MODEL, on_delete=models.CASCADE, related_name="safeguarding_grants")
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["-created_at"]

    def is_current(self, now=None) -> bool:
        now = now or timezone.now()
        if self.revoked_at:
            return False
        return self.expires_at is None or self.expires_at > now


class AccessLog(models.Model):
    """Append-only record of every read and write. Never contains narrative text."""

    class Action(models.TextChoices):
        LIST = "LIST", "Listed incidents"
        VIEW = "VIEW", "Viewed incident"
        CREATE = "CREATE", "Created incident"
        UPDATE = "UPDATE", "Updated incident"
        ACTION = "ACTION", "Added chronology entry"
        ALERT = "ALERT", "Sent alert"
        GRANT = "GRANT", "Granted access"
        REVOKE = "REVOKE", "Revoked access"
        UPLOAD = "UPLOAD", "Uploaded attachment"
        DOWNLOAD = "DOWNLOAD", "Downloaded attachment"
        EXPORT = "EXPORT", "Exported record"
        LOOKUP = "LOOKUP", "Student lookup"
        STUDENT_TAB = "STUDENT_TAB", "Viewed student safeguarding tab"
        ROLE_CHANGE = "ROLE_CHANGE", "Changed safeguarding roles"
        CONFIG = "CONFIG", "Changed configuration"
        DENIED = "DENIED", "Access denied"
        SOFT_DELETE = "SOFT_DELETE", "Soft-deleted incident"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    username = models.CharField(max_length=150, blank=True)
    employee_id = models.IntegerField(null=True, blank=True)
    action = models.CharField(max_length=16, choices=Action.choices)
    incident = models.ForeignKey(Incident, null=True, blank=True, on_delete=models.SET_NULL, related_name="access_logs")
    incident_reference = models.CharField(max_length=20, blank=True)
    student_id = models.IntegerField(null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
