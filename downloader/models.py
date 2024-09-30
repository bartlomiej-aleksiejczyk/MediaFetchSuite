from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max
from django.core.validators import RegexValidator

from .domain.download_media_strategies import MediaDownloadStrategies
from .domain.save_media_strategies import MediaSaveStrategies
from .domain.task_state import TaskState
from .domain.task_model_services import (
    reorder_priorities_to_updated_task,
    reorder_task_priorities_after_unset,
    clean_up_stale_priorities,
)

infrastructure_safe_characters_validator = RegexValidator(
    regex=r"^[a-z0-9_-]*$",
    message="Only letters, numbers, dots, underscores, and hyphens are allowed.",
)


class DownloadTask(models.Model):
    urls = models.TextField(
        blank=True,
        help_text="Enter multiple URLs separated by commas or new lines.",
    )
    download_strategy = models.CharField(
        max_length=50,
        choices=MediaDownloadStrategies.choices(),
        default=MediaDownloadStrategies.VIDEO_HIGHEST.value,
    )
    save_strategy = models.CharField(
        max_length=50,
        choices=MediaSaveStrategies.choices(),
        default=MediaSaveStrategies.LOCAL_FILESYSTEM.value,
    )
    state = models.CharField(
        max_length=20, choices=TaskState.choices, default=TaskState.PENDING.value
    )
    priority = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)
    catalogue_name = models.CharField(
        blank=True,
        max_length=255,
        validators=[infrastructure_safe_characters_validator],
        help_text="Only letters, numbers, underscores, and hyphens are allowed.",
    )

    class Meta:
        ordering = ["-priority", "created_at"]

    def __str__(self):
        return f"Task {self.id}: {self.urls}"

    def get_absolute_url(self):
        return reverse("delete_task", kwargs={"pk": self.pk})

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().save(*args, **kwargs)
        reorder_task_priorities_after_unset()

    @transaction.atomic
    def save(self, *args, **kwargs):
        clean_up_stale_priorities()
        is_new = self._state.adding
        is_pending = self.state == TaskState.PENDING.value
        new_priority = self.priority

        if is_new and is_pending:
            new_priority = (
                DownloadTask.objects.filter(state=TaskState.PENDING.value).aggregate(
                    Max("priority")
                )["priority__max"]
                or 0
            ) + 1

        if not is_pending:
            new_priority = None

        self.priority = new_priority
        super().save(*args, **kwargs)

        if not is_new and is_pending:
            reorder_priorities_to_updated_task(self)

        if not is_pending:
            reorder_task_priorities_after_unset()


class TaskExecutionWindow(models.Model):
    """
    Stores the start and end times for the task execution window.
    """

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Task Execution Window: {self.start_time} - {self.end_time}"

    @classmethod
    def get_current_window(cls):
        """
        Returns the current processing window.
        If multiple windows are defined, returns the first one.
        """
        return cls.objects.first()
