"""Re-encrypt every narrative field with the first key in SG_FIELD_KEYS.

Put the new key FIRST in SG_FIELD_KEYS (keep the old ones after it), restart,
then run:  python manage.py sg_rotate_keys
Afterwards the old keys can be removed from the setting.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from safeguarding.models import Action, BodyMapMark, Incident


class Command(BaseCommand):
    help = "Re-save encrypted safeguarding fields with the current primary key"

    def handle(self, *args, **opts):
        n = 0
        with transaction.atomic():
            for inc in Incident.objects.all().iterator():
                inc.save(update_fields=["body"])
                n += 1
            for a in Action.objects.all().iterator():
                a.save(update_fields=["body"])
                n += 1
            for m in BodyMapMark.objects.all().iterator():
                m.save(update_fields=["note"])
                n += 1
        self.stdout.write(self.style.SUCCESS(f"Re-encrypted {n} rows."))
