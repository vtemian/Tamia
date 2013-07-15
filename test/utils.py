# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import os.path
from shutil import rmtree
import tarfile
from tempfile import mkdtemp
from unittest import TestCase


class BaseTestCase(TestCase):
    TARFILE = None
    REPO_PATH = None

    def setUp(self):
        if self.TARFILE:
            repofile = os.path.join(os.path.dirname(__file__), 'data/%s' % self.TARFILE)
            if os.path.exists(repofile):
                self.REPO_PATH = mkdtemp()
                tar = tarfile.open(repofile)
                tar.extractall(self.REPO_PATH)
                tar.close()

    def tearDown(self):
        if self.REPO_PATH:
            rmtree(self.REPO_PATH)
