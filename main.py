import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph.opengl as gl
from Main.ToolsWindow_Main import ToolsWindow
if __name__ == '__main__':
    app = QApplication(sys.argv)

    MainWindow = ToolsWindow()
    MainWindow.show()

    sys.exit(app.exec_())
