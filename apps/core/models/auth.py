from django.db import models

from apps.core.models.base import TimeStampedModel

class BaseUserSession(TimeStampedModel):
    email = models.EmailField(null=False)
    exp = models.DateTimeField(null=False)
    is_valid = models.BooleanField(default=True)