"""One-off: load seed data and name the first DSL.

    python manage.py sg_bootstrap --employee-no E0001
    python manage.py sg_bootstrap --employee-id 12 --skip-seed

Run by IT on the server, once. It is logged, and the output should be kept
with the change record. After this, roles are managed only inside the module.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from safeguarding import integration
from safeguarding.audit import log_access
from safeguarding.models import Role, RoleAssignment, Section


class Command(BaseCommand):
    help = "Load safeguarding seed data and create the first DSL role assignment"

    def add_arguments(self, parser):
        parser.add_argument("--employee-id", type=int)
        parser.add_argument("--employee-no", type=str)
        parser.add_argument("--skip-seed", action="store_true")

    def handle(self, *args, **opts):
        if not opts["skip_seed"]:
            call_command("loaddata", "safeguarding_seed")
            self.stdout.write(self.style.SUCCESS("Seed data loaded (categories, locations, time bands, alert groups)."))
        Employee = integration.employee_model()
        emp = None
        if opts.get("employee_id"):
            emp = Employee.objects.filter(pk=opts["employee_id"]).first()
        elif opts.get("employee_no"):
            emp = Employee.objects.filter(employee_no=opts["employee_no"]).first()
        if emp is None:
            if opts.get("employee_id") or opts.get("employee_no"):
                raise CommandError("Employee not found.")
            self.stdout.write("No employee given; no DSL created.")
            return
        obj, created = RoleAssignment.objects.get_or_create(
            employee=emp, role=Role.DSL, defaults={"section": Section.WHOLE, "note": "bootstrap"}
        )
        log_access(None, "ROLE_CHANGE", employee=emp, detail={"op": "bootstrap", "role": "DSL", "assignment_id": obj.pk})
        self.stdout.write(self.style.SUCCESS(f"DSL {'created' if created else 'already present'}: {emp} (assignment {obj.pk})"))
