from django.db import transaction, IntegrityError, DatabaseError
from django.core.exceptions import ValidationError

from ..models import DownloadTask
from .task_state import TaskState


@transaction.atomic
def create_and_enqueue_download_task(url, download_strategy, save_strategy, priority=0):
    """
    Creates a DownloadTask instance and enqueues it for processing if creation is successful.
    Ensures atomicity of database operations and returns a consistent response suitable for views.
    """
    response = {"success": False, "task": None, "error": None}

    try:
        task = DownloadTask(
            url=url,
            download_strategy=download_strategy,
            save_strategy=save_strategy,
            priority=priority,
            state=TaskState.PENDING.value,
        )
        task.full_clean()
        task.save()
        response["task"] = task
        response["success"] = True
    except ValidationError as e:
        error_messages = e.message_dict
        response["error"] = f"Validation error: {error_messages}"
    except IntegrityError as e:
        response["error"] = f"Database integrity error: {str(e)}"
    except DatabaseError as e:
        response["error"] = f"Database error: {str(e)}"
    return response


