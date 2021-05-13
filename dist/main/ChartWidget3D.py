
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic.Compiler.qtproxies import QtGui
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph import Vector


class ChartWidget3D(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.w = gl.GLViewWidget()

        self.w.opts["elevation"]=90
        self.w.opts["azimuth"]=0
        self.w.opts['distance'] = 500

        # self.w.setWindowOpacity(0)
        # self.w.show()
        # self.w.setBackgroundColor((88,88,88))


        self.w.setParent(self)
        self.w.move(0,0)
        # self.show()
    def setData(self,img):

        data=np.array(img.convert("L"))

        w,h=data.shape
        step=np.random.randint(100,255)/w/255

        for row in range(w):
            lines = []
            for col in range(h):
                g = [row, col, data[row][col]]
                lines.append(g)
                # colors.append(img.getpixel((row,col)))
            # _r/=255
            _r=row*step
            color=(1-_r,.1,_r,.3)
            plt = gl.GLLinePlotItem(pos=np.array(lines),color=color, width=1, antialias=True)
            self.w.addItem(plt)

            # plt=gl.GLScatterPlotItem(pos=np.array(line), color=color, size=2, pxMode=False)
            # self.w.addItem(plt)


        self.w.opts['center']= Vector(w//2,h/2)

        # self.gx = gl.GLGridItem()
        # self.gx.setSize(255,w,1)
        # self.gx.rotate(90, 0, 1, 0)
        # self.gx.translate(0, h//2, 255//2)
        # self.w.addItem(self.gx)
        #
        # self.gy = gl.GLGridItem()
        # self.gy.setSize(h,255 , 1)
        # self.gy.rotate(90, 1, 0, 0)
        # self.gy.translate(w//2,0, 255//2)
        # self.w.addItem(self.gy)
        # #
        # self.gz = gl.GLGridItem()
        # self.gz.setSize(w, h, 1)
        # self.gz.translate(w//2, h//2, 0)
        # self.w.addItem(self.gz)
        # data = data.T
        # w,h=data.shape
        # for row in range(w):
        #     line=[]
        #
        #     for col in range(h):
        #         g=[col,row,data[row][col]]
        #         line.append(g)
        #         # colors.append(img.getpixel((row,col)))
        #     plt = gl.GLLinePlotItem(pos=np.array(line), color=(0.,1.,0.,1), width=1, antialias=True)
        #     self.w.addItem(plt)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.w.setFixedWidth(self.width())
        self.w.setFixedHeight(self.height())

if __name__ == '__main__':

    app=QApplication(sys.argv)
    cw=ChartWidget3D()
    cw.show()
    app.exit(app.exec_())



