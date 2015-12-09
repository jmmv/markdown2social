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

"""Implementation of a Markdown to Google+ converter."""

import collections
import htmlentitydefs
import re
import xml.etree.ElementTree as ET

import markdown
import markdown2social


# list(str).  Bullet types for unordered lists.  Each entry in this list is used
# as the first element of a list, and the position of the element in the list
# indicates the nesting level at which the bullet type is used.
_UNORDERED_BULLETS = ['#', '-', 'o']


# list(str).  Bullet types for unordered lists.  Each entry in this list is used
# as the first element of a list, and the position of the element in the list
# indicates the nesting level at which the bullet type is used.
_ORDERED_BULLETS = ['1', 'A', 'a']


def _replace_match(text, match, replacement):
    """Expands a regexp match in the text with its replacement.

    Args:
        text: str.  The text in which to perform the replacement.
        match: re.MatchObject.  A match object that applies to "text".
        replacement: str.  The string to replace the match with.

    Returns:
        (str, int).  The text with the substitution performed and the first
        position in the text after the replacement that was done.
    """
    new_text = text[:match.start()] + replacement + text[match.end():]
    new_start_pos = match.start() + len(replacement)
    return new_text, new_start_pos


def _replace_entities(text):
    """Replaces any HTML entities in the  text with their UTF-8 characters.

    Args:
        text: str.  The line of text to be processed.

    Returns:
        str.  The modified text with all HTML entities stripped.
    """
    pattern = re.compile(r'&(([A-Za-z]+)|#x([0-9]+)|#([0-9]+));')
    name_match_id = 2
    hex_match_id = 3
    dec_match_id = 4

    start_pos = 0
    while True:
        match = pattern.search(text, start_pos)
        if not match:
            break

        if match.group(name_match_id):
            name = match.group(name_match_id)
            if name in htmlentitydefs.name2codepoint:
                text, start_pos = _replace_match(
                    text, match, unichr(htmlentitydefs.name2codepoint[name]))
            else:
                markdown2social.LOGGER.warning('Ignoring unknown entity: %s',
                                               name)
                start_pos = match.end() + 1
        elif match.group(hex_match_id):
            codepoint = int(match.group(hex_match_id), 16)
            text, start_pos = _replace_match(text, match, unichr(codepoint))
        else:
            assert match.group(dec_match_id)
            codepoint = int(match.group(dec_match_id), 10)
            text, start_pos = _replace_match(text, match, unichr(codepoint))

    return text


def _flatten_text(text):
    """Flattens a text node.

    Args:
        text: str.  The raw contents of a text node.

    Returns:
        str.  The contents of the text node in a single line.
    """
    flattened = ' '.join(text.rstrip('\n').split('\n'))

    collapse_space = re.compile('[ \t]+')
    flattened = collapse_space.sub(' ', flattened)

    return flattened


class _Locator(collections.namedtuple('_Locator',
                                      'ancestors cardinality rank')):
    """Holds information for the location of an element within an etree.

    We need this auxiliary class because the elements in the standard xml.etree
    module do not carry ancestry information.  This prevents us from navigating
    "up the tree" when we need details about parents or siblings in order to
    perform formatting decisions.

    Fields:
        ancestors: list(str).  List of element tags to the current element.
        cardinality: int.  Number of siblings, including self.
        rank: int.  Rank within the element; zero-indexed.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a _Locator and validates preconditions."""
        super(_Locator, self).__init__(*args, **kwargs)
        assert self.rank < self.cardinality

    def is_last(self):
        """Returns true if this element is the last among its siblings."""
        return self.rank + 1 == self.cardinality


class _Formatter(object):
    """Formatting hooks for an etree element type.

    Subclasses may override any of the methods in this class to tune the
    behavior for different element types.
    """

    def format_text(self, unused_locator, element):
        """Formats the text attribute of an etree element.

        Args:
            unused_locator: _Locator.  Information about the position of the
                element in the etree.
            element: ET.ElementTree.  The element being processed.

        Returns:
            str.  The modified text.
        """
        return _flatten_text(element.text)

    def format_contents(self, unused_locator, unused_element, text):
        """Formats a piece of text based on the semantics of the element.

        Args:
            unused_locator: _Locator.  Information about the position of the
                element in the etree.
            unused_element: ET.ElementTree.  The element containing the expanded
                text in the text argument.
            text: str.  The element text plus the already-formatted children.

        Returns:
            str.  The modified text.
        """
        return text

    def format_tail(self, unused_locator, element):
        """Formats the tail attribute of an etree element.

        Args:
            unused_locator: _Locator.  Information about the position of the
                element in the etree.
            element: ET.ElementTree.  The element being processed.

        Returns:
            str.  The modified text.
        """
        return _flatten_text(element.tail)


class _Boldify(_Formatter):
    """Enables bold face on an element."""

    def format_contents(self, unused_locator, unused_element, text):
        """See docstring in parent class for details."""
        return '*%s*' % text


class _Emphasize(_Formatter):
    """Enables emphasis on an element."""

    def format_contents(self, unused_locator, unused_element, text):
        """See docstring in parent class for details."""
        return '_%s_' % text


class _MakeLink(_Formatter):
    """Adds a link to an element."""

    def format_contents(self, unused_locator, element, text):
        """See docstring in parent class for details."""
        link = ''
        for attribute, value in element.items():
            if attribute == 'href':
                link = value
        return '%s [%s]' % (text, link)


class _MakeList(_Formatter):
    """Adds a link to an element."""

    def format_contents(self, locator, unused_element, text):
        """See docstring in parent class for details."""
        if len(locator.ancestors) > 1:
            # We are starting a nested list so we must introduce a line break.
            # This is necessary because the nested list starts within a previous
            # <li> element which has not yet been closed.
            return '\n' + text
        else:
            return text


class _MakeListItem(_Formatter):
    """Adds a link to an element."""

    def format_contents(self, locator, unused_element, text):
        """See docstring in parent class for details."""
        list_tags = [tag for tag in locator.ancestors if tag in ['ol', 'ul']]
        indentation = ' ' * ((len(list_tags) - 1) * 4)

        bullet = None
        if list_tags[-1] == 'ul':
            level = len([tag for tag in list_tags if tag == 'ul'])
            bullet = _UNORDERED_BULLETS[(level - 1) % len(_UNORDERED_BULLETS)]
        else:
            level = len([tag for tag in list_tags if tag == 'ol'])
            bullet = chr(
                ord(_ORDERED_BULLETS[(level - 1) % len(_ORDERED_BULLETS)]) +
                locator.rank) + '.'
        assert bullet is not None

        if not locator.is_last():
            # We need to separate all intermediate <li> elements with a newline,
            # but not the last one.  The reason is that the last list element
            # will get its own newline either due to the start of a nested list
            # or due to it being at the end of a paragraph.
            text += '\n'

        return '%s*%s* %s' % (indentation, bullet, text)


class _PassText(_Formatter):
    """Lets a piece of text pass verbatim."""

    def __init__(self, warn_unknown):
        """Constructor.

        Args:
            warn_unknown: bool.  If true, emit a warning when the element being
                processed is unknown.  This often indicates a possibility in
                improving this converter.
        """
        self._warn_unknown = warn_unknown

    def format_contents(self, unused_locator, element, text):
        """See docstring in parent class for details."""
        if self._warn_unknown:
            markdown2social.LOGGER.warning('Unhandled element type: %s',
                                           element.tag)
        return text


class _Quote(_Formatter):
    """Quotes the contents with a unique delimiter."""

    def format_text(self, locator, element):
        """See docstring in parent class for details."""
        if 'pre' in locator.ancestors:
            return element.text
        else:
            return super(_Quote, self).format_text(locator, element)

    def format_contents(self, locator, unused_element, text):
        """See docstring in parent class for details."""
        if 'pre' in locator.ancestors:
            return text
        else:
            delimiter = '"'
            while delimiter in text:
                delimiter += delimiter[0]
            return '%s%s%s' % (delimiter, text, delimiter)

    def format_tail(self, locator, element):
        """See docstring in parent class for details."""
        if 'pre' in locator.ancestors:
            return element.tail
        else:
            return super(_Quote, self).format_tail(locator, element)


class _QuoteVerbatim(_Formatter):
    """Quotes the verbatim block."""

    def format_contents(self, unused_locator, unused_element, text):
        """See docstring in parent class for details."""
        return '----\n%s\n----' % text.rstrip('\n')


# dict(str, func(ET.Element, _Formatter)).
# Mapping of HTML element names to _Formatter objects for Google+ output.
_ELEMENTS = {
    'h1': _Boldify(),
    'h2': _Boldify(),
    'h3': _Emphasize(),
    'h4': _Emphasize(),
    'h5': _Emphasize(),
    'h6': _Emphasize(),

    'b': _Boldify(),
    'strong': _Boldify(),

    'em': _Emphasize(),
    'i': _Emphasize(),

    'a': _MakeLink(),

    'code': _Quote(),
    'tt': _Quote(),

    'pre': _QuoteVerbatim(),

    'li': _MakeListItem(),
    'ol': _MakeList(),
    'ul': _MakeList(),

    'p': _PassText(False),

    None: _PassText(True),
}


def _format_element(locator, element):
    """Formats an element of the document.

    An element, as defined by the Markdown library, is composed of a leading
    literal text, an optional ordered list of subelements, and an optional
    literal tail.

    Args:
        locator: _Locator.  Information about the position of the element in
            the etree.
        element: ET.Element.  An element in the tree.

    Returns:
        str.  A string representing the formatted element or None if there is
        nothing to output for this element.

    """
    formatter = _ELEMENTS.get(element.tag, _ELEMENTS[None])

    line = ''
    if element.text:
        line += formatter.format_text(locator, element)

    for i, item in enumerate(element):
        item_locator = _Locator(ancestors=locator.ancestors + [element.tag],
                                cardinality=len(element),
                                rank=i)
        item_line = _format_element(item_locator, item)

        # Add a space between items if necessary.  In particular, we must only
        # do this if neither the current line ends nor the item's line starts
        # with a newline character because otherwise we would end up with
        # trailing spaces.  This could happen because of the way we handle the
        # formatting of lists.
        if ((line and line[-1] not in ' \n\t') and
            (item_line and item_line[0] not in ' \n\t')):
            line += ' '
        line += item_line

    line = formatter.format_contents(locator, element, line)

    if element.tail:
        line += formatter.format_tail(locator, element)

    return line


class _Markdown(markdown.Markdown):
    """Custom Markdown parser to extend the output formats."""

    @classmethod
    def _format_gplus(cls, document):
        """Convert a Markdown document to a Google+ post.

        The root element of the document is special, and this is why we handle
        it directly here: we want each top-level element of the HTML tree to end
        up as a separate "paragraph" in the final Google+ post.  All other
        elements should be considered span-level and are handled in our
        recursive algorithm.

        Args:
            document: ET.ElementTree.

        Returns:
            str.  The textual Google+ post.

        """
        root = ET.ElementTree(document).getroot()

        paragraphs = []
        for element in root:
            paragraph = _format_element(
                _Locator(ancestors=[], cardinality=1, rank=0), element)
            if paragraph is not None:
                paragraphs.append(paragraph)
        return '\n\n'.join(paragraphs)

    def __init__(self, *args, **kwargs):
        """Constructor for a _Markdown object."""
        # Override the definition of possible formats in the parent class.  This
        # is a class attribute in the parent class and is queried in the
        # constructor, so we must override this before we call init.
        self.output_formats = {
            'gplus': self._format_gplus,
        }

        markdown.Markdown.__init__(self, *args, **kwargs)

        # We need to disable this to avoid confusing the markdown processor with
        # our plain-text output.
        self.stripTopLevelTags = False  # pylint: disable=invalid-name


def convert(raw_markdown):
    """Converts a Markdown document in raw form to a Google+ post.

    Args:
        raw_markdown: unicode.  The Markdown document in raw format.

    Returns:
        unicode.  The Google+ text ready to be pasted into the browser.
    """
    markdown_document = _Markdown(output_format='gplus')
    text = markdown_document.convert(raw_markdown) + '\n'

    # The markdown library does some strange extraction of HTML entities and
    # puts them aside until its postprocessing stage.  We cannot hook into the
    # process easily, which means we cannot process entities as part of the
    # conversion algorithm above.  Therefore, just expand entities afterwards.
    text = _replace_entities(text)

    return text
