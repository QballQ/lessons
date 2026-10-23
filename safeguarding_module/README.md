# Safeguarding module pack for SIMS

A CPOMS-style, ring-fenced safeguarding log to build into the school's in-house SIMS (Vue 3 + Django REST Framework). Prepared October 2026.

| Path | What it is |
|---|---|
| `docs/01_Brief_for_IT.md` | Start here. Requirements, access model, field-by-field form spec, integration points, security controls, acceptance checklist, decisions needed |
| `docs/01_Brief_for_IT.zh-CN.md` | The same brief in Simplified Chinese (中文版说明文件), for the IT colleague; the English file is authoritative where they differ |
| `docs/02_AI_Build_Prompt.md` | Copy-paste prompts for DeepSeek or Claw: a master prompt plus seven phased prompts with done-when criteria and guardrails |
| `docs/03_Data_Model_and_API.md` | Tables, fields, endpoints, payloads and permissions |
| `backend/INSTALL.md` | Settings, URLs, migrations, seed and tests |
| `backend/safeguarding/` | Django app: models, encrypted fields, ring-fence services, DRF views and serializers, audit, export, seed fixture, management commands, 18 passing tests |
| `frontend/safeguarding/` | Vue 3 pages and pieces: API client, Pinia store, routes, Add Incident form, list with dashboard, detail with chronology, DSL access page, student profile tab, English and Chinese messages |

Verified: the backend app was migrated and its test suite run against stub SIMS models (Django 5.2, DRF 3.18). The Vue files follow the SIMS stack but have not been compiled against the SIMS project; expect import path adjustments.

Not coded, specified in the brief (section 7): the clickable body map figure, the Blank Screen overlay, the idle lock, the sidebar badge, PDF rendering of the export.
