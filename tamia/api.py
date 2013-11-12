# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from datetime import datetime
import os.path
from StringIO import StringIO

import pygit2

from .errors import RepositoryNotFound, NodeNotFound, RevisionNotFound
from .index import Index
from .utils import clean_path, TZ


class Repository(object):
    def __init__(self, repo_path, create=False, **kwargs):
        try:
            self._repo = pygit2.Repository(repo_path)
        except KeyError:
            if not create:
                raise RepositoryNotFound('Repository "{0}" does not exist'.format(repo_path))

            self._repo = pygit2.init_repository(repo_path, **kwargs)

        self.path = self._repo.path
        self.is_empty = self._repo.is_empty
        self.is_bare = self._repo.is_bare

        self._ref_map = {}
        self._set_refs()

    def __repr__(self):
        return b'<{0}: {1}>'.format(self.__class__.__name__, self.path.encode('UTF-8'))

    def _set_refs(self):
        self._ref_map = {}

        for r in self._repo.listall_references():
            if not r.startswith('refs'):
                continue

            parts = r.split('/', 2)
            if len(parts) != 3:
                continue

            parts.pop(0)
            reftype = parts[0]
            refname = parts[1]
            refid = self._repo.revparse_single(r).hex
            if refid not in self._ref_map:
                self._ref_map[refid] = {}

            if reftype not in self._ref_map[refid]:
                self._ref_map[refid][reftype] = []

            self._ref_map[refid][reftype].append(refname)

    @property
    def branches(self):
        return self._repo.listall_branches()

    @property
    def tags(self):
        return tuple([x[10:] for x in self._repo.listall_references() if x.startswith('refs/tags/')])

    def get_revision(self, revision=None):
        try:
            instance = self._repo.revparse_single(revision or 'HEAD')
        except KeyError:
            raise RevisionNotFound('Revision "{0}" does not exist'.format(revision))

        return Revision(self, instance)

    def history(self, revision=None, reverse=False):
        initial = self.get_revision(revision)._commit
        sort = reverse and pygit2.GIT_SORT_REVERSE or pygit2.GIT_SORT_TIME

        for instance in self._repo.walk(initial.oid, sort):
            yield Revision(self, instance)

    def diff(self, rev1, rev2):
        return self.get_revision(rev1).node().diff(rev2)

    def index(self, revision=None):
        index = Index(self)
        if revision:
            index.set_revision(revision)

        return index

    def __iter__(self):
        return self.history()


class Revision(object):
    def __init__(self, repository, commit):
        self._repository = repository
        self._commit = commit
        self.id = commit.hex
        self.short_id = self.id[:7]
        self.author = Signature(commit.author)
        self.committer = Signature(commit.committer)
        self.message = commit.message
        self.offset = self._commit.commit_time_offset
        self.date = datetime.fromtimestamp(self._commit.commit_time, TZ(self.offset))
        self._parents = None

        self.tags = self._repository._ref_map.get(commit.hex, {}).get('tags', [])
        self.branches = self._repository._ref_map.get(commit.hex, {}).get('heads', [])

    def __repr__(self):
        return b'<{0}: {1}>'.format(self.__class__.__name__, self.id)

    @property
    def parents(self):
        if self._parent is None:
            self._parents = [Revision(self._repository, x) for x in self._commit.parents]

        return self._parents

    def node(self, path=None):
        path = clean_path(path or '')

        return Node(self, path)


class Signature(object):
    def __init__(self, sig):
        self.name = sig.name
        self.email = sig.email
        self.offset = sig.offset
        self.date = datetime.fromtimestamp(sig.time, TZ(self.offset))

    def __unicode__(self):
        return '{name} <{email}> {date}{offset}'.format(**self.__dict__)

    def __repr__(self):
        return '<{0}> {1}'.format(self.__class__.__name__, self.name).encode('UTF-8')


class Node(object):
    DIR = 1
    FILE = 2

    def __init__(self, revision, path=None):
        self._revision = revision

        if path in (None, '', '.'):
            self._obj = revision._commit.tree
            self.name = ''
            self.type = self.DIR
        else:
            try:
                entry = revision._commit.tree[path]
            except KeyError:
                raise NodeNotFound('Node "{0}" does not exist'.format(path))
            self._obj = revision._repository._repo.get(entry.oid)
            self.name = path
            self.type = entry.filemode in (16384, 57344) and self.DIR or self.FILE

    def __unicode__(self):
        return self.name

    def __repr__(self):
        suffix = self.isdir() and '/' or ''
        return '<{0}: {1}{2}>'.format(self.__class__.__name__, self.name, suffix).encode('UTF-8')

    def isdir(self):
        return self.type == self.DIR

    def isfile(self):
        return self.type == self.FILE

    @property
    def dirname(self):
        return os.path.dirname(self.name)

    @property
    def basename(self):
        return os.path.basename(self.name)

    def children(self, recursive=False):
        obj = self._obj
        if isinstance(obj, pygit2.Tree):
            for entry in obj:
                dirname = self.isdir() and self.name or self.dirname
                node = Node(self._revision, os.path.join(dirname, entry.name.decode('UTF-8')))

                yield node
                if recursive and node.isdir() and node._obj is not None:
                    for x in node.children(recursive=True):
                        yield x

    def open(self):
        blob = self._obj
        if not isinstance(blob, pygit2.Blob):
            raise TypeError('Node if not a file')

        return FileBlob(blob)

    def history(self, revision=None):
        initial = self._revision._repository.get_revision(revision or self._revision.id)._commit
        walker = self._revision._repository._repo.walk(initial.oid, pygit2.GIT_SORT_TIME)

        last = None
        c0 = walker.next()
        try:
            e0 = c0.tree[self.name]
            last = c0
        except KeyError:
            e0 = None

        for c1 in walker:
            try:
                e1 = c1.tree[self.name]
                if e0 and e0.oid != e1.oid:
                    yield Revision(self._revision._repository, c0)
            except KeyError:
                e1 = None

            c0 = c1
            e0 = e1
            if e1:
                last = c1

        if last:
            yield Revision(self._revision._repository, last)

    def diff(self, revision):
        return Diff(self, revision)


class FileBlob(object):
    def __init__(self, blob):
        self._blob = blob
        self._data = None

    def _get_data(self):
        if not self._data:
            self._data = StringIO(self._blob.data)

        return self._data

    def read(self, size=None):
        return self._get_data().read(size)

    def write(self, data):
        return self._get_data().write(data)

    def close(self):
        self._data = None


class Diff(object):
    def __init__(self, node, revision, reversed=False):
        self._node = node
        self._t0 = node._revision._commit.tree

        self._rev = node._revision._repository.get_revision(revision)
        self._t1 = self._rev._commit.tree

        self._diff = None

    def __repr__(self):
        return '<{0}: {1}..{2}>'.format(self.__class__.__name__,
            self._node._revision.short_id,
            self._rev.short_id
        )

    def __iter__(self):
        if self._diff is None:
            self._init_diff()

        for f in self._files:
            yield f

    @property
    def patch(self):
        if self._diff is None:
            self._init_diff()

        return self._diff.patch

    def _init_diff(self):
        self._diff = self._t1.diff_to_tree(self._t0)

        files = {}

        for p in self._diff:
            if self._node.name and not (
                p.old_file_path.startswith(self._node.name.encode('UTF-8')) or
                p.new_file_path.startswith(self._node.name.encode('UTF-8'))
            ):
                continue

            _id = '%s@%s' % (p.old_file_path.decode('UTF-8'), p.new_file_path.decode('UTF-8'))
            if not _id in files:
                files[_id] = Patch(p)

            for h in p.hunks:
                files[_id].hunks.append(Hunk(h))

        self._files = files.values()


class Patch(object):
    def __init__(self, patch):
        self.old_path = patch.old_file_path.decode('UTF-8')
        self.new_path = patch.new_file_path.decode('UTF-8')
        self.hunks = []


class Hunk(object):
    def __init__(self, hunk):
        self.old_start = hunk.old_start
        self.new_start = hunk.new_start
        self.lines = hunk.lines
