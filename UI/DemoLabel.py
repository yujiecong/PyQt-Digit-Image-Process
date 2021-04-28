import os

from PIL import ImageSequence, Image
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie, QPen
from PyQt5.QtWidgets import QLabel, QApplication

import Global_Main

class DemoLabel(QLabel):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(1)
        self.setAlignment(Qt.AlignCenter)
        self.format = ''
        self.r = QRect()
        self.drawImg = None
        self.scaledFactor = 1.1
        self.leftButtonClicked = 0
        self.pixmap=None
        self.imgPath= ''
        self.startPos=0
        self.movie=''

        self.color=0
        self.draw=False
        self.drawPos=0
    @property
    def _draw(self):
        return self.draw
    def _draw(self,v):
        self.draw=v

    def drawInit(self,color):
        self.draw=True
        self.color=color
    def backup(self):
        return QPixmap(self.pixmap)

    def crop(self, r: QRect):
        self.setPx(self.pixmap.copy(r))

    def setPx(self, px: QPixmap):
        self.pixmap=px
        self.drawImg = px.toImage()
        self.r.setWidth(self.drawImg.width())
        self.r.setHeight(self.drawImg.height())
        self.format = self.imgPath.split('.')[-1]
        self.setFixedHeight(self.drawImg.height())
        self.setFixedWidth(self.drawImg.width())
        self.setGeometry(self.r)
        self.update()
        if self.format=='gif':
            self.movie=QMovie(self.imgPath)
            self.setMovie(self.movie)
            self.movie.start()
        else:
            if self.movie:
                self.movie.stop()
                # self.setMovie(None)
                self.movie.deleteLater()
                self.movie=None
        if Global_Main.getGlobalValue("SAVE_TEMP"):
            os.remove(self.imgPath)
    def setStBar(self, stBar):
        self.stBar = stBar

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QPainter(self)

        # if self.format=="gif":
        #     pix=QPixmap(self.pxName)
        #     painter.drawPixmap(self.r,pix)
        # else:
        #     painter.drawImage(0,0,self.drawImg,0,0,self.r.width(),self.r.height());#QPoint()
        painter.drawImage(self.r,self.drawImg)
        QLabel.paintEvent(self,a0)

        #当放大倍数很大时,尝试在每一个点上画一个rgb值

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            if a0.angleDelta().y() > 0:  # 放大
                self.r.setWidth(self.r.width() * self.scaledFactor)
                self.r.setHeight(self.r.height() * self.scaledFactor)
                self.setFixedHeight(self.r.height())
                self.setFixedWidth(self.r.width())
                # self.setGeometry(self.r)
                self.update()
            else:
                self.r.setWidth(self.r.width() / self.scaledFactor)
                self.r.setHeight(self.r.height() / self.scaledFactor)
                self.setFixedHeight(self.r.height())
                self.setFixedWidth(self.r.width())
                # self.setGeometry(self.r)
                self.update()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.leftButtonClicked = 1
            self.startPos=ev.pos()


    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.leftButtonClicked = 0

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        # print(a0.pos())
        if self.leftButtonClicked and  self.draw:
            self.drawImg.setPixelColor(a0.x(),a0.y(),self.color)
            self.update()
            return
        if not self.drawImg:
            return
        x = a0.x()
        y = a0.y()
        rgba = self.drawImg.pixelColor(x, y)
        imgInfo = f'(X,Y)=({x},{y})   RGBA=({rgba.red(), rgba.green(), rgba.blue(), rgba.alpha()})'
        self.stBar.showMessage(imgInfo)
        if self.leftButtonClicked:
            pos = self.mapToParent(a0.pos())-self.startPos
            self.move(pos)


