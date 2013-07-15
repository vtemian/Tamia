# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from tamia import Repository, NodeNotFound
from tamia.api import Revision

from .utils import BaseTestCase


class BareTestCase(BaseTestCase):
    TARFILE = 'barerepo.tar.gz'

    def setUp(self):
        super(BareTestCase, self).setUp()
        self.repo = Repository(self.REPO_PATH)

    def test_bare(self):
        self.assertTrue(self.repo.is_bare)

    def test_empty(self):
        self.assertFalse(self.repo.is_empty)

    def test_head(self):
        head = self.repo.get_revision()
        self.assertEqual(head.id, '543b6794d5ff8d031b3b4ea45f6917a2b2f61bf1')
        self.assertTrue(isinstance(head, Revision))

    def test_branches(self):
        self.assertEqual(self.repo.branches, ('master',))

    def test_tags(self):
        self.assertEqual(self.repo.tags, tuple())

    def test_history(self):
        h = self.repo.history()
        self.assertEqual([x.short_id for x in h], ['543b679', 'eb257a3'])

        h = self.repo.history(reverse=True)
        self.assertEqual([x.short_id for x in h], ['eb257a3', '543b679'])

    def test_nodes(self):
        node = self.repo.get_revision().node()

        self.assertEqual(node.basename, '')
        self.assertEqual(node.dirname, '')
        self.assertFalse(node.isfile())
        self.assertTrue(node.isdir())

        for i, n in enumerate(node.children()):
            pass

        self.assertEqual(i+1, 3)

        for i, n in enumerate(node.children(True)):
            pass

        self.assertEqual(i+1, 5)

class EmptyTestCase(BaseTestCase):
    TARFILE = 'emptyrepo.tar.gz'

    def setUp(self):
        super(EmptyTestCase, self).setUp()
        self.repo = Repository(self.REPO_PATH)

    def test_bare(self):
        self.assertFalse(self.repo.is_bare)

    def test_empty(self):
        self.assertTrue(self.repo.is_empty)


class IndexTestCase(BaseTestCase):
    TARFILE = 'testrepo.tar.gz'

    def setUp(self):
        super(IndexTestCase, self).setUp()
        self.repo = Repository(self.REPO_PATH)

