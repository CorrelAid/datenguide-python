# -*- coding: utf-8 -*-
from datenguidepy.query_builder import Query  # noqa: F401
from datenguidepy.query_builder import Field  # noqa: F401
from datenguidepy.query_helper import get_regions  # noqa: F401
from datenguidepy.query_helper import get_statistics  # noqa: F401
from datenguidepy.query_helper import get_availability_summary  # noqa: F401

import os.path

"""Top-level package for Datenguide Python."""

version_fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
with open(version_fp) as version_file:
    version = version_file.readline().strip()

__author__ = """CorrelAid"""
__email__ = "packages@correlaid.org"
__version__ = version
