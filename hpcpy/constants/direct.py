"""Constants for direct execution (no scheduler)."""

from hpcpy.status import Status
import hpcpy.constants as hc

# Commands
COMMANDS = dict(
    submit="bash {job_script}",
    status="ps -p {job_id} -o stat=",
    delete="kill {job_id}",
    hold="kill -s STOP {job_id}",
    release="kill -s CONT {job_id}",
)

# Directives (none for direct execution)
DIRECTIVES = dict()

# Statuses - mapped from ps(1) stat codes
STATUSES = [
    Status("R", "RUNNING", "Process is running.", generic=hc.STATUS_RUNNING),
    Status(
        "S",
        "SLEEPING",
        "Process is sleeping (interruptible).",
        generic=hc.STATUS_RUNNING,
    ),
    Status(
        "D",
        "DISK_SLEEP",
        "Process is in uninterruptible disk sleep.",
        generic=hc.STATUS_RUNNING,
    ),
    Status("I", "IDLE", "Process is idle.", generic=hc.STATUS_RUNNING),
    Status(
        "T", "STOPPED", "Process has been stopped by a signal.", generic=hc.STATUS_HELD
    ),
    Status(
        "Z",
        "ZOMBIE",
        "Process is a zombie (awaiting reaping).",
        generic=hc.STATUS_EXITING,
    ),
    Status(
        "F",
        "FINISHED",
        "Job has finished, or never existed",
        generic=hc.STATUS_FINISHED,
    ),
]
