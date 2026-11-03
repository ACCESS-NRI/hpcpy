"""Tests for acquiring installed templates."""

import hpcpy.templates as ht
import hpcpy.utilities as hu


def test_list_templates():
    """Test that the template listing works."""
    templates = ht.list_templates()
    assert len(templates) > 0


def test_auto_population():
    """Test the path to a given template is correct and that the auto-population works."""
    result = ht.PAYU_SIMPLE
    expected = hu.get_installed_root() / "data" / "templates" / "payu_simple.j2"
    assert result == expected
