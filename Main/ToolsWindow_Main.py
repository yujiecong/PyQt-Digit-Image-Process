import os
import datetime
import random
import time

import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat

import matplotlib.pyplot as plt
from PIL import ImageDraw
from PIL import ImageFont
from matplotlib.patches import Circle

from Thread_Main import Convert_Object
from .CustomFilter_Main import CustomFilter
from .Global_Main import CONVERT_MODE, MIRROR, FILTER, CHOPS, ENHANCE, FORMAT_MODE

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

from PyQt5.QtCore import Qt, QRect, QThread
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QColorDialog
from PyQt5.uic.Compiler.qtproxies import QtGui

from Main.ScreenShot_Main import ScreenShowWindow
from UI.ToolsWindow_Ui import Ui_ToolsWindow

class ToolsWindow(QMainWindow, Ui_ToolsWindow):
    obj: None #用于 线程的obj
    initImg = "img/lena.bmp"
    FILE_FILTER = "*.BMP *.GIF *.JPG *.JPEG *.PNG *.PBM *.PGM *.PPM *.XBM *.XPM"
    global_dict = {
        "TEMP_DIR": os.getcwd() + "\\cache_img\\",

        "SAVE_TEMP": 0,
    }


    def AutoSet(func):
        def autosave(self, *args, **kwargs):

            # try:
                print(
                    f"[AUTO-SET]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs}")
                if args:
                    if args[0] == False:
                        f = func(self, **kwargs)
                    else:
                        f = func(self, *args, **kwargs)
                else:
                    f = func(self, *args, **kwargs)

                self.__setDemoImg()
                self.__getImgInfo()

                return f
            # except Exception as e:
            #     self.showError(f"{type(self).__name__}->{func.__name__}:{e.__str__()}")

        return autosave

    def logging(func):
        def wrapper(self, *args, **kwargs):

            # try:
                print(
                    f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs}")
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
                print(
                    f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} leaved func **{func.__name__}** args={args} kwargs={kwargs}")
                return f
            # except Exception as e:
            #     self.showError(f"{type(self).__name__}->{func.__name__}:{e.__str__()}")

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
        self.tempFn=''


        """临时图片格式"""
        # TEMP_FORMAT = self.formatBox.currentIndex()
        self.__specificConn()

        """初始化一个测试图片"""

        self.__readImg(self.initImg)
        if not os.path.exists(self.getGlobalValue("TEMP_DIR")):
            os.mkdir(self.getGlobalValue("TEMP_DIR"))
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
        self.changePatternBtn.clicked.connect(self.__convertPattern)
        self.filterBtn.clicked.connect(self.__filterImg)
        self.histogramBtn.clicked.connect(self.__histogramShow)
        self.histogramBalancedBtn.clicked.connect(self.__histogramBalanced)
        self.customFilterBtn.clicked.connect(self.__customFliter)
        self.randomNoiseBtn.clicked.connect(self.__randomNoise)
        self.gaussianNoiseBtn.clicked.connect(self.__gaussianNoise)
        self.saltNoiseBtn.clicked.connect(self.__saltAndPepperNoise)
        self.fftBtn.clicked.connect(self.__ffTransform)
        self.hideInfoBtn.clicked.connect(self.__hideInfoInImg)
        self.customDialog.accepted.connect(self.__customizeFilter)
        """图像增强"""
        self.enhanceBtn.clicked.connect(self.__enhance)
        """"""
        # self.actionopen_file.triggered.connect(self.__readImg)
        # self.actionsave_file.triggered.connect(self.__saveImg)

        # self.formatBox.currentIndexChanged.connect(lambda: self.setGlobalValue("TEMP_FORMAT", self.formatBox.currentIndex()))
        "二值化时出现阈值"
        self.patternBox.currentIndexChanged.connect(lambda
                                                        index: self.thresholdBox.show() if index == CONVERT_MODE.CONVERT_MODE_1bit
                                                                                           or index == CONVERT_MODE.CONVERT_MODE_GAMA else self.thresholdBox.hide())
        self.patternBox.currentIndexChanged.connect(lambda idx: Convert_Object.setGlobalValue("CONVERT_IDX", idx))
        """图像生成"""
        self.generateBtn.clicked.connect(self.__generateValidation)

        """全局参数绑定"""
        self.filterBox.currentIndexChanged.connect(lambda idx: Convert_Object.setGlobalValue("FILTER_BOX", idx))
        self.filterBox.currentIndexChanged.connect(lambda idx: self.radiusGroupBox.show() if idx == FILTER.GaussianBlur  else self.radiusGroupBox.hide())
        self.filterBox.currentIndexChanged.connect(lambda idx: self.rankEdit.show() if idx == FILTER.RANK  else self.rankEdit.hide())
        self.filterBox.currentIndexChanged.connect(lambda idx: self.rankGroupBox.show()


        if idx == FILTER.RANK or idx == FILTER.MAX or idx == FILTER.MEDIAN or idx == FILTER.MIN
           or idx == FILTER.MODE else self.rankGroupBox.hide())

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


            except Exception as e:
                self.showError("注意不要乱输参数")

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

        self.chopsBox.currentIndexChanged.connect(lambda idx: self.setGlobalValue("CHOPS", idx))
        self.chopsBox.currentIndexChanged.connect(lambda idx: self.chopParaWidget.show()
        if idx == CHOPS.ADD1 or idx == CHOPS.SUB1 else self.chopParaWidget.hide())




        self.new_image = ''

    @logging
    def showError(self, e: str):
        self.stBar.showMessage(e)
        QMessageBox.warning(self, 'error!!!', e)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.modifiers() == Qt.ControlModifier:
            if a0.key() == Qt.Key_Z:
                self.__withdraw()
            elif a0.key() == Qt.Key_N:
                self.__readImg()


    # def __saveTempImg(self):
    #     fn = getTempFileName()
    #     self.new_image.save(fn)
    #     self.demoLabel.setImg(QPixmap(fn).toImage())





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
        else:
            QMessageBox.warning(self, '警告', '没东西撤回了亲')

    @logging
    def __getImgInfo(self):

        im = self.new_image

        arr = np.array(im)

        if len(arr.shape) == 2:
            width, height = arr.shape
            channels = 1
        else:
            width, height, channels = arr.shape
        # self.nameLabel.setText(self.demoLabel.imgPath)

        self.widthLabel.setText(str(height))
        self.heightLabel.setText(str(width))
        self.channelsLabel.setText(str(channels))
        self.nameLabel.setText(self.demoLabel.imgPath.split('\\')[-1])
        self.formatLabel.setText(self.demoLabel.format)
        stat = ImageStat.Stat(im)
        self.extremaLabel.setText(str(stat._getextrema()))
        self.pixelsNumLabel.setText(str(stat._getcount()))
        self.pixelsSumLabel.setText(str(stat._getsum()))
        self.averageLabel.setText(str(stat._getmean()))
        self.medianLabel.setText(str(stat._getmedian()))
        self.rmsLabel.setText(str(stat._getrms()))
        self.varLabel.setText(str(stat._getvar()))
        self.stddevLabel.setText(str(stat._getstddev()))

        self.depthLabel.setText(str(self.demoLabel.drawImg.depth()))
        self.patternLabel.setText(str(im.mode))
        self.sizeLabel.setText(f"({width},{height})")
    def __image2QImg(self,img:Image):
        # 默认是32位RGB
        fmt=QImage.Format_RGB32

        self.new_image = img.toqimage().convertToFormat(fmt)
        # pass
    # @logging
    def __readImg(self, fn=None):

        imgPath = fn or QFileDialog.getOpenFileName(self, "选择一张图片", "", self.FILE_FILTER)
        fn = fn or imgPath[0]
        if fn:
            self.demoLabel.first=1
            self.demoLabel.imgPath = fn
            # self.__image2QImg(Image.open(fn))
            self.new_image=Image.open(fn)
            self.demoLabel.setImg(QImage(fn),fn)

            if self.backup:
                self.__convertInit()
            self.formatBox.setCurrentIndex(FORMAT_MODE.modeDict[self.demoLabel.format])
            self.widthEdit.setText(str(self.demoLabel.drawImg.width()))
            self.heightEdit.setText(str(self.demoLabel.drawImg.height()))

            self.__getImgInfo()
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
        if self.tempFn!="":
            os.remove(self.tempFn)
        fn = self.getTempFileName()

        self.new_image.save(fn)

        self.demoLabel.setImg(QImage(fn),fn)


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
        self.__setDemoImg()


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
        self.tempFn=fn

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
        fn=self.getTempFileName()
        self.demoLabel.drawImg.save(fn)
        self.new_image=Image.open(fn)
        img=QImage(fn).copy()
        self.demoLabel.setImg(img,fn)
        self.tempFn=fn
    @logging
    def __penDownImg(self):
        self.__convertInit()
        color = QColorDialog.getColor()
        self.demoLabel.drawInit(color)


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
        new_image = self.__convertInit()
        thread = Convert_Object(new_image, Convert_Object.CONVERT_OP)
        thread.filename=self.getTempFileName()
        self.__getConvertThread(thread)

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
        self.__setDemoImg()

    @logging
    def __customFliter(self):
        self.customDialog.show()


    @logging
    def __filterImg(self):
        new_image = self.__convertInit()
        thread = Convert_Object(new_image, Convert_Object.FILTER_OP)
        self.__getConvertThread(thread)

    # @logging
    def __histogramShow(self):
        """
        :return:
        """
        """
        灰度直方图是灰度级的函数，描述的是图像中具有该灰度级的像元的个数。确定图像像元的灰度值范围，
        以适当的灰度间隔为单位将其划分为若干等级，以横轴表示灰度级，
        以纵轴表示每一灰度级具有的像元数或该像元数占总像元数的比例值，做出的条形统计图即为灰度直方图。
        
        直方图反映了图像中的灰度分布规律。它描述每个灰度级具有的像元个数，但不包含这些像元在图像中的位置信息。
        任何一幅特定的图像都有唯一的直方图与之对应，但不同的图像可以有相同的直方图。
        如果一幅图像有两个不相连的区域组成，并且每个区域的直方图已知，则整幅图像的直方图是该两个区域的直方图之和
        """

        new_image = self.__convertInit()
        # new_image=new_image.convert("RGB")

        channels = int(self.channelsLabel.text())
        if channels >= 3:
            if channels == 3:
                r, g, b = new_image.split()
            else:
                r, g, b, a = new_image.split()

            plt.subplot(221)
            ar = np.array(r).flatten()
            plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
            plt.legend(('r'), loc='upper left')
            plt.subplot(222)

            ag = np.array(g).flatten()

            plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
            plt.legend(('g'), loc='upper left')
            plt.subplot(223)
            ab = np.array(b).flatten()

            plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
            plt.legend(('b'), loc='upper left')

            plt.subplot(224)
            plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
            plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
            plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
            plt.legend(('r', 'g', 'b'), loc='upper left')

        elif channels == 1:

            ar = np.array(new_image).flatten()

            plt.subplot(111)
            plt.hist(ar, 256, [0, 256], facecolor='grey', edgecolor='grey')

            plt.legend(('grey'), loc='upper left')
        plt.title(self.demoLabel.imgPath.split('/')[-1])
        plt.xlabel("灰度值(0~255)")
        plt.ylabel("出现频率")
        plt.show()

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
        channels = int(self.channelsLabel.text())

        if channels >= 3:
            if channels == 3:
                r, g, b = new_image.split()
            else:
                r, g, b, a = new_image.split()

        plt.subplot(221)
        plt.axis('off')
        plt.title("均衡化前")
        plt.imshow(new_image, cmap="gray")

        plt.subplot(222)
        plt.xlabel("灰度值(0~255)")
        plt.ylabel("出现频率")
        if channels >= 3:
            ar = np.array(r).flatten()
            plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
            ag = np.array(g).flatten()
            plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
            ab = np.array(b).flatten()
            plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
        else:
            agr = np.array(new_image).flatten()
            plt.hist(agr, 256, [0, 256], facecolor='gray', edgecolor='gray')

        hist, bins = np.histogram(np.array(new_image).flatten(), 256, [0, 256])
        cdf = hist.cumsum()

        # 均衡前的cdf
        cdf_normalized = cdf * hist.max() / cdf.max()

        plt.plot(cdf_normalized, color='y')

        if channels >= 3:
            plt.legend(('cdf', 'r', 'g', 'b'), loc='upper left')
        else:
            plt.legend(('cdf', 'gray'), loc='upper left')

        new_image = ImageOps.equalize(new_image)
        plt.subplot(223)
        plt.axis('off')
        plt.title("均衡化后")
        plt.imshow(new_image, cmap='gray')

        hist, bins = np.histogram(np.array(new_image).flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        # 均衡后的cdf
        cdf_normalized = cdf * hist.max() / cdf.max()

        plt.subplot(224)
        plt.xlabel("灰度值(0~255)")
        plt.ylabel("出现频率")

        if channels >= 3:
            if channels == 3:
                r, g, b = new_image.split()
            else:
                r, g, b, a = new_image.split()
        if channels >= 3:
            ar = np.array(r).flatten()
            plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
            ag = np.array(g).flatten()
            plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
            ab = np.array(b).flatten()
            plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
            plt.legend(('cdf', 'r', 'g', 'b'), loc='upper left')
        else:
            agr = np.array(new_image).flatten()
            plt.hist(agr, 256, [0, 256], facecolor='grey', edgecolor='grey')
            plt.legend(('cdf', 'grey'), loc='upper left')

        plt.plot(cdf_normalized, color='y')
        plt.show()

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

        img = np.array(self.new_image.convert("L"))
        f = np.fft.fft2(img)

        fshift = np.fft.fftshift(f)  # 将频谱对称轴从左上角移至中心

        magnitude_spectrum = 20 * np.log(np.abs(fshift))
        rows, cols = img.shape
        crow, ccol = int(rows / 2), int(cols / 2)
        fshift[crow - 30:crow + 30, ccol - 30:ccol + 30] = 0
        #去中心化
        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)

        plt.subplot(221), plt.imshow(img, cmap='gray')
        plt.title('输入图'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('幅度谱'), plt.xticks([]), plt.yticks([])
        plt.subplot(223), plt.imshow(img_back, cmap='gray')  # 恢复图像
        plt.title('fft'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(np.angle(f_ishift), cmap='gray')
        plt.title('相位谱'), plt.xticks([]), plt.yticks([])
        plt.show()

    # @logging
    def __hideInfoInImg(self):

        carrier_image = self.__convertInit()
        hide_image = Image.new(carrier_image.mode, carrier_image.size)

        textDraw = ImageDraw.Draw(hide_image)
        # 计算要写入的大小
        plainText = self.hideInfoEdit.toPlainText()
        length = len(plainText)
        # 计算输入信息的字体大小
        carrier_image_arr = np.array(carrier_image)
        plt.subplot(421)

        plt.axis("off")
        plt.title("原图")
        plt.imshow(carrier_image)
        channels = int(self.channelsLabel.text())
        height, width = carrier_image_arr.shape[:2]
        size = self.fontSizeEdit.text()
        fontSize = 50 if size == '' else int(size)
        font = ImageFont.truetype(r"C:\Windows\Fonts\Arial\arial.ttf", size=fontSize)

        # 自动换行
        textList = list(plainText)
        fontLength = fontSize * length

        if fontLength >= width:
            for i in range(width, fontLength, width):
                textList.insert(i, "\n")
            plainText = ''.join(textList)
        if channels >= 3:
            color = (255, 255, 255)
        else:
            color = 100
        textDraw.text((0, height // 3), "asdadd", font=font, fill=color)

        # plt.imshow(hide_image)
        # plt.show()
        if channels >= 3:
            for i in range(height):
                for j in range(width):
                    # 把整幅图的B通道全设置为偶数
                    if carrier_image_arr[i, j, 0] % 2 == 1:
                        carrier_image_arr[i, j, 0] -= 1
        else:
            for i in range(height):
                for j in range(width):
                    # 把整幅图的B通道全设置为偶数
                    if carrier_image_arr[i, j] % 2 == 1:
                        carrier_image_arr[i, j] -= 1

        hide_image_arr = np.array(hide_image)
        if channels >= 3:
            for i in range(height):
                for j in range(width):

                    if tuple(hide_image_arr[i, j]) == color:
                        carrier_image_arr[i, j, 0] += 1
        else:
            for i in range(height):
                for j in range(width):

                    if hide_image_arr[i, j] == color:
                        carrier_image_arr[i, j] += 1
        plt.subplot(422)
        plt.title("隐藏后")
        plt.axis("off")
        plt.imshow(carrier_image_arr)

        self.new_image = Image.fromarray(carrier_image_arr)

        img = Image.new(carrier_image.mode, carrier_image.size)
        img = np.array(img)
        h, w = img.shape[:2]
        # 新建一张图用来放解出来的信息
        hideInfoImg = np.zeros((h, w, 3), np.uint8)
        if channels >= 3:
            for i in range(h):
                for j in range(w):
                    # 发现B通道为奇数则为信息的内容

                    if carrier_image_arr[i, j, 0] % 2 == 1:
                        hideInfoImg[i, j, 0] = color[0]
                        hideInfoImg[i, j, 1] = color[1]
                        hideInfoImg[i, j, 2] = color[2]
        else:
            for i in range(h):
                for j in range(w):
                    # 发现B通道为奇数则为信息的内容
                    if carrier_image_arr[i, j] % 2 == 1:
                        hideInfoImg[i, j] = color

        plt.subplot(423)
        plt.axis("off")
        plt.title("隐藏的信息")
        plt.imshow(hide_image)

        plt.subplot(424)
        plt.axis("off")
        plt.title("还原的信息")
        plt.imshow(hideInfoImg)
        plt.show()



    @AutoSet
    @logging
    def __generateValidation(self):
        self.__convertInit()
        # 创建一个 图片后 加入数字和英文
        w=self.vdWidthEdit.text()
        w=128 if w=="" else int(w)
        h=self.vdHeightEdit.text()
        h=64 if h=="" else int(h)
        bg=(0,43,56)
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
            textDraw.text((0,0) ,text[i], fill=(random.randint(100,255),random.randint(100,255),random.randint(100,255)), font=font)
            ever=ever.rotate(random.randint(-30,30),expand=True,fillcolor=bg)

            validation.paste(ever,((i)*(int(xinterval)), yinterval))

        self.new_image = validation

    """图像增强"""

    @AutoSet
    @logging
    def __enhance(self):

        new_image = self.__convertInit()

        color = ENHANCE.getEnhance(ENHANCE.COLOR, new_image)
        new_image = color.enhance(float(self.colorEdit.text()))
        contrast = ENHANCE.getEnhance(ENHANCE.CONTRAST, new_image)
        new_image = contrast.enhance(float(self.contrastEdit.text()))
        brightness = ENHANCE.getEnhance(ENHANCE.BRIGHTNESS, new_image)
        new_image = brightness.enhance(float(self.brightnessEdit.text()))
        sharpeness = ENHANCE.getEnhance(ENHANCE.SHARPNESS, new_image)
        new_image = sharpeness.enhance(float(self.sharpnessEdit.text()))
        self.new_image = new_image
