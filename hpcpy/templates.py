"""Code for accessing templates installed to the data/templates folder."""

import sys

from hpcpy.constants import TEMPLATE_ROOT


def list_templates() -> list:
    """List all of the installed templates.

    Returns
    -------
    list
        List of paths with the j2 extension in the template dir
    """
    return sorted(TEMPLATE_ROOT.glob("*.j2"))


# Automatically populate the module space with the installed templates.
for template_path in list_templates():
    template_name = str(template_path.name).replace(".j2", "").upper()
    setattr(sys.modules[__name__], template_name, template_path)
