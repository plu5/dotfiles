# This file is part of KanvasBuddy.

# KanvasBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# KanvasBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.

# CONTRIBUTORS:
# Kapyia @ https://krita-artists.org/ 

import importlib

from krita import Krita, Extension
from PyQt5.QtWidgets import QMessageBox
from . import uikanvasbuddy

class KanvasBuddy(Extension):

    def __init__(self, parent):
        super(KanvasBuddy, self).__init__(parent)
        self.isActive = False
        self.ui = None


    def setup(self):
        pass


    def createActions(self, window): # Called by Krita on startup
        action = window.createAction("kanvasbuddy", "KanvasBuddy")
        action.setToolTip("A floating minimalist GUI")
        action.triggered.connect(self.launchInterface)

        action = window.createAction("kanvasbuddy2", "KanvasBuddy switch between panels")
        action.setToolTip("A floating minimalist GUI")
        action.triggered.connect(self.switchBetweenPanels)

        action = window.createAction("kanvasbuddy3", "KanvasBuddy switch between panels inverse")
        action.setToolTip("A floating minimalist GUI")
        action.triggered.connect(lambda: self.switchBetweenPanels(True))


    def launchInterface(self):
        if not self.ui and not Krita.instance().activeDocument():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.setWindowTitle('KanvasBuddy')
            msg.setText("No active documents found. \n\n" +  
                        "KanvasBuddy requires at least one active document to launch.")
            msg.exec_()
        if self.isActive:
            self.isActive = False
            self.ui.hide()
        else:
            # importlib.reload(uikanvasbuddy) # FOR TESTING ONLY
            self.isActive = True
            if self.ui:
                #self.ui.setGeometry(0,0,500,500)
                self.ui.show()
            else:
                self.ui = uikanvasbuddy.UIKanvasBuddy(self)
                self.ui.launch()
                self.ui.setGeometry(0,100, self.ui.width(), self.ui.height())
                self.ui.togglePinnedMode()
        self.curpanelnum = 0
        self.panels = [ID for ID in self.ui.panelStack._panels.keys()]

    def switchBetweenPanels(self, reverse=False):
        if not self.isActive:
            return
        delta = -1 if reverse else 1
        self.curpanelnum = (self.curpanelnum + delta) % len(self.panels)
        self.ui.panelStack._panels[self.panels[self.curpanelnum]].activate()

#        len(self.ui.panelStack._panels)
        # self.ui.panelStack._panels[self.curpanelnum].activate()


    def setIsActive(self, b):
        if isinstance(b, bool):
            self.isActive = b
        else:
            raise TypeError("invalid argument; active state must be a boolean")

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(KanvasBuddy(Krita.instance()))
