# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# Changes: Stefan van den Akker <srvandenakker.dev@gmail.com>

from aqt.qt import *
from aqt.utils import openHelp, showInfo
from anki.utils import isWin, isMac
import aqt
from BeautifulSoup import BeautifulSoup
if isWin:
    from utility import Utility
    import const
else:
    from ...utility import Utility
    from ... import const

def onHtmlEdit(self):
    self.saveNow()
    d = QDialog(self.widget)
    form = aqt.forms.edithtml.Ui_Dialog()
    form.setupUi(d)
    d.connect(form.buttonBox, SIGNAL("helpRequested()"),
             lambda: openHelp("editor"))
    orgHTML = self.note.fields[self.currentField]
    HTMLWithoutData = orgHTML
    start_md_data = orgHTML.find(const.START_HTML_MARKER)
    end_md_data = orgHTML.find(const.END_HTML_MARKER, start_md_data)
    containsData = start_md_data != -1 and end_md_data != -1
    if containsData:
        mdData = orgHTML[start_md_data:(end_md_data+len(const.END_HTML_MARKER))]
        print repr(mdData)
        HTMLWithoutData = orgHTML[:start_md_data]
    form.textEdit.setPlainText(HTMLWithoutData)
    form.textEdit.moveCursor(QTextCursor.End)
    d.exec_()
    html = form.textEdit.toPlainText()
    if containsData:
        html += mdData
    # filter html through beautifulsoup so we can strip out things like a
    # leading </div>
    html = unicode(BeautifulSoup(html))
    self.note.fields[self.currentField] = html
    self.loadNote()
    # focus field so it's saved
    self.web.setFocus()
    self.web.eval("focusField(%d);" % self.currentField)
