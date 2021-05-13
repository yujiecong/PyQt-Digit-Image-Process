import os
import datetime
import random
import time
import pyqtgraph as pg
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat

from PIL import ImageDraw
from PIL import ImageFont

from Thread_Main import Convert_Object
from .CustomFilter_Main import CustomFilter
from .Global_Main import CONVERT_MODE, MIRROR, FILTER, ENHANCE, FORMAT_MODE


from PyQt5.QtCore import Qt, QRect, QThread
from PyQt5.QtGui import QImage, QImageIOHandler
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QColorDialog
from PyQt5.uic.Compiler.qtproxies import QtGui

from Main.ScreenShot_Main import ScreenShowWindow
from UI.ToolsWindow_Ui import Ui_ToolsWindow

class ToolsWindow(QMainWindow, Ui_ToolsWindow):
    obj: None #用于 线程的obj
    initImg = "img/QQ图片20210510115737.jpg"
    FILE_FILTER = "*.BMP *.GIF *.JPG *.JPEG *.PNG *.PBM *.PGM *.PPM *.XBM *.XPM"
    global_dict = {
        "TEMP_DIR": os.getcwd() + "/cache_img/",
        "SAVE_TEMP": 0,
        "FFT_DIR":os.getcwd() + "/fft_img/",
    }
    ERROR_LOG=''


    def AutoSet(func):
        def autosave(self, *args, **kwargs):

            try:
                debug=f"[AUTO-SET]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs}\n"
                self.ERROR_LOG+=debug
                print(
                    debug
                    )
                if args:
                    if args[0] == False:
                        f = func(self, **kwargs)
                    else:
                        f = func(self, *args, **kwargs)
                else:
                    f = func(self, *args, **kwargs)

                self.__setDemoImg()
                self.__UpdateImgInfo()

                return f
            except Exception as e:
                debug=f"{type(self).__name__}->{func.__name__}:{e.__str__()}\n"
                self.ERROR_LOG+=debug
                self.showError(debug)

        return autosave

    def logging(func):
        def wrapper(self, *args, **kwargs):
            try:
                debug=f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs} \n"
                self.ERROR_LOG+=debug
                print(debug
                    )
                t1 = time.time()
                if args:
                    if args[0] == False:
                        f = func(self, **kwargs)
                    else:
                        f = func(self, *args, **kwargs)
                else:
                    f = func(self, *args, **kwargs)
                t2 = time.time()
                print(f"[TIME COST]:func **{func.__name__}** cost {t2 - t1} s")
                debug=f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} leaved func **{func.__name__}** args={args} kwargs={kwargs} \n"
                print(debug)
                self.ERROR_LOG+=debug
                return f
            except Exception as e:
                err=f"{type(self).__name__}->{func.__name__}:{e.__str__()}\n"
                self.ERROR_LOG+=err
                self.showError(err)
                self.__withdraw()
        return wrapper


    @logging
    def __init__(self, *args, **kwargs):
        # 调用父类构造
        super(ToolsWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.demoLabel.setStBar(self.stBar)
        self.scrollAreaWidgetContents_3.setMouseTracking(1)
        self.backup = []
        self.screenShotWindow = ScreenShowWindow(self)
        self.customDialog = CustomFilter(self)
        self.obj=None

        # self.setWindowOpacity(1)
        self.setWindowTitle("图像蕴含着许多你不知道的事^^ By - Yjc")




        """临时图片格式"""
        # TEMP_FORMAT = self.formatBox.currentIndex()
        self.__specificConn()

        """初始化一个测试图片"""

        self.__readImg(self.initImg)
        if not os.path.exists(self.getGlobalValue("TEMP_DIR")):
            os.mkdir(self.getGlobalValue("TEMP_DIR"))
        if not os.path.exists(self.getGlobalValue("FFT_DIR")):
            os.mkdir(self.getGlobalValue("FFT_DIR"))
        self.tempFileName = ''
    def setGlobalValue(self,s: str, v):
        self.global_dict[s] = v

    def getGlobalValue(self,s):
        return self.global_dict[s]

    def getTempFileName(self):
        p = f"{self.getGlobalValue('TEMP_DIR')}{str(time.time()).replace('.','-')}.{self.formatBox.currentText()}"
        return p
    @logging
    def __specificConn(self):
        """
        专门用来绑定 connect
        :return:
        """
        # self.dockWidget_2.resize.connect(self.__resizeDock)
        """可视化"""
        self.graphicsView_3.plot.setTitle("图像RGB通道直方图")

        self.graphicsView_6.plot.setTitle("图像灰度直方图")


        """图像编辑开始"""
        self.readImgBtn.clicked.connect(self.__readImg)
        self.resizeImgBtn.clicked.connect(self.__resizeImg)
        self.fillImgBtn.clicked.connect(self.__autoFillImg)
        self.saveImgBtn.clicked.connect(self.__saveImg)
        self.blendBtn.clicked.connect(self.__blendImg)
        self.alphaCompositeBtn.clicked.connect(self.__alphaCompositeImg)
        self.copyImgBtn.clicked.connect(self.__copyImg)

        self.screenShotWindow.signals_copyImg.connect(self.__crop)
        self.restoreSizeBtn.clicked.connect(self.__restoreSize)
        self.changeRotBtn.clicked.connect(self.__rotateImg)

        self.withdrawBtn.clicked.connect(self.__withdraw)
        self.penBtn.clicked.connect(self.__penDownImg)
        self.penUpBtn.clicked.connect(self.__penUpImg)
        self.expandBtn.clicked.connect(self.__expandImg)
        self.chopsBtn.clicked.connect(self.__chopsImg)
        self.screenShotWindow.signals_ScreenShot.connect(self.__screenShot)
        self.pasteBtn.clicked.connect(self.__pasteImg)

        def updateInfo(r):
            self.sizeLabel.setText(f"({r.width()},{r.height()})")

        self.demoLabel.sizeChanged.connect(updateInfo)



        """图像变换开始"""
        self.newImgBtn.clicked.connect(self.__createNewImg)
        self.changePatternBtn.clicked.connect(self.__convertPattern)
        self.filterBtn.clicked.connect(self.__filterImg)

        self.histogramBalancedBtn.clicked.connect(self.__histogramBalanced)
        self.customFilterBtn.clicked.connect(self.__customFliter)
        self.randomNoiseBtn.clicked.connect(self.__randomNoise)
        self.gaussianNoiseBtn.clicked.connect(self.__gaussianNoise)
        self.saltNoiseBtn.clicked.connect(self.__saltAndPepperNoise)
        self.fftBtn.clicked.connect(self.__ffTransform)
        self.ifftBtn.clicked.connect(self.__iffTransform)
        # self.angleBtn.clicked.connect(self.__phaseImg)

        self.hideInfoBtn.clicked.connect(self.__hideInfoInImg)
        self.deHideInfoBtn.clicked.connect(self.deHideInfoImg)
        self.ArnoldBtn.clicked.connect(self.__ArnoldImg)
        self.ArnoldBtn_2.clicked.connect(self.__DeArnoldImg)
        self.customDialog.accepted.connect(self.__customizeFilter)


        """图像增强"""
        self.enhanceBtn.clicked.connect(self.__enhanceImg)
        """"""
        # self.actionopen_file.triggered.connect(self.__readImg)
        # self.actionsave_file.triggered.connect(self.__saveImg)

        # self.formatBox.currentIndexChanged.connect(lambda: self.setGlobalValue("TEMP_FORMAT", self.formatBox.currentIndex()))
        "二值化时出现阈值"
        self.patternBox.currentIndexChanged.connect(lambda idx:self.gammaGroupBox.show() if idx==CONVERT_MODE.CONVERT_MODE_GAMA else self.gammaGroupBox.hide())

        self.patternBox.currentIndexChanged.connect(lambda
                                                        index: self.thresholdBox.show() if index == CONVERT_MODE.CONVERT_MODE_1bit
                                                                                            else self.thresholdBox.hide())
        self.patternBox.currentIndexChanged.connect(lambda idx: Convert_Object.setGlobalValue("CONVERT_IDX", idx))
        """图像生成"""
        self.generateBtn.clicked.connect(self.__generateValidation)

        """全局参数绑定"""
        self.convCoreBox.hide()
        self.gammaGroupBox.hide()
        def filterChanged(idx,self):
            Convert_Object.setGlobalValue("FILTER_BOX", idx)
            self.radiusGroupBox.show() if idx == FILTER.GaussianBlur else self.radiusGroupBox.hide()
            self.rankEdit.show() if idx == FILTER.RANK else self.rankEdit.hide()
            self.convCoreBox.show() if idx == FILTER.RANK or idx == FILTER.MAX or idx == FILTER.MEDIAN or idx == FILTER.MIN or idx == FILTER.MODE else self.convCoreBox.hide()
            self.rankGroupBox.show() if idx == FILTER.RANK else self.rankGroupBox.hide()


        self.filterBox.currentIndexChanged.connect(lambda idx: filterChanged(idx,self))

        def editingFinished():
            try:
                if self.randomEdit.text()!="":
                    Convert_Object.setGlobalValue("RANDOM_NOISE_NUM", eval(self.randomEdit.text()))
                if  self.meanEdit.text()!="":

                    Convert_Object.setGlobalValue("GS_MEAD", eval(self.meanEdit.text()))
                if  self.sigmaEdit.text()!="":
                    Convert_Object.setGlobalValue("GS_SIGMA", eval(self.sigmaEdit.text()))
                if  self.saltEdit.text()!="":
                    Convert_Object.setGlobalValue("NOISE_PROPORTION", eval(self.saltEdit.text()))
                if  self.sizeEdit.text()!="":
                    Convert_Object.setGlobalValue("RANK_SIZE", eval(self.sizeEdit.text()))
                if  self.rankEdit.text()!="":
                    Convert_Object.setGlobalValue("RANK_LEVEL", eval(self.rankEdit.text()))
                if self.radiusEdit.text()!="":
                    Convert_Object.setGlobalValue("BLUR_RADIUS", eval(self.radiusEdit.text()))
                if self.gammaclineEdit.text()!="":
                    Convert_Object.setGlobalValue("GAMA_C",eval(self.gammaclineEdit.text()))
                if self.gammalineEdit.text()!="":
                    Convert_Object.setGlobalValue("GAMMA",eval(self.gammalineEdit.text()))

            except Exception as e:
                self.showError("注意不要乱输参数")
        self.gammalineEdit.editingFinished.connect(editingFinished)
        self.gammaclineEdit.editingFinished.connect(editingFinished)
        self.radiusEdit.editingFinished.connect(editingFinished)
        self.randomEdit.editingFinished.connect(editingFinished)
        self.meanEdit.editingFinished.connect(editingFinished)
        self.sigmaEdit.editingFinished.connect(editingFinished)
        self.saltEdit.editingFinished.connect(editingFinished)

        self.rankGroupBox.hide()


        self.sizeEdit.editingFinished.connect(editingFinished)
        self.rankEdit.editingFinished.connect(editingFinished)
        self.thresholdSlider.valueChanged.connect(lambda v: Convert_Object.setGlobalValue("L_THRESHOLD", v))

        self.saveTempCheck.stateChanged.connect(lambda f: self.setGlobalValue("SAVE_TEMP", f))

        self.chopsBox.currentIndexChanged.connect(lambda idx: Convert_Object.setGlobalValue("CHOPS", idx))
        self.new_image = ''


    def showError(self, e: str):

        QMessageBox.warning(self, '出错了!请联系开发者日志已经记录在当前当前目录的logs下,请联系开发者', e)
        if not os.path.exists("logs/"):
            os.mkdir("logs/")
        with open(f"logs/error-{time.time()}.txt",'a')as f:
            f.write(self.ERROR_LOG)
        self.ERROR_LOG=''
    # def __resizeDock(self):
    #     self.graphicsView.plot.setFixedWidth(self.dockWidget_2.width())
    #     self.graphicsView.plot.setFixedHeight(self.graphicsView.height())
    #
    #     self.graphicsView_2.plot.setFixedWidth(self.dockWidget_2.width())
    #     self.graphicsView_2.plot.setFixedHeight(self.graphicsView_2.height())
        # self.graphicsView.plot.setFixedHeight(self.graphicsView.height())
        # self.graphicsView_2.plot.setFixedHeight(self.graphicsView.height())
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.modifiers() == Qt.ControlModifier:
            if a0.key() == Qt.Key_Z:
                self.__withdraw()
            elif a0.key() == Qt.Key_N:
                self.__readImg()
            elif a0.key() ==Qt.Key_F:
                self.__autoFillImg()
            elif a0.key() == Qt.Key_C:
                self.__copyImg()
            elif a0.key()==Qt.Key_S:
                self.__saveImg()
            elif a0.key()==Qt.Key_R:
                self.demoLabel.setRestore()
        if a0.key()==Qt.Key_F1:
            self.scrollArea.verticalScrollBar().setValue(self.label_17.y())
        elif a0.key() ==Qt.Key_F2:
            self.scrollArea.verticalScrollBar().setValue(self.label_57.y())
        elif a0.key() == Qt.Key_F3:
            self.scrollArea.verticalScrollBar().setValue(self.label_58.y())
        elif a0.key() == Qt.Key_F4:
            self.scrollArea.verticalScrollBar().setValue(self.label_67.y())
        elif a0.key() == Qt.Key_F5:
            self.scrollArea.verticalScrollBar().setValue(self.label_69.y())
        elif a0.key()==Qt.Key_Space:
            self.dockWidget.show() if not self.dockWidget.isVisible() else self.dockWidget.hide()
            self.dockWidget_2.show() if not self.dockWidget_2.isVisible() else self.dockWidget_2.hide()
        # QMainWindow.keyPressEvent(self,a0)






    """
    图像编辑开始
    """

    @logging
    def __saveImg(self):
        path = QFileDialog.getSaveFileName(self, "保存路径", ".", "*." + self.formatBox.currentText())
        fn = path[0]
        if not fn:
            return

        self.new_image.save(fn)
        # img=Image.fromqimage(self.demoLabel.drawImg)

        # self.demoLabel.pixmap.save(fn)
        self.stBar.showMessage("已保存到" + fn)
        pass




    @logging
    def __withdraw(self):

        if self.backup:
            img=self.backup.pop()
            fn=self.getTempFileName()
            img.save(fn)
            self.new_image=Image.open(fn).copy()
            self.demoLabel.setImg(QImage(fn),fn)

            if not self.getGlobalValue("SAVE_TEMP"):
                os.remove(fn)
            self.obj=None
            if self.autoStretchBox.isChecked():
                self.demoLabel.setRestore()
            self.__UpdateImgInfo()
        else:
            QMessageBox.warning(self, '警告', '没东西撤回了亲')

    @logging
    def __UpdateImgInfo(self):


        self.obj = Convert_Object(self.new_image, Convert_Object.UPDATE_OP,parent=self)
        self.thr = QThread(self)
        self.obj.moveToThread(self.thr)
        def deleteObj():
            self.thr.exit(0)
            self.obj.deleteLater()
            self.obj=None
        self.obj.finished.connect(deleteObj)
        self.thr.start()
        self.thr.started.connect(self.obj.run)
        # self.new_image = self.obj.new_image.copy()

        # im = self.new_image
        #
        # arr = np.array(im)
        #
        # if len(arr.shape) == 2:
        #     width, height = arr.shape
        #     channels = 1
        # else:
        #     width, height, channels = arr.shape
        # # self.nameLabel.setText(self.demoLabel.imgPath)
        #
        # self.widthLabel.setText(str(height))
        # self.heightLabel.setText(str(width))
        # self.channelsLabel.setText(str(channels))
        # self.nameLabel.setText(self.demoLabel.imgPath.split('/')[-1])
        # self.formatLabel.setText(self.demoLabel.format)
        # stat = ImageStat.Stat(im)
        # self.extremaLabel.setText(str(stat._getextrema()))
        # self.pixelsNumLabel.setText(str(stat._getcount()))
        # self.pixelsSumLabel.setText(str(stat._getsum()))
        #
        # self.averageLabel.setText(str(stat._getmean()))
        #
        # # if np.mean(stat._getmean())<30:
        # #     self._3DWidget.w.setBackgroundColor((222,222,222))
        #
        # #根据平均rgb 设置背景颜色
        # if len(stat._getmean())>=3:
        #     rgb=stat._getmean()[:3]
        #
        #     rgb=list(map(int,rgb))
        #
        #     fontColor = (255 - rgb[0], 255 -rgb[1], 222)
        #
        #     rgba=f"background-color:rgba{(rgb[0],rgb[1],rgb[2],233)};"
        #     self.scrollAreaWidgetContents_3.setStyleSheet(rgba)
        #     style="QWidget#scrollAreaWidgetContents{%s}QLabel{%s}"%(rgba,f"color:rgb{fontColor};")
        #     self.scrollAreaWidgetContents.setStyleSheet(style)
        #     self.stBar.setStyleSheet(rgba+f"color:rgb{fontColor};")
        #
        #     self.scrollArea.setStyleSheet("QScrollBar:vertical{%s}"%rgba)
        #     dockstyle="""
        #     QDockWidget::title {
        #         %s
        #     }
        #     """%rgba
        #     self.dockWidget.setStyleSheet(dockstyle)
        #     self.dockWidget_2.setStyleSheet(dockstyle)
        #     self.dockWidget_3.setStyleSheet(dockstyle)
        #     # self._3DWidget.w.setBackgroundColor(rgb)
        #     # self.centralwidget.setStyleSheet(rgba)
        #
        #
        # else:
        #     g=stat._getmean()[0]
        #     g=int(g)
        #     # self._3DWidget.w.setBackgroundColor((g, g, g,100))
        #     self.scrollAreaWidgetContents_3.setStyleSheet(f"background-color:rgba{(g, g, g,100)}")
        #     ga=f"background-color:rgba{(255-g, 255-g, 255-g,100)}"
        #     style="QWidget#scrollAreaWidgetContents{%s}QLabel{%s}"%(ga,f"color:rgb{ga};")
        #     self.scrollAreaWidgetContents.setStyleSheet(style)
        #     self.scrollArea.setStyleSheet("QScrollBar:vertical{%s}" % ga)
        #     self.stBar.setStyleSheet(ga)
        #
        #     docks="""
        #     QDockWidget::title {
        #         %s
        #     }
        #     """ % ga
        #     self.dockWidget.setStyleSheet(docks)
        #     self.dockWidget_2.setStyleSheet(docks)
        #     self.dockWidget_3.setStyleSheet(docks)
        # self._3DWidget.w.clear()
        # self._3DWidget.setData(im)
        #
        # self.medianLabel.setText(str(stat._getmedian()))
        # self.rmsLabel.setText(str(stat._getrms()))
        # self.varLabel.setText(str(stat._getvar()))
        # self.stddevLabel.setText(str(stat._getstddev()))
        #
        # self.depthLabel.setText(str(self.demoLabel.drawImg.depth()))
        # self.patternLabel.setText(str(im.mode))
        # self.sizeLabel.setText(f"({width},{height})")
        #
        #
        #
        #
        #
        # hist =im.histogram() #np.reciprocal(np.array(),dtype=)
        # # im.getpi
        # if channels >= 3:
        #
        #     self.graphicsView_6.hide()
        #     self.graphicsView_3.show()
        #     self.graphicsView_3.plot.clear()
        #     self.graphicsView_3.plot.setXRange(0, 256)
        #     self.graphicsView_3.setData(hist[:256],'r')
        #     self.graphicsView_3.setData(hist[256:512],'g')
        #     self.graphicsView_3.setData(hist[512:768],'b')
        #
        #
        # elif channels == 1:
        #     self.graphicsView_3.hide()
        #     self.graphicsView_6.show()
        #     self.graphicsView_6.plot.clear()
        #     self.graphicsView_6.plot.setXRange(0, 256)
        #
        #     self.graphicsView_6.setData(hist,(200,200,200))



    @logging
    def __readImg(self, fn=None):

        imgPath = fn or QFileDialog.getOpenFileName(self, "选择一张图片", "", self.FILE_FILTER)
        fn = fn or imgPath[0]
        if fn:
            self.demoLabel.first=1
            self.demoLabel.imgPath = fn

            self.new_image=Image.open(fn)
            self.demoLabel.setImg(QImage(fn),fn)

            if self.backup:
                self.__convertInit()
            self.formatBox.setCurrentIndex(FORMAT_MODE.modeDict[self.demoLabel.format])
            self.widthEdit.setText(str(self.demoLabel.drawImg.width()))
            self.heightEdit.setText(str(self.demoLabel.drawImg.height()))

            self.__UpdateImgInfo()
    @logging
    def __convertInit(self):
        img = self.demoLabel.drawImg
        if not img:
            raise Exception("没有图片,你在变nm呢?")
            # QMessageBox.warning(self,'没有图片','你在变nm呢')
            return
        # 先备份
        self.backup.append(self.new_image.copy())
        fn=self.getTempFileName()
        img.save(fn)
        im=Image.open(fn).copy()
        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)
        return im
    @logging
    def __setDemoImg(self):
        """
        线程结束时 保存一个临时的图片 然后读进去
        """

        fn = self.getTempFileName()

        self.new_image.save(fn)
        self.demoLabel.setImg(QImage(fn), fn)


        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)
        if self.obj:
            self.obj.deleteLater()
            self.obj=None
        if self.autoStretchBox.isChecked():
            self.demoLabel.setRestore()

    @logging
    def __threadSetImg(self):

        self.new_image = self.obj.new_image.copy()
        self.thr.exit(0)
        self.obj.deleteLater()
        self.obj=None
        self.__setDemoImg()
        self.__UpdateImgInfo()



    # except Exception as e:
    # QMessageBox.warning(self, '错误的图片格式', "请选择正确的图片,例如:\nBMP GIF JPG JPEG PNG PBM PGM PPM XBM XPM")
    # self.showError("readImg:"+e.__str__())
    # @autoSaveTempFile
    @logging
    def __restoreSize(self):

        self.demoLabel.setRestore()

    @logging
    def __crop(self, r: QRect):
        self.__convertInit()
        fn=self.getTempFileName()
        self.demoLabel.drawImg.copy(r).save(fn)
        self.show()
        self.new_image = Image.open(fn).copy()
        self.demoLabel.setImg(QImage(fn),fn)
        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)
        self.__UpdateImgInfo()

    @logging
    def __screenShot(self,img):
        self.show()
        self.screenShotWindow.hide()
        self.__convertInit()
        fn=self.getTempFileName()
        img.save(fn)
        self.new_image=Image.open(fn).copy()
        self.demoLabel.setImg(img,fn)
        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)
        if self.autoStretchBox.isChecked():
            self.demoLabel.setRestore()
        self.__UpdateImgInfo()

    @logging
    def __copyImg(self):
        #     将当前图片输入到screenshot
        # 注意要深拷贝
        self.__convertInit()
        self.hide()
        self.screenShotWindow.copyImg(QImage(self.demoLabel.drawImg))



    @logging
    def __autoFillImg(self):

        if not self.demoLabel.hasScaledContents():
            # self.demoLabel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
            # self.demoLabel.setPx(self.backup.pop())
            self.demoLabel.r.setHeight(self.scrollAreaWidgetContents_3.height())
            self.demoLabel.r.setWidth(self.scrollAreaWidgetContents_3.width())
            self.demoLabel.setFixedHeight(self.scrollAreaWidgetContents_3.height())
            self.demoLabel.setFixedWidth(self.scrollAreaWidgetContents_3.width())
            self.demoLabel.setScaledContents(1)
            self.demoLabel.update()
        else:
            self.demoLabel.setFixedHeight(self.demoLabel.drawImg.height())
            self.demoLabel.setFixedWidth(self.demoLabel.drawImg.width())
            self.demoLabel.r.setHeight(self.demoLabel.drawImg.height())
            self.demoLabel.r.setWidth(self.demoLabel.drawImg.width())

            self.demoLabel.setScaledContents(0)
            self.demoLabel.update()

    @AutoSet
    @logging
    def __resizeImg(self):
        # 调用screenshot
        self.__convertInit()

        new_image = self.demoLabel.drawImg.scaled(int(self.widthEdit.text()), int(self.heightEdit.text()),
                                                  Qt.IgnoreAspectRatio,
                                                  Qt.FastTransformation if self.checkBox_2.isChecked() else Qt.SmoothTransformation)
        fn=self.getTempFileName()
        new_image.save(fn)
        img=Image.open(fn)
        self.new_image = img.copy()
        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)

    @AutoSet
    @logging
    def __rotateImg(self):

        new_image = self.__convertInit()
        new_image = new_image.rotate(int(self.rotatationEdit.text() if self.rotatationEdit.text()!="" else 0))

        if self.mirrorBox.currentIndex() == MIRROR.NO_MIRROR:
            pass
        elif self.mirrorBox.currentIndex() == MIRROR.FLIP_LEFT_RIGHT:
            new_image = new_image.transpose(Image.FLIP_LEFT_RIGHT)
        elif self.mirrorBox.currentIndex() == MIRROR.FLIP_TOP_BOTTOM:
            new_image = new_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.new_image = new_image

    @AutoSet
    @logging
    def __expandImg(self):

        new_image = self.__convertInit()
        size = int(self.expandSizeEdit.text() if self.expandSizeEdit.text()!="" else 0)
        color = int(self.expandColorEdit.text() if self.expandSizeEdit.text()!="" else 0)
        new_image = ImageOps.expand(new_image, border=size, fill=color)
        self.new_image = new_image
    @AutoSet
    @logging
    def __pasteImg(self):

        pastePos=self.pasteEdit.text()
        pastePos=(0,0) if pastePos=="" else eval(pastePos)

        new_image = self.__convertInit()

        other = QFileDialog.getOpenFileName(self, "选择另一张图片融合", ".", self.FILE_FILTER)[0]
        if other == '':
            return
        otherImg = Image.open(other)
        otherImg = otherImg.convert(new_image.mode)
        new_image.paste( otherImg, pastePos,mask=None)
        self.new_image = new_image

    @AutoSet
    @logging
    def __alphaCompositeImg(self):
        new_image = self.__convertInit()
        other = QFileDialog.getOpenFileName(self, "选择另一张图片融合", ".", self.FILE_FILTER)[0]
        if other == '':
            return
        otherImg = Image.open(other)
        otherImg = otherImg.convert(new_image.mode).resize(new_image.size)
        composite = Image.alpha_composite(new_image, otherImg)
        self.new_image = composite
    @AutoSet
    @logging
    def __blendImg(self):
        new_image = self.__convertInit()
        other = QFileDialog.getOpenFileName(self, "选择另一张图片融合", ".", self.FILE_FILTER)[0]
        if other == '' or self.blendAlphaEdit.text() == '':
            return
        otherImg = Image.open(other)
        otherImg = otherImg.convert(new_image.mode).resize(new_image.size)
        blend = Image.blend(new_image, otherImg, float(self.blendAlphaEdit.text() if self.blendAlphaEdit.text()!="" else 0.1))
        self.new_image = blend

    @logging
    def __chopsImg(self):
        new_image = self.__convertInit()
        other = QFileDialog.getOpenFileName(self, "选择另一张图片操作", ".", self.FILE_FILTER)[0]
        if other=="":
            return
        otherImg = Image.open(other)
        otherImg = otherImg.convert(new_image.mode).resize(new_image.size)

        thread = Convert_Object(new_image, Convert_Object.CHOPS_OP, otherImg)
        scale = self.scaleEdit.text()
        thread.scale = 1.0 if not scale else float(scale)
        offset = self.scaleEdit.text()
        thread.offset = 1 if not scale else int(offset)
        self.__getConvertThread(thread)
    @logging
    def __penUpImg(self):
        if not self.demoLabel.draw:
            self.showError("你需要先拿起画笔 画!")
            return
        self.demoLabel.draw=False
        fn=self.getTempFileName()
        self.demoLabel.drawImg.save(fn)
        self.new_image=Image.open(fn).copy()


        if not self.getGlobalValue("SAVE_TEMP"):
            os.remove(fn)
        self.__setDemoImg()
        self.__UpdateImgInfo()
    @logging
    def __penDownImg(self):
        self.__convertInit()
        color = QColorDialog.getColor()
        self.demoLabel.drawInit(color)
    @AutoSet
    @logging
    def __createNewImg(self):
        newmode=self.patternBox.currentText() if self.newModelineEdit.text()=="" else self.newModelineEdit.text()

        newWidth=128 if self.newWidthlineEdit_3.text()=="" else int(self.newWidthlineEdit_3.text())
        newHeight=128 if self.newHeightlineEdit_4.text()=="" else int(self.newHeightlineEdit_4.text())
        if newmode=="L" or newmode=="1":
            newBg=0 if self.newBglineEdit_5.text()=="" else eval(self.newBglineEdit_5.text())
        else:
            newBg = (0,0,0) if self.newBglineEdit_5.text() == "" else eval(self.newBglineEdit_5.text())

        self.new_image=Image.new(newmode,(newHeight,newWidth),newBg)

    """
    图像编辑结束
    """

    """
    图像操作开始
    """


    @logging
    def __getConvertThread(self, obj: Convert_Object):
        if self.obj==None:
            self.obj = obj
            self.thr = QThread(self)
            self.obj.moveToThread(self.thr)
            self.obj.finished.connect(self.__threadSetImg)
            # self.obj.finished.connect(self.obj.deleteLater)
            self.thr.start()
            self.thr.started.connect(self.obj.run)

    @logging
    def __convertPattern(self):
        if self.patternBox.currentIndex()==CONVERT_MODE.CONVERT_MODE_RGB:
            self.formatBox.setCurrentIndex(FORMAT_MODE.modeDict["jpg"])
        elif self.patternBox.currentIndex()==CONVERT_MODE.CONVERT_MODE_RGBA:
            self.formatBox.setCurrentIndex(FORMAT_MODE.modeDict["png"])
        new_image = self.__convertInit()
        thread = Convert_Object(new_image, Convert_Object.CONVERT_OP)
        thread.filename=self.getTempFileName()
        self.__getConvertThread(thread)
    @AutoSet
    @logging
    def __customizeFilter(self):
        new_image = self.__convertInit()

        kernal = eval(self.customDialog.plainTextEdit.toPlainText().replace("\n", ''))
        size = 3 if self.customDialog.comboBox.currentIndex() == 0 else 5
        scale = self.customDialog.scaleEdit.text() or None
        offset = self.customDialog.offsetEdit.text()
        new_image = new_image.filter(
            ImageFilter.Kernel((size, size), kernal, None if not scale else float(scale),
                               0 if not offset else int(offset)))
        self.customDialog.plainTextEdit.setPlainText(self.customDialog.plainTextEdit.toPlainText())
        self.new_image = new_image


    @logging
    def __customFliter(self):
        self.customDialog.show()


    @logging
    def __filterImg(self):
        new_image = self.__convertInit()
        thread = Convert_Object(new_image, Convert_Object.FILTER_OP)
        self.__getConvertThread(thread)


    @AutoSet
    @logging
    def __histogramBalanced(self):
        """
        :return:
        """
        """
        假设我们有四个灰度级a,b,c,d，做个类比的话可以将她们理解为四个描述情感的词喜、怒、哀、乐。
        一般情况下我们得到的直方图可认为是p(a)=0.5,p(b)=0.5,p(c)=0,p(d)=0，
        而均衡化后的直方图是p(a)=0.25,p(b)=0.25,p(c)=0.25,p(d)=0.25. 
        如果我们以均衡化前的词描述人的情感则只有喜、怒，而均衡化后的词则有喜、怒、哀、乐。试问，哪种情形能够描述人更细微的情感变化呢？
        这也是笔者认为直方图均衡化之后能够描述更多图像细节的原因。
        """
        """
        均衡化过程中，必须要保证两个条件：①像素无论怎么映射，一定要保证原来的大小关系不变，较亮的区域，依旧是较亮的，较暗依旧暗，只是对比度增大，绝对不能明暗颠倒
        如果是八位图像，那么像素映射函数的值域应在0和255之间的，不能越界。综合以上两个条件，累积分布函数是个好的选择，因为累积分布函数是单调增函数（控制大小关系），并且值域是0到1（控制越界问题），所以直方图均衡化中使用的是累积分布函数。
        """

        new_image = self.__convertInit()
        new_image = ImageOps.equalize(new_image)
        self.new_image=new_image


    @logging
    def __randomNoise(self):

        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.ADD_NOISE_OP)
        self.__getConvertThread(thread)

    @logging
    def __gaussianNoise(self):
        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.GS_NOISE_OP)
        self.__getConvertThread(thread)

    @logging
    def __saltAndPepperNoise(self):

        new_image = self.__convertInit()

        self.__getConvertThread(Convert_Object(new_image, Convert_Object.SALT_NOISE_OP))

    @logging
    def __ffTransform(self):
        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.FFT_OP,parent=self)
        self.__getConvertThread(thread)


    @logging
    def __iffTransform(self):
        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.IFFT_OP,parent=self)
        self.__getConvertThread(thread)


    # @AutoSet
    @logging
    def __hideInfoInImg(self):
        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.HIDE_INFO_OP,parent=self)
        self.__getConvertThread(thread)


    @logging
    def deHideInfoImg(self):
        new_image = self.__convertInit()

        thread = Convert_Object(new_image, Convert_Object.DEHIDE_INFO_OP,parent=self)
        self.__getConvertThread(thread)


    @AutoSet
    @logging
    def __ArnoldImg(self):
        times=self.ArnoldTimesEdit.text()
        times=1 if times=="" else int(times)
        img = np.array(self.__convertInit())
        if len(img.shape)>=3:

            r, c, channels = img.shape
            p = np.zeros((r, c, channels), np.uint8)
        else:
            r, c = img.shape
            channels=1
            p = np.zeros((r, c), np.uint8)


        a = self.aArnoldEdit.text()
        a = 1 if a=="" else int(a)
        b = self.bArnoldEdit.text()
        b=1 if b=="" else int(b)
        for _ in range(times):
            for i in range(r):
                for j in range(c):
                    x = (i + b * j) % r
                    y = (a * i + (a * b + 1) * j) % c
                    p[x, y] = img[i, j]
        self.new_image = Image.fromarray(p)
    @AutoSet
    @logging
    def __DeArnoldImg(self):
        times=self.ArnoldTimesEdit.text()
        times=1 if times=="" else int(times)

        img=np.array(self.__convertInit())

        if len(img.shape)>=3:

            r, c, channels = img.shape
            p = np.zeros((r, c, channels), np.uint8)
        else:
            r, c = img.shape
            channels=1
            p = np.zeros((r, c), np.uint8)

        a = self.aArnoldEdit.text()
        a = 1 if a=="" else int(a)
        b = self.bArnoldEdit.text()
        b=1 if b=="" else int(b)

        for _ in range(times):
            for i in range(r):
                for j in range(c):
                    x = ((a * b + 1) * i - b * j) % r
                    y = (-a * i + j) % c
                    p[x, y] = img[i, j]
        self.new_image=Image.fromarray(p)

    @AutoSet
    @logging
    def __generateValidation(self):
        self.__convertInit()
        # 创建一个 图片后 加入数字和英文
        w=self.vdWidthEdit.text()
        w=128 if w=="" else int(w)
        h=self.vdHeightEdit.text()
        h=64 if h=="" else int(h)
        bg=self.vdBgEdit.text()
        bg=tuple(np.random.randint(255,size=3)) if bg=="" else eval(bg)
        text=self.vdTextEdit.text()

        _char=[chr(i) for i in range(ord('A'),ord('Z')+1)]+[str(i) for i in range(10)]

        text=''.join([random.choice(_char) for i in range(4)]) if text=="" else text

        validation = Image.new("RGB", (w, h),bg)

        # size = 20
        fontSize = self.vdFontEdit.text()  # if size == '' else int(size)
        fontSize = 30 if fontSize=="" else int(fontSize)
        vdFontPath = r"C:\Windows\Fonts\Arial\arial.ttf" if self.vdFontPathEdit.text()=="" else self.vdFontPathEdit.text()


        font = ImageFont.truetype(vdFontPath, size=fontSize)

        xinterval=abs(w-len(text)*(fontSize//4))//(len(text))+fontSize//3

        yinterval=abs(h-len(text))//2-fontSize//2

        for i in range(len(text)):
            ever = Image.new("RGB", (fontSize, fontSize),bg)
            textDraw = ImageDraw.Draw(ever)
            textDraw.text((0,0) ,text[i], fill=(tuple(np.random.randint(100,255,size=3))), font=font)
            ever=ever.rotate(random.randint(-30,30),expand=True,fillcolor=bg)

            validation.paste(ever,((i)*(int(xinterval)), yinterval))

        self.new_image = validation

    """图像增强"""

    @AutoSet
    @logging
    def __enhanceImg(self):

        new_image = self.__convertInit()

        color = ENHANCE.getEnhance(ENHANCE.COLOR, new_image)
        c=self.colorEdit.text()
        c=1. if c=="" else float(c)
        new_image = color.enhance(c)
        contrast = ENHANCE.getEnhance(ENHANCE.CONTRAST, new_image)
        c=self.contrastEdit.text()
        c=1. if c=="" else float(c)
        new_image = contrast.enhance(c)
        brightness = ENHANCE.getEnhance(ENHANCE.BRIGHTNESS, new_image)
        c=self.brightnessEdit.text()
        c=1. if c=="" else float(c)
        new_image = brightness.enhance(c)
        sharpeness = ENHANCE.getEnhance(ENHANCE.SHARPNESS, new_image)
        c=self.sharpnessEdit.text()
        c=1. if c=="" else float(c)
        new_image = sharpeness.enhance(c)
        self.new_image = new_image
