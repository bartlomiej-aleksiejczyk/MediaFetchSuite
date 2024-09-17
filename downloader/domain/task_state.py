import enum

class TaskState(enum.Enum):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @classmethod
    def choices(cls):
        return [(key.value, key.description) for key in cls]
