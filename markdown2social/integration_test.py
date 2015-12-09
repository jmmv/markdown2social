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

"""Integration tests for the main program."""

import codecs
import os
import StringIO
import sys
import tempfile
import unittest

from markdown2social import __main__


class MainTest(unittest.TestCase):
    """Integration tests for the main program."""

    TEST_INPUT = '# This is my post\n\nAnd a paragraph!\n'
    TEST_OUTPUT = '*This is my post*\n\nAnd a paragraph!\n'
    TEST_UTF8 = 'A string %s with Unicode in it\n' % unichr(0x2014)

    def _run(self, args=None, stdin=None, stdout=None, stderr=None,
             expected_exit_code=0):
        """Runs the main method with stream redirection.

        Args:
            args: list(str).  Optional arguments to pass to main.  The program
                name is automatically included.
            stdin: file.  Stream to feed as stdin.  If not provided, an empty
                StringIO object is supplied.
            stdout: file.  Stream to feed as stdout.  If not provided, an empty
                StringIO is provided and returned to the caller.
            stderr: file.  Stream to feed as stderr.  If not provided, an empty
                StringIO is provided and returned to the caller.
            expected_exit_code: int.  The expected return value of main.

        Returns:
            (file, file).  The stdout and stderr fed to the main process.  These
            will match the input stdout and stderr parameters if those were
            None, and otherwise will point at StringIO objects created by this
            function.
        """
        fake_stdin = stdin or StringIO.StringIO()
        fake_stdout = stdout or StringIO.StringIO()
        fake_stderr = stderr or StringIO.StringIO()

        real_stdin, real_stdout, real_stderr = sys.stdin, sys.stdout, sys.stderr
        try:
            sys.stdin, sys.stdout, sys.stderr = (
                fake_stdin, fake_stdout, fake_stderr)
            exit_code = __main__.main(args or [])
        finally:
            sys.stdin, sys.stdout, sys.stderr = (
                real_stdin, real_stdout, real_stderr)

        self.assertEquals(expected_exit_code, exit_code)
        return fake_stdout, fake_stderr

    def test_use_as_filter(self):
        stdout, stderr = self._run(stdin=StringIO.StringIO(self.TEST_INPUT))
        self.assertEquals(self.TEST_OUTPUT, stdout.getvalue())
        self.assertEquals('', stderr.getvalue())

    def test_use_as_filter__dash_argument(self):
        stdout, stderr = self._run(args=['-'],
                                   stdin=StringIO.StringIO(self.TEST_INPUT))
        self.assertEquals(self.TEST_OUTPUT, stdout.getvalue())
        self.assertEquals('', stderr.getvalue())

    def test_use_as_filter__utf8_in_memory(self):
        stdin = StringIO.StringIO()
        stdin.write(codecs.encode(self.TEST_UTF8, 'utf-8'))
        stdin.seek(0)
        stdout, stderr = self._run(stdin=stdin)
        self.assertEquals(self.TEST_UTF8,
                          codecs.decode(stdout.getvalue(), 'utf-8'))
        self.assertEquals('', stderr.getvalue())

    def test_use_as_filter__utf8_simulate_non_utf8_console(self):
        tempdir = tempfile.mkdtemp()
        input_name = os.path.join(tempdir, 'input')
        output_name = os.path.join(tempdir, 'output')
        try:
            with codecs.open(input_name, 'w', 'utf-8') as input_file:
                input_file.write(self.TEST_UTF8)

            with open(input_name, 'r') as input_file:
                with open(output_name, 'w') as output_file:
                    self._run(stdin=input_file, stdout=output_file)

            with codecs.open(output_name, 'r', 'utf-8') as output_file:
                self.assertEquals(self.TEST_UTF8, output_file.read())
        finally:
            for name in [output_name, input_name]:
                try:
                    os.remove(name)
                except OSError:
                    pass  # Might not have been created.
            os.rmdir(tempdir)

    def test_explicit_input(self):
        with tempfile.NamedTemporaryFile() as input_file:
            input_file.write(self.TEST_INPUT)
            input_file.seek(0)

            stdout, stderr = self._run(args=[input_file.name])
            self.assertEquals(self.TEST_OUTPUT, stdout.getvalue())
            self.assertEquals('', stderr.getvalue())

    def test_explicit_input__missing_file(self):
        stdout, stderr = self._run(args=['does-not-exist'],
                                   expected_exit_code=1)
        self.assertEquals('', stdout.getvalue())
        self.assertRegexpMatches(stderr.getvalue(), r'error.*does-not-exist')

    def test_explicit_output(self):
        with tempfile.NamedTemporaryFile() as output_file:
            stdout, stderr = self._run(args=['-o', output_file.name],
                                       stdin=StringIO.StringIO(self.TEST_INPUT))
            self.assertEquals('', stdout.getvalue())
            self.assertEquals('', stderr.getvalue())

            self.assertEquals(self.TEST_OUTPUT, output_file.read())

    def test_explicit_input_and_output(self):
        with tempfile.NamedTemporaryFile() as input_file:
            input_file.write(self.TEST_INPUT)
            input_file.seek(0)

            with tempfile.NamedTemporaryFile() as output_file:
                stdout, stderr = self._run(
                    args=['--output_file=%s' % output_file.name,
                          input_file.name])
                self.assertEquals('', stdout.getvalue())
                self.assertEquals('', stderr.getvalue())

                self.assertEquals(self.TEST_OUTPUT, output_file.read())

    def test_explicit_input_and_output__utf8(self):
        with tempfile.NamedTemporaryFile() as input_file:
            input_file.write(codecs.encode(self.TEST_UTF8, 'utf-8'))
            input_file.seek(0)

            with tempfile.NamedTemporaryFile() as output_file:
                unused_stdout, unused_stderr = self._run(
                    args=['-o', output_file.name, input_file.name])
                self.assertEquals(self.TEST_UTF8,
                                  codecs.decode(output_file.read(), 'utf-8'))


if __name__ == '__main__':
    unittest.main()
