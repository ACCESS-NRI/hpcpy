"""Constants."""

from pathlib import Path

# Location for rendered job scripts
JOB_SCRIPT_DIR = Path.home() / ".hpcpy" / "job_scripts"
JOB_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# Statuses
STATUS_CYCLE_HARVESTING = "U"
STATUS_EXITING = "E"
STATUS_FINISHED = "F"
STATUS_HAS_SUBJOB = "B"
STATUS_HELD = "H"
STATUS_MOVED = "M"
STATUS_MOVING = "T"
STATUS_QUEUED = "Q"
STATUS_RUNNING = "R"
STATUS_SUBJOB_COMPLETED = "X"
STATUS_SUSPENDED = "S"
STATUS_WAITING = "W"

# PBS status translation
PBS_STATUSES = dict(
    B=STATUS_HAS_SUBJOB,
    E=STATUS_EXITING,
    F=STATUS_FINISHED,
    H=STATUS_HELD,
    M=STATUS_MOVED,
    Q=STATUS_QUEUED,
    R=STATUS_RUNNING,
    S=STATUS_SUSPENDED,
    T=STATUS_MOVING,
    U=STATUS_CYCLE_HARVESTING,
    W=STATUS_WAITING,
    X=STATUS_SUBJOB_COMPLETED,
)

# PBS command templates
PBS_SUBMIT = "qsub{directives} {job_script}"
PBS_STATUS = "qstat -f -F json {job_id}"
PBS_DELETE = "qdel {job_id}"
