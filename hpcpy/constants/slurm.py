"""SLURM Constants."""

from hpcpy.constants import (
    STATUS_FINISHED,
    STATUS_QUEUED,
    STATUS_RUNNING,
    STATUS_SUSPENDED,
)
from hpcpy.status import Status

DELAY_DIRECTIVE_FMT = "%Y-%m-%dT%H:%M:%S"

# SLURM command templates
COMMANDS = dict(
    submit="sbatch{directives} {job_script}",
    status="squeue -j {job_id} --json",
    delete="scancel {job_id}",
    hold="scontrol hold {job_id}",
    release="scontrol release {job_id}",
)

# Directives
DIRECTIVES = dict(
    delay="--begin={delay_str}",
    depends_on="--dependency=afterok:{depends_on_str}",
    queue="-p {queue}",
    walltime="--time {walltime_str}",
)

# SLURM status codes
STATUSES = [
    Status(
        "BF",
        "BOOT_FAIL",
        "Job terminated due to launch failure, typically due to a hardware failure (e.g. unable to boot the node or block and the job can not be requeued).",
    ),
    Status(
        "CA",
        "CANCELLED",
        "Job was explicitly cancelled by the user or system administrator.  The job may or may not have been initiated.",
    ),
    Status(
        "CD",
        "COMPLETED",
        "Job has terminated all processes on all nodes with an exit code of zero.",
        generic=STATUS_FINISHED,
    ),
    Status(
        "CF",
        "CONFIGURING",
        "Job has been allocated resources, but are waiting for them to become ready for use (e.g. booting).",
    ),
    Status(
        "CG",
        "COMPLETING",
        "Job is in the process of completing. Some processes on some nodes may still be active.",
    ),
    Status("DL", "DEADLINE", "Job terminated on deadline."),
    Status(
        "F",
        "FAILED",
        "Job terminated with non-zero exit code or other failure condition.",
    ),
    Status(
        "NF",
        "NODE_FAIL",
        "Job terminated due to failure of one or more allocated nodes.",
    ),
    Status("OOM", "OUT_OF_MEMORY", "Job experienced out of memory error."),
    Status(
        "PD", "PENDING", "Job is awaiting resource allocation.", generic=STATUS_QUEUED
    ),
    Status("PR", "PREEMPTED", "Job terminated due to preemption."),
    Status("R", "RUNNING", "Job currently has an allocation.", generic=STATUS_RUNNING),
    Status(
        "RD",
        "RESV_DEL_HOLD",
        "Job is being held after requested reservation was deleted.",
    ),
    Status("RF", "REQUEUE_FED", "Job is being requeued by a federation."),
    Status("RH", "REQUEUE_HOLD", "Held job is being requeued."),
    Status("RQ", "REQUEUED", "Completing job is being requeued."),
    Status("RS", "RESIZING", "Job is about to change size."),
    Status(
        "RV",
        "REVOKED",
        "Sibling was removed from cluster due to other cluster starting the job.",
    ),
    Status("SI", "SIGNALING", "Job is being signaled."),
    Status(
        "SE",
        "SPECIAL_EXIT",
        "The job was requeued in a special state. This state can be set by users, typically in EpilogSlurmctld, if the job has terminated with a particular exit value.",
    ),
    Status("SO", "STAGE_OUT", "Job is staging out files."),
    Status(
        "ST",
        "STOPPED",
        "Job has an allocation, but execution has been stopped with SIGSTOP signal.  CPUS have been retained by this job.",
    ),
    Status(
        "S",
        "SUSPENDED",
        "Job has an allocation, but execution has been suspended and CPUs have been released for other jobs.",
        generic=STATUS_SUSPENDED,
    ),
    Status("TO", "TIMEOUT", "Job terminated upon reaching its time limit."),
]
