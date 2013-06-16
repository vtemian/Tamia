# -*- coding: utf-8 -*-
from __future__ import (print_function, division, absolute_import, unicode_literals)

import os.path
from shutil import rmtree
import tarfile
from tempfile import mkdtemp
from unittest import TestCase


class BaseTestCase(TestCase):
    TARFILE = None
    REPO_PATH = None

    @classmethod
    def setUpClass(cls):
        if cls.TARFILE:
            repofile = os.path.join(os.path.dirname(__file__), 'data/%s' % cls.TARFILE)
            if os.path.exists(repofile):
                cls.REPO_PATH = mkdtemp()
                with tarfile.open(repofile) as tar:
                    tar.extractall(cls.REPO_PATH)

    @classmethod
    def tearDownClass(cls):
        if cls.REPO_PATH:
            rmtree(cls.REPO_PATH)
