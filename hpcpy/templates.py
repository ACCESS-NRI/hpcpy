"""Code for accessing templates installed to the data/templates folder."""

import sys

from hpcpy.constants import TEMPLATE_ROOT


def list_templates() -> list:
    """List all of the installed templates.

    Returns
    -------
    list
        List of paths with the sh extension in the template dir
    """
    return sorted(TEMPLATE_ROOT.glob("*.sh"))


# Automatically populate the module space with the installed templates.
for template_path in list_templates():
    template_name = str(template_path.name).replace(".sh", "").upper()
    setattr(sys.modules[__name__], template_name, template_path)
