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
import json

from PyQt4 import QtGui, QtCore
import const
from utility import Utility

class Hyperlink(object):
    def __init__(self, other, parent_window, selected_text):
        self.editor_instance          = other
        self.parent_window  = parent_window
        self.selected_text  = selected_text
        self.hyperlink_dialog()

    def hyperlink_dialog(self):
        dialog = QtGui.QDialog(self.parent_window)
        dialog.setWindowTitle("Create a hyperlink")
        dialog.resize(const.DIALOG_SIZE_X, const.DIALOG_SIZE_Y)

        ok_button_anchor = QtGui.QPushButton("&OK", dialog)
        ok_button_anchor.setEnabled(False)
        ok_button_anchor.clicked.connect(lambda: self.insert_anchor(
            url_edit.text(), urltext_edit.text()))
        ok_button_anchor.clicked.connect(dialog.hide)

        ok_button_anchor.setAutoDefault(True)

        cancel_button_anchor = QtGui.QPushButton("&Cancel", dialog)
        cancel_button_anchor.clicked.connect(dialog.hide)
        cancel_button_anchor.setAutoDefault(True)

        url_label = QtGui.QLabel("Link to:")
        url_edit = QtGui.QLineEdit()
        url_edit.setPlaceholderText("URL")
        url_edit.textChanged.connect(lambda: self.enable_ok_button(ok_button_anchor,
            url_edit.text(), urltext_edit.text()))

        urltext_label = QtGui.QLabel("Text to display:")
        urltext_edit = QtGui.QLineEdit()
        urltext_edit.setPlaceholderText("Text")
        urltext_edit.textChanged.connect(lambda: self.enable_ok_button(ok_button_anchor,
            url_edit.text(), urltext_edit.text()))

        # if user already selected text, put it in urltext_edit
        if self.selected_text:
            urltext_edit.setText(self.selected_text)

        button_box = QtGui.QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(cancel_button_anchor)
        button_box.addWidget(ok_button_anchor)

        dialog_vbox = QtGui.QVBoxLayout()
        dialog_vbox.addWidget(url_label)
        dialog_vbox.addWidget(url_edit)
        dialog_vbox.addWidget(urltext_label)
        dialog_vbox.addWidget(urltext_edit)
        dialog_vbox.addLayout(button_box)

        dialog.setLayout(dialog_vbox)

        # give url_edit focus
        url_edit.setFocus()

        dialog.exec_()

    def enable_ok_button(self, button, url, text):
        if url and text:
            button.setEnabled(True)
        else:
            button.setEnabled(False)

    def insert_anchor(self, url, text):
        """Inserts a HTML anchor <a> into the text field, using url as hyperlink
        and text as text to-be-displayed."""
        # check for valid URL
        pattern = re.compile(r"(?i)https?://")
        match = re.match(pattern, url)
        if not match:
            url = "http://" + url

        text = Utility.escape_html_chars(text)

        replacement = u"<a href=\"{0}\">{1}</a>".format(url, text)

        self.editor_instance.web.eval("document.execCommand('insertHTML', false, %s);"
                      % json.dumps(replacement))

    

class Hyperlink2(object):
    def __init__(self, other, parent_window, selected_text):
        self.editor_instance          = other
        self.parent_window  = parent_window
        self.selected_text  = selected_text
        self.hyperlink2_dialog()


    def enable_ok_button(self, button, url, text):
        if url and text:
            button.setEnabled(True)
        else:
            button.setEnabled(False)

    def hyperlink2_dialog(self):
        dialog = QtGui.QDialog(self.parent_window)
        dialog.setWindowTitle("Create a hyperlink2")
        dialog.resize(const.DIALOG_SIZE_X, const.DIALOG_SIZE_Y)

        ok_button_anchor = QtGui.QPushButton("&OK", dialog)
        ok_button_anchor.setEnabled(False)
        ok_button_anchor.clicked.connect(lambda: self.insert_anchor2(
            url_edit.text()))
        ok_button_anchor.clicked.connect(dialog.hide)

        ok_button_anchor.setAutoDefault(True)

        cancel_button_anchor = QtGui.QPushButton("&Cancel", dialog)
        cancel_button_anchor.clicked.connect(dialog.hide)
        cancel_button_anchor.setAutoDefault(True)

        url_label = QtGui.QLabel("Link to:")
        url_edit = QtGui.QLineEdit()
        url_edit.setPlaceholderText("URL")
        url_edit.textChanged.connect(lambda: self.enable_ok_button(ok_button_anchor,
            url_edit.text(), url_edit.text()))

        # urltext_label = QtGui.QLabel("Text to display:")
        # urltext_edit = QtGui.QLineEdit()
        # urltext_edit.setPlaceholderText("Text")
        # urltext_edit.textChanged.connect(lambda: self.enable_ok_button(ok_button_anchor,
        #     url_edit.text(), urltext_edit.text()))

        # # if user already selected text, put it in urltext_edit
        # if self.selected_text:
        #     urltext_edit.setText(self.selected_text)

        button_box = QtGui.QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(cancel_button_anchor)
        button_box.addWidget(ok_button_anchor)

        dialog_vbox = QtGui.QVBoxLayout()
        dialog_vbox.addWidget(url_label)
        dialog_vbox.addWidget(url_edit)
        # dialog_vbox.addWidget(urltext_label)
        # dialog_vbox.addWidget(urltext_edit)
        dialog_vbox.addLayout(button_box)

        dialog.setLayout(dialog_vbox)

        # give url_edit focus
        url_edit.setFocus()

        dialog.exec_()
    
    def insert_anchor2(self, url):
        """Inserts a anchor <a> into the text field, using url as hyperlink
        and url also as text to-be-displayed."""
        text = Utility.escape_html_chars(url)

        replacement = u"<a href=\"{0}\">{1}</a>".format(url, text)

        self.editor_instance.web.eval("document.execCommand('insertHTML', false, %s);"
                      % json.dumps(replacement))
        
