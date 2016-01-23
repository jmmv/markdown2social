#! /usr/bin/env python
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

import re
import sys

from distutils.cmd import Command
from distutils.core import setup

package = {}
with open('markdown2social/package.py') as init_file:
    exec(init_file.read(), package)


# Define a TestCommand command if and only if nose is present.
try:
    from nose.core import TestProgram
except ImportError:
    TestCommand = None
else:
    class TestCommand(Command):
        """setup.py command to run unit tests via nose."""

        description = 'run unit tests'
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            TestProgram(argv=[sys.argv[0], '--verbose'])


def read_requirements(requirements_txt):
    """Converts the contents of requirements.txt to requires stanzas.

    Args:
        requirements_txt: str.  The path to the requirements.txt file.

    Returns:
        list(str).  The list of requirements in the format accepted by the
        requires stanza of setup().

    Raises:
        ValueError: If any of the input lines in requirements.txt cannot be
            successfully parsed.
    """
    requires = []
    prog = re.compile('^([A-Za-z_-]+)(.*)$')
    with open(requirements_txt, 'r') as requirements:
        for line in requirements.readlines():
            match = prog.search(line.strip())
            if not match or len(match.groups()) != 2:
                raise ValueError('Invalid requirements entry %s' % line.strip())
            requires.append('%s(%s)' % (match.group(1), match.group(2)))
    return requires

setup(
    name='markdown2social',
    version=package['VERSION'],
    # TODO(jmmv): Should convert README.md to README.rst and bundle it into
    # the description, as recommended by the setuptools package.
    description='Converts Markdown documents to Google+ posts',
    url='https://github.com/jmmv/markdown2social',

    author='Julio Merino',
    author_email='jmmv@google.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Markup',
    ],
    keywords='markdown converter googleplus social',
    license='Apache',

    packages=['markdown2social'],
    scripts=['scripts/markdown2social'],

    requires=read_requirements('requirements.txt'),

    cmdclass={'test': TestCommand},

    data_files=[
        ('share/doc/markdown2social', [
            'AUTHORS',
            'CONTRIBUTING',
            'CONTRIBUTORS',
            'LICENSE',
            'NEWS.md',
            'README.md',
        ]),
        ('share/man/man1', [
            'scripts/markdown2social.1',
        ]),
        ('share/man/man5', [
            'scripts/markdown2social.conf.5',
        ]),
    ],
)
