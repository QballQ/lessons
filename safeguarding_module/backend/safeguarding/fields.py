"""Field-level encryption for safeguarding free text.

Why: the database is administered by IT staff who must not be able to read
incident narratives. Narrative fields are encrypted with a key that lives
outside the database (an environment variable read into settings.SG_FIELD_KEYS).

Settings
--------
SG_FIELD_KEYS: list of Fernet keys (urlsafe base64, 32 bytes), newest first.
    Generate one with:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    Rotation: put the new key first, keep old keys after it, then run
    `manage.py sg_rotate_keys` (re-saves every encrypted row with the new key).

If SG_FIELD_KEYS is empty the field stores plain text (development only) and
apps.py logs a warning at startup.

Limits: encrypted text cannot be searched with SQL (icontains etc.). Search
by student, reference, category, dates and location instead.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

PREFIX = "enc:v1:"
_cache = {"keys": None, "fernet": None}


def _fernet():
    keys = tuple(getattr(settings, "SG_FIELD_KEYS", None) or ())
    if not keys:
        return None
    if _cache["keys"] != keys:
        from cryptography.fernet import Fernet, MultiFernet

        _cache["fernet"] = MultiFernet([Fernet(k) for k in keys])
        _cache["keys"] = keys
    return _cache["fernet"]


def encrypt_text(value: str) -> str:
    f = _fernet()
    if f is None or value is None or value == "":
        return value
    if value.startswith(PREFIX):
        return value
    return PREFIX + f.encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_text(value):
    if value is None or not isinstance(value, str) or not value.startswith(PREFIX):
        return value
    f = _fernet()
    if f is None:
        raise ImproperlyConfigured(
            "Encrypted safeguarding data found but SG_FIELD_KEYS is not configured."
        )
    return f.decrypt(value[len(PREFIX):].encode("ascii")).decode("utf-8")


class EncryptedTextField(models.TextField):
    """TextField whose database value is a Fernet token."""

    description = "Encrypted text"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == "":
            return value
        return encrypt_text(str(value))

    def from_db_value(self, value, expression, connection):
        return decrypt_text(value)
