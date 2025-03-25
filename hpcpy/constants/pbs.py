"""Constants for the PBS implementation."""

from hpcpy.status import Status
import hpcpy.constants as hc

DELAY_DIRECTIVE_FMT = "%Y%m%d%H%M.%S"


# Commands
COMMANDS = dict(
    submit="qsub{directives} {job_script}",
    status="qstat -f -F json {job_id}",
    delete="qdel {job_id}",
    hold="qhold {job_id}",
    release="qrls {job_id}",
)

# Directives
DIRECTIVES = dict(
    delay="-a {delay_str}",
    depends_on="-W depend=afterok:{depends_on_str}",
    queue="-q {queue}",
    walltime="-l walltime={walltime_str}",
)

# Statuses
STATUSES = [
    Status(
        "B",
        None,
        "Array job has at least one subjob running",
        generic=hc.STATUS_HAS_SUBJOB,
    ),
    Status("E", None, "Job is exiting after having run", generic=hc.STATUS_EXITING),
    Status("F", None, "Job is finished", generic=hc.STATUS_FINISHED),
    Status("H", None, "Job is held", generic=hc.STATUS_HELD),
    Status("M", None, "Job was moved to another server", generic=hc.STATUS_MOVED),
    Status("Q", None, "Job is queued", generic=hc.STATUS_QUEUED),
    Status("R", None, "Job is running", generic=hc.STATUS_RUNNING),
    Status("S", None, "Job is suspended", generic=hc.STATUS_SUSPENDED),
    Status("T", None, "Job is being moved to new location", generic=hc.STATUS_MOVING),
    Status(
        "U",
        None,
        "Cycle-harvesting job is suspended due to keyboard activity",
        generic=hc.STATUS_CYCLE_HARVESTING,
    ),
    Status(
        "W",
        None,
        "Job is waiting for its submitter-assigned start time to be reached",
        generic=hc.STATUS_WAITING,
    ),
    Status(
        "X",
        None,
        "Subjob has completed execution or has been deleted",
        generic=hc.STATUS_SUBJOB_COMPLETED,
    ),
]
