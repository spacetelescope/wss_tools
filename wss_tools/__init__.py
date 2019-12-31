# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Python tools for JWST Wavefront Sensing Software.
"""

# Set up the version
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = 'unknown'

# UI
from . import utils  # noqa
from . import quip  # noqa
