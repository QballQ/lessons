import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class SafeguardingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "safeguarding"
    verbose_name = "Safeguarding 安全保障"

    def ready(self):
        if not getattr(settings, "SG_FIELD_KEYS", None):
            logger.warning(
                "SG_FIELD_KEYS is not set: safeguarding free text will be stored "
                "unencrypted. Set it before this module is used with real data."
            )
