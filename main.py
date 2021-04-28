import sys
from PyQt5.QtWidgets import QApplication

# from ScreenShot_Main import ScreenShowWindow
from Main.ToolsWindow_Main import ToolsWindow
if __name__ == '__main__':
    app = QApplication(sys.argv)

    MainWindow = ToolsWindow()
    MainWindow.show()

    sys.exit(app.exec_())
