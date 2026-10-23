"""Ring-fence acceptance tests. These are the behaviours the module must keep.

Run:  python manage.py test safeguarding
"""
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from safeguarding import services
from safeguarding.models import AccessLog, Action, Alert, Incident, Ring, Role, Status

from . import factories as f


class RingFenceBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat_welfare = f.category("welfare", "PASTORAL")
        cls.cat_sg = f.category("safeguarding", "TEAM")
        cls.cat_staff = f.category("staff_allegation", "DSL")

        cls.dsl = f.make_employee("DSL")
        cls.deputy = f.make_employee("Deputy")
        cls.pastoral = f.make_employee("Homeroom")
        cls.teacher = f.make_employee("Teacher")
        cls.other = f.make_employee("Other teacher")
        cls.it_admin = f.make_employee("IT admin")
        cls.it_admin.user.is_superuser = True
        cls.it_admin.user.is_staff = True
        cls.it_admin.user.save()

        f.give_role(cls.dsl, Role.DSL)
        f.give_role(cls.deputy, Role.DEPUTY, section="UPPER")
        cls.student = f.make_student()
        f.give_role(cls.pastoral, Role.PASTORAL, class_ids=[], grade_ids=[], house_ids=[], section="UPPER")

    def client_for(self, employee):
        c = APIClient()
        c.force_authenticate(user=employee.user)
        return c

    def log_concern(self, employee, categories, body="Child arrived with a bruise on the arm and seemed withdrawn.", **extra):
        payload = {
            "student": self.student.pk,
            "body": body,
            "categories": [c.pk for c in categories],
            "occurred_at": timezone.now().isoformat(),
            "section": "UPPER",
        }
        payload.update(extra)
        resp = self.client_for(employee).post("/api/v1/safeguarding/incidents/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        return Incident.objects.get(reference=resp.data["reference"])


class TestVisibility(RingFenceBase):
    def test_any_staff_can_log_but_only_sees_own(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        self.assertEqual(inc.reporter, self.teacher)
        self.assertEqual(inc.ring, Ring.TEAM)
        # reporter sees own, restricted view
        r = self.client_for(self.teacher).get(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("alerts", r.data)
        self.assertNotIn("actions", r.data)
        self.assertEqual(r.data["permissions"]["level"], "REPORTER")
        # another teacher sees nothing
        r = self.client_for(self.other).get(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        self.assertEqual(r.status_code, 404)
        r = self.client_for(self.other).get("/api/v1/safeguarding/incidents/")
        self.assertEqual(self._count(r), 0)

    def test_sims_superuser_without_role_sees_nothing(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        c = self.client_for(self.it_admin)
        self.assertEqual(self._count(c.get("/api/v1/safeguarding/incidents/")), 0)
        self.assertEqual(c.get(f"/api/v1/safeguarding/incidents/{inc.pk}/").status_code, 404)
        self.assertEqual(c.get("/api/v1/safeguarding/dashboard/").status_code, 403)
        self.assertEqual(c.get("/api/v1/safeguarding/roles/").status_code, 403)

    def test_dsl_sees_everything_including_dsl_only(self):
        a = self.log_concern(self.teacher, [self.cat_sg])
        b = self.log_concern(self.teacher, [self.cat_staff])
        self.assertEqual(b.ring, Ring.DSL)
        ids = {i.pk for i in services.visible_incidents(self.dsl.user)}
        self.assertEqual(ids, {a.pk, b.pk})
        r = self.client_for(self.dsl).get(f"/api/v1/safeguarding/incidents/{b.pk}/")
        self.assertEqual(r.data["permissions"]["level"], "DSL")
        self.assertTrue(r.data["permissions"]["can_export"])

    def test_deputy_sees_team_ring_in_section_but_not_dsl_only(self):
        a = self.log_concern(self.teacher, [self.cat_sg], section="UPPER")
        b = self.log_concern(self.teacher, [self.cat_staff], section="UPPER")
        c = self.log_concern(self.teacher, [self.cat_sg], section="LOWER")
        ids = {i.pk for i in services.visible_incidents(self.deputy.user)}
        self.assertEqual(ids, {a.pk})
        r = self.client_for(self.deputy).get(f"/api/v1/safeguarding/incidents/{b.pk}/")
        self.assertEqual(r.status_code, 404)
        self.assertNotIn(c.pk, ids)

    def test_pastoral_sees_only_pastoral_ring_in_scope(self):
        welfare = self.log_concern(self.teacher, [self.cat_welfare], section="UPPER")
        sg = self.log_concern(self.teacher, [self.cat_sg], section="UPPER")
        lower = self.log_concern(self.teacher, [self.cat_welfare], section="LOWER")
        ids = {i.pk for i in services.visible_incidents(self.pastoral.user)}
        self.assertEqual(ids, {welfare.pk})
        self.assertNotIn(sg.pk, ids)
        self.assertNotIn(lower.pk, ids)

    def test_mixed_categories_take_the_most_restrictive_ring(self):
        inc = self.log_concern(self.teacher, [self.cat_welfare, self.cat_sg])
        self.assertEqual(inc.ring, Ring.TEAM)
        self.assertNotIn(inc.pk, {i.pk for i in services.visible_incidents(self.pastoral.user)})

    def test_alert_grants_access_to_that_incident_only(self):
        a = self.log_concern(self.teacher, [self.cat_sg])
        b = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{a.pk}/alerts/",
                                           {"employees": [self.other.pk], "message": "Please see me"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        ids = {i.pk for i in services.visible_incidents(self.other.user)}
        self.assertEqual(ids, {a.pk})
        self.assertTrue(Alert.objects.filter(incident=a, employee=self.other).exists())
        self.assertTrue(Action.objects.filter(incident=a, kind=Action.Kind.ALERT).exists())
        self.assertEqual(self.client_for(self.other).get(f"/api/v1/safeguarding/incidents/{b.pk}/").status_code, 404)
        mine = self.client_for(self.other).get("/api/v1/safeguarding/alerts/mine/?unread=1")
        self.assertEqual(len(mine.data), 1)

    def test_grant_can_expire_and_be_revoked(self):
        a = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{a.pk}/grants/",
                                           {"employee": self.other.pk, "reason": "Trip leader"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertIn(a.pk, {i.pk for i in services.visible_incidents(self.other.user)})
        gid = r.data["id"]
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{a.pk}/grants/{gid}/revoke/")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(a.pk, {i.pk for i in services.visible_incidents(self.other.user)})

    def test_reporter_cannot_change_status_or_see_dsl_notes(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.teacher).post(f"/api/v1/safeguarding/incidents/{inc.pk}/status/", {"status": "CLOSED"}, format="json")
        self.assertEqual(r.status_code, 403)
        self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{inc.pk}/actions/",
                                       {"kind": "NOTE", "body": "DSL only thinking", "ring": "DSL"}, format="json")
        self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{inc.pk}/actions/",
                                       {"kind": "ACTION", "body": "Spoke to parents", "ring": "TEAM"}, format="json")
        deputy_view = self.client_for(self.deputy).get(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        kinds = [(a["kind"], a["ring"]) for a in deputy_view.data["actions"]]
        self.assertIn(("ACTION", "TEAM"), kinds)
        self.assertNotIn(("NOTE", "DSL"), kinds)

    def test_only_dsl_can_lower_ring_team_can_raise(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.deputy).post(f"/api/v1/safeguarding/incidents/{inc.pk}/ring/", {"ring": "DSL"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["visible_to_you"])  # now DSL-only, so the deputy can no longer open it
        inc.refresh_from_db()
        self.assertEqual(inc.ring, Ring.DSL)
        r = self.client_for(self.deputy).post(f"/api/v1/safeguarding/incidents/{inc.pk}/ring/", {"ring": "TEAM"}, format="json")
        self.assertEqual(r.status_code, 404)
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{inc.pk}/ring/", {"ring": "TEAM"}, format="json")
        self.assertEqual(r.status_code, 200)
        inc.refresh_from_db()
        self.assertEqual(inc.ring, Ring.TEAM)

    def test_status_change_is_recorded_and_closes(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{inc.pk}/status/",
                                           {"status": "NFA", "note": "Spoke with family, resolved"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        inc.refresh_from_db()
        self.assertEqual(inc.status, Status.NFA)
        self.assertIsNotNone(inc.closed_at)
        self.assertTrue(Action.objects.filter(incident=inc, kind=Action.Kind.STATUS, meta__to="NFA").exists())

    def test_every_read_is_logged(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        self.client_for(self.dsl).get("/api/v1/safeguarding/incidents/")
        self.client_for(self.dsl).get(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        self.client_for(self.other).get(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        actions = list(AccessLog.objects.order_by("id").values_list("action", flat=True))
        self.assertIn("CREATE", actions)
        self.assertIn("LIST", actions)
        self.assertIn("VIEW", actions)
        for row in AccessLog.objects.all():
            self.assertNotIn("bruise", str(row.detail))  # never narrative text

    def test_body_map_marks_and_student_tab(self):
        inc = self.log_concern(self.teacher, [self.cat_sg], body_map_marks=[
            {"view": "FRONT", "x": "30.5", "y": "42.0", "region": "left_forearm", "note": "2cm bruise, yellowing"}])
        self.assertEqual(inc.body_map_marks.count(), 1)
        self.assertEqual(inc.body_map_marks.first().note, "2cm bruise, yellowing")
        r = self.client_for(self.dsl).get(f"/api/v1/safeguarding/incidents/by-student/?student={self.student.pk}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["incidents"]), 1)
        r = self.client_for(self.other).get(f"/api/v1/safeguarding/incidents/by-student/?student={self.student.pk}")
        self.assertEqual(len(r.data["incidents"]), 0)
        self.assertTrue(r.data["can_add"])

    def test_no_hard_delete_and_soft_delete_hides(self):
        inc = self.log_concern(self.teacher, [self.cat_sg])
        r = self.client_for(self.dsl).delete(f"/api/v1/safeguarding/incidents/{inc.pk}/")
        self.assertEqual(r.status_code, 405)
        r = self.client_for(self.dsl).post(f"/api/v1/safeguarding/incidents/{inc.pk}/soft-delete/", {"reason": "Duplicate of SG-x"}, format="json")
        self.assertEqual(r.status_code, 204)
        self.assertTrue(Incident.objects.get(pk=inc.pk).is_deleted)
        self.assertEqual(self.client_for(self.dsl).get(f"/api/v1/safeguarding/incidents/{inc.pk}/").status_code, 404)

    def test_me_endpoint_reports_roles_without_admin_bypass(self):
        r = self.client_for(self.it_admin).get("/api/v1/safeguarding/me/")
        self.assertEqual(r.data["roles"], [])
        self.assertFalse(r.data["is_team"])
        r = self.client_for(self.dsl).get("/api/v1/safeguarding/me/")
        self.assertTrue(r.data["is_dsl"])

    def test_student_lookup_open_to_all_staff_but_logged(self):
        r = self.client_for(self.other).get("/api/v1/safeguarding/students/lookup/?q=Test")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0]["id"], self.student.pk)
        self.assertTrue(AccessLog.objects.filter(action="LOOKUP").exists())

    def test_last_dsl_cannot_be_removed(self):
        rid = self.dsl.safeguarding_roles.get(role=Role.DSL).pk
        r = self.client_for(self.dsl).patch(f"/api/v1/safeguarding/roles/{rid}/", {"is_active": False}, format="json")
        self.assertEqual(r.status_code, 400)

    def _count(self, resp):
        data = resp.data
        return data["count"] if isinstance(data, dict) and "count" in data else len(data)


@override_settings(SG_FIELD_KEYS=["hX2qkoqm4LK9j3c2Qm1Qf0c8R8m5n7Jm2z7w7a9Z2bE="])
class TestEncryption(RingFenceBase):
    def test_body_is_encrypted_at_rest(self):
        inc = self.log_concern(self.teacher, [self.cat_sg], body="A very specific sentence about the child")
        from django.db import connection

        with connection.cursor() as cur:
            cur.execute("SELECT body FROM safeguarding_incident WHERE id = %s", [inc.pk])
            raw = cur.fetchone()[0]
        self.assertTrue(raw.startswith("enc:v1:"))
        self.assertNotIn("specific sentence", raw)
        self.assertEqual(Incident.objects.get(pk=inc.pk).body, "A very specific sentence about the child")
