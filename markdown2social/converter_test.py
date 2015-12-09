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

import codecs
import os
import unittest

from markdown2social import converter


class GoldenDataTest(unittest.TestCase):
    """Integration tests using external data files."""

    # Markers used in the data files to separate their various chunks.
    #
    # It is easier for human editing to keep all the parts in the same data file
    # than to split them into separate files.
    GPLUS_SEPARATOR = '---- gplus ----\n'
    MARKDOWN_SEPARATOR = '---- markdown ----\n'

    # List of known test data files.
    TESTDATA_FILES = [
        'code.txt',
        'complex.txt',
        'entities.txt',
        'headings.txt',
        'links.txt',
        'lists.txt',
        'one_paragraph.txt',
        'spacing.txt',
        'span_elements.txt',
        'utf8.txt',
    ]

    def setUp(self):
        self.testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')

        # Make unittest print the whole diff between the expected and the actual
        # value when we fail a test.
        self.maxDiff = None

    def _load_data_file(self, data_file):
        """Load a file from the testdata directory and split it into its parts.

        Args:
            data_file: str.  Basename of the file to be loaded.

        Returns:
            (str, str).  The first return value is the contents of the markdown
            document and the second return value is the contents of the gplus
            post.
        """
        markdown_lines = []
        gplus_lines = []

        self.assertIn(data_file, self.TESTDATA_FILES,
                      msg='TESTDATA_FILES is out of date')

        path = os.path.join(self.testdata_dir, data_file)
        with codecs.open(path, 'r', 'utf-8') as f:
            line = f.readline()
            self.assertEquals(
                self.MARKDOWN_SEPARATOR, line,
                msg='Data file does not start with markdown separator')
            for line in f:
                if line == self.GPLUS_SEPARATOR:
                    break
                markdown_lines.append(line)
            self.assertEquals(self.GPLUS_SEPARATOR, line,
                              msg='EOF reached and no gplus separator found')
            for line in f:
                gplus_lines.append(line)

        return ''.join(markdown_lines), ''.join(gplus_lines)

    def _test_one_file(self, data_file):
        """Tests the conversion of the data in a testdata file.

        Args:
            data_file: str.  Basename of the file to be loaded.
        """
        markdown, gplus = self._load_data_file(data_file)
        gplus_actual = converter.convert(markdown)
        self.assertListEqual(gplus.split('\n'), gplus_actual.split('\n'))

    def test_all_data_files_are_referenced(self):
        self.assertEquals(self.TESTDATA_FILES,
                          sorted(os.listdir(self.testdata_dir)))

    def test_code(self):
        self._test_one_file('code.txt')

    def test_complex(self):
        self._test_one_file('complex.txt')

    def test_entities(self):
        self._test_one_file('entities.txt')

    def test_headings(self):
        self._test_one_file('headings.txt')

    def test_links(self):
        self._test_one_file('links.txt')

    def test_lists(self):
        self._test_one_file('lists.txt')

    def test_one_paragraph(self):
        self._test_one_file('one_paragraph.txt')

    def test_spacing(self):
        self._test_one_file('spacing.txt')

    def test_span_elements(self):
        self._test_one_file('span_elements.txt')

    def test_utf8(self):
        self._test_one_file('utf8.txt')


if __name__ == '__main__':
    unittest.main()
