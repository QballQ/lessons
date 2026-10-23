# Build prompts for the coding agent (DeepSeek, Claw)

Use the master prompt once, then the phase prompts in order. Each phase ends with a "Done when" list; do not start the next phase until the current one passes. Paste the guardrails into every session.

---

## Master prompt

```
You are extending an existing school management system (SIMS) with a safeguarding module.
Stack: Django + Django REST Framework at /api/v1 with SimpleJWT; Vue 3 + Vite + Pinia +
vue-router + vue-i18n (zh-cn and en) + Element Plus. The repository you are in is the SIMS
project. A pack of files has been placed in ./safeguarding_pack/ containing:

  safeguarding_pack/backend/safeguarding/   a complete Django app (models, services, views,
                                            serializers, audit, export, fixture, tests)
  safeguarding_pack/frontend/safeguarding/  Vue pages, API client, store, routes, i18n
  safeguarding_pack/docs/                   the brief, the data model and API reference
  safeguarding_pack/backend/INSTALL.md      settings and wiring

Your job is to integrate this app into SIMS, adapt the one adapter file to the real model
names, make the tests pass, wire the frontend, and build the three UI pieces that are
specified but not coded (clickable body map figure, Blank Screen overlay, idle lock).

Read docs/01_Brief_for_IT.md sections 3, 4 and 5 before touching code. The access rules in
section 3 are the product. Any change that lets a SIMS super admin, or a staff member
without a safeguarding role, read a record they are not alerted to is a defect.

Guardrails (apply in every phase):
1. Every read of safeguarding data starts from services.visible_incidents(user). Never query
   Incident directly in a view. Never check user.is_superuser or positions_info.is_admin
   for safeguarding access.
2. Do not register safeguarding models in Django admin.
3. Do not expose attachment files through MEDIA_URL. Only AttachmentDownloadView serves them.
4. Never log, print or put narrative text (Incident.body, Action.body, BodyMapMark.note) in
   AccessLog.detail, in the SIMS audit log, in notifications, in console output or in tests'
   assertion messages.
5. No hard deletes of incidents. DELETE on /incidents/ stays 405.
6. Every user-visible string has an English and a Chinese message key under `safeguarding`.
7. Do not send incident text to any external API or model.
8. Keep the adapter pattern: SIMS-specific lookups live only in safeguarding/integration.py.
9. Run `python manage.py test safeguarding` after every backend change; all tests must pass.
10. Report what you changed as a list of files with one line each. Do not summarise the brief back.
```

---

## Phase 0: reconnaissance (read-only)

```
Phase 0. Do not modify files. Produce a report answering, with file paths and line numbers:
a) The exact model labels and field names for: the student model (student number, English and
   Chinese name fields, class FK, enrollment status), the employee model (name, employee number,
   link to the auth user, status/active flag), the class model (name, grade FK, room FK), the
   grade model, the room model, the subject model, the schedule model (class FK, layer class FK
   if any, course FK, teacher FK, room FK, day_of_week, period, week_type, term).
b) How a logged-in user maps to an employee (related_name on Employee.user).
c) Whether /users/employees/ supports page_size and a status filter, and the field names it returns.
d) The project's pagination class and default permission classes.
e) Where the frontend keeps: the shared axios instance, the router's beforeEach guard, the
   i18n message files, the sidebar menu definition, StudentProfile.vue and its tabs, the
   user Pinia store (hasPosition, isAdmin).
f) Whether a PDF renderer and an email sender already exist, and their import paths.
Output a table: "pack assumes" vs "SIMS actually has" for each of the names in
safeguarding_pack/backend/safeguarding/integration.py and tests/factories.py.
```

Done when: the table is complete and every row has a file reference.

---

## Phase 1: backend install and adaptation

```
Phase 1. Copy safeguarding_pack/backend/safeguarding into the project as an app. Apply the
settings and URL wiring from safeguarding_pack/backend/INSTALL.md. Using the Phase 0 table,
edit ONLY safeguarding/integration.py and safeguarding/tests/factories.py so model labels,
attribute names and search fields match SIMS. Set SG_LOWER_SCHOOL_GRADES to the real grade
names. Generate migrations, migrate, load the seed fixture, and run the tests.
If a test fails because a SIMS field is named differently, fix the adapter, not the test.
If a test fails because a rule is wrong for this school, stop and ask; do not weaken the test.
```

Done when: `python manage.py test safeguarding` passes, `sg_bootstrap --employee-no <x>` creates the first DSL, and `GET /api/v1/safeguarding/me/` returns `is_dsl: true` for that user and `roles: []` for a super admin without a role.

---

## Phase 2: timetable, rooms and sections

```
Phase 2. Make the context endpoint real. In integration.lessons_at(), use the actual schedule
fields found in Phase 0 so that GET /api/v1/safeguarding/context/?student=<id>&at=<iso>&period=<n>
returns the lesson(s), subject, teacher and room for that student's class (and streamed class
if present) at that day and period, honouring week_type. Link each CLASSROOM Location to a
SIMS room where one exists (write a data migration or a management command that creates one
Location per academic.Room with kind=CLASSROOM, bilingual name from the room name).
Replace the sample TimeBand rows with the school's bell schedule from the data I provide.
Add tests: a schedule row for Tuesday period 3 is returned for a student in that class at a
Tuesday 10:20 incident, and not for Wednesday.
```

Done when: the new tests pass and a manual call returns a lesson for a real class.

---

## Phase 3: frontend wiring

```
Phase 3. Copy safeguarding_pack/frontend/safeguarding into src/modules/safeguarding. Then:
a) Fix the import of the shared axios instance in api/safeguarding.ts and the views.
b) Merge i18n/safeguarding.en.ts and i18n/safeguarding.zh-cn.ts under the `safeguarding` key
   of the existing message trees. Add common.cancel and common.save if missing.
c) Register router/safeguarding.routes.ts as children of MainLayout.
d) Add the `meta.sgRole` check to beforeEach exactly as described in the routes file. It must
   not consult isAdmin.
e) Add a sidebar entry "Safeguarding 安全保障" (icon Lock) shown only when the safeguarding
   store reports a role, with an unread-alert badge. Add "Add Incident" to the student profile
   header for all staff.
f) Add the Safeguarding tab to StudentProfile.vue using components/StudentSafeguardingTab.vue.
g) Build and fix type errors. Do not change the API client's endpoint paths.
```

Done when: `npm run build` passes; a teacher can log a concern from a student profile; a super admin without a role lands on /forbidden when opening /safeguarding.

---

## Phase 4: the three specified UI pieces

```
Phase 4. Build, in src/modules/safeguarding/components:
a) BodyMapFigure.vue. Front and back outlines in one SVG each with viewBox "0 0 200 440".
   Props: modelValue (BodyMapMark[]), readonly. A click converts the pointer position to
   x and y as percentages of the figure box (two decimals), assigns an area code from a list
   of rectangles keyed by the codes in i18n safeguarding.regions, appends a mark and emits
   update:modelValue. Marks render as numbered red pins; a list below shows number, view,
   area and an editable note. Replace the list editor in views/IncidentForm.vue with it and
   show it read-only in views/IncidentDetail.vue. Data shape must stay exactly as the API
   defines (view, x, y, region, note).
b) BlankScreen.vue. A full-window neutral overlay bound to the store flag `blank`, dismissed
   by click or any key, mounted once in MainLayout.
c) Idle lock in the store: on any safeguarding route, after settings.idle_timeout_minutes
   without pointer or key input, set blank=true and call the SIMS logout action.
```

Done when: a mark placed on the figure round-trips through POST /incidents/ and appears on the detail page; the overlay appears on the button and on idle.

---

## Phase 5: notifications, audit and export

```
Phase 5.
a) Implement SG_NOTIFY_HOOK using the existing email sender (Phase 0 f). Message content: the
   reference, the student's name, the sender, a link. Never the narrative.
b) In safeguarding/audit.py, also call the SIMS audit-log helper for CREATE, UPDATE, EXPORT,
   ROLE_CHANGE and DENIED so they appear in /auditlog/ as security events.
c) Route the export endpoint's HTML through the existing PDF renderer; keep the HTML path.
d) Confirm SafeguardingNoStoreMiddleware is active (response header Cache-Control: no-store on
   /api/v1/safeguarding/me/).
```

Done when: an alert produces an email in the log, an export appears in the SIMS audit log, and the PDF opens.

---

## Phase 6: hardening and handover

```
Phase 6.
a) Generate a production SG_FIELD_KEY, store it in the service's environment file readable by
   the service account only, confirm ciphertext in the database, document the rotation steps.
b) Set SG_PRIVATE_MEDIA_ROOT outside the web root with service-account-only permissions.
c) Run the acceptance checklist in docs/01_Brief_for_IT.md section 9 by hand with four test
   accounts (teacher, homeroom with pastoral scope, deputy for Upper School, DSL) and one
   super admin without a role. Record each result.
d) Write docs/SAFEGUARDING_OPERATIONS.md: how to add a DSL, rotate keys, restore a soft-deleted
   record, export a child's file for transfer, and review the access log monthly.
```

Done when: the checklist is all ticked and the operations document exists.

---

## If the agent asks to change the rules

The agent may propose changes to categories, time bands, alert groups and section mapping: these are data. It may not change the ring logic, the admin exclusion, the audit coverage or the encryption without a written decision from the DSL and the Head.
