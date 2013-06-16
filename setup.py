# -*- coding: utf-8 -*-
#
# This file is part of Octopus released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import pkg_resources
from setuptools import find_packages, setup

version = pkg_resources.require('octopus')[0].version
packages = ['octopus'] + ['octopus.%s' % x for x in find_packages('octopus',)]

setup(
    name='Octopus',
    version=version,
    description='A wrapper for pygit2',
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    license='FreeBSD',
    keywords='git vcs',
    install_requires='pygit2',
    packages=packages,
    classifiers=[
        'Development Status :: %s' % version,
        'Environment :: Library',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: FreeBSD',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
