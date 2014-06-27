# -*- coding: utf-8 -*-
#
# This file is part of Tamia released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import os

from setuptools import find_packages, setup
from setuptools.command.install import install


class Pygit2Install(install):
    def run(self):
        os.system("./install_pygit2.sh")
        install.run(self)


execfile('tamia/version.py')
packages = [b'tamia'] + [b'tamia.{0}'.format(x)
                         for x in find_packages(b'tamia',)]

setup(
    name='Tamia',
    version=__version__,
    description='A wrapper for pygit2',
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    url='https://github.com/olivier-m/Tamia',
    license='MIT License',
    keywords='git vcs libgit2',
    packages=[b'tamia'],
    test_suite='test',
    cmdclass={'install': Pygit2Install},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
)
