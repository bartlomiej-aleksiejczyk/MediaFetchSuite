from huey.contrib.djhuey import db_task, periodic_task
from huey import crontab
from django.utils import timezone
from django.db import transaction, DatabaseError, IntegrityError
from django.core.exceptions import ValidationError
from .models import DownloadTask, TaskExecutionWindow
from .domain.task_state import TaskState
from .domain.save_media_strategies import MediaSaveStrategies
from .domain.download_media_strategies import MediaDownloadStrategies


@periodic_task(crontab(minute="*"))
def process_tasks_in_window():
    """
    Periodic task that runs every minute.
    Checks if the current time is within the allowed window.
    If it is, processes one task with the highest priority.
    """
    task_execution_window = TaskExecutionWindow.get_current_window()
    if not task_execution_window:
        return

    now = timezone.now().time()

    if not is_within_time_window(
        now, task_execution_window.start_time, task_execution_window.end_time
    ):
        return

    in_progress_exists = DownloadTask.objects.filter(
        state=TaskState.IN_PROGRESS.value
    ).exists()
    if in_progress_exists:
        return

    task = (
        DownloadTask.objects.filter(state=TaskState.PENDING.value)
        .order_by("-priority", "created_at")
        .first()
    )

    if task:
        process_download_and_save_task(task.id)


def is_within_time_window(current_time, start_time, end_time):
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        return current_time >= start_time or current_time <= end_time


@db_task()
def process_download_and_save_task(task_id):
    try:
        with transaction.atomic():
            task = DownloadTask.objects.get(id=task_id)
            if task.state != TaskState.PENDING.value:
                return
            task.state = TaskState.IN_PROGRESS
            task.error_message = ""
            task.save()
    except (DownloadTask.DoesNotExist, DatabaseError, IntegrityError) as _e:
        return

    try:

        download_strategy_func = MediaDownloadStrategies.get_strategy_function(
            task.download_strategy
        )
        if not download_strategy_func:
            raise ValueError(f"Unknown download strategy: {task.download_strategy}")

        download_result = download_strategy_func(task.url)

        if not download_result.get("success"):
            raise DownloadError(
                download_result.get("error", "Unknown error during download.")
            )

        file_paths = download_result.get("file_paths", [])

        save_strategy_func = MediaSaveStrategies.get_strategy_function(
            task.save_strategy
        )
        if not save_strategy_func:
            raise ValueError(f"Unknown save strategy: {task.save_strategy}")

        save_result = save_strategy_func(file_paths)

        if not save_result.get("success"):
            raise SaveError(save_result.get("error", "Unknown error during saving."))

        with transaction.atomic():
            task.state = TaskState.COMPLETED
            task.save()

    except (DownloadError, SaveError, ValueError) as e:
        with transaction.atomic():
            task.state = TaskState.FAILED
            task.error_message = str(e)
            task.save()
    except (DatabaseError, IntegrityError, ValidationError) as e:
        with transaction.atomic():
            task.state = TaskState.FAILED
            task.error_message = f"Database error: {str(e)}"
            task.save()


class DownloadError(Exception):
    """Exception raised when a download error occurs."""

    def __init__(self, message, url=None, original_exception=None):
        self.message = message
        self.url = url
        self.original_exception = original_exception
        super().__init__(message)

    def __str__(self):
        info = f"DownloadError: {self.message}"
        if self.url:
            info += f" | URL: {self.url}"
        if self.original_exception:
            info += f" | Original Exception: {str(self.original_exception)}"
        return info


class SaveError(Exception):
    """Exception raised when a save error occurs."""

    def __init__(self, message, file_paths=None, original_exception=None):
        self.message = message
        self.file_paths = file_paths
        self.original_exception = original_exception
        super().__init__(message)

    def __str__(self):
        info = f"SaveError: {self.message}"
        if self.file_paths:
            info += f" | File Paths: {self.file_paths}"
        if self.original_exception:
            info += f" | Original Exception: {str(self.original_exception)}"
        return info
