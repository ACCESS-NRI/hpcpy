"""Constants."""

from pathlib import Path
from hpcpy.status import Status

# Location for rendered job scripts
JOB_SCRIPT_DIR = Path.home() / ".hpcpy" / "job_scripts"
JOB_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# Generic Statuses
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

# # PBS status translation
# PBS_STATUSES = dict(
#     B=STATUS_HAS_SUBJOB,
#     E=STATUS_EXITING,
#     F=STATUS_FINISHED,
#     H=STATUS_HELD,
#     M=STATUS_MOVED,
#     Q=STATUS_QUEUED,
#     R=STATUS_RUNNING,
#     S=STATUS_SUSPENDED,
#     T=STATUS_MOVING,
#     U=STATUS_CYCLE_HARVESTING,
#     W=STATUS_WAITING,
#     X=STATUS_SUBJOB_COMPLETED,
# )

# PBS command templates
PBS_COMMANDS = dict(
    submit="qsub{directives} {job_script}",
    status="qstat -f -F json {job_id}",
    delete="qdel {job_id}",
    hold="qhold {job_id}",
    release="qrls {job_id}",
)

# SLURM command templates
SLURM_COMMANDS = dict(
    submit="sbatch{directives} {job_script}",
    status="squeue -j {job_id} --json",
    delete="scancel {job_id}",
    hold="scontrol hold {job_id}",
    release="scontrol release {job_id}"
)

# SLURM status codes
SLURM_STATUSES = list(
    Status("BF", "BOOT_FAIL", "Job terminated due to launch failure, typically due to a hardware failure (e.g. unable to boot the node or block and the job can not be requeued)."),
    Status("CA", "CANCELLED", "Job was explicitly cancelled by the user or system administrator.  The job may or may not have been initiated."),
    Status("CD", "COMPLETED", "Job has terminated all processes on all nodes with an exit code of zero.", generic=STATUS_FINISHED),
    Status("CF", "CONFIGURING", "Job has been allocated resources, but are waiting for them to become ready for use (e.g. booting)."),
    Status("CG", "COMPLETING", "Job is in the process of completing. Some processes on some nodes may still be active."),
    Status("DL", "DEADLINE", "Job terminated on deadline."),
    Status("F", "FAILED", "Job terminated with non-zero exit code or other failure condition."),
    Status("NF", "NODE_FAIL", "Job terminated due to failure of one or more allocated nodes."),
    Status("OOM", "OUT_OF_MEMORY", "Job experienced out of memory error."),
    Status("PD", "PENDING", "Job is awaiting resource allocation.", generic=STATUS_QUEUED),
    Status("PR", "PREEMPTED", "Job terminated due to preemption."),
    Status("R", "RUNNING", "Job currently has an allocation.", generic=STATUS_RUNNING),
    Status("RD", "RESV_DEL_HOLD", "Job is being held after requested reservation was deleted."),
    Status("RF", "REQUEUE_FED", "Job is being requeued by a federation."),
    Status("RH", "REQUEUE_HOLD", "Held job is being requeued."),
    Status("RQ", "REQUEUED", "Completing job is being requeued."),
    Status("RS", "RESIZING", "Job is about to change size."),
    Status("RV", "REVOKED", "Sibling was removed from cluster due to other cluster starting the job."),
    Status("SI", "SIGNALING", "Job is being signaled."),
    Status("SE", "SPECIAL_EXIT", "The job was requeued in a special state. This state can be set by users, typically in EpilogSlurmctld, if the job has terminated with a particular exit value."),
    Status("SO", "STAGE_OUT", "Job is staging out files."),
    Status("ST", "STOPPED", "Job has an allocation, but execution has been stopped with SIGSTOP signal.  CPUS have been retained by this job."),
    Status("S", "SUSPENDED", "Job has an allocation, but execution has been suspended and CPUs have been released for other jobs.", generic=STATUS_SUSPENDED),
    Status("TO", "TIMEOUT", "Job terminated upon reaching its time limit.")
)

# PBS status codes
PBS_STATUSES = list(
    Status("B", None, "Array job has at least one subjob running", generic=STATUS_HAS_SUBJOB),
    Status("E", None, "Job is exiting after having run", generic=STATUS_EXITING),
    Status("F", None, "Job is finished", generic=STATUS_FINISHED),
    Status("H", None, "Job is held", generic=STATUS_HELD),
    Status("M", None, "Job was moved to another server", generic=STATUS_MOVED),
    Status("Q", None, "Job is queued", generic=STATUS_QUEUED),
    Status("R", None, "Job is running", generic=STATUS_RUNNING),
    Status("S", None, "Job is suspended", generic=STATUS_SUSPENDED),
    Status("T", None, "Job is being moved to new location", generic=STATUS_MOVING),
    Status("U", None, "Cycle-harvesting job is suspended due to keyboard activity", generic=STATUS_CYCLE_HARVESTING),
    Status("W", None, "Job is waiting for its submitter-assigned start time to be reached", generic=STATUS_WAITING),
    Status("X", None, "Subjob has completed execution or has been deleted", generic=STATUS_SUBJOB_COMPLETED)
)