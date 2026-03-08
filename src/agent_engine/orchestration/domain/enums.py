from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """The lifecycle state of a task."""

    PENDING = "pending"

    BLOCKED = "blocked"

    READY = "ready"

    IN_PROGRESS = "in_progress"

    REVIEW = "review"

    DONE = "done"

    CHANGES_REQUESTED = "changes_requested"

    SKIPPED = "skipped"

    DISCARDED = "discarded"


class PlanningLevel(str, Enum):
    """Defines the uncertainty and granularity of the task."""

    INITIATIVE = "initiative"

    MILESTONE = "milestone"

    ARCHITECTURAL = "architectural"

    FEATURE = "feature"

    ATOMIC = "atomic"


class RecurrenceType(str, Enum):

    ON_SUCCESS = "on_success"

    CRON = "cron"

    ON_FAILURE = "on_failure"
