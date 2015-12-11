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

from setuptools import setup

package = {}
with open('markdown2social/package.py') as init_file:
    exec(init_file.read(), package)

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
    entry_points={
        'console_scripts': 'markdown2social=markdown2social.__main__:main',
    },

    install_requires=['Markdown'],

    test_suite='nose.collector',
    tests_require=['nose'],
)
