import ctypes
from ctypes.wintypes import MSG

from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QImage, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic.Compiler.qtproxies import QtGui

from UI.ScreenShot_Ui import Ui_MainWindow
from system_hotkey import SystemHotkey


class ScreenShowWindow(QMainWindow, Ui_MainWindow):

    signals_copyImg=pyqtSignal(QRect)
    signal_HotKey = pyqtSignal(str)
    signals_ScreenShot=pyqtSignal(QImage)
    def __init__(self, *args, **kwargs):
        # 调用父类构造
        super(ScreenShowWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.__toolInit()

    def __del__(self):
        self.deleteLater()

    def __toolInit(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.setMouseTracking(1)

        # self.setStyleSheet("background:#D1EEEE");
        # 触发resize的宽度
        self.leftButtonClicked = False
        self.startPoint = QPoint(0,0)
        self.beforeResizeGeometry = 0
        self.signal_HotKey.connect(self.__screenShot)
        self.hk_start = SystemHotkey()
        self.hk_start.register(('control', 'alt', 'e'), callback=self.slots_StartScreenShot)
        #label选择后给我
        self.mainPx.signals_ScreenShot.connect(self.signals_ScreenShot.emit)
        self.mainPx.seleted.connect(self.__seletedScreenShow)
        self.hide()


    def __seletedScreenShow(self,r:QRect):
        #将这个地方截图下来
        # self.toolsWindowUi.label.setPixmap(self.mainPx.pixmap().copy(r))
        # self.toolsWindowUi.lineEdit.setText(str(r.width()))
        # self.toolsWindowUi.lineEdit_2.setText(str(r.height()))
        # self.toolsWindowUi.show()
        self.mainPx.screenSHot = False
        self.signals_copyImg.emit(r)
        self.hide()


    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.canResize = self.NO_RESIZE
        self.leftButtonClicked = False

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.hide()
            self.parent().show()

    def slots_StartScreenShot(self, other: ctypes.wintypes.MSG):
        self.signal_HotKey.emit('')

    def copyImg(self,img:QImage):

        self.mainPx.setImg(img)
        dep=QApplication.desktop()

        self.move((dep.width()-img.width())/2,(dep.height()-img.height())/2)
        self.show()


    def __screenShot(self, s):
        if not self.isVisible():
            px = QGuiApplication.primaryScreen().grabWindow(0);
            self.mainPx.setImg(px.toImage())
            self.move(0, 0)
            self.window().showMaximized()
            self.mainPx.screenSHot=True
        else:
            self.hide()

    def mouseDoubleClickEvent(self, event):
        """ 双击最大化/还原窗口 """
        # self.__showRestoreWindow()
        pass



    def __showRestoreWindow(self):
        """ 复原窗口并更换最大化按钮的图标 """
        if self.window().isMaximized():
            self.window().showNormal()
            # 更新标志位用于更换图标

        else:
            self.window().showMaximized()
