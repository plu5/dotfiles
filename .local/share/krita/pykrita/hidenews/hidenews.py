from krita import *

def no(*variables):
    for i, var in enumerate(variables):
        if not var:
            print(f"hidenews: object {i} not found")
            return True
    return False

class Hidenews(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        notify = Krita.instance().notifier()
        notify.setActive(True)
        # One-shot connection. Not quite early enough.
        self.connection = notify.windowCreated.connect(self.openViewEvent, 128)

    def setup(self):
        pass

    def createActions(self, window):
        pass

    def openViewEvent(self):
        self.do()

    def do(self):
        qwin = Krita.instance().activeWindow().qwindow()
        if no(qwin):
            return
        right = qwin.findChild(QWidget,'widgetRight')
        left = qwin.findChild(QWidget,'widgetCenter')
        recent = qwin.findChild(QListView,'recentDocumentsListView')
        lab = qwin.findChild(QLabel, "labelSupportText")
        l1 = qwin.findChild(QHBoxLayout, "horizontalLayout_12")
        drop = qwin.findChild(QFrame, "dropAreaIndicator")
        l2 = qwin.findChild(QVBoxLayout, "verticalLayout_3")
        l3 = qwin.findChild(QHBoxLayout, "horizontalLayout_16")
        if no(right, left, recent, lab, l1, drop, l2, l3):
            return
        for w in (left, right, lab):
            w.setVisible(False)
        recent.setStyleSheet("QListView::item {width: 195px;}")
        recent.setSpacing(3)
        while l1.count():
            l1.takeAt(0)
        for layout in (l1, l2, l3):
            layout.setSpacing(0)
            layout.setContentsMargins(0,0,0,0)
        drop.setContentsMargins(0,0,0,0)

Krita.instance().addExtension(Hidenews(Krita.instance()))
