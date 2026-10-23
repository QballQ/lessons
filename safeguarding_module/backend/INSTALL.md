# Installing the safeguarding app into the SIMS Django project

1. Copy `backend/safeguarding/` into the Django project next to `users`, `academic`, `courses`.
2. Settings:

```python
INSTALLED_APPS += ["safeguarding"]
MIDDLEWARE += ["safeguarding.middleware.SafeguardingNoStoreMiddleware"]

# Model labels (change only if SIMS names differ)
SG_STUDENT_MODEL = "users.Student"
SG_EMPLOYEE_MODEL = "users.Employee"
SG_ROOM_MODEL = "academic.Room"
SG_SUBJECT_MODEL = "courses.Subject"
SG_SCHEDULE_MODEL = "courses.Schedule"

# Relation names used by integration.py (confirm against the models)
SG_STUDENT_CLASS_ATTR = "class_obj"          # Student -> regular class FK attribute
SG_STUDENT_LAYER_CLASSES_ATTR = "layer_classes"
SG_SCHEDULE_CLASS_FIELD = "class_obj"        # Schedule -> class FK field name
SG_SCHEDULE_LAYER_CLASS_FIELD = "layer_class"

SG_LOWER_SCHOOL_GRADES = ["G1", "G2", "G3", "G4", "G5", "G6"]   # as stored in academic.Grade.name
SG_REPORTER_SEES_OWN = True
SG_IDLE_TIMEOUT_MINUTES = 10
SG_OVERDUE_DAYS = 5
SG_MAX_UPLOAD_BYTES = 20 * 1024 * 1024
SG_PRIVATE_MEDIA_ROOT = "/srv/sims/private_media"   # outside the web root, service account only
SG_FIELD_KEYS = [os.environ["SG_FIELD_KEY"]]          # generate: Fernet.generate_key()
# SG_NOTIFY_HOOK = "notifications.safeguarding_notify"  # optional email / WeCom sender
```

3. URLs:

```python
urlpatterns += [path("api/v1/safeguarding/", include("safeguarding.urls"))]
```

4. Database and seed data:

```bash
python manage.py makemigrations safeguarding
python manage.py migrate
python manage.py sg_bootstrap --employee-no <DSL employee number>
```

5. Tests (adjust `tests/factories.py` field names if the SIMS models differ):

```bash
python manage.py test safeguarding
```

6. nginx: nothing extra. Attachments are streamed by Django; for large files add `X-Accel-Redirect` later.

7. Key rotation: put the new key first in `SG_FIELD_KEYS`, restart, run `python manage.py sg_rotate_keys`, then drop the old key.

## Settings the frontend expects

- Pagination: the API client handles both plain lists and `{count, results}` pages.
- `/users/employees/` must accept `page_size` and return `id`, `employee_no`, `name`.
- `/academic/classes/` and `/academic/grades/` return `id` and `name`.
