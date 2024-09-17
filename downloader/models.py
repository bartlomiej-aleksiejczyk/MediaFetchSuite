from django.db import models, transaction
from django.utils import timezone
from django.db.models import Max, F
from django.urls import reverse

from .domain.download_media_strategies import MediaDownloadStrategies
from .domain.save_media_strategies import MediaSaveStrategies
from .domain.task_state import TaskState


class DownloadTask(models.Model):
    url = models.URLField()
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

    class Meta:
        ordering = ["-priority", "created_at"]

    def __str__(self):
        return f"Task {self.id}: {self.url}"

    @transaction.atomic
    def reorganize_priorities(self):
        pending_tasks = list(
            DownloadTask.objects.select_for_update()
            .filter(state=TaskState.PENDING.value)
            .order_by("created_at")
        )
        for idx, task in enumerate(pending_tasks, start=1):
            task.priority = idx
        DownloadTask.objects.bulk_update(pending_tasks, ["priority"])

    @transaction.atomic
    def insert_priority(self):
        if self.priority < 1:
            raise ValueError("Priority must be a positive integer.")

        max_priority = (
            DownloadTask.objects.filter(state=TaskState.PENDING).aggregate(
                Max("priority")
            )["priority__max"]
            or 0
        )

        if self.priority > max_priority + 1:
            self.priority = max_priority + 1

        DownloadTask.objects.filter(
            state=TaskState.PENDING.value, priority__gte=self.priority
        ).update(priority=F("priority") + 1)

    @transaction.atomic
    def update_priority(self, old_priority):
        if self.priority < 1:
            raise ValueError("Priority must be a positive integer.")

        if self.priority == old_priority:
            return

        max_priority = (
            DownloadTask.objects.filter(state=TaskState.PENDING)
            .exclude(pk=self.pk)
            .aggregate(Max("priority"))["priority__max"]
            or 0
        )

        if self.priority > max_priority + 1:
            self.priority = max_priority + 1

        if self.priority < old_priority:
            DownloadTask.objects.filter(
                state=TaskState.PENDING,
                priority__gte=self.priority,
                priority__lt=old_priority,
            ).update(priority=F("priority") + 1)
        else:
            DownloadTask.objects.filter(
                state=TaskState.PENDING,
                priority__gt=old_priority,
                priority__lte=self.priority,
            ).update(priority=F("priority") - 1)

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_state = None

        if not is_new:
            old_state = DownloadTask.objects.get(pk=self.pk).state

        if self.state == TaskState.PENDING:
            if is_new or old_state != TaskState.PENDING:
                max_priority = (
                    DownloadTask.objects.filter(state=TaskState.PENDING).aggregate(
                        Max("priority")
                    )["priority__max"]
                    or 0
                )
                self.priority = max_priority + 1
        else:
            if old_state == TaskState.PENDING:
                self.priority = None
                super().save(*args, **kwargs)
                self.reorganize_priorities()
                return
            else:
                self.priority = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("downloadtask_detail", args=[str(self.id)])


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
