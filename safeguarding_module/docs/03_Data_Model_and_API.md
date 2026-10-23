# Data model and API reference

Base path `/api/v1/safeguarding/`. All endpoints need a logged-in SIMS user with an active employee record. Visibility is decided per record by `services.access_level`.

## Tables

| Table | Purpose | Key fields |
|---|---|---|
| `RoleAssignment` | Who holds safeguarding access | employee, role (DSL, DEPUTY, PASTORAL), section, class_ids, grade_ids, house_ids, is_active, starts_on, ends_on, granted_by |
| `Category` | Bilingual categories with a ring | code, name_en, name_zh, ring, uses_body_map, colour |
| `Location` | Where incidents happen; classrooms link to SIMS rooms | name_en, name_zh, kind, room, section |
| `TimeBand` | Bell schedule plus boarding and weekend bands; lesson bands carry the SIMS period number | code, label_en, label_zh, start_time, end_time, period_number, applies_to |
| `AlertGroup` | Buttons on the form (Safeguarding Team, SLT-US ...) | code, name_en, name_zh, members |
| `Incident` | One concern about one student | reference (SG-YYYY-NNNNNN), student, linked_students, section, class/grade/house snapshot, reporter, source, body (encrypted), categories, occurred_at, time_band, period_number, location, location_detail, subject, schedule, staff_present, status, ring, severity, assigned_to, agency_involved, agency_reference, logged_at, last_action_at, closed_at, is_deleted |
| `BodyMapMark` | Marks on the body map | incident, view (FRONT, BACK), x, y (percent), region, note (encrypted) |
| `Attachment` | Private files | incident, file (private storage), original_name, content_type, size, sha256, uploaded_by |
| `Action` | Chronology | incident, kind, body (encrypted), ring (TEAM or DSL), meta, author |
| `Alert` | Alerted colleagues; grants access by default | incident, employee, message, grants_access, read_at |
| `AccessGrant` | Time-limited per-record access | incident, employee, reason, expires_at, revoked_at |
| `AccessLog` | Append-only read and write audit | user, action, incident, student_id, detail (no narrative), ip, user_agent |
| `ReferenceSequence` | Per-year counter for references | year, last |

Rings: `PASTORAL` < `TEAM` < `DSL`. An incident's ring is the widest of its categories' rings; DSLs can set any ring, team members can only raise it.

## Endpoints

| Method and path | Who | Notes |
|---|---|---|
| GET `me/` | staff | roles, scopes, unread alerts, settings |
| GET `dashboard/` | team | open, overdue, by status, severity, category, location, time band |
| GET `students/lookup/?q=` | staff | minimal student summaries; logged |
| GET `context/?student=&at=&period=` | staff | section, time band, period, timetabled lessons |
| GET, POST `alerts/mine/` | staff | my alerts; POST `{ids}` marks read |
| GET `attachments/{id}/download/` | visible | permission-checked file stream |
| GET, POST, PUT, PATCH `categories/`, `locations/`, `time-bands/`, `alert-groups/` | read: staff; write: DSL | no DELETE; deactivate instead |
| GET, POST, PATCH, DELETE `roles/` | DSL | logs and notifies DSLs; last DSL cannot be removed |
| GET `incidents/` | visible | filters: student, status, open, category, ring, section, severity, assigned_to, location, time_band, date_from, date_to, q |
| POST `incidents/` | staff | the form; see payload below |
| GET `incidents/{id}/` | visible | detail; reporters get the restricted serializer |
| PATCH `incidents/{id}/` | team | facts only; status and ring have their own actions |
| GET `incidents/mine/` | staff | my submissions |
| GET `incidents/by-student/?student=` | visible | student profile tab: primary and linked records |
| GET, POST `incidents/{id}/actions/` | visible / can_add_action | kind NOTE, ACTION, PARENT_CONTACT, AGENCY, REFERRAL; ring DSL only for DSLs |
| POST `incidents/{id}/status/` | team | `{status, note}` |
| POST `incidents/{id}/ring/` | DSL, or team raising | `{ring, note}`; returns `visible_to_you: false` if the caller can no longer open it |
| POST `incidents/{id}/alerts/` | can_alert | `{employees:[], groups:[], message, grants_access}` |
| POST `incidents/{id}/grants/` | team | `{employee, reason, expires_at}` |
| POST `incidents/{id}/grants/{gid}/revoke/` | team | |
| POST `incidents/{id}/body-map/` | can_edit_body_map | one mark |
| POST `incidents/{id}/body-map/{mid}/remove/` | can_edit_body_map | own marks unless team |
| POST `incidents/{id}/attachments/` | can_upload | multipart `file` |
| GET `incidents/{id}/export/` | DSL | watermarked HTML, logged |
| POST `incidents/{id}/soft-delete/` | DSL | `{reason}` |

## Create payload

```json
{
  "student": 123,
  "body": "At 10:20 J arrived at my lesson with ...",
  "categories": [2, 6],
  "linked_students": [456],
  "occurred_at": "2026-10-17T10:09:00+08:00",
  "time_band": 6,
  "period_number": 3,
  "location": 1,
  "location_detail": "Room 204",
  "subject": 7,
  "schedule": 1588,
  "staff_present": [12],
  "severity": "HIGH",
  "source": "STAFF_OBSERVED",
  "status": "ACTIVE",
  "assigned_to": 3,
  "agency_involved": "",
  "section": "UPPER",
  "ring": "DSL",
  "body_map_marks": [{"view": "FRONT", "x": 30.5, "y": 42.0, "region": "left_forearm", "note": "2cm bruise, yellowing"}],
  "alert_employees": [3, 9],
  "alert_groups": [1],
  "alert_message": "Please see me before period 5"
}
```

`ring` is ignored unless the caller is on the team. `section` defaults from the student's grade. `time_band` and `period_number` default from `occurred_at`.

## Permissions block on a detail response

```json
"permissions": {"level": "TEAM", "can_view": true, "can_edit": true, "can_change_status": true,
  "can_change_ring": false, "can_lower_ring": false, "can_alert": true, "can_grant": true,
  "can_add_action": true, "can_add_dsl_note": false, "can_upload": true, "can_edit_body_map": true,
  "can_export": false, "can_soft_delete": false, "sees_chronology": true, "sees_dsl_notes": false}
```

The frontend shows or hides controls from this block; the backend enforces the same rules independently.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `SG_STUDENT_MODEL`, `SG_EMPLOYEE_MODEL`, `SG_ROOM_MODEL`, `SG_SUBJECT_MODEL`, `SG_SCHEDULE_MODEL` | users.Student, users.Employee, academic.Room, courses.Subject, courses.Schedule | SIMS model labels |
| `SG_STUDENT_CLASS_ATTR`, `SG_SCHEDULE_CLASS_FIELD`, `SG_SCHEDULE_LAYER_CLASS_FIELD`, `SG_STUDENT_LAYER_CLASSES_ATTR` | class_obj, class_obj, layer_class, layer_classes | relation names |
| `SG_LOWER_SCHOOL_GRADES` | [] | grade names in the Lower School |
| `SG_REPORTER_SEES_OWN` | True | reporters can open their own entries |
| `SG_FIELD_KEYS` | [] | Fernet keys, newest first; empty means unencrypted (development only) |
| `SG_PRIVATE_MEDIA_ROOT` | BASE_DIR/private_media | attachment storage outside the web root |
| `SG_MAX_UPLOAD_BYTES`, `SG_ALLOWED_UPLOAD_TYPES` | 20 MB, images, PDF, audio, video, Word, text | upload limits |
| `SG_IDLE_TIMEOUT_MINUTES`, `SG_OVERDUE_DAYS` | 10, 5 | UI idle lock, dashboard overdue rule |
| `SG_NOTIFY_HOOK` | None | dotted path to an outbound notifier |
| `SG_API_PREFIX` | /api/v1/safeguarding/ | path the no-store middleware protects |
