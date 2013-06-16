# -*- coding: utf-8 -*-
#
# This file is part of Octopus released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from setuptools import find_packages, setup

execfile('octopus/version.py')
packages = ['octopus'] + ['octopus.%s' % x for x in find_packages('octopus',)]

setup(
    name='Octopus',
    version=__version__,
    description='A wrapper for pygit2',
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    license='FreeBSD',
    keywords='git vcs',
    install_requires='pygit2',
    packages=packages,
    test_suite='test',
    classifiers=[
        'Development Status :: %s' % __version__,
        'Environment :: Library',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: FreeBSD',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
