"""Common constants."""

from pathlib import Path

from hpcpy.utilities import get_installed_root

# Location for rendered job scripts
JOB_SCRIPT_DIR = Path.home() / ".hpcpy" / "job_scripts"

# Location of installed templates
TEMPLATE_ROOT = get_installed_root() / "data" / "templates"

# Generic Statuses (actually just PBS statuses, but used as a generic status)
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
