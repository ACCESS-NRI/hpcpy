#!/usr/bin/env python
"""Setup."""

import versioneer
from setuptools import setup

setup(version=versioneer.get_version(), cmdclass=versioneer.get_cmdclass())
