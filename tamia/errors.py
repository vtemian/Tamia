# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)


class TamiaError(Exception):
    pass


class RepositoryNotFound(TamiaError):
    pass


class NodeNotFound(TamiaError):
    pass


class RevisionNotFound(TamiaError):
    pass


class IdxError(TamiaError):
    pass
