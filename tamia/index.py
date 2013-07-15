# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from heapq import heappush, heappop
import os.path

import pygit2

from .errors import NodeNotFound, RevisionNotFound, IdxError
from .utils import clean_path


class Index(object):
    def __init__(self, repository):
        self._repository = repository
        self._revision = None
        self._stash = {}
        self._contents = set()
        self._dirty = False

    def set_revision(self, revision):
        try:
            self._revision = self._repository.get_revision(revision)
        except RevisionNotFound as e:
            raise IdxError(e)

    def add(self, path, contents, mode=None):
        self._assert_revision()
        path = clean_path(path).encode('UTF-8')
        mode = int('0100{0}'.format(str(mode or '644')), 0)

        if isinstance(contents, unicode):
            contents = contents.encode('UTF-8')

        self._stash[path] = (pygit2.hash(contents), mode)
        self._contents.add(contents)

    def remove(self, path):
        self._assert_revision()
        path = clean_path(path).encode('UTF-8')

        self._stash[path] = (None, None)

    def commit(self, message, author_name, author_email, **kwargs):
        self._assert_revision()
        if self._dirty:
            raise IdxError('Index already commited')

        ref = kwargs.pop('ref', 'HEAD')
        commiter_name = kwargs.pop('commiter_name', author_name)
        commiter_email = kwargs.pop('commiter_email', author_email)
        parents = kwargs.pop('parents', [self._revision.id])

        author = pygit2.Signature(author_name, author_email)
        commiter = pygit2.Signature(commiter_name, commiter_email)

        # Sort index items
        items = self._stash.items()
        items.sort(key=lambda x: (x[1][0], x[0]))  # Sort by remove status then path

        # Create tree
        tree = IndexTree(self._revision)
        while len(items) > 0:
            path, (oid, mode) = items.pop(0)

            if oid is None:
                tree.remove(path)
            else:
                tree.add(path, oid, mode)

        oid = tree.write(self._contents)
        self._dirty = True

        try:
            self._repository._repo.create_commit(ref, author, commiter, message, oid, parents)
        finally:
            self._repository._set_refs()

    def _assert_revision(self):
        if self._revision is None:
            raise IdxError('No base revision')


class IndexHeap(object):
    def __init__(self):
        self._dict = {}
        self._heap = []

    def __len__(self):
        return len(self._dict)

    def get(self, path):
        return self._dict.get(path)

    def __setitem__(self, path, value):
        if path not in self._dict:
            n = -path.decode('UTF-8').count('/') if path else 1
            heappush(self._heap, (n, path))

        self._dict[path] = value

    def popitem(self):
        key = heappop(self._heap)
        path = key[1]
        return path, self._dict.pop(path)


class IndexTree(object):
    def __init__(self, revision):
        self._repository = revision._repository
        self._revision = revision
        self._builders = IndexHeap()
        self._builders[b''] = (None, self._repository._repo.TreeBuilder(self._revision._commit.tree))

    def get_builder(self, path):
        parts = path.split(os.path.sep)

        # Create builders if needed
        for i in range(len(parts)):
            _path = os.path.join(*parts[0:i+1])

            if self._builders.get(_path):
                continue

            args = []
            try:
                node = self._revision.node(_path.decode('UTF-8'))
                if node.isfile():
                    raise IdxError('Cannot create a tree builder. "{0}" is a file'.format(node.name))
                args.append(node._obj.oid)
            except NodeNotFound:
                pass

            self._builders[_path] = (os.path.dirname(_path), self._repository._repo.TreeBuilder(*args))

        return self._builders.get(path)[1]

    def add(self, path, oid, mode):
        builder = self.get_builder(os.path.dirname(path))
        builder.insert(os.path.basename(path), oid, mode)

    def remove(self, path):
        self._revision.node(path.decode('UTF-8'))  # Check if node exists
        builder = self.get_builder(os.path.dirname(path))
        builder.remove(os.path.basename(path))

    def write(self, contents=None):
        """
        Attach and writes all builders and return main builder oid
        """
        # Create trees
        while len(self._builders) > 0:
            path, (parent, builder) = self._builders.popitem()
            if parent is not None:
                oid = builder.write()
                builder.clear()
                self._builders.get(parent)[1].insert(os.path.basename(path), oid, pygit2.GIT_FILEMODE_TREE)

        oid = builder.write()
        builder.clear()

        # Create contents
        [self._repository._repo.create_blob(x) for x in contents or []]

        return oid
