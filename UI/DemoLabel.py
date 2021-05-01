import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QObject
from PyQt5.QtGui import QImage, QPainter, QMovie
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import  pyqtSignal


from Main import Global_Main


class DemoLabel(QLabel):


    NO_ACTION = -1
    DARG_ACTION = 0
    TOP_RESIZE = 1
    BOTTOM_RESIZE = 2
    LEFT_RESIZE = 3
    RIGHT_RISIZE = 4
    LEFT_TOP_RESIZE = 5
    LEFT_BOTTOM_RESIZE = 6
    RIGHT_TOP_RESIZE = 7
    RIGHT_BOTTOM_RESIZE = 8

    _maxWidth: int
    drawImg: QImage
    sizeChanged = pyqtSignal(QSize)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(1)
        self.setAlignment(Qt.AlignCenter)
        self.format = ''
        self.r = QRect()
        self.drawImg = QImage()
        self.scaledFactor = 1.1
        self.leftButtonClicked = 0
        self.imgPath = ''
        self.startPoint = 0
        self.movie = ''

        self.color = 0
        self.draw = False
        self.drawPos = 0
        self.first = 1
        self._maxHeight = 0
        self._maxWidth = 0

        self.mousePos = QPoint(0, 0)
        self.startPoint = QPoint(0, 0)
        self.interceptRect = QRect(self.startPoint, self.mousePos)
        self.resizewidth = 5
        self.leftTopPoint = QPoint(0, 0)
        self.rightBottomPoint = QPoint(0, 0)
        self.interceptFinish = False

        self.saveTemp=0
        self.randomFn=''



    def getMaxHeight(self):
        return self._maxHeight

    def getMaxWidth(self):
        return self._maxWidth

    def setRestore(self):
        self.r.setWidth(self.drawImg.width())
        self.r.setHeight(self.drawImg.height())
        self.setFixedWidth(self.drawImg.width() + 1)
        self.setFixedWidth(self.drawImg.width() - 1)
        self.setFixedHeight(self.drawImg.height())
        self._maxWidth = self.drawImg.width()
        self._maxHeight = self.drawImg.height()
        self.update()

    def drawInit(self, color):
        self.draw = True
        self.color = color

    def backup(self):
        return QImage(self.drawImg)

    def setImg(self, img: QImage,fn:str):

        self.drawImg = img
        self.imgPath=fn
        self.format = self.imgPath.split('.')[-1]

        if self.first:
            self.r.setWidth(self.drawImg.width())
            self.r.setHeight(self.drawImg.height())
            self.setFixedWidth(img.width())
            self.setFixedHeight(img.height())
            self._maxWidth = self.drawImg.width()
            self._maxHeight = self.drawImg.height()
            self.first = 0
        else:
            self.r.setWidth(self._maxWidth)
            self.r.setHeight(self._maxHeight)
            self.setFixedWidth(self._maxWidth + 1)
            self.setFixedWidth(self._maxWidth - 1)
            self.setFixedHeight(self._maxHeight)



        self.setGeometry(self.r)

        if self.format == 'gif':
            self.movie = QMovie(self.imgPath)
            self.setMovie(self.movie)
            self.movie.start()
        else:
            if self.movie:
                self.movie.stop()
                # self.setMovie(None)
                self.movie.deleteLater()
                self.movie = None
        self.update()



    def setStBar(self, stBar):
        self.stBar = stBar

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QPainter(self)
        # print(self.r,self.drawImg)
        painter.drawImage(self.r, self.drawImg)
        # painter.drawPixmap(self.r,QPixmap(self.drawImg))
        # print(a0)
        # QLabel.paintEvent(self, a0)

        # 当放大倍数很大时,尝试在每一个点上画一个rgb值

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            if a0.angleDelta().y() > 0:  # 放大
                self.r.setWidth(self.r.width() * self.scaledFactor)
                self.r.setHeight(self.r.height() * self.scaledFactor)

            else:
                self.r.setWidth(self.r.width() / self.scaledFactor)
                self.r.setHeight(self.r.height() / self.scaledFactor)

            self._maxHeight = self.r.height()
            self._maxWidth = self.r.width()
            self.setFixedWidth(self._maxWidth + 1)
            self.setFixedWidth(self._maxWidth - 1)
            self.setFixedHeight(self._maxHeight)
            self.update()
    def setR(self,a,b,c,d):
        r=QRect(a,b,c,d)
        self._maxHeight = r.height()
        self._maxWidth = r.width()
        self.setFixedWidth(self._maxWidth + 1)
        self.setFixedWidth(self._maxWidth - 1)
        self.setFixedHeight(self._maxHeight)
        self.r.setWidth(self._maxWidth )
        self.r.setHeight(self._maxHeight)
        self.update()


    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.leftButtonClicked = 1
            self.startPoint = ev.pos()

            self.leftButtonClicked = True

            self.beforeResizeGeometry = QRect(self.r)
            self.mousePos = ev.pos()



    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        # print(a0.pos())
        if self.leftButtonClicked and self.draw:

            self.drawImg.setPixelColor(a0.x(), a0.y(), self.color)
            self.update()
            return
        if not self.drawImg:
            return
        x = a0.x()
        y = a0.y()
        rgba = self.drawImg.pixelColor(x, y)
        imgInfo = f'(X,Y)=({x},{y})   RGBA=({rgba.red(), rgba.green(), rgba.blue(), rgba.alpha()})'
        self.stBar.showMessage(imgInfo)

        ...
        """
        
        """
        if self.leftButtonClicked:
            self.repaint()
            self.mousePos = a0.pos()
            if self.canResize == self.TOP_RESIZE or self.canResize == self.BOTTOM_RESIZE:
                # 上下拖动,只能移动height
                delta = a0.y() - self.startPoint.y()
                # print(delta)
                if self.canResize == self.TOP_RESIZE:
                    self.setR(self.beforeResizeGeometry.x(),
                                   self.beforeResizeGeometry.y() + delta,
                                   self.beforeResizeGeometry.width(),
                                   self.beforeResizeGeometry.height() - delta)
                else:
                    self.setR(self.beforeResizeGeometry.x(),
                                   self.beforeResizeGeometry.y(),
                                   self.beforeResizeGeometry.width(),
                                   self.beforeResizeGeometry.height() + delta)

            elif self.canResize == self.LEFT_RESIZE or self.canResize == self.RIGHT_RISIZE:
                delta = a0.x() - self.startPoint.x()
                if self.canResize == self.LEFT_RESIZE:
                    self.setR(self.beforeResizeGeometry.x() + delta,
                                   self.beforeResizeGeometry.y(),
                                   self.beforeResizeGeometry.width() - delta,
                                   self.beforeResizeGeometry.height())
                else:
                    self.setR(self.beforeResizeGeometry.x(),
                                   self.beforeResizeGeometry.y(),
                                   self.beforeResizeGeometry.width() + delta,
                                   self.beforeResizeGeometry.height())
            elif self.canResize == self.LEFT_TOP_RESIZE or self.canResize == self.RIGHT_BOTTOM_RESIZE:
                delta = a0.pos() - self.startPoint
                if self.canResize == self.LEFT_TOP_RESIZE:
                    self.setR(self.beforeResizeGeometry.x() + delta.x(),
                                   self.beforeResizeGeometry.y() + delta.y(),
                                   self.beforeResizeGeometry.width() - delta.x(),
                                   self.beforeResizeGeometry.height() - delta.y())
                else:
                    self.setR(self.beforeResizeGeometry.x(),
                                   self.beforeResizeGeometry.y(),
                                   self.beforeResizeGeometry.width() + delta.x(),
                                   self.beforeResizeGeometry.height() + delta.y())
            elif self.canResize == self.LEFT_BOTTOM_RESIZE or self.canResize == self.RIGHT_TOP_RESIZE:
                delta = a0.pos() - self.startPoint
                if self.canResize == self.LEFT_BOTTOM_RESIZE:
                    self.setR(self.beforeResizeGeometry.x() + delta.x(),
                                               self.beforeResizeGeometry.y(),
                                               self.beforeResizeGeometry.width() - delta.x(),
                                               self.beforeResizeGeometry.height() + delta.y())
                else:
                    self.setR(self.beforeResizeGeometry.x(),
                                               self.beforeResizeGeometry.y() + delta.y(),
                                               self.beforeResizeGeometry.width() + delta.x(),
                                               self.beforeResizeGeometry.height() - delta.y())

            else:

                pos = self.mapToParent(a0.pos())-self.startPoint
                self.move(pos)
            self.sizeChanged.emit(QSize(self._maxWidth,self._maxHeight))

        else:

            self.canResize = self.__canItResize(a0.pos())
            self.__setMouseCursor()

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._maxHeight = self.parent().height()
        self._maxWidth = self.parent().width()
        self.setFixedWidth(self._maxWidth + 1)
        self.setFixedWidth(self._maxWidth - 1)
        self.setFixedHeight(self._maxHeight)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.leftButtonClicked = False

        if self.startPoint != self.mousePos:
            self.interceptFinish = True


    def __setMouseCursor(self):

        if self.canResize == self.TOP_RESIZE or self.canResize == self.BOTTOM_RESIZE:
            self.setCursor(Qt.SplitVCursor)
        elif self.canResize == self.LEFT_RESIZE or self.canResize == self.RIGHT_RISIZE:
            self.setCursor(Qt.SplitHCursor)
        elif self.canResize == self.LEFT_BOTTOM_RESIZE or self.canResize == self.RIGHT_TOP_RESIZE:
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.canResize == self.LEFT_TOP_RESIZE or self.canResize == self.RIGHT_BOTTOM_RESIZE:
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

    def __canItResize(self, pos: QPoint):
        """
        :type pos: 鼠标坐标 映射到
        """

        # 如果在规定的抓取范围内

        tlx, tly = self.rect().topLeft().x(), self.rect().topLeft().y()  # topleft
        brx, bry = self.rect().bottomRight().x(), self.rect().bottomRight().y()  #
        mousex, mousey = pos.x(), pos.y()
        # 上下边界
        if tlx + self.resizewidth <= mousex <= brx - self.resizewidth:
            if tly - self.resizewidth <= mousey <= tly + self.resizewidth:
                return self.TOP_RESIZE
            elif bry - self.resizewidth <= mousey <= bry + self.resizewidth:
                return self.BOTTOM_RESIZE
        # 左右边界
        elif tly + self.resizewidth <= mousey <= bry - self.resizewidth:
            if tlx <= mousex <= tlx + self.resizewidth:
                return self.LEFT_RESIZE
            elif brx <= mousex <= brx + self.resizewidth:
                return self.RIGHT_RISIZE
        # 腾出来4个正方形用于调整
        else:
            # 左
            if tlx <= mousex <= tlx + self.resizewidth:
                # 左上
                if tly <= mousey <= tly + self.resizewidth:
                    return self.LEFT_TOP_RESIZE
                else:  # 左下
                    return self.LEFT_BOTTOM_RESIZE
            # 右
            elif brx - self.resizewidth <= mousex <= brx:
                if bry - self.resizewidth <= mousey <= bry:
                    return self.RIGHT_BOTTOM_RESIZE
                else:
                    return self.RIGHT_TOP_RESIZE

        return self.DARG_ACTION
        pass
