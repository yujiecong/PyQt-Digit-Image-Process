from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QDockWidget
from PyQt5.uic.Compiler.qtproxies import QtGui


class MyDockWidget(QDockWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        # if event.key()==Qt.Key_Space:
        #     self.hide()
        self.parent().keyPressEvent(event)
    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.showMaximized() if not self.isMaximized() else self.showNormal()