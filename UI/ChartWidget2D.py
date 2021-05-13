
import sys
import pyqtgraph as pg
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QGraphicsView
from PyQt5.uic.Compiler.qtproxies import QtGui


class ChartWidget2D(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.plot = pg.PlotWidget(enableAutoRange=True,parent=self)
        self.plot.setGeometry(self.rect())
        self.canvas = self.plot.plot()
        self.plot.setBackground((255,255,255))
        # print(dir(self.canvas))
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # self.fitInView()
    def setData(self,data,color):
        self.canvas.setPen(color)
        self.canvas.setData(data)


    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.plot.setFixedWidth(self.width())
        self.plot.setFixedHeight(self.height())





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChartWidget()
    ex.show()
    sys.exit(app.exec_())