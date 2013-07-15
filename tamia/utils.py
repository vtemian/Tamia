# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from datetime import timedelta, tzinfo
import os.path


def clean_path(path):
    path = os.path.normpath(path)
    if path.startswith('/'):
        path = path[1:]

    return path


class TZ(tzinfo):
    def __init__(self, offset):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(minutes=self._offset)

    def tzname(self, dt):
        return dt.strftime('%z')

    def dst(self, dt):
        return timedelta(minutes=self._offset)
