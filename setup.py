# -*- coding: utf-8 -*-
#
# This file is part of Octopus released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from setuptools import find_packages, setup

execfile('octopus/version.py')
packages = [b'octopus'] + [b'octopus.{0}'.format(x) for x in find_packages(b'octopus',)]

setup(
    name='Octopus',
    version=__version__,
    description='A wrapper for pygit2',
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    license='MIT License',
    keywords='git vcs libgit2',
    install_requires='pygit2',
    packages=[b'octopus'],
    test_suite='test',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Library',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
)
