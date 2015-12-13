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

import unittest
import tempfile

from markdown2social import config


class ConfigTest(unittest.TestCase):
    """Unit tests for the _Config data type."""

    def test_public_fields(self):
        cfg = config._Config(replacements=[('first', 'second')])
        self.assertEquals([('first', 'second')], cfg.replacements)

    def test_defaults(self):
        cfg = config._Config.defaults()
        self.assertIsNone(cfg.replacements)


class LoadConfigTest(unittest.TestCase):
    """Unit tests for the load_config function."""

    def assert_config(self, cfg, replacements=None):
        """Ensures the parsed configuration matches expected values.

        Args:
            replacements: collection(tuple(str, str)).  If not None, the value
            to expect in cfg.replacements.
        """
        self.assertEquals(replacements or None, cfg.replacements)

    def test_missing_file(self):
        self.assertEquals(config._Config.defaults(),
                          config.load_config('/non-existent/missing-file'))

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            self.assertEquals(config._Config.defaults(),
                              config.load_config(tmp.name))

    def test_contents_error_when_parsing(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write('[]invalid-section')
            tmp.flush()
            self.assertRaises(config.ContentsError,
                              config.load_config, tmp.name)

    def test_some_replacements(self):
        replacements = [
            (r'(\A|\s)(magic/[0-9_-]+)', r'\1http://\2'),
            (r'^anchored', r'replaced'),
        ]

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write('[replacements]\n')
            for i, regex_subst_pair in enumerate(replacements):
                tmp.write('%d = %s -> %s\n' % (
                    i, regex_subst_pair[0], regex_subst_pair[1]))
            tmp.flush()

            self.assert_config(config.load_config(tmp.name),
                               replacements=replacements)

    def test_bad_replacement(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write('[replacements]\n')
            tmp.write('1 = foo -> bar\n')
            tmp.write('2 = invalid\n')
            tmp.write('3 = bar -> baz\n')
            tmp.flush()

            try:
                config.load_config(tmp.name)
                fail('ContentsError not raised')
            except config.ContentsError as e:
                self.assertIn('Bad replacement with name 2:', str(e))


if __name__ == '__main__':
    unittest.main()
