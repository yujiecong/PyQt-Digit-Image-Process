import random
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
class PlotCanvas(
    FigureCanvas):  # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height),
                     dpi=dpi)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure

        FigureCanvas.__init__(self,self.fig)  # 初始化父类
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotr(self,data):

        ax = self.figure.add_subplot(111)

        ax.plot(data, 'r-')
        ax.set_title('R通道波形')

        self.draw()
    def plotg(self,data):

        ax = self.figure.add_subplot(111)
        ax.plot(data, 'g')
        ax.set_title('G通道波形')

        self.draw()
    def plotb(self,data):

        ax = self.figure.add_subplot(111)

        ax.plot(data, 'b')
        ax.set_title('B通道波形')
        self.draw()

    def plotgray(self,data):

        ax = self.figure.add_subplot(111)

        ax.plot(data, 'gray')
        ax.set_title('灰度波形')
        self.draw()


class ChartWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = PlotCanvas(self, width=10, height=2)
        # self.canvas.plotgray([1,2,3])
        # self.setFixedWidth(self.canvas.width())








if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChartWidget()
    ex.show()
    sys.exit(app.exec_())