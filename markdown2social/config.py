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

"""Configuration file reader."""

import ConfigParser
import collections

import markdown2social


class Error(Exception):
    """Base class for exceptions raised by this module."""


class ContentsError(Error):
    """Error when processing the structure of the configuration file."""


class _Config(collections.namedtuple('_Config', 'replacements')):
    """High-level representation of the configuration file.

    Fields:
        replacements: collection(tuple(str, str)).  List of pairs representing
            a regular expression to match text and its corresponding
            replacement.  The replacement can use backreferences.
    """

    @classmethod
    def defaults(cls):
        """Returns a new configuration object with default settings."""
        return _Config(replacements=None)


def _parse_replacements(parser, section):
    """Parses the replacements section of the configuration file.

    Args:
        parser: ConfigParser.ConfigParser.  Open parser from which to read the
            section.
        section: str.  Name of the section from which to read the replacements.

    Returns:
        collection(tuple(str, str)).  List of pairs representing a regular
        expression to match text and its corresponding replacement.  The
        replacement can use backreferences.  None if there are no replacements.

    Raises:
        ContentsError: If any of the replacements is incorrectly specified.
    """

    replacements = []

    for key, value in parser.items(section, raw=True):
        fields = value.split(' -> ')
        if len(fields) != 2:
            raise ContentsError('Bad replacement with name %s: not of the form '
                                '"regex -> substitution"' % key)
        replacements.append(tuple(fields))

    return replacements or None


def load_config(path):
    """Reads a configuration file.

    Args:
        path: str.  Path to the configuration file to read.  The path is used
            verbatim, without the typical user expansion needed to load files
            from the home directory.

    Returns:
        Config.  The parsed configuration.

    Raises:
        ContentsError: If the user-provided configuration file is invalid.
    """
    parser = ConfigParser.ConfigParser()
    try:
        parser.read(path)
    except ConfigParser.Error as e:
        raise ContentsError(e)

    replacements = None
    for section in parser.sections():
        if section == 'replacements':
            assert replacements is None, 'Duplicate section'
            replacements = _parse_replacements(parser, section)
        else:
            markdown2social.LOGGER.warning('Ignoring unknown section %s '
                                           'in config file %s', section, path)
    return _Config(replacements=replacements)
