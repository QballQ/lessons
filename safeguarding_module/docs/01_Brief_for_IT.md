# Safeguarding module for SIMS: brief for the School Systems Manager

Prepared October 2026 for Wycombe Abbey School Changzhou. Audience: the IT colleague building the in-house SIMS (SIMS 国际学校教务管理系统) and the coding agents (DeepSeek, Claw) he is using.

## 1. Executive summary

The school needs a CPOMS-style safeguarding log inside SIMS, not a separate tool. A concern must be loggable by any member of staff in under two minutes, and then visible only to the people who need to know. The module in this pack does that:

- **Reuses SIMS data.** Students, staff, classes, rooms, subjects and the timetable come from the existing SIMS tables. Nothing is copied.
- **Ring-fenced by design.** Three access rings (pastoral, safeguarding team, DSL only) plus per-record grants. The SIMS super-admin flag gives no access to safeguarding records.
- **Bilingual.** Every label, category and status has English and Chinese, following the pattern already used in SIMS (vue-i18n, en and zh-cn).
- **Pinpoints the incident.** Date and time, time band or lesson period, location (linked to SIMS rooms), subject and the timetabled lesson looked up automatically from the student's class.
- **Body map, files, chronology, alerts, agency fields.** The same shape as the CPOMS form in the screenshots.
- **Everything is audited**, including reads. Narrative text is encrypted at rest with a key that is not in the database.

The pack contains a working Django app (tested against stub SIMS models), Vue 3 pages and components, bilingual message files, seed data, a build prompt for the coding agents, and this brief.

## 2. What we learned about the current SIMS build

Taken from the deployed frontend at the internal address. No backend code was read; the API shape was inferred from the compiled bundle.

| Area | Finding | Why it matters |
|---|---|---|
| Frontend | Vue 3, Vite, Pinia, vue-router, vue-i18n (zh-cn and en), Element Plus, axios, ECharts | The new pages use the same stack and conventions |
| Backend | REST API at `/api/v1`, JWT with `access` and `refresh` tokens, endpoints end with a slash, custom actions like `by_class/` and `batch_assign/` | This is the Django REST Framework convention, so the app is written as a Django app |
| Auth | `/users/login/`, `/users/token/refresh/`, `/users/me/` returning `positions_info` with `is_admin`, `positions`, `scopes.class_ids`, `scopes.subject_ids`, and `employee_id` | Safeguarding reads the employee, never `is_admin` |
| Account roles | SUPER_ADMIN, ADMIN, ACADEMIC_ADMIN, TEACHER, STAFF | Not used for safeguarding access |
| Position matrix | SUBJECT_TEACHER, HOMEROOM, VICE_HOMEROOM, SUBJECT_LEADER, GRADE_LEADER, HOUSE_LEADER, ACADEMIC_DEAN, VICE_PRINCIPAL, PRINCIPAL, with subject and grade scopes | Useful for suggesting pastoral scope, but safeguarding roles are held in their own table |
| Router guard | `meta.adminOnly` and `meta.requiredPosition`, both short-circuit to allow when `isAdmin` | The safeguarding routes need a separate `meta.sgRole` check with no admin bypass |
| Students | `/users/students/` with `student_id`, `first_name_en`, `last_name_en`, `first_name_zh`, `last_name_zh`, `gender`, `class_id`, `enrollment_status`, `graduating_year`, guardian fields | Student lookup and snapshot fields |
| Student profile | Tabs: Overview, Profile, Academic, Behavior, Contact Records | A Safeguarding tab is added here |
| Academic | `/academic/classes/`, `/academic/grades/`, `/academic/rooms/`, `/academic/houses/`, `/academic/terms/`, `/academic/student_contact_records/` | Rooms link to locations; classes, grades and houses define pastoral scope |
| Timetable | `/courses/schedules/` with `term`, `day_of_week`, `period`, `room`, `week_type`, class, course and teacher | Lesson lookup for an incident time |
| Attendance | `/attendance/records/` and medical visit fields (clinic, diagnosis, treatment, doctor, follow-up) | Attendance and medical categories can later pre-fill from these |
| Behaviour and houses | `/behavior/points/...`, `/academic/houses/...` | Separate from safeguarding; a behaviour record is never a safeguarding record |
| Audit | `/auditlog/audit-logs/`, `system-logs/`, `security-events/` with permission-denied and data-export events | Safeguarding writes its own read-audit table and can also post to this log |
| Email | A system log category for email exists | The notify hook can send email if the server is allowed to |

## 3. Access model: the ring fences

### 3.1 Roles (held in the safeguarding app, not in the SIMS position matrix)

| Role | Who | Sees | Can do |
|---|---|---|---|
| DSL | Designated Safeguarding Lead, and the Head if you choose | Every record including DSL-only | Everything: change status and visibility, grant and revoke access, manage categories, locations, time bands, alert groups and roles, export, soft delete |
| DEPUTY | Deputy DSLs and the safeguarding team, optionally scoped to Lower School, Upper School or Boarding | Team-ring and pastoral-ring records in their section; not DSL-only records unless alerted or granted | Edit facts, change status, raise visibility to DSL-only (never lower it), alert staff, grant per-record access, add actions |
| PASTORAL | Homeroom teachers, heads of year, house staff, scoped to classes, grades, houses or a section | Pastoral-ring records only (Welfare, Attendance, Medical by default) for students in scope | Read, add a note, upload a file |
| Any active staff | Everyone with a SIMS staff account | Their own submissions (toggle `SG_REPORTER_SEES_OWN`) | Log a concern about any student, add a note to their own entry |
| Alerted or granted | Any staff member named on an alert or a time-limited grant | That one record | Read, add actions, upload, alert others |
| SIMS SUPER_ADMIN or IT | Without a safeguarding role | Nothing | Nothing. The tests prove this. |

### 3.2 Rings on a record

- Every category carries a ring. A record's ring is the most restrictive ring of its categories. Welfare plus Safeguarding is a team-ring record.
- A team member can raise a record to DSL-only. Only a DSL can lower it. Both leave a chronology entry.
- `Allegation against staff` is DSL-only by default and should stay that way.
- An alert or a grant opens one record to one person. It never opens the student's other records.

### 3.3 Where the data flows

```
Any staff member ──► POST /safeguarding/incidents/ ──► Incident (ring computed) ──► Alerts to team / groups
                                                              │
         Reporter sees own entry only ◄───────────────────────┤
         DSL sees all ◄───────────────────────────────────────┤
         DEPUTY (section) sees TEAM + PASTORAL rings ◄────────┤
         PASTORAL (scope) sees PASTORAL ring ◄────────────────┤
         Alerted / granted person sees that record ◄──────────┘
         Every read and write ──► AccessLog (append-only, no narrative text)
```

One function, `visible_incidents(user)` in `services.py`, is the single source of truth. Every list, detail, student tab, attachment download and dashboard count starts from it. If a new endpoint is added, it must start from it too.

### 3.4 What IT can and cannot see

IT administers the server and the database. The design limits what that gives them:

- Narrative fields (the account, chronology notes, body map notes) are encrypted with a key held in an environment variable, not in the database. A database dump shows ciphertext.
- Attachments live outside the web root with no public URL and are served only through a permission-checked view.
- Safeguarding models are not registered in Django admin.
- Every change to who holds a safeguarding role is logged and notifies all current DSLs, so a self-grant is visible the same day.
- Someone with root on the server can still read the key. That is a governance control, not a technical one: keep the key in a file readable only by the service account, restrict server logins, and review the access log monthly.

## 4. The incident form, field by field

Mirrors the CPOMS form in the screenshots, bilingual throughout.

| CPOMS field | SIMS implementation | Source of options |
|---|---|---|
| Student | Typeahead on name or ID, any active student | `/safeguarding/students/lookup/` over SIMS students |
| Incident | Free text, encrypted at rest, minimum 10 characters | |
| Category Suggestions | Not in version 1 (see section 8) | |
| Categories | Bilingual checkboxes, each with a ring and a body-map flag | Seeded: Safeguarding Concern 安全保障关注, Safeguarding 安全保障, Peer on Peer 同伴之间, Welfare 福利/福祉, Attendance 出勤, Physical injury, Bullying, Online safety, Mental health, Self-harm, Disclosure, Family/home, Boarding, Medical, Allegation against staff |
| Linked student(s) | Multi-select; each linked student shows the record under "linked" on their profile tab | SIMS students |
| Maps | Body map marks: front or back, position as a percentage of the figure, area code, note | Stored in `BodyMapMark`; the clickable figure is specified in section 7 |
| Date and time of the incident | Date-time picker; defaults to now; separate from the logged timestamp | |
| Period | Time band (bell schedule including boarding and weekend bands) plus the SIMS period number | `TimeBand` table, seeded with a sample bell schedule to replace with the school's own |
| Location of the incident | Location list; classroom-type locations can link to a SIMS room; free-text detail | `Location` table, seeded; link rooms to `/academic/rooms/` |
| Subject and lesson | Looked up from the student's class, the day and the period; the reporter confirms with one click | `/safeguarding/context/` reading SIMS schedules |
| Status | Active or No Further Action at creation; Monitoring, Referred and Closed later | |
| Assign to | Staff typeahead | `/users/employees/` |
| Files | Multiple files, stored privately, hashed | |
| Alert Staff Members | Staff typeahead plus alert groups (Safeguarding Team, SLT-US, SLT-LS, Boarding, Medical); the hint about red-highlighted colleagues is kept | `AlertGroup` table |
| Agency Involved | Text plus an agency reference | |
| Date/Time (logged) | Server timestamp, read-only | |
| Extra: Section | Lower, Upper, Boarding, derived from the student's grade and editable | `SG_LOWER_SCHOOL_GRADES` setting |
| Extra: Source | Observed by staff, student disclosure, peer report, parent, external, other | |
| Extra: Severity | Low, medium, high, critical | |
| Extra: Staff present | Multi-select of staff | `/users/employees/` |

## 5. Integration points (so it is not a standalone module)

1. **Student profile tab.** `StudentSafeguardingTab.vue` goes in `StudentProfile.vue` next to Contact Records. It shows only what the viewer may see, plus a "Log a concern" button for everyone.
2. **Sidebar menu.** A `Safeguarding 安全保障` entry under the System or Basic group, shown only when `/safeguarding/me/` returns a role. The "Add Incident" route is reachable from the student profile for everyone.
3. **Router guard.** A new `meta.sgRole` check that reads the safeguarding store, with no `isAdmin` short-circuit. Details in `frontend/safeguarding/router/safeguarding.routes.ts`.
4. **`/users/me/`.** Optionally add a `safeguarding` key with the roles so the menu can render before the module loads. The module also exposes `/safeguarding/me/`.
5. **Timetable and rooms.** The context endpoint reads SIMS schedules; locations link to SIMS rooms.
6. **Attendance and medical.** Later: a button on an attendance record or medical visit that opens the form pre-filled with student, time and category.
7. **Audit log.** The module keeps its own `AccessLog`. If the SIMS audit log has a Python helper, call it from `audit.py` as well so security events appear in one place.
8. **Notifications.** `SG_NOTIFY_HOOK` points at a function that sends email or WeCom. Alerts also appear in-app at `/safeguarding/alerts/mine/`. Messages carry a reference and a student, never the narrative.

## 6. Privacy, security and compliance controls

| Control | Where |
|---|---|
| Field encryption at rest (Fernet, key rotation command) | `fields.py`, `sg_rotate_keys` |
| Private attachment storage with permission-checked download | `models.py`, `AttachmentDownloadView` |
| Read auditing, not only write auditing | `audit.py`, every view |
| No `Cache-Control` leaks: `no-store` on every safeguarding response | `middleware.py` |
| No hard delete; soft delete with reason, DSL only | `soft-delete` action |
| Upload type and size limits, SHA-256 of each file | `views.py` |
| Export only by DSL, watermarked with name and time, logged | `export.py` |
| Hide Names toggle in lists and detail pages | `useSafeguarding.ts` store |
| Blank Screen button, idle lock | Specified in section 7, to build |
| Access only inside the school network or over WireGuard | Existing hosting decision; keep it |

Compliance notes, to confirm with the school's legal adviser:

- **China PIPL.** Information about minors under 14 is sensitive personal information: separate consent, strict purpose limitation, minimum necessary access, and the data stays in China. Internal hosting satisfies localisation. Keep the access log as evidence of need-to-know handling.
- **UK practice (KCSIE, COBIS and BSO expectations).** A named DSL with deputies, a single chronological record per child, transfer of the file when a child moves school, and retention long after the child leaves (UK practice commonly keeps child protection files to the 25th birthday). The export endpoint is the transfer mechanism.
- **Staff allegations** sit in their own DSL-only category so that deputies do not see concerns about colleagues.

## 7. Pieces specified here for IT to build (not coded in this pack)

1. **Clickable body map figure.** Front and back outlines in an SVG with a fixed viewBox. A click places a numbered marker and stores `x` and `y` as percentages of the figure box, with an `area` code chosen from the region list in the i18n file. Marks render as numbered pins and as a list with a note each. Read-only on the detail page. The form currently uses a simple list editor with the same data shape, so the figure is a drop-in replacement.
2. **Blank Screen overlay.** A full-window neutral overlay toggled by the store flag `blank`, dismissed by click or key. Used when someone approaches the desk.
3. **Idle lock.** After `idle_timeout_minutes` (from `/safeguarding/me/`) without input on a safeguarding page, show the overlay and call the SIMS logout action.
4. **Sidebar entry and badge.** Unread alert count from `/safeguarding/me/`.
5. **PDF export.** Route the HTML from the export endpoint through the PDF renderer already used for term reports.

## 8. Out of scope for version 1

- **AI category suggestions.** Only acceptable with a model running on the school's own server. Never send incident text to an external API. Leave the button out until an on-premises model exists.
- **Parent or student access.** Never.
- **Behaviour points integration.** Behaviour is a separate system with different visibility.
- **Full-text search inside narratives.** Encryption prevents SQL search; search by student, reference, category, date, location and time band instead.

## 9. Acceptance checklist

- [ ] A teacher with no safeguarding role can log a concern about any student, upload a photo, alert the Safeguarding Team group, and afterwards see only their own entry.
- [ ] A SIMS super admin with no safeguarding role sees no records, no dashboard, no roles page (tests `test_sims_superuser_without_role_sees_nothing`).
- [ ] A deputy scoped to Upper School cannot open a Lower School record or a DSL-only record.
- [ ] A homeroom teacher with pastoral scope sees a Welfare record for their class and not a Safeguarding record for the same child.
- [ ] Alerting a colleague opens that record only; revoking a grant closes it immediately.
- [ ] The DSL sees everything, can lower visibility, export a watermarked record, and mark a duplicate as deleted with a reason.
- [ ] The access log shows every list, view, download and export with user, time and IP, and never contains narrative text.
- [ ] A database dump shows ciphertext in `safeguarding_incident.body`.
- [ ] The student profile shows a Safeguarding tab that respects the viewer's role.
- [ ] Every label appears in English and Chinese.
- [ ] The timetable lookup pre-fills subject and room for a lesson-time incident.
- [ ] Removing the last active DSL is refused.

## 10. Decisions needed from the school

1. Who is the DSL, who are deputies, and which sections do deputies cover.
2. Grade names that count as Lower School (`SG_LOWER_SCHOOL_GRADES`).
3. The real bell schedule and boarding time bands to replace the sample `TimeBand` rows.
4. Membership of each alert group.
5. Whether reporters may see their own entries after submission (default yes).
6. Retention period and who holds the export duty when a child leaves.
7. Whether email or WeCom notifications are allowed from the internal server.
