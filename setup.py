#!/usr/bin/env python
"""Setup."""
from setuptools import setup
import versioneer

setup(version=versioneer.get_version(), cmdclass=versioneer.get_cmdclass())
