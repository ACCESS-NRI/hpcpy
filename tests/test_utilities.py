"""Tests for utilities.py"""
import hpcpy.utilities as hu


def test_interpolate_string_template():
    assert hu.interpolate_string_template('hello {{arg}}', arg='world') == 'hello world'