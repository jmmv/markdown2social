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

"""Entry point to the markdown2social command-line utility."""

import codecs
import fileinput
import optparse
import sys

import markdown2social
from markdown2social import converter
from markdown2social import package


def main(args=None):
    """Program entry point.

    Args:
        args: list(str).  Optional list of arguments passed to the program.  If
        not provided, as is the case when invoked from the command-line, the
        arguments are read from sys.argv.

    Returns:
        int.  The exit code of the program.
    """
    parser = optparse.OptionParser(
        usage='%prog [options] [input-file1 .. [input-fileN]]',
        description=('%prog reads one or more Markdown documents and outputs '
                     'formats that are more amenable for sharing.  If no input '
                     'files are provided as arguments or if a lone "-" is '
                     'given, the Markdown content is read from stdin.  If no '
                     'output file is specified via --output_file, the output '
                     'is written to stdout.'),
        version='%prog ' + package.VERSION)
    parser.add_option('-o', '--output_file', dest='output_file', default=None,
                      help='File to write the output to; use stdout if empty')

    options, args = parser.parse_args(args)

    raw_markdown = ''
    try:
        for line in fileinput.input(args):
            raw_markdown += codecs.decode(line, 'utf-8')
    except IOError, e:
        sys.stderr.write('%s: error: %s\n' % (parser.get_prog_name(), e))
        return 1

    gplus = converter.convert(raw_markdown)

    if options.output_file:
        with codecs.open(options.output_file, 'w', 'utf-8') as output:
            output.write(gplus)
    else:
        sys.stdout.write(codecs.encode(gplus, 'utf-8'))

    return 0


if __name__ == '__main__':
    main()
