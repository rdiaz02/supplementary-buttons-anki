# -*- coding: utf-8 -*-
#
# Copyright 2014-2015 Stefan van den Akker <srvandenakker.dev@gmail.com>
#
# This file is part of Supplementary Buttons for Anki.
#
# Supplementary Buttons for Anki is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Supplementary Buttons for Anki is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with Supplementary Buttons for Anki. If not, see http://www.gnu.org/licenses/.

import string
import sys
import os
import re
import base64
import time
import HTMLParser

from PyQt4 import QtGui
import BeautifulSoup
from anki.utils import intTime, json, isWin, isMac

from html2text import html2text
import const

import markdown
from markdown.extensions import Extension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.smart_strong import SmartEmphasisExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.attr_list import AttrListExtension
from markdown.extensions.def_list import DefListExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.abbr import AbbrExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.admonition import AdmonitionExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.sane_lists import SaneListExtension

class Utility(object):
    """Utility class with all helper functions that are needed throughout
    the addon. All methods are static, and all fields are constants."""

    # Constants
    ##################################################

    const.PROGRAM_NAME  = "Supplementary Buttons for Anki"
    const.VERSION       = "0.8.1"
    const.YEAR_START    = 2014
    const.YEAR_LAST     = 2015
    const.ANKIWEB_URL   = "https://ankiweb.net/shared/info/162313389"
    const.GITHUB_URL    = "https://github.com/Neftas/supplementary-buttons-anki"
    const.EMAIL         = "srvandenakker.dev@gmail.com"
    const.FOLDER_NAME   = "extra_buttons"

    const.OPERATING_SYSTEMS = {
        "linux2": "Linux",
        "win32" : "Windows",
        "cygwin": "Windows",
        "darwin": "Mac OS X"
    }
    const.PLATFORM              = sys.platform

    # size of the dialog windows
    const.DIALOG_SIZE_X         = 350
    const.DIALOG_SIZE_Y         = 200
    const.MIN_COMBOBOX_WIDTH    = 140

    const.HTML_TAGS     = ("b", "i", "u", "span", "font", "sup", "sub",
                           "dl", "dt", "dd", "code", "s", "pre", "kbd",
                           "a", "strike", "blockquote", "abbr")

    const.HEADING_TAGS  = ("h1", "h2", "h3", "h4", "h5", "h6")

    const.CODE_AND_PRE_CLASS = "myCodeClass"

    # names of the buttons used for the keybindings
    const.CODE                          = "code"
    const.UNORDERED_LIST                = "unordered_list"
    const.ORDERED_LIST                  = "ordered_list"
    const.STRIKETHROUGH                 = "strikethrough"
    const.PRE                           = "pre"
    const.HORIZONTAL_RULE               = "horizontal_rule"
    const.INDENT                        = "indent"
    const.OUTDENT                       = "outdent"
    const.DEFINITION_LIST               = "definition_list"
    const.TABLE                         = "table"
    const.KEYBOARD                      = "keyboard"
    const.HYPERLINK                     = "hyperlink"
    const.HYPERLINK2                    = "hyperlink2"    
    const.REMOVE_HYPERLINK              = "remove_hyperlink"
    const.BACKGROUND_COLOR              = "background_color"
    const.BACKGROUND_COLOR_CHANGE       = "background_color_change"
    const.BLOCKQUOTE                    = "blockquote"
    const.TEXT_ALLIGN                   = "text_align"
    const.TEXT_ALLIGN_FLUSH_LEFT        = "text_align_flush_left"
    const.TEXT_ALLIGN_FLUSH_RIGHT       = "text_align_flush_right"
    const.TEXT_ALLIGN_JUSTIFIED         = "text_align_justified"
    const.TEXT_ALLIGN_CENTERED          = "text_align_centered"
    const.HEADING                       = "heading"
    const.ABBREVIATION                  = "abbreviation"
    const.MARKDOWN                      = "markdown"
    const.CODE_CLASS                    = "code_class"
    const.LAST_BG_COLOR                 = "last_bg_color"
    const.FIXED_OL_TYPE                 = "fixed_ol_type"
    const.MARKDOWN_SYNTAX_STYLE         = "markdown_syntax_style"
    const.MARKDOWN_LINE_NUMS            = "markdown_line_nums"
    const.MARKDOWN_CODE_DIRECTION       = "markdown_code_direction"
    const.MARKDOWN_ALWAYS_REVERT        = "markdown_always_revert"

    # constants for key sequence
    const.KEY_MODIFIERS                 = ("ctrl", "alt", "shift")
    const.KEY_MODIFIERS_MACOSX          = ("meta",)
    const.KEYS_SEQUENCE                 = tuple(string.ascii_lowercase) + \
                                          tuple(string.punctuation) + \
                                          tuple(string.digits)
    const.FUNCTION_KEYS                 = ("f1", "f2", "f3", "f4", "f5", "f6",
                                           "f7", "f8", "f9", "f10", "f11", "f12")

    # markers to be wrapped around Markdown data in fields
    const.START_HTML_MARKER             = "<!----SBAdata:"
    const.END_HTML_MARKER               = "---->"

    # change field to this background color
    const.MARKDOWN_BG_COLOR             = "#FFEDD3"

    # dictionary to store Markdown data
    const.MARKDOWN_PREFS                = dict(disable_buttons=False,
                                               safe_block=False,
                                               start_time=0.0,
                                               isconverted=None)

    # max number of bytes read from preference file
    const.MAX_BYTES_PREFS               = 32768

    # check if image present in Markdown
    const.IS_LINK_OR_IMG_REGEX = re.compile(r"!?\[[^\]]*\]\(.*?(?<!\\)\)")
    # to unescape image data
    const.HTML_PARSER                   = HTMLParser.HTMLParser()

    # Methods
    ##################################################

    @staticmethod
    def convert_html_to_markdown(org_html, keep_empty_lines=False):
        """
        Take a org_html string and return a Markdown string. Empty lines are
        removed from the result, unless `keep_empty_lines` is set to `True`.
        """
        if not org_html:
            return u""
        assert isinstance(org_html, unicode), "Input `org_html` is not Unicode"
        h = html2text.HTML2Text()
        h.body_width = 0
        md_text = h.handle(org_html)
        clean_md = u""
        if keep_empty_lines:
            clean_md = md_text
        else:
            # remove white lines
            for line in md_text.split(u"\n"):
                if line:
                    clean_md += (line + u"\n")

        # undo the html2text escaping of dots (which interferes
        # with the creation of ordered lists) and parentheses
        dot_regex = re.compile(ur"(\d+)\\(\.\s)")
        clean_md = re.sub(dot_regex, ur"\g<1>\g<2>", clean_md)

        left_paren_regex = re.compile(ur"\\\(")
        clean_md = Utility.replace_link_img_matches(left_paren_regex, u"&#40;", clean_md)
        right_paren_regex = re.compile(ur"\\\)")
        clean_md = Utility.replace_link_img_matches(right_paren_regex, u"&#41;", clean_md)
        whitespace_regex = re.compile(ur"\s+")
        clean_md = Utility.replace_link_img_matches(whitespace_regex, u"&#32;", clean_md)

        assert isinstance(clean_md, unicode)
        return clean_md

    @staticmethod
    def replace_link_img_matches(regex, new, s):
        """
        Escape characters in Markdown links and images that may break in
        regular HTML.
        >>> replace_link_img_matches(re.compile(ur"\s+"), u"&#32;", u"[](i .jpg)")
        u'[](i&#32;.jpg)
        """
        assert isinstance(s, unicode), "Input `s` is not Unicode"
        result = re.finditer(const.IS_LINK_OR_IMG_REGEX, s)
        if result:
            for match in result:
                str_to_be_replaced = match.group(0)
                start = s.find(str_to_be_replaced)
                end   = start + len(str_to_be_replaced)
                replacement = re.sub(regex, new, str_to_be_replaced)
                # put string back in original string
                str_start = s[:start]
                str_end = s[end:]
                s = str_start + replacement + str_end
        assert isinstance(s, unicode), "Result `s` is not Unicode"
        return s

    @staticmethod
    def convert_clean_md_to_html(md, put_breaks=False):
        """
        Convert a string containing Markdown syntax to a string with HTML that
        Anki expects.
        """
        assert isinstance(md, unicode), "Input `md` is not Unicode"
        result = u"<div>"
        location_last_nbsp = -999999999
        last_char = u""
        for index, char in enumerate(md):
            if char == u"\n":
                result += u"</div><div>"
            elif char == " ":
                if (index - location_last_nbsp) == 1:
                    result += char
                else:
                    if last_char == u"\n" or last_char in u" ":
                        result += u"&nbsp;"
                        location_last_nbsp = index
                    else:
                        result += char
            else:
                result += char
            last_char = char
        # remove last opening <div> tag
        if result.endswith(u"<div>"):
            result = result[:(len(result) - len(u"<div>"))]
        # or add a closing <div> tag
        else:
            result += u"</div>"

        # <div></div> needs to be a visible empty line
        if put_breaks:
            soup = BeautifulSoup.BeautifulSoup(result)
            for elem in soup.findAll(u"div"):
                if not elem.contents:
                    elem.append(BeautifulSoup.Tag(soup, u"br"))
            result = unicode(soup)
            soup = None

        # remove "empty" lines that consist solely of (non-breakable) spaces
        soup = BeautifulSoup.BeautifulSoup(result)
        for elem in soup.findAll("div"):
            if elem.string is not None:
                if all(x in ("&nbsp;", " ") for x in elem.string.split()):
                    elem.setString(BeautifulSoup.Tag(soup, "br"))
        result = unicode(soup)

        assert isinstance(result, unicode), "Result `result` is not Unicode"
        return result

    @staticmethod
    def convert_markdown_to_html(clean_md):
        assert isinstance(clean_md, unicode), "Input `clean_md` is not Unicode"
        new_html = markdown.markdown(clean_md, output_format="xhtml1",
            extensions=[
                SmartEmphasisExtension(),
                FencedCodeExtension(),
                FootnoteExtension(),
                AttrListExtension(),
                DefListExtension(),
                TableExtension(),
                AbbrExtension(),
                Nl2BrExtension(),
                CodeHiliteExtension(
                    noclasses=True,
                    pygments_style=const.preferences.prefs.get(const.MARKDOWN_SYNTAX_STYLE),
                    linenums=const.preferences.prefs.get(const.MARKDOWN_LINE_NUMS)),
                SaneListExtension()
            ], lazy_ol=False)
        assert isinstance(new_html, unicode)
        return new_html

    @staticmethod
    def is_same_html(html_one, html_two):
        """
        Return True when html_one is the same as html_two, False otherwise.
        """
        assert isinstance(html_one, unicode), "Input `html_one` is not Unicode"
        assert isinstance(html_two, unicode), "Input `html_two` is not Unicode"
        return html_one == html_two

    @staticmethod
    def is_same_markdown(md_one, md_two):
        """
        Return True when md_one is the same as md_two, False otherwise.
        """
        assert isinstance(md_one, unicode), "Input `md_one` is not Unicode"
        assert isinstance(md_two, unicode), "Input `md_two` is not Unicode"
        compare_one = Utility.remove_white_space(md_one)
        compare_two = Utility.remove_white_space(md_two)
        return compare_one == compare_two

    @staticmethod
    def is_same_text(text_one, text_two):
        """
        Return True when text_one is the same as text_two, False otherwise.
        """
        assert isinstance(text_one, unicode), "Input `text_one` is not Unicode"
        assert isinstance(text_two, unicode), "Input `text_two` is not Unicode"
        return text_one == text_two

    @staticmethod
    def remove_white_space(s):
        assert isinstance(s, unicode), "Input `s` is not Unicode"
        return u"".join(char for char in s if not char.isspace())

    @staticmethod
    def put_md_data_in_json_format(unique_id, isconverted, md):
        """
        Return a dictionary with information that is needed for the database.
        """
        assert isinstance(md, unicode), "Input `md` is not Unicode"
        return  {
                    "id": unique_id,
                    "isconverted": isconverted,
                    "md": md,
                    "lastmodified": intTime()
                }

    @staticmethod
    def merge_dicts(existing, new):
        """
        Merge two dictionaries. The values from `new` dictionary take
        precedence over the values from the `existing` dictionary where
        there are duplicate keys. Return a dictionary that contains the
        key-value pairs from both dicts.
        """
        return dict(existing.items() + new.items())

    @staticmethod
    def json_dump_and_compress(data):
        ret = unicode(base64.b64encode(json.dumps(data)))
        assert isinstance(ret, unicode), "Output `ret` is not Unicode"
        return ret

    @staticmethod
    def decompress_and_json_load(data):
        if not data:
            return u""
        assert isinstance(data, unicode), "Input `data` is not Unicode"
        try:
            b64data = base64.b64decode(data)
        except (TypeError, UnicodeEncodeError) as e:
            # `data` is not a valid base64-encoded string
            print e # TODO: should be logged
            return "corrupted"

        try:
            ret = json.loads(b64data)
            return ret
        except ValueError as e:
            print e # TODO: should be logged
            return "corrupted"

    @staticmethod
    def wrap_string(at_start, a_string, at_end):
        """
        Return a string `a_string` that has the `at_start` string prepended and
        the `at_end` string appended to it.
        >>> wrap_string("a", "b", "c")
        'abc'
        """
        return at_start + a_string + at_end

    @staticmethod
    def append_data_to_string(html, wrapped_compr_data):
        """
        Return a string that contains compressed data at the end. The data
        is wrapped in a marker to signify it is data and not to be displayed
        in the field.
        """
        return html + wrapped_compr_data

    @staticmethod
    def make_data_ready_to_insert(unique_id, isconverted, md, html):
        md_dict = Utility.put_md_data_in_json_format(
                unique_id, isconverted, md)
        md_dict_compr = Utility.json_dump_and_compress(md_dict)
        wrapped_md_dict_compr = Utility.wrap_string(const.START_HTML_MARKER,
                                                    md_dict_compr,
                                                    const.END_HTML_MARKER)
        return Utility.append_data_to_string(html, wrapped_md_dict_compr)

    @staticmethod
    def get_md_data_from_string(html):
        """
        Read a string `html` and extract compressed Markdown data from it, if it is
        available. Return a dictionary that contains this data, otherwise
        return None.
        """
        if not html:
            return u""
        assert isinstance(html, unicode), "Input `html` is not Unicode"
        if not const.START_HTML_MARKER in html:
            return u""
        start = html.find(const.START_HTML_MARKER) + \
                len(const.START_HTML_MARKER)
        end = html.find(const.END_HTML_MARKER, start)
        if start == -1 or end == -1:
            return u""
        compr_str = html[start:end]
        return compr_str

    @staticmethod
    def counter(start=0, step=1):
        """
        Generator that creates infinite numbers.
        """
        num = start
        while True:
            yield num
            num += step

    @staticmethod
    def set_icon(button, name):
        """
        Define the path for the icon the corresponding button should have.
        """
        icon_path = os.path.join(const.preferences.get_addons_folder(),
            const.FOLDER_NAME, "icons", "{}.png".format(name))
        button.setIcon(QtGui.QIcon(icon_path))

    @staticmethod
    def escape_html_chars(s):
        """
        Escape HTML characters in a string. Return a safe string.
        >>> escape_html_chars(u"this&that")
        u'this&amp;that'
        """
        if not s:
            return u""

        assert isinstance(s, unicode), "Input `s` is not Unicode"

        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }

        result = u"".join(html_escape_table.get(c, c) for c in s)
        assert isinstance(result, unicode)
        return result

    @staticmethod
    def check_alignment(s):
        """
        Return the alignment of a table based on input `s`. If `s` not in the
        list, return the default value.
        >>> check_alignment(u":-")
        u'left'
        >>> check_alignment(u"random text")
        u'left'
        """
        assert isinstance(s, unicode), "Input is not Unicode"
        alignments = {u":-": u"left", u":-:": u"center", u"-:": u"right"}
        default = u"left"
        if not s in alignments:
            return default
        return alignments[s]

    @staticmethod
    def check_size_heading(s):
        """
        Determine by counting the number of leading hashes in the string the
        size of the heading. Return an int that is the length of the hashes.
        """
        assert isinstance(s, unicode), "Input is not Unicode"
        # HTML headers go from <h1> to <h6>
        regex = re.compile(ur"^(#{1,6})")
        s = s.strip()
        if s.startswith(u"#"):
            size_heading = len(regex.match(s).group(1))
            return size_heading
        else:
            return -1

    @staticmethod
    def strip_leading_whitespace(s):
        """
        Remove leading whitespace from a string `s`. Whitespace is defined as
        a space, a tab, linefeed, return, formfeed, vertical tab or a
        non-breakable space.
        """
        assert isinstance(s, unicode), "Input is not Unicode"
        if not s: return s
        while True:
            if any(s.startswith(c) for c in string.whitespace):
                s = s.lstrip()
            elif s.startswith(u"&nbsp;"):
                s = s.lstrip(u"&nbsp;")
            else:
                break
        return s

    @staticmethod
    def create_horizontal_rule():
        """
        Returns a QFrame that is a sunken, horizontal rule.
        """
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        frame.setFrameShadow(QtGui.QFrame.Sunken)
        return frame

    @staticmethod
    def normalize_user_prefs(default_prefs, user_prefs):
        """
        Check if the user preferences are compatible with the currently
        used preferences within the addon. Add keys if they don't exist, and
        remove those that are not recognized.
        >>> default_prefs   = dict(b="two")
        >>> user_prefs      = dict(a="one")
        >>> normalize_user_prefs(default_prefs, user_prefs)
        {u'b': u'two'}
        """
        result_dict = user_prefs
        # add items that are not in prefs, but should be (e.g. after update)
        for key, value in default_prefs.iteritems():
            user_val = user_prefs.get(key)
            if user_val is None:
                result_dict[key] = value
        # delete items in prefs that should not be there (e.g. after update)
        for key in user_prefs.keys()[:]:
            if default_prefs.get(key) is None:
                del result_dict[key]

        return result_dict

    @staticmethod
    def split_string(text, splitlist):
        """
        Change all separators defined in a string `splitlist` to the first
        separator in `splitlist` and then split the text on that one separator.
        Return a list with the original string if `splitlist` is the empty string
        or `None`. Return a list of strings, with no empty strings in it.
        >>> splitlist = u"@#$"
        >>> s = u"one@two#three$"
        >>> split_string(s, splitlist)
        [u'one', u'two', u'three']
        """
        assert isinstance(text, unicode), "Input `text` is not Unicode"
        assert isinstance(splitlist, unicode), "Input `splitlist` is not Unicode"
        if not splitlist:
            return [text]
        for sep in splitlist:
            text = text.replace(sep, splitlist[0])
        return [x for x in text.split(splitlist[0]) if x]

    @staticmethod
    def validate_key_sequence(sequence, platform=u""):
        """
        Check a string that contains a key sequence and determine whether it
        fulfills the key sequence contract: one non-modifier key, and optionaly
        one or more modifier keys. Return a prettified key sequence when the
        key sequence is valid, or else an empty string.
        >>> validate_key_sequence(u"Alt-ctrl-Q")
        u'ctrl+alt+q'
        """
        if not sequence:
            return u""
        assert isinstance(sequence, unicode), "Input `sequence` not in Unicode"
        modkeys = const.KEY_MODIFIERS
        # Mac OS X has a special modifier, the Cmd key
        if isMac or platform == "darwin":
            modkeys += const.KEY_MODIFIERS_MACOSX
        sequence = sequence.lower()
        # the plus and minus signs can also be part of the key sequence
        # not just serve as delimiters
        if any(sequence.endswith(c) for c in u"+-"):
            parts = Utility.split_string(sequence[:-1], u"+-")
            parts += list(sequence[-1:])
        else:
            parts = Utility.split_string(sequence, u"+-")
        parts = Utility.filter_duplicates(parts)
        # sequence can only contain one function key and cannot be used
        # in combination with a character key
        function_key_found = False
        char_key_found = False
        for word in parts:
            if word in const.KEYS_SEQUENCE:
                # f12+a
                if function_key_found:
                    return u""
                char_key_found = True
            if word in const.FUNCTION_KEYS:
                # f12+f11 or a+f12
                if function_key_found or char_key_found:
                    return u""
                function_key_found = True
        # sequence should contain at least one non-modifier key
        if all(word in modkeys for word in parts):
            return u""
        for word in parts:
            # unknown modifiers or non-modifiers are not allowed
            if not word in modkeys + const.KEYS_SEQUENCE + const.FUNCTION_KEYS:
                return u""
        return Utility.create_pretty_sequence(parts)

    @staticmethod
    def filter_duplicates(sequence):
        """
        Return a list of elements without duplicates. The order of the
        original collection may be changed in the returned list.
        """
        if not sequence: return list()
        return list(set(sequence))

    @staticmethod
    def create_pretty_sequence(sequence):
        """
        Return an ordered string created from a key sequence that contains
        modifier and non-modifier keys. The returned order is ctrl, meta, shift,
        alt, non-modifier.
        """
        if not sequence: return ""
        seq = sequence[:]
        pretty_sequence = list()
        if "ctrl" in sequence:
            seq.remove("ctrl")
            pretty_sequence.append("ctrl")
        if "meta" in sequence:
            seq.remove("meta")
            pretty_sequence.append("meta")
        if "shift" in sequence:
            seq.remove("shift")
            pretty_sequence.append("shift")
        if "alt" in sequence:
            seq.remove("alt")
            pretty_sequence.append("alt")
        pretty_sequence += seq
        return "+".join(x for x in pretty_sequence if x)

    @staticmethod
    def check_user_keybindings(default_keybindings, user_keybindings, platform=u""):
        """
        Check the correctness of the user keybindings. If not correct, the
        default binding will be used instead. Return a checked dictionary of
        valid keybindings.
        """
        validated_keybindings = dict()
        for key, value in user_keybindings.iteritems():
            assert isinstance(key, unicode), "Key `{!r}` is not Unicode".format(key)
            assert isinstance(value, unicode), "Value `{!r}` is not Unicode".format(value)
            val_binding = Utility.validate_key_sequence(value, platform)
            if not val_binding:
                validated_keybindings[key] = default_keybindings.get(key)
            else:
                validated_keybindings[key] = val_binding
        return validated_keybindings

    @staticmethod
    def unescape_html(html):
        return const.HTML_PARSER.unescape(html)

    @staticmethod
    def start_safe_block(hashmap):
        """
        Mark the start of a safe block for the onFocus event.
        """
        if not all(key in hashmap for key in (u"start_time", u"safe_block")):
            return None
        hashmap[u"safe_block"] = True
        hashmap[u"start_time"] = time.time()

    @staticmethod
    def end_safe_block(hashmap):
        """
        Mark the end of a safe block for the onFocus event.
        """
        if not all(key in hashmap for key in (u"start_time", u"safe_block")):
            return None
        hashmap[u"safe_block"] = False

    @staticmethod
    def remove_whitespace_before_abbreviation_definition(md):
        """
        Remove the two leading spaces that are put by `html2text` when it
        translates an HTML abbreviation to Markdown.
        """
        if not md:
            return md
        assert isinstance(md, unicode), "Input `md` is not Unicode"
        regex = re.compile(r"( |\&nbsp;)+(\*\[.*?\]:)")
        return re.sub(regex, r"\2", md)

    @staticmethod
    def remove_leading_whitespace_from_dd_element(md, add_newline=False):
        """
        Change the input `md` to make sure it will transform to the correct HTML.
        """
        if not md:
            return md
        assert isinstance(md, unicode), "Input `md` is not Unicode"
        markdown = md
        regex = re.compile(r"(\n) {4}(: .*?\n)")
        result = re.findall(regex, markdown)
        replacement = r"\1\2\n" if add_newline else r"\1\2"
        markdown = re.sub(regex, replacement, markdown, count=(len(result)-1))
        markdown = re.sub(regex, r"\1\2", markdown)
        return markdown

    @staticmethod
    def put_colons_in_html_def_list(html):
        """
        Insert colons as the first child of a `<dd>` tag.
        """
        assert isinstance(html, unicode), "Input `html` is not Unicode"
        if not html:
            return html
        soup = BeautifulSoup.BeautifulSoup(html)
        dds = soup.findAll(name="dd")
        for dd in dds:
            # catch rare cases when `<dd>` is defined, but `<dt>` not
            prevSib = dd.previousSibling
            while unicode(prevSib) == u"\n":
                prevSib = prevSib.previousSibling
            if (prevSib is None or prevSib.name != u"dt"):
                continue
            dd.insert(0, u": ")
        return unicode(soup)
