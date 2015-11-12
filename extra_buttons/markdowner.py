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
import sqlite3

from anki.utils import json, intTime
from aqt import mw
from PyQt4 import QtGui
from anki.hooks import addHook

from utility import Utility
import const


class Markdowner(object):
    """
    Convert HTML to Markdown and the other way around. Store the data in a
    database. Revert to previous Markdown or overwrite the data when conflicts
    arise.
    """
    # signal that we don't want the onEdit focus behavior
    button_pressed = False

    def __init__(self, other, parent_window, note, html,
                 current_field, selected_html):
        self.editor_instance                = other
        self.parent_window                  = parent_window
        self.col                            = mw.col
        self.db                             = mw.col.db
        self.note                           = note
        self.html                           = html
        self.current_field                  = current_field
        self.selected_html                  = selected_html
        self.current_note_id_and_field      = str(self.note.id) + \
                                              "-{:03}".format(self.current_field)
        self._id                            = None
        self.isconverted                    = None
        self.md                             = None
        self._html                          = None
        self._lastmodified                  = None
        self.has_data                       = self.get_data_from_field()
        self.check_for_data_existence()
        const.MARKDOWN_PREFS["isconverted"] = self.isconverted

    def on_focus_gained(self):
        if self.isconverted:
            const.MARKDOWN_PREFS["disable_buttons"] = True
            self.warn_about_changes(self.editor_instance,
                                    self.current_field,
                                    const.MARKDOWN_BG_COLOR)
        else:
            const.MARKDOWN_PREFS["disable_buttons"] = False

    def current_field_exists_in_db(self):
        """
        Check if the current field exists in the database. Return True if
        it does, False otherwise.
        """
        sql = "select 1 from markdown where id=?"
        if self.db.first(sql, self.current_note_id_and_field):
            return True
        return False

    def check_for_data_existence(self):
        """
        Check if the data from the field also exists in the database. If it
        exists, but differs, update the database to reflect the changes.
        """
        if self.has_data and self.current_field_exists_in_db():
        # check timestamps and store if newer version
            timestamp_field = self._lastmodified
            timestamp_db = self.db.first("select mod from markdown where id=?",
                                         self.current_note_id_and_field)[0]
            print "timestamp db:", repr(timestamp_db)
            print "timestamp field:", repr(timestamp_field)
            print "field >= db:", timestamp_field >= timestamp_db
            assert timestamp_field >= timestamp_db, \
                    "field timestamp is older than db timestamp!"
            if timestamp_field > timestamp_db:
                self.store_new_markdown_version_in_db(
                    self.isconverted, self.md, self._html, self._lastmodified)

    def apply_markdown(self):
        # convert self.md to html; convert html to markdown; compare
        clean_md = Utility.convert_html_to_markdown(self.html)
        clean_md_escaped = Utility.escape_html_chars(clean_md)
        if not clean_md:
            return
        # check for changed Markdown between the database and the current text
        if (self.has_data and self.isconverted == "True"):
            # if self.selected_html:
            #     # only convert the selected text
            #     selected_clean_md = Utility.convert_html_to_markdown(
            #             self.selected_html)
            #     selected_new_html = Utility.convert_markdown_to_html(
            #             selected_clean_md)
            #     self.editor_instance.web.eval(
            #             "document.execCommand('insertHTML', false, %s);"
            #             % json.dumps(new_html))
            #     new_html = self.note.fields[self.current_field]
            #     self.store_new_markdown_version_in_db("True", new_html)
            #     return

            compare_md = Utility.convert_markdown_to_html(self.md)
            compare_md = Utility.convert_html_to_markdown(compare_md)
            compare_md_escaped = Utility.escape_html_chars(compare_md)
            if (Utility.is_same_markdown(clean_md_escaped, compare_md_escaped) or
                   const.preferences.prefs.get(const.MARKDOWN_ALWAYS_REVERT)):
                self.revert_to_stored_markdown()
            else:
                self.handle_conflict()
        else:
            new_html = Utility.convert_markdown_to_html(clean_md)
            html_with_data = Utility.make_data_ready_to_insert(
                    self.current_note_id_and_field, "True",
                    clean_md_escaped, new_html)
            self.insert_markup_in_field(
                    html_with_data, self.editor_instance.currentField)
            self.left_align_elements()
            # store the Markdown so we can reuse it when the button gets toggled
            self.store_new_markdown_version_in_db(
                    "True", clean_md_escaped, new_html)
            const.MARKDOWN_PREFS["disable_buttons"] = True
            self.warn_about_changes(self.editor_instance,
                                    self.current_field,
                                    const.MARKDOWN_BG_COLOR)

    def get_data_from_db(self):
        """
        Fill a variable with information from the database, if any.
        Return True when data is retrieved, False if the result set is empty.
        """
        sql = "select * from markdown where id=?"
        resultset = self.db.first(sql, self.current_note_id_and_field)
        print "DATA WE GOT BACK FROM DB:", resultset
        if resultset:
            (self._id,
             self.isconverted,
             self.md,
             self._html,
             self._lastmodified) = resultset
            return True
        return False

    def get_data_from_field(self):
        """
        Get the HTML from the current field and try to extract Markdown data
        from it. The side effect of calling this function is that several
        instance variables get set. Return True when data was found in the
        field, False otherwise.
        """
        md_dict = Utility.get_md_data_from_string(self.html)
        if md_dict and md_dict == "corrupted":
            print "MD_DICT CORRUPTED!!!"
            # TODO: fallback when JSON is corrupted
            pass
        elif md_dict:
            self._id            = md_dict.get("id")
            self.md             = md_dict.get("md")
            self._html          = md_dict.get("html")
            self.isconverted    = md_dict.get("isconverted")
            self._lastmodified  = md_dict.get("lastmodified")
            print "DATA FROM FIELD:\n{!r}\n{!r}\n{!r}\n{!r}".format(
                    self.md, self._html, self.isconverted, self._lastmodified)
            return True
        return False

    def insert_markup_in_field(self, markup, field):
        """
        Put markup in the specified field.
        """
        self.editor_instance.web.eval("""
            document.getElementById('f%s').innerHTML = %s;
        """ % (field, json.dumps(unicode(markup))))

    @staticmethod
    def warn_about_changes(editor_instance, field, color):
        """
        Disable the specified contenteditable field.
        """
        warning_text = "WARNING: changes you make here will be lost when " + \
                       "you toggle the Markdown button again."
        editor_instance.web.eval("""
            if (document.getElementById('mdwarn%s') === null) {
                var style_tag = document.getElementsByTagName('style')[0];
                if (style_tag.innerHTML.indexOf('mdstyle') === -1) {
                    style_tag.innerHTML +=
                            '.mdstyle { background-color: %s !important; }\\n';
                }

                var field = document.getElementById('f%s');
                field.setAttribute('title', '%s');
                field.classList.add('mdstyle');

                var warn_div = document.createElement('div');
                warn_div.id = 'mdwarn%s';
                warn_div.setAttribute('style', 'margin: 10px 0px;');
                var text = document.createTextNode('%s');
                warn_div.appendChild(text);
                field.parentNode.insertBefore(warn_div, field.nextSibling);
            }
        """ % (field, color, field, warning_text, field, warning_text))

    @staticmethod
    def remove_warn_msg(editor_instance, field):
        editor_instance.web.eval("""
            if (document.getElementById('mdwarn%s') !== null) {
                var field = document.getElementById('f%s');
                field.classList.remove('mdstyle');
                field.removeAttribute('title');
                var warn_msg = document.getElementById('mdwarn%s');
                warn_msg.parentNode.removeChild(warn_msg);
            }
        """ % (field, field, field))

    def handle_conflict(self):
        """
        Show a warning dialog. Based on the user decision, either revert the
        changes to the text, replace the stored data, or cancel.
        """
        ret = self.show_overwrite_warning()
        if ret == 0:
            self.revert_to_stored_markdown()
        elif ret == 1:
            # overwrite database
            self.overwrite_stored_data()
        else:
            print "User canceled on warning dialog."

    def overwrite_stored_data(self):
        """
        Create new Markdown from the current HTML. Remove the data about the
        current field from the database.
        """
        clean_md = Utility.convert_html_to_markdown(
                self.html, keep_empty_lines=True)
        new_html = Utility.convert_clean_md_to_html(
                clean_md, put_breaks=True)
        print "INSERTING THIS:\n", new_html
        self.insert_markup_in_field(new_html, self.editor_instance.currentField)
        sql = """
            delete from markdown
            where id=?
        """
        self.db.execute(sql, self.current_note_id_and_field)
        self.db.commit()
        const.MARKDOWN_PREFS["disable_buttons"] = False
        const.MARKDOWN_PREFS["isconverted"] = False
        self.remove_warn_msg(self.editor_instance, self.current_field)

    def revert_to_stored_markdown(self):
        print "REVERTING TO OLD MARKDOWN"
        new_html = Utility.convert_clean_md_to_html(self.md)
        # new_html = Utility.make_data_ready_to_insert(
        #         self.current_note_id_and_field, "False", self.md, new_html)
        print "Inserting this:", repr(new_html)
        self.insert_markup_in_field(new_html, self.editor_instance.currentField)
        # store the fact that the Markdown is currently not converted to HTML
        sql = """
            update markdown
            set isconverted=?, mod=?
            where id=?
        """
        self.db.execute(sql,
                        "False",
                        self._lastmodified,
                        self.current_note_id_and_field)
        self.db.commit()
        const.MARKDOWN_PREFS["disable_buttons"] = False
        const.MARKDOWN_PREFS["isconverted"] = False
        self.remove_warn_msg(self.editor_instance, self.current_field)

    def store_new_markdown_version_in_db(self, isconverted, new_md, new_html,
                                         lastmodified=None):
        """
        Update current database with new data, or insert a new row into the
        database when there is no prior data.
        """
        replace_stmt = """
            insert or replace into markdown (id, isconverted, md, html, mod)
            values (?, ?, ?, ?, ?)
        """
        self.db.execute(replace_stmt, self.current_note_id_and_field,
                        isconverted, new_md, new_html,
                        intTime() if lastmodified is None else lastmodified)
        self.db.commit()

    def show_overwrite_warning(self):
        """
        Show a warning modal dialog box, informing the user that the changes
        have taken place in the formatted text that are not in the Markdown.
        Returns a 0 for replacing the new changes with the database version of
        the Markdown, 1 for overwriting the database, and QMessageBox.Cancel for
        no action.
        """
        mess = QtGui.QMessageBox(self.parent_window)
        mess.setIcon(QtGui.QMessageBox.Warning)
        # TODO: think about putting the text of the dialog in property files
        mess.setWindowTitle("Content of card changed!")
        mess.setText("<b>The text of this field seems to have changed while "
                "Markdown mode was disabled, or the original syntax cannot be "
                "automatically restored.</b>")
        mess.setInformativeText("Please choose whether to store "
                "your current version of this field (overwriting the old "
                "version), replace your current version with the stored "
                "version, or cancel.\n\nWARNING: Overwriting may result "
                "in the loss of of some of your original Markdown syntax.")
        replaceButton = QtGui.QPushButton("&Replace", mess)
        mess.addButton(replaceButton, QtGui.QMessageBox.ApplyRole)
        mess.addButton("&Overwrite", QtGui.QMessageBox.ApplyRole)
        mess.setStandardButtons(QtGui.QMessageBox.Cancel)
        mess.setDefaultButton(replaceButton)
        return mess.exec_()

    def left_align_elements(self):
        """
        Left align footnotes, code blocks, etc. that would otherwise get
        centered or be at the mercy of the general alignment CSS of the card.
        """
        # code blocks
        self.editor_instance.web.eval("""
            var elems = document.getElementsByClassName('codehilite');
            for (var i = 0; i < elems.length; i++) {
                elems[i].setAttribute('align', 'left');
            }
        """)

        # footnotes
        self.editor_instance.web.eval("""
            var elems = document.getElementsByTagName('*');
            var regex = /fn:/;
            for (var i = 0; i < elems.length; i++) {
                var elem = elems[i].id;
                if (regex.test(elem)) {
                    elems[i].children[0].setAttribute('align', 'left');
                }
            }
        """)

        # definition lists, lists
        self.editor_instance.web.eval("""
            var elems = document.querySelectorAll('dt,dd,li');
            for (var i = 0; i < elems.length; i++) {
                elems[i].setAttribute('align', 'left');
            }
        """)
