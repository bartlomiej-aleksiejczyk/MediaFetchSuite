import re

from django.core.exceptions import ValidationError
from django.db import models

from mediafetchxpress.link_type_choices import LINK_TYPE_CHOICES, VIDEO


def validate_s3_bucket_name(value):
    if not re.match(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", value):
        raise ValidationError(
            "Name must be between 3 and 63 characters long, "
            "can contain lowercase letters, numbers, and hyphens, "
            "and must start and end with a lowercase letter or number."
        )


class Group(models.Model):
    name = models.CharField(
        max_length=63,
        unique=True,
        validators=[validate_s3_bucket_name]
    )
    link_type = models.CharField(max_length=50, choices=LINK_TYPE_CHOICES, default=VIDEO)


class Link(models.Model):
    url = models.CharField(max_length=2048)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class Event(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)
