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
    TARFILE = 'barerepo.tar.gz'

    def setUp(self):
        super(IndexTestCase, self).setUp()
        self.repo = Repository(self.REPO_PATH)

    def test_add(self):
        index = self.repo.index('HEAD')
        index.add('test', 'Some content\n')
        index.add('woot/foo', 'coucou')
        index.add('woot/bar', 'toto')
        index.add('woot/toow/stuff', 'machin')

        index.commit('First commit', 'John Doe', 'john@example.net')

        self.assertEqual([x.message for x in self.repo.history()][0], 'First commit')
        self.assertEqual(self.repo.get_revision().node('test').name, 'test')

        # No exception
        self.repo.get_revision().node('woot/foo')
        self.repo.get_revision().node('woot/bar')
        self.repo.get_revision().node('woot/toow/stuff')

        index = self.repo.index('HEAD')
        index.remove('woot/toow/stuff')
        index.remove('woot/bar')
        index.remove('test')
        index.commit('Removed test', 'John Doe', 'john@example.net')

        self.assertEqual([x.message for x in self.repo.history()][0], 'Removed test')

        self.assertRaises(NodeNotFound, self.repo.get_revision().node, 'test')
        self.assertRaises(NodeNotFound, self.repo.get_revision().node, 'woot/toow/stuff')
        self.assertRaises(NodeNotFound, self.repo.get_revision().node, 'woot/bar')
        self.assertEqual(self.repo.get_revision().node('woot/foo').name, 'woot/foo')

        self.assertEqual(self.repo.get_revision('HEAD~1').node('test').name, 'test')

    def test_complex(self):
        index = self.repo.index('HEAD')
        index.add('test/accentué', 'Some content\n')
        index.commit('First commit accentué', 'John Doe', 'john@example.net')

        self.assertEqual([x.name for x in self.repo.get_revision('HEAD').node('test').children()],
            ['test/accentué']
        )

        index = self.repo.index('HEAD')
        index.add('test/accentué', 'Some content\ntesté\n')
        index.commit('Second commit €', 'John Doe', 'john@example.net')

        node = self.repo.get_revision().node('test/accentué')
        self.assertEqual(node.open().read(), 'Some content\ntesté\n'.encode('UTF-8'))

        self.assertEqual([x.message for x in self.repo.history()][1], 'First commit accentué')
        self.assertEqual([x.message for x in self.repo.history()][0], 'Second commit €')

        diff = self.repo.get_revision().node().diff('HEAD~1')
        self.assertEqual(diff.patch, 'diff --git c/test/accentué c/test/accentué\nindex 0ee3895..69997c2 100644\n--- c/test/accentué\n+++ c/test/accentué\n@@ -1 +1,2 @@\n Some content\n+testé\n')

        for patch in diff:
            self.assertEqual(patch.old_path, 'test/accentué')
            self.assertEqual(patch.new_path, 'test/accentué')
            for hunk in patch.hunks:
                self.assertEqual(hunk.old_start, 1)
                self.assertEqual(hunk.new_start, 1)
                self.assertEqual(hunk.lines, [(' ', 'Some content\n'), ('+', 'testé\n')])

        index = self.repo.index('HEAD')
        index.add('test/acc2é/acc3é', 'New content\n€\n')
        index.remove('test/accentué')
        index.add('test/acc-renamed', 'Some content\ntesté\n')
        index.commit('Third commit ö', 'John Doe', 'john@example.net')

        diff = self.repo.get_revision().node().diff('HEAD~1')
        self.assertEqual(len(list(diff)), 3)

        self.assertRaises(NodeNotFound, self.repo.get_revision().node, 'test/accentué')

        node = self.repo.get_revision().node('test/acc2é/acc3é')
        self.assertEqual(node.name, 'test/acc2é/acc3é')
        contents = node.open().read()
        self.assertEqual(contents, 'New content\n€\n'.encode('UTF-8'))

        h = list(self.repo.history())
        self.assertEqual(h[0].message, 'Third commit ö')
