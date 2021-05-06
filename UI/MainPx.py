from typing import Union

from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.uic.Compiler.qtproxies import QtGui


class MainPx(QLabel):
    seleted = pyqtSignal(QRect)

    signals_ScreenShot = pyqtSignal(QImage)
    # 调整边界的触发值
    resizewidth: int
    # 全局鼠标坐标
    mousePos: Union[QPoint, QPoint]
    # 是否是resize状态 值如下
    canResize: int
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(1)
        self.leftButtonClicked = False
        self.canResize = self.DARG_ACTION
        self.mousePos = QPoint(0, 0)
        self.startPoint = QPoint(0, 0)
        self.interceptRect = QRect(self.startPoint, self.mousePos)
        self.resizewidth = 5
        self.leftTopPoint = QPoint(0, 0)
        self.rightBottomPoint = QPoint(0, 0)
        self.interceptFinish = False

        self.r=QRect()
        self.drawImg=QImage()




        self.screenSHot=False
    def setImg(self,img):
        # self.r=r
        self.drawImg=img
        self.update()
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QPainter(self)
        painter.drawImage(self.drawImg.rect(), self.drawImg)
        painter.setPen(Qt.blue)

        painter.drawRect(self.interceptRect)


    def mousePressEvent(self, event):
        """ 移动窗口 """
        # 判断鼠标点击位置是否允许拖动
        if event.button() == Qt.LeftButton :
            self.leftButtonClicked = True
            self.startPoint = event.pos()  # 第一次按下的坐标
            self.beforeResizeGeometry = QRect(self.interceptRect)
            self.mousePos = event.pos()
    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        msx,msy=self.interceptRect.bottomRight().x(),self.interceptRect.bottomRight().y()
        spx,spy=self.interceptRect.topLeft().x(),self.interceptRect.topLeft().y()
        if not self.screenSHot:
            if msx>spx:
                if  msy>spy:
                    self.seleted.emit(QRect(spx,spy,msx-spx,msy-spy))
                else:
                    self.seleted.emit(QRect(msx,msy,msx-spx,spy-spy))
            else:
                if msy > spy:
                    self.seleted.emit(QRect(msx,spy,spx-msx,msy-spy))
                else:
                    self.seleted.emit(QRect(self.mousePos,self.startPoint))

        else:
            if msx > spx:
                if msy > spy:
                    self.signals_ScreenShot.emit(self.drawImg.copy(QRect(spx, spy, msx - spx, msy - spy)))
                else:
                    self.signals_ScreenShot.emit(self.drawImg.copy(QRect(msx, msy, msx - spx, spy - spy)))
            else:
                if msy > spy:
                    self.signals_ScreenShot.emit(self.drawImg.copy(QRect(msx, spy, spx - msx, msy - spy)))
                else:
                    self.signals_ScreenShot.emit(self.drawImg.copy(QRect(self.mousePos, self.startPoint)))
        self.interceptFinish = False
        self.interceptRect = QRect()
        self.update()
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.leftButtonClicked = False

        if self.startPoint != self.mousePos:
            self.interceptFinish = True



    def __setMouseCursor(self, ):

        if self.canResize == self.TOP_RESIZE or self.canResize == self.BOTTOM_RESIZE:
            self.setCursor(Qt.SplitVCursor)
        elif self.canResize == self.LEFT_RESIZE or self.canResize == self.RIGHT_RISIZE:
            self.setCursor(Qt.SplitHCursor)
        elif self.canResize == self.LEFT_BOTTOM_RESIZE or self.canResize == self.RIGHT_TOP_RESIZE:
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.canResize == self.LEFT_TOP_RESIZE or self.canResize == self.RIGHT_BOTTOM_RESIZE:
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.canResize==self.NO_ACTION:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.leftButtonClicked:
            self.repaint()
            self.mousePos = a0.pos()
            if  self.interceptFinish:
                if self.canResize == self.TOP_RESIZE or self.canResize == self.BOTTOM_RESIZE:
                    # 上下拖动,只能移动height
                    delta = a0.y() - self.startPoint.y()
                    # print(delta)
                    if self.canResize == self.TOP_RESIZE:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x(),
                                                   self.beforeResizeGeometry.y() + delta,
                                                   self.beforeResizeGeometry.width(),
                                                   self.beforeResizeGeometry.height() - delta)
                    else:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x(),
                                                   self.beforeResizeGeometry.y(),
                                                   self.beforeResizeGeometry.width(),
                                                   self.beforeResizeGeometry.height() + delta)

                elif self.canResize == self.LEFT_RESIZE or self.canResize == self.RIGHT_RISIZE:
                    delta = a0.x() - self.startPoint.x()
                    if self.canResize == self.LEFT_RESIZE:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x() + delta,
                                                   self.beforeResizeGeometry.y(),
                                                   self.beforeResizeGeometry.width() - delta,
                                                   self.beforeResizeGeometry.height())
                    else:
                        self.interceptRect.setRect(self.beforeResizeGeometry.x(),
                                                   self.beforeResizeGeometry.y(),
                                                   self.beforeResizeGeometry.width() + delta,
                                                   self.beforeResizeGeometry.height())
                elif self.canResize == self.LEFT_TOP_RESIZE or self.canResize == self.RIGHT_BOTTOM_RESIZE:
                    delta = a0.pos() - self.startPoint
                    if self.canResize == self.LEFT_TOP_RESIZE:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x() + delta.x(),
                                                   self.beforeResizeGeometry.y() + delta.y(),
                                                   self.beforeResizeGeometry.width() - delta.x(),
                                                   self.beforeResizeGeometry.height() - delta.y())
                    else:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x(),
                                                   self.beforeResizeGeometry.y(),
                                                   self.beforeResizeGeometry.width() + delta.x(),
                                                   self.beforeResizeGeometry.height() + delta.y())
                elif self.canResize == self.LEFT_BOTTOM_RESIZE or self.canResize == self.RIGHT_TOP_RESIZE:
                    delta = a0.pos() - self.startPoint
                    if self.canResize == self.LEFT_BOTTOM_RESIZE:
                        self.interceptRect .setRect(self.beforeResizeGeometry.x() + delta.x(),
                                                   self.beforeResizeGeometry.y(),
                                                   self.beforeResizeGeometry.width() - delta.x(),
                                                   self.beforeResizeGeometry.height() + delta.y())
                    else:
                        self.interceptRect.setRect(self.beforeResizeGeometry.x(),
                                                   self.beforeResizeGeometry.y() + delta.y(),
                                                   self.beforeResizeGeometry.width() + delta.x(),
                                                   self.beforeResizeGeometry.height() - delta.y())
                elif self.canResize == self.DARG_ACTION:
                    newPos=a0.pos() - self.startPoint + self.beforeResizeGeometry.topLeft()
                    self.interceptRect.setRect(newPos.x(),newPos.y(),self.beforeResizeGeometry.width(),self.beforeResizeGeometry.height())


            else:
                self.interceptRect=QRect(self.startPoint,self.mousePos)
        else:

            self.canResize = self.__canItResize(a0.pos())
            self.__setMouseCursor()

    def __canItResize(self, pos: QPoint):
        """
        :type pos: 鼠标坐标 映射到
        """
        # 如果在矩阵外面
        if not self.interceptRect.contains(pos):
            return self.NO_ACTION

        # 如果在规定的抓取范围内

        tlx, tly = self.interceptRect.topLeft().x(), self.interceptRect.topLeft().y()  # topleft
        brx, bry = self.interceptRect.bottomRight().x(), self.interceptRect.bottomRight().y()  #
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
                if bry- self.resizewidth <= mousey <= bry :
                    return self.RIGHT_BOTTOM_RESIZE
                else:
                    return self.RIGHT_TOP_RESIZE

        return self.DARG_ACTION
        pass
