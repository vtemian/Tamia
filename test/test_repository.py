# -*- coding: utf-8 -*-
from __future__ import (print_function, division, absolute_import, unicode_literals)

from octopus import Repository
from octopus.api import Revision

from .utils import BaseTestCase


class BareTestCase(BaseTestCase):
    TARFILE = 'barerepo.tar.gz'

    def setUp(self):
        self.repo = Repository(self.REPO_PATH)

    def test_bare(self):
        self.assertTrue(self.repo.is_bare)

    def test_empty(self):
        self.assertFalse(self.repo.is_empty)

    def test_head(self):
        head = self.repo.get_revision()
        self.assertEqual(head.id, '543b6794d5ff8d031b3b4ea45f6917a2b2f61bf1')
        self.assertTrue(isinstance(head, Revision))
