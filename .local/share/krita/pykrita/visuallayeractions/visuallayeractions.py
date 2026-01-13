from krita import Krita, Extension
from PyQt5.QtCore import QTimer
from time import time

def exe(name):
    Krita.instance().action(name).trigger()

def flash():
    d = Krita.instance().activeDocument()
    n = d.activeNode()
    v = n.visible()
    s = d.selection()
    exe('deselect')
    exe('selectopaque')
    n.setVisible(not v)
    d.refreshProjection()
    def restore():
        n.setVisible(v)
        d.setSelection(s)
        d.refreshProjection()
    QTimer.singleShot(100, restore)

class Visuallayeractions(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.in_play = False
        self.batch_detected = False
        self.last_called = 0
        self.flash_threshold = 0.4

    def play(self, action_name):
        if self.in_play:
            self.batch_detected = True
            exe(action_name)
            return
        self.in_play = True
        self.batch_detected = False
        exe(action_name)
        if (not self.batch_detected and
                self.last_called < time() - self.flash_threshold):
            self.last_called = time()
            flash()

        self.in_play = False

    def setup(self):
        pass

    def createActions(self, window):
        def ac(ID, name, f, tooltip=""):
            action = window.createAction(ID, name)
            len(tooltip) and action.setToolTip(tooltip)
            action.triggered.connect(f)
        ac("visuallayeractions_uplayer", "Visual activate next layer",
           lambda: self.play('activateNextLayer'))
        ac("visuallayeractions_downlayer", "Visual activate previous layer",
           lambda: self.play('activatePreviousLayer'))
        ac("visuallayeractions_merge", "Visual merge layer",
           lambda: self.play('merge_layer'))
        ac("visuallayeractions_duplicate", "Visual duplicate layer",
           lambda: self.play('duplicatelayer'))
        ac("visuallayeractions_inheritalpha", "Visual toggle layer inherit alpha",
           lambda: self.play('toggle_layer_inherit_alpha'))
        ac("visuallayeractions_alphalock", "Visual toggle layer alpha lock",
           lambda: self.play('toggle_layer_alpha_lock'))
        ac("visuallayeractions_properties", "Visual layer properties",
           lambda: self.play('layer_properties'))
        ac("visuallayeractions_moveup", "Visual move layer up",
           lambda: self.play('move_layer_up'))
        ac("visuallayeractions_movedown", "Visual move layer down",
           lambda: self.play('move_layer_down'))

Krita.instance().addExtension(Visuallayeractions(Krita.instance()))
