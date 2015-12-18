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


import re
import sys
import os
import time

from anki.utils import json, stripHTMLMedia, fieldChecksum, intTime
from aqt import editor, mw
from anki.hooks import wrap
from anki.utils import isWin, isMac
import anki, aqt
from anki.hooks import addHook
from PyQt4 import QtGui, QtCore
import BeautifulSoup

import const
from utility import Utility
from preferences import Preferences
from menu import ExtraButtons_Options
from html2text import html2text
from markdowner import Markdowner
from anki_modules.aqt import editor as myeditor
from abbreviation import Abbreviation
from orderedlist import OrderedList
from hyperlink import Hyperlink
from hyperlink import Hyperlink2
from deflist import DefList
from table import Table
from blockquote import Blockquote
from heading import Heading

# Overrides
##################################################
editor.Editor.onHtmlEdit = myeditor.onHtmlEdit

# Buttons
##################################################

def setup_buttons(self):

    if preferences.prefs.get(const.CODE):
        shortcut = preferences.get_keybinding(const.CODE)
        b = self._addButton(const.CODE, lambda: self.wrap_in_tags("code",
            preferences.prefs.get(const.CODE_CLASS)), _(shortcut),
            _("Code format text ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.CODE)

    if preferences.prefs.get(const.UNORDERED_LIST):
        shortcut = preferences.get_keybinding(const.UNORDERED_LIST)
        b = self._addButton(const.UNORDERED_LIST, self.toggleUnorderedList,
            _(shortcut), _("Create unordered list ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.UNORDERED_LIST)

    if preferences.prefs.get(const.ORDERED_LIST):
        shortcut = preferences.get_keybinding(const.ORDERED_LIST)
        b = self._addButton(const.ORDERED_LIST, self.toggleOrderedList, _(shortcut),
            _("Create ordered list ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.ORDERED_LIST)

    if preferences.prefs.get(const.STRIKETHROUGH):
        shortcut = preferences.get_keybinding(const.STRIKETHROUGH)
        b = self._addButton(const.STRIKETHROUGH, self.toggleStrikeThrough,
            _(shortcut), _("Strikethrough text ({})".format(shortcut)),
            check=True)
        Utility.set_icon(b, const.STRIKETHROUGH)

    # FIXME: think of better symbol to represent a <pre> block
    if preferences.prefs.get(const.PRE):
        shortcut = preferences.get_keybinding(const.PRE)
        b = self._addButton(const.PRE, lambda: self.wrap_in_tags("pre",
            preferences.prefs.get(const.CODE_CLASS)), _(shortcut),
            tip=_("Create a code block ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.PRE)

    if preferences.prefs.get(const.HORIZONTAL_RULE):
        shortcut = preferences.get_keybinding(const.HORIZONTAL_RULE)
        b = self._addButton(const.HORIZONTAL_RULE, self.toggleHorizontalLine,
                            _(shortcut),
            tip=_("Create a horizontal rule ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.HORIZONTAL_RULE)

    if preferences.prefs.get(const.INDENT):
        shortcut = preferences.get_keybinding(const.INDENT)
        b = self._addButton(const.INDENT, self.toggleIndent, _(shortcut),
            _("Indent text or list ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.INDENT)

    if preferences.prefs.get(const.OUTDENT):
        shortcut = preferences.get_keybinding(const.OUTDENT)
        b = self._addButton(const.OUTDENT, self.toggleOutdent, _(shortcut),
            _("Outdent text or list ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.OUTDENT)

    # FIXME: better symbol for <dl>
    if preferences.prefs.get(const.DEFINITION_LIST):
        shortcut = preferences.get_keybinding(const.DEFINITION_LIST)
        b = self._addButton(const.DEFINITION_LIST, self.toggleDefList, _(shortcut),
            _("Create definition list (shortcut)"), check=False)
        Utility.set_icon(b, const.DEFINITION_LIST)

    if preferences.prefs.get(const.TABLE):
        shortcut = preferences.get_keybinding(const.TABLE)
        b = self._addButton(const.TABLE, self.toggleTable, _(shortcut),
            _("Create a table ({})".format(shortcut)), check=False)
        Utility.set_icon(b, const.TABLE)

    if preferences.prefs.get(const.KEYBOARD):
        shortcut = preferences.get_keybinding(const.KEYBOARD)
        b = self._addButton(const.KEYBOARD, lambda: self.wrap_in_tags("kbd"),
            _(shortcut), _("Create a keyboard button ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.KEYBOARD)

    if preferences.prefs.get(const.HYPERLINK):
        shortcut = preferences.get_keybinding(const.HYPERLINK)
        b1 = self._addButton(const.HYPERLINK, self.toggleHyperlink, _(shortcut),
            _("Insert link ({})".format(shortcut)), check=False)
        Utility.set_icon(b1, const.HYPERLINK)

        shortcut = preferences.get_keybinding(const.REMOVE_HYPERLINK)
        b2 = self._addButton(const.REMOVE_HYPERLINK, self.unlink, _(shortcut),
            _("Unlink ({})".format(shortcut)), check=False)
        Utility.set_icon(b2, const.REMOVE_HYPERLINK)

    if preferences.prefs.get(const.HYPERLINK2):
        shortcut = preferences.get_keybinding(const.HYPERLINK2)
        b1 = self._addButton(const.HYPERLINK2, self.toggleHyperlink2, _(shortcut),
            _("Insert link2 ({})".format(shortcut)), check=False)
        Utility.set_icon(b1, const.HYPERLINK2)
        # No remove_hyperlink2 defined
        # shortcut = preferences.get_keybinding(const.REMOVE_HYPERLINK)
        # b2 = self._addButton(const.REMOVE_HYPERLINK, self.unlink, _(shortcut),
        #     _("Unlink ({})".format(shortcut)), check=False)
        # Utility.set_icon(b2, const.REMOVE_HYPERLINK)
        
    if preferences.prefs.get(const.BACKGROUND_COLOR):
        shortcut = preferences.get_keybinding(const.BACKGROUND_COLOR)
        b1 = self._addButton(const.BACKGROUND_COLOR, self.on_background, _(shortcut),
            _("Set background color ({})".format(shortcut)), text=" ")
        self.setup_background_button(b1)
        shortcut = preferences.get_keybinding(const.BACKGROUND_COLOR_CHANGE)
        b2 = self._addButton(const.BACKGROUND_COLOR_CHANGE,
                             self.on_change_col, _(shortcut),
                             _("Change color ({})".format(shortcut)),
                             text=u"▾")
        b2.setFixedWidth(12)

    if preferences.prefs.get(const.BLOCKQUOTE):
        shortcut = preferences.get_keybinding(const.BLOCKQUOTE)
        b = self._addButton(const.BLOCKQUOTE, self.toggleBlockquote,
            _(shortcut), _("Insert blockquote ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.BLOCKQUOTE)

    if preferences.prefs.get(const.TEXT_ALLIGN):
        shortcut = preferences.get_keybinding(const.TEXT_ALLIGN_FLUSH_LEFT)
        b1 = self._addButton(const.TEXT_ALLIGN_FLUSH_LEFT, self.justifyLeft,
        _(shortcut), _("Align text left ({})".format(shortcut)),
        check=False)
        Utility.set_icon(b1, const.TEXT_ALLIGN_FLUSH_LEFT)

        shortcut = preferences.get_keybinding(const.TEXT_ALLIGN_CENTERED)
        b2 = self._addButton(const.TEXT_ALLIGN_CENTERED, self.justifyCenter,
            _(shortcut), _("Align text center ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b2, const.TEXT_ALLIGN_CENTERED)

        shortcut = preferences.get_keybinding(const.TEXT_ALLIGN_FLUSH_RIGHT)
        b3 = self._addButton(const.TEXT_ALLIGN_FLUSH_RIGHT, self.justifyRight,
            _(shortcut), _("Align text right ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b3, const.TEXT_ALLIGN_FLUSH_RIGHT)

        shortcut = preferences.get_keybinding(const.TEXT_ALLIGN_JUSTIFIED)
        b4 = self._addButton(const.TEXT_ALLIGN_JUSTIFIED, self.justifyFull,
            _(shortcut), _("Justify text ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b4, const.TEXT_ALLIGN_JUSTIFIED)

    if preferences.prefs.get(const.HEADING):
        shortcut = preferences.get_keybinding(const.HEADING)
        b = self._addButton(const.HEADING, self.toggleHeading,
            _(shortcut), _("Insert heading ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.HEADING)

    if preferences.prefs.get(const.ABBREVIATION):
        shortcut = preferences.get_keybinding(const.ABBREVIATION)
        b = self._addButton(const.ABBREVIATION, self.toggleAbbreviation,
            _(shortcut), _("Insert abbreviation ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.ABBREVIATION)

    if preferences.prefs.get(const.MARKDOWN):
        shortcut = preferences.get_keybinding(const.MARKDOWN)
        b = self._addButton(const.MARKDOWN, self.toggleMarkdown,
            _(shortcut), _("Toggle Markdown ({})".format(shortcut)),
            check=False)
        Utility.set_icon(b, const.MARKDOWN)

def wrap_in_tags(self, tag, class_name=None):
    """Wrap selected text in a tag, optionally giving it a class."""
    selection = self.web.selectedText()

    if not selection:
        return

    selection = Utility.escape_html_chars(selection)

    tag_string_begin = ("<{0} class='{1}'>".format(tag, class_name) if
        class_name else "<{0}>".format(tag))
    tag_string_end = "</{0}>".format(tag)

    html = self.note.fields[self.currentField]

    if "<li><br /></li>" in html:
        # an empty list means trouble, because somehow Anki will also make the
        # line in which we want to put a <code> tag a list if we continue
        replacement = tag_string_begin + selection + tag_string_end
        self.web.eval("document.execCommand('insertHTML', false, %s);"
            % json.dumps(replacement))

        self.web.setFocus()
        self.web.eval("focusField(%d);" % self.currentField)
        self.saveNow()

        html_after = self.note.fields[self.currentField]

        if html_after != html:
            # you're in luck!
            return
        else:
            # nothing happened :( this is another Anki bug :( that has to do
            # with <code> tags following <div> tags
            return

    # Due to a bug in Anki or BeautifulSoup, we cannot use a simple
    # wrap operation like with <a>. So this is a very hackish way of making
    # sure that a <code> tag may precede or follow a <div> and that the tag
    # won't eat the character immediately preceding or following it
    pattern = "@%*!"
    len_p = len(pattern)

    # first, wrap the selection up in a pattern that the user is unlikely
    # to use in its own cards
    self.web.eval("wrap('{0}', '{1}')".format(pattern, pattern[::-1]))

    # focus the field, so that changes are saved
    # this causes the cursor to go to the end of the field
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)

    self.saveNow()

    html = self.note.fields[self.currentField]

    begin = html.find(pattern)
    end = html.find(pattern[::-1], begin)

    html = (html[:begin] + tag_string_begin + selection + tag_string_end +
            html[end+len_p:])

    # delete the current HTML and replace it by our new & improved one
    self.note.fields[self.currentField] = html

    # reload the note: this is needed on OS X, because it will otherwise
    # falsely show that the formatting of the element at the start of
    # the HTML has spread across the entire note
    self.loadNote()

    # focus the field, so that changes are saved
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)
    self.saveNow()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)

def unlink(self):
    self.web.eval("setFormat('unlink')")

def toggleUnorderedList(self):
    self.web.eval("""
        document.execCommand('insertUnorderedList');
        var ulElem = window.getSelection().focusNode.parentNode;
        if (ulElem.toString() !== "[object HTMLUListElement]") {
            ulElem = ulElem.parentNode;
        }
        ulElem.style.marginLeft = "20px";
        """
    )

def toggleOrderedList(self):
    if preferences.prefs["fixed_ol_type"]:
        ol = OrderedList(self, self.parentWindow, preferences, True)
    else:
        ol = OrderedList(self, self.parentWindow, preferences)

def toggleStrikeThrough(self):
    self.web.eval("setFormat('strikeThrough')")

def togglePre(self):
    self.web.eval("setFormat('formatBlock', 'pre')")

def toggleHorizontalLine(self):
    self.web.eval("setFormat('insertHorizontalRule')")

def toggleIndent(self):
    self.web.eval("setFormat('indent')")

def toggleOutdent(self):
    self.web.eval("setFormat('outdent')")

def toggleDefList(self):
    selection = self.web.selectedText()
    dl = DefList(self, self.parentWindow, selection if selection else None)

def toggleTable(self):
    selection = self.web.selectedText()
    table = Table(self, self.parentWindow, selection if selection else None)

def setup_background_button(self, but):
    self.background_frame = QtGui.QFrame()
    self.background_frame.setAutoFillBackground(True)
    self.background_frame.setFocusPolicy(QtCore.Qt.NoFocus)
    self.bg_color = preferences.prefs.get("last_bg_color", "#00f")
    self.on_bg_color_changed()
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(self.background_frame)
    hbox.setMargin(5)
    but.setLayout(hbox)

# use last background color
def on_background(self):
    self._wrap_with_bg_color(self.bg_color)

# choose new color
def on_change_col(self):
    new = QtGui.QColorDialog.getColor(QtGui.QColor(self.bg_color), None)
    # native dialog doesn't refocus us for some reason
    self.parentWindow.activateWindow()
    if new.isValid():
        self.bg_color = new.name()
        self.on_bg_color_changed()
        self._wrap_with_bg_color(self.bg_color)

def _update_background_button(self):
    self.background_frame.setPalette(QtGui.QPalette(QtGui.QColor(self.bg_color)))

def on_bg_color_changed(self):
    self._update_background_button()
    preferences.prefs["last_bg_color"] = self.bg_color
    preferences.save_prefs()

def _wrap_with_bg_color(self, color):
    """Wrap the selected text in an appropriate tag with a background color."""
    # On Linux, the standard 'hiliteColor' method works. On Windows and OSX
    # the formatting seems to get filtered out by Anki itself

    self.web.eval("""
        if (!setFormat('hiliteColor', '%s')) {
            setFormat('backcolor', '%s');
        }
        """ % (color, color))

    if isWin or isMac:
        # remove all Apple style classes thus enabling
        # text highlighting for other platforms besides Linux
        self.web.eval("""
        var matches = document.querySelectorAll(".Apple-style-span");
        for (var i = 0; i < matches.length; i++) {
            matches[i].removeAttribute("class");
        }
        """)

def power_remove_format(self):
    """Remove formatting from selected text."""
    # For Windows and OS X we need to override the standard removeFormat
    # method, because it currently doesn't work as it should in (Anki 2.0.31).
    # Specifically, the background-color <span> gives trouble. This method
    # should work fine in all but a few rare cases that are easily avoided,
    # such as a <pre> at the beginning of the HTML.

    selection = self.web.selectedText()

    # normal removeFormat method
    self.web.eval("setFormat('removeFormat');")

    self.web.eval("setFormat('selectAll')")
    complete_sel = self.web.selectedText()

    # if we have selected the complete card, we can remove more thoroughly
    if selection == complete_sel:
        self.remove_garbage()

    # deselect all text
    self.web.eval("window.getSelection().removeAllRanges();")

    # on Linux just refocus the field
    if not isWin and not isMac:
        # refocus on the field we're editing
        self.web.eval("focusField(%d);" % self.currentField)
        return

    # reload the note: this is needed on OS X and possibly Windows to
    # display in the editor that the markup is indeed gone
    self.loadNote()

    self.saveNow()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)

def remove_garbage(self):
    """Remove HTML that doesn't get deleted automatically."""
    self.saveNow()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)

    html = self.note.fields[self.currentField]
    soup = BeautifulSoup.BeautifulSoup(html)

    for tag in const.HEADING_TAGS + const.HTML_TAGS:
        for match in soup.findAll(tag):
            match.replaceWithChildren()

    self.note.fields[self.currentField] = unicode(soup)
    self.loadNote()

def toggleBlockquote(self):
    selected = self.web.selectedHtml()
    Blockquote(self, selected)

def justifyCenter(self):
    self.web.eval("setFormat('justifyCenter');")

def justifyLeft(self):
    self.web.eval("setFormat('justifyLeft');")

def justifyRight(self):
    self.web.eval("setFormat('justifyRight');")

def justifyFull(self):
    self.web.eval("setFormat('justifyFull');")

def toggleHeading(self):
    selected = self.web.selectedText()
    heading = Heading(self, self.parentWindow, selected)

def toggleAbbreviation(self):
    selected = self.web.selectedText()
    abbreviation = Abbreviation(self, self.parentWindow, selected)

def toggleHyperlink(self):
    selected = self.web.selectedText()
    hyperlink = Hyperlink(self, self.parentWindow, selected)

def toggleHyperlink2(self):
    selected = self.web.selectedText()
    hyperlink = Hyperlink2(self, self.parentWindow, selected)
    
def toggleMarkdown(self):
    Utility.start_safe_block(const.MARKDOWN_PREFS)
    self.saveNow()
    selected = self.web.selectedHtml()
    current_field = self.currentField
    html_field = self.note.fields[self.currentField]
    # if not isinstance(html_field, unicode):
    #     html_field = unicode(html_field)
    # if not isinstance(selected, unicode):
    #     selected = unicode(selected)
    if not html_field:
        html_field = u""
    if not selected:
        selected = u""
    markdowner = Markdowner(self, self.parentWindow, self.note,
                            html_field, current_field, selected)
    markdowner.apply_markdown()
    self.saveNow()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)
    Utility.end_safe_block(const.MARKDOWN_PREFS)

def on_focus_gained(self, note, field):
    tags = note.tags
    if const.MARKDOWN_PREFS.get("disable_buttons"):
        # disable all buttons except for the Markdown toggle
        self.disableButtons()
        markdown_button = self._buttons.get(const.MARKDOWN)
        if markdown_button:
            markdown_button.setEnabled(True)
    if const.MARKDOWN_PREFS.get("safe_block"):
        return
    if not const.MARKDOWN_PREFS.get("safe_block"):
        Utility.start_safe_block(const.MARKDOWN_PREFS)
        try:
            time.sleep(0.01)
            self.saveNow()
        except AttributeError as e:
            print e # TODO: log error
        html_field = note.fields[field]
        # if not isinstance(html_field, unicode):
        #     html_field = unicode(html_field)
        if not html_field:
            html_field = u""
        markdowner = Markdowner(self, self.parentWindow, note,
                                html_field, field, u"")
        markdowner.on_focus_gained()
        self.web.setFocus()
        self.web.eval("focusField(%d);" % self.currentField)
        note.tags = tags
        try:
            time.sleep(0.01)
            self.updateTags()
        except AttributeError as e:
            print e # TODO: log error
        Utility.end_safe_block(const.MARKDOWN_PREFS)

def init_hook(self, mw, widget, parentWindow, addMode=False):
    addHook("editFocusGained", self.on_focus_gained)

editor.Editor.on_focus_gained = on_focus_gained
editor.Editor.__init__ = wrap(editor.Editor.__init__, init_hook)

editor.Editor.toggleMarkdown = toggleMarkdown
editor.Editor.toggleHeading = toggleHeading
editor.Editor.toggleAbbreviation = toggleAbbreviation
editor.Editor.toggleHyperlink = toggleHyperlink
editor.Editor.toggleHyperlink2 = toggleHyperlink2
editor.Editor.remove_garbage = remove_garbage
editor.Editor.unlink = unlink
editor.Editor.justifyFull = justifyFull
editor.Editor.justifyRight = justifyRight
editor.Editor.justifyLeft = justifyLeft
editor.Editor.justifyCenter = justifyCenter
editor.Editor.toggleBlockquote = toggleBlockquote
editor.Editor.removeFormat = power_remove_format
editor.Editor.on_background = on_background
editor.Editor.setup_background_button = setup_background_button
editor.Editor.on_bg_color_changed = on_bg_color_changed
editor.Editor._update_background_button = _update_background_button
editor.Editor.on_change_col = on_change_col
editor.Editor._wrap_with_bg_color = _wrap_with_bg_color
editor.Editor.wrap_in_tags = wrap_in_tags
editor.Editor.toggleOrderedList = toggleOrderedList
editor.Editor.toggleUnorderedList = toggleUnorderedList
editor.Editor.toggleStrikeThrough = toggleStrikeThrough
editor.Editor.togglePre = togglePre
editor.Editor.toggleHorizontalLine = toggleHorizontalLine
editor.Editor.toggleIndent = toggleIndent
editor.Editor.toggleOutdent = toggleOutdent
editor.Editor.toggleDefList = toggleDefList
editor.Editor.toggleTable = toggleTable
editor.Editor.setupButtons = wrap(editor.Editor.setupButtons, setup_buttons)

preferences = Preferences(mw)
try:
    const.preferences
except AttributeError:
    const.preferences = preferences

mw.ExtraButtons_Options = ExtraButtons_Options(mw, preferences)
mw.ExtraButtons_Options.setup_extra_buttons_options()
