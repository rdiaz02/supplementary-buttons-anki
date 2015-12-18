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

import os
import string
import copy
import base64
import codecs

from anki.utils import json, isWin, isMac

import const
from utility import Utility

class Preferences(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.prefs_path = os.path.join(self.get_addons_folder(),
                    const.FOLDER_NAME, ".extra_buttons_prefs")
        if isMac:
            self.keybindings_path = os.path.join(self.get_addons_folder(),
                    const.FOLDER_NAME, "keybindings_macosx.json")
        else:
            self.keybindings_path = os.path.join(self.get_addons_folder(),
                    const.FOLDER_NAME, "keybindings_linux_windows.json")

        # the default preferences that are used when no custom preferences
        # are found, or when the user preferences are corrupted
        self._default_conf = {
                const.CODE_CLASS:               const.CODE_AND_PRE_CLASS,
                const.LAST_BG_COLOR:            "#00f",
                const.FIXED_OL_TYPE:            "",
                const.MARKDOWN_SYNTAX_STYLE:    "tango",
                const.MARKDOWN_CODE_DIRECTION:  "left",
                const.MARKDOWN_LINE_NUMS:       False,
                const.MARKDOWN_ALWAYS_REVERT:   False,
                const.CODE:                     True,
                const.UNORDERED_LIST:           True,
                const.ORDERED_LIST:             True,
                const.STRIKETHROUGH:            True,
                const.PRE:                      True,
                const.HORIZONTAL_RULE:          True,
                const.INDENT:                   True,
                const.OUTDENT:                  True,
                const.DEFINITION_LIST:          True,
                const.TABLE:                    True,
                const.KEYBOARD:                 True,
                const.HYPERLINK:                True,
                const.HYPERLINK2:               True,            
                const.BACKGROUND_COLOR:         True,
                const.BLOCKQUOTE:               True,
                const.TEXT_ALLIGN:              True,
                const.HEADING:                  True,
                const.ABBREVIATION:             True,
                const.MARKDOWN:                 True
        }

        # the default keybindings that are used when no custom keybindings
        # are found, or when the user keybindings are corrupted
        self._default_keybindings_linux_windows = {
                const.CODE:                         u"ctrl+,",
                const.UNORDERED_LIST:               u"ctrl+[",
                const.ORDERED_LIST:                 u"ctrl+]",
                const.STRIKETHROUGH:                u"alt+shift+5",
                const.PRE:                          u"ctrl+.",
                const.HORIZONTAL_RULE:              u"ctrl+shift+alt+_",
                const.INDENT:                       u"ctrl+shift+]",
                const.OUTDENT:                      u"ctrl+shift+[",
                const.DEFINITION_LIST:              u"ctrl+shift+d",
                const.TABLE:                        u"ctrl+shift+3",
                const.KEYBOARD:                     u"ctrl+shift+k",
                const.HYPERLINK:                    u"ctrl+shift+h",
                const.HYPERLINK2:                   u"ctrl+shift+u",            
                const.REMOVE_HYPERLINK:             u"ctrl+shift+alt+h",
                const.BACKGROUND_COLOR:             u"ctrl+shift+b",
                const.BACKGROUND_COLOR_CHANGE:      u"ctrl+shift+n",
                const.BLOCKQUOTE:                   u"ctrl+shift+y",
                const.TEXT_ALLIGN_FLUSH_LEFT:       u"ctrl+shift+alt+l",
                const.TEXT_ALLIGN_FLUSH_RIGHT:      u"ctrl+shift+alt+r",
                const.TEXT_ALLIGN_JUSTIFIED:        u"ctrl+shift+alt+s",
                const.TEXT_ALLIGN_CENTERED:         u"ctrl+shift+alt+b",
                const.HEADING:                      u"ctrl+alt+1",
                const.ABBREVIATION:                 u"shift+alt+a",
                const.MARKDOWN:                     u"ctrl+shift+d"
        }
        # Mac OS Xbindings are the same as Linux/Windows bindings,
        # except for the following
        self._default_keybindings_macosx = \
                copy.deepcopy(self._default_keybindings_linux_windows)
        self._default_keybindings_macosx[const.CODE] = u"ctrl+shift+,"
        self._default_keybindings_macosx[const.PRE] = u"ctrl+shift+."

        self._default_keybindings = None
        if isMac:
            self._default_keybindings = self._default_keybindings_macosx
        else:
            self._default_keybindings = self._default_keybindings_linux_windows

        self.prefs = None
        self.keybindings = None

        # load the preferences
        try:
            with codecs.open(self.prefs_path, encoding="utf8") as f:
                encoded_prefs = f.read(const.MAX_BYTES_PREFS)
                decoded_prefs = base64.b64decode(encoded_prefs)
                self.prefs = json.loads(decoded_prefs)
        except:
            # file does not exist or is corrupted: fall back to default
            with codecs.open(self.prefs_path, "w", encoding="utf8") as f:
                self.prefs = self._default_conf
                json.dump(self.prefs, f)
        else:
            Utility.normalize_user_prefs(self._default_conf, self.prefs)
            self.save_prefs()

        # load the keybindings
        try:
            with codecs.open(self.keybindings_path, encoding="utf8") as f:
                # validate JSON
                result_json = u""
                for line in f:
                    line = line.strip()
                    if line == u"":
                        continue
                    # strip out comments from keybindings file
                    if line.startswith(u"//"):
                        continue
                    else:
                        result_json += line
                self.keybindings = json.loads(result_json)
        except (ValueError, IOError) as e:
            # file is missing or is not valid JSON: revert to default bindings
            # and create a keybindings file if it doesn't exist
            print e # TODO: log error
            self.keybindings = self._default_keybindings
            if not os.path.exists(self.keybindings_path):
                self.create_keybindings_file()
        else:
            # keybindings loaded from file should have exactly as many
            # key-value pairs as in the default keybindings
            self.keybindings = Utility.normalize_user_prefs(
                    self._default_keybindings, self.keybindings)
            self.keybindings = Utility.check_user_keybindings(
                    self._default_keybindings, self.keybindings, const.PLATFORM)

    def get_keybinding(self, name_of_key):
        """
        Return the keybinding indicated by `name_of_key`, and capitalize
        the name of each key before the delimiter `+`.
        """
        keybinding = self.keybindings.get(name_of_key, "")
        return string.capwords(keybinding, "+")

    def get_addons_folder(self):
        """
        Return the addon folder used by Anki.
        """
        return self.main_window.pm.addonFolder()

    def save_prefs(self):
        """
        Save the preferences to disk, encoded.
        """
        encoded_prefs = base64.b64encode(json.dumps(self.prefs))
        with codecs.open(self.prefs_path, "w", encoding="utf8") as f:
            f.write(encoded_prefs)

    def create_keybindings_file(self):
        """
        Create a default keybindings file with comments. This function is
        called when Supplementary Buttons for Anki cannot find an existing
        keybindings file. Override any changes made to an existing file.
        """

        contents = u"""\
// This file contains the keybindings that are used for Supplementary Buttons
// for Anki. Here you can assign new shortcuts. Please keep in mind that there
// is no check for duplicate keybindings. This means that when a keybinding is
// already taken by either your OS, Anki, this addon, or some other running
// program, the result is undefined.
//
// This file needs to contain valid JSON. Basically this means that
// the key-value pairs should be enclosed in double quotes:
// "key": "value"
// The opening and closing braces { and } are mandatory. Each key-value pair
// should contain a colon : and should end with a comma, except for the last
// pair.
//
// Invalid JSON cannot be parsed and will result in the use of the default
// keybindings. If you find that your new keybindings don't work (i.e. they
// don't show up in Anki, despite you changing this file), please use
// a JSON validator to check for faulty JSON.
//
// Modifier keys that can be used include: the function keys (F1 through F12),
// Ctrl, Alt, Shift, ASCII alphanumeric characters, and ASCII punctuation
// characters. For Mac OS X, be advised that Ctrl maps to the Cmd key (or
// "Apple key"), NOT to Ctrl. If you want to use the Ctrl modifier on Mac OS X,
// use Meta instead. So, Ctrl+Shift+[ on Linux or Windows maps to Meta+Shift+[
// on Mac OS X. Ctrl+Shift+[ on Mac OS X will require you to type Cmd+Shift+[
// in Anki. Please make sure you understand this before opening bug reports.
//
// The use of an invalid key sequence will silently revert the sequence to the
// default setting. For example, invalid sequences are:
// * only modifier keys: Ctrl+Shift
// * empty sequence
// * non-existing modifier keys: Ctrl+Iota+j
//
// The order or case of the keys is unimportant. Ctrl+Alt+p is the same as
// ALT+CTRL+P or even p+Ctrl+Alt.
//
// If you want to revert your changes to the default keybindings provided by
// Supplementary Buttons for Anki, please remove this JSON file in your addon
// folder.
{
"""
        for key, value in sorted(self.keybindings.iteritems()):
            contents += u"\"{}\": \"{}\",\n".format(key, value)
        contents += u"\"_version\": \"{}\"\n".format(const.VERSION)
        contents += u"}"

        try:
            with codecs.open(self.keybindings_path, "w", encoding="utf8") as f:
                f.write(contents)
        except IOError as e:
            raise e
