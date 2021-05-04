
from PyQt5.QtWidgets import QDialog

from UI.CustomFilter_Ui import Ui_CustomFilterDialog

class CustomFilter(QDialog,Ui_CustomFilterDialog):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.x33="""[1, 1, 1,
1, -4, 1,
1, 1, 1]"""
        self.x55="""[1,  1,  1,  1,  1,
1,  0,  0,  0,  1,
1,  0,  0,  0,  1,
1,  0,  0,  0,  1,
1,  1,  1,  1,  1]"""
        self.plainTextEdit.setPlainText(self.x33)
        self.comboBox.currentIndexChanged.connect(lambda idx:self.plainTextEdit.setPlainText(self.x33) if idx==0 else self.plainTextEdit.setPlainText(self.x55))