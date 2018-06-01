# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Python tools for JWST Wavefront Sensing Software.
"""
import sys

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

# For egg_info test builds to pass, put package imports here.
if not _ASTROPY_SETUP_:
    from . import utils
    from . import quip


class UnsupportedPythonError(Exception):
    pass


# This is the same check as the one at the top of setup.py
__minimum_python_version__ = '3.5'
if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    raise UnsupportedPythonError("wss_tools does not support Python < {}".format(__minimum_python_version__))
