from django.db import models

from mediafetchxpress.link_type_choices import LINK_TYPE_CHOICES, VIDEO


class Group(models.Model):
    name = models.CharField(max_length=100)
    link_type = models.CharField(max_length=50, choices=LINK_TYPE_CHOICES, default=VIDEO)


class Link(models.Model):
    url = models.CharField(max_length=2048)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class Event(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)
