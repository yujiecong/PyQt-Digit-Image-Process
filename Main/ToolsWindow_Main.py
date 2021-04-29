import os
import random
import datetime
import time


import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageStat, ImageChops

import matplotlib.pyplot as plt
from PIL import ImageDraw
from PIL import ImageFont

from .CustomFilter_Main import CustomFilter
from .Global_Main import CONVERT_MODE, MIRROR, getTempFileName, FILTER, CHOPS
from .Global_Main import getGlobalValue, setGlobalValue

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QColorDialog
from PyQt5.uic.Compiler.qtproxies import QtGui

from Main.ScreenShot_Main import ScreenShowWindow
from UI.ToolsWindow_Ui import Ui_ToolsWindow

class ENHANCE:
    COLOR = 0
    CONTRAST = 1
    BRIGHTNESS = 2
    SHARPNESS = 3

    @staticmethod
    def getEnhance(mode, img):
        if mode == ENHANCE.COLOR:
            return ImageEnhance.Color(img)
        elif mode == ENHANCE.CONTRAST:
            return ImageEnhance.Contrast(img)
        elif mode == ENHANCE.BRIGHTNESS:
            return ImageEnhance.Brightness(img)
        elif mode == ENHANCE.SHARPNESS:
            return ImageEnhance.Sharpness(img)


"""
警告 线程是不安全的
"""


class Convert_Object(QObject):
    finished = pyqtSignal()

    def process(self):
        self.finished.emit()
        pass

class Convert_Thread(QThread):
    """
    线程不安全
    """
    CONVERT_OP = 0
    FILTER_OP = 1
    ADD_NOISE_OP = 2
    GS_NOISE_OP = 3
    SALT_NOISE_OP = 4
    CHOPS_OP=5
    DEBUG=False

    def thread_logging(func):
        def wrapper(self, *args, **kwargs):
            print(f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} entered thread-func **{func.__name__}** args={args} kwargs={kwargs}")
            t1=time.time()
            # print(f"[START TIMER]:{t1}")
            try:
                if args:
                    if args[0]==False:
                        f=func(self,  **kwargs)
                    else:
                        f = func(self,*args, **kwargs)
                else:
                    f = func(self,*args, **kwargs)

                t2 = time.time()
                print(f"[THREAD TIME COST]:{t2 - t1}")
                print(
                f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} leaved thread-func **{func.__name__}** args={args} kwargs={kwargs}")
                return f
            except Exception as e:
                self.errorFlag=f"{type(self).__name__}->{func.__name__}:{e.__str__()}"
        return wrapper
    @thread_logging
    def __init__(self, new_image, op,other_image=None, parent=None):
        """
        线程不安全的
        """
        super(Convert_Thread, self).__init__(parent)

        self.other_image = other_image

        self.mean = getGlobalValue("GS_MEAD")
        self.sigma = getGlobalValue("GS_SIGMA")
        self.randomNum = getGlobalValue("RANDOM_NOISE_NUM")
        self.proportion = getGlobalValue("NOISE_PROPORTION")

        self.new_image = new_image

        self.filename = getTempFileName()  # +self.new_image.format
        self.errorFlag = ''
        self.threshold = getGlobalValue("L_THRESHOLD")
        #烦死了
        self.scale=0
        self.offset=0

        self.__op = op
    @thread_logging
    def run(self):
        if self.__op == self.CONVERT_OP:
            self.convert()
        elif self.__op == self.FILTER_OP:
            self.filter()
        elif self.__op == self.ADD_NOISE_OP:
            self.addRandomNoise()
        elif self.__op == self.GS_NOISE_OP:
            self.addGaussianNoise()
        elif self.__op == self.SALT_NOISE_OP:
            self.addSaltNoise()
        elif self.__op==self.CHOPS_OP:
            self.chops()
        pass
    @thread_logging
    def convert(self):

            convertIdx = getGlobalValue("CONVERT_IDX")
            if convertIdx == CONVERT_MODE.CONVERT_MODE_1:
                self.new_image = self.new_image.convert("L")
                arr = np.array(self.new_image)
                for i in range(self.new_image.height):
                    for j in range(self.new_image.width):
                        arr[i][j] = 255 if arr[i][j] >= self.threshold else 0
                self.new_image = Image.fromarray(arr)
                # self.new_image = self.new_image.convert("1")
                # self.new_image = self.new_image.convert("1")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_L:
                self.new_image = self.new_image.convert("L")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_P:
                self.new_image = self.new_image.convert("P")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_RGB:
                self.new_image = self.new_image.convert("RGB")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_RGBA:
                self.new_image = self.new_image.convert("RGBA")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_CMYK:
                self.new_image = self.new_image.convert("CMYK")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_YCbCr:
                self.new_image = self.new_image.convert("YCbCr")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_I:
                self.new_image = self.new_image.convert("I")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_F:
                self.new_image = self.new_image.convert("F")
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_REVERSE:
                arr = np.array(self.new_image)
                height, width, channels = arr.shape
                for i in range(height):
                    for j in range(width):
                        for k in range(channels):
                            arr[i, j, k] = 255 - arr[i, j, k]
                self.new_image = Image.fromarray(arr)
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_LOG:
                """
                改变换将输入中范围较窄的低灰度值映射为输出中较宽范围的灰度值。相反的，对高的输入灰度值也是如此。我们使用这种类型的变换来扩展图像中暗像素的值，同时压缩更高灰度级的值。反对数变换的作用与此相反。
                """
                arr = np.array(self.new_image)
                output = self.threshold * np.log(1.0 + arr)
                output = np.uint8(output + 0.5)
                self.new_image = Image.fromarray(output)
                ...
            elif convertIdx == CONVERT_MODE.CONVERT_MODE_GAMA:
                pass
                # lut = np.zeros(256, dtype=np.float32)
                # for i in range(256):
                #     lut[i] = c * i ** v
                # output_img = cv2.LUT(img, lut)  # 像素灰度值的映射
                # output_img = np.uint8(output_img + 0.5)



    @thread_logging
    def filter(self):

            filterIdx = getGlobalValue("FILTER_BOX")
            if filterIdx == FILTER.GaussianBlur:
                self.new_image = self.new_image.filter(ImageFilter.GaussianBlur)
            elif filterIdx == FILTER.BLUR:
                self.new_image = self.new_image.filter(ImageFilter.BLUR)
            elif filterIdx == FILTER.EDGE_ENHANCE:
                self.new_image = self.new_image.filter(ImageFilter.EDGE_ENHANCE)
            elif filterIdx == FILTER.FIND_EDGES:
                self.new_image = self.new_image.filter(ImageFilter.FIND_EDGES)
            elif filterIdx == FILTER.EMBOSS:
                self.new_image = self.new_image.filter(ImageFilter.EMBOSS)
            elif filterIdx == FILTER.CONTOUR:
                self.new_image = self.new_image.filter(ImageFilter.CONTOUR)
            elif filterIdx == FILTER.SHARPEN:
                self.new_image = self.new_image.filter(ImageFilter.SHARPEN)
            elif filterIdx == FILTER.SMOOTH:
                self.new_image = self.new_image.filter(ImageFilter.SMOOTH)
            elif filterIdx == FILTER.DETAIL:
                self.new_image = self.new_image.filter(ImageFilter.DETAIL)
            elif filterIdx == FILTER.RANK:
                self.new_image = self.new_image.filter(
                    ImageFilter.RankFilter(getGlobalValue("RANK_SIZE"), getGlobalValue("RANK_LEVEL")))
            elif filterIdx == FILTER.MEDIAN:
                self.new_image = self.new_image.filter(ImageFilter.MedianFilter(getGlobalValue("RANK_SIZE")))

            elif filterIdx == FILTER.MIN:
                self.new_image = self.new_image.filter(ImageFilter.MinFilter(getGlobalValue("RANK_SIZE")))

            elif filterIdx == FILTER.MAX:
                self.new_image = self.new_image.filter(ImageFilter.MaxFilter(getGlobalValue("RANK_SIZE")))
            elif filterIdx == FILTER.MODE:
                self.new_image = self.new_image.filter(ImageFilter.ModeFilter(getGlobalValue("RANK_SIZE")))
            self.new_image.save(self.filename)

    @thread_logging
    def addRandomNoise(self):

            arr = np.array(self.new_image)
            rows, cols, dims = arr.shape
            for i in range(self.randomNum):
                x = np.random.randint(0, rows)
                y = np.random.randint(0, cols)
                arr[x, y, :] = random.randint(0, 255)
            new_image = Image.fromarray(arr)
            new_image.save(self.filename)

    @thread_logging
    def addSaltNoise(self):

        imageArr = np.array(self.new_image)
        # 求得其高宽

        img_Y, img_X, img_Z = imageArr.shape
        # 噪声点的 X 坐标
        X = np.random.randint(img_X, size=(int(self.proportion * img_X * img_Y * img_Z),))
        # 噪声点的 Y 坐标
        Y = np.random.randint(img_Y, size=(int(self.proportion * img_X * img_Y * img_Z),))

        Z = np.random.randint(img_Z, size=(int(self.proportion * img_X * img_Y * img_Z),))
        # 噪声点的坐标赋值
        imageArr[Y, X, Z] = np.random.choice([0, 255], size=(int(self.proportion * img_X * img_Y * img_Z),))

        # 噪声容器
        # sp_noise_plate = np.ones_like(image_copy) * 127
        # 将噪声给噪声容器
        # sp_noise_plate[Y, X] = image_copy[Y, X]

        # new_image=Image.fromarray()

        new_image = Image.fromarray(imageArr)
        new_image.save(self.filename)

    #
    # except Exception as e:
    #     self.errorFlag = e.__str__()

    # pass
    @thread_logging
    def addGaussianNoise(self):
        imageArr = np.array(self.new_image)
        # 将图片灰度标准化
        img = imageArr / 255
        # 产生高斯 noise
        noise = np.random.normal(self.mean, self.sigma, img.shape)
        # 将噪声和图片叠加
        gaussian_out = img + noise
        # 将超过 1 的置 1，低于 0 的置 0
        gaussian_out = np.clip(gaussian_out, 0, 1)
        # 将图片灰度范围的恢复为 0-255
        gaussian_out = np.uint8(gaussian_out * 255)
        # 将噪声范围搞为 0-255
        # noise = np.uint8(noise*255)
        new_image = Image.fromarray(gaussian_out)
        new_image.save(self.filename)
    @thread_logging
    def chops(self):
            cop=getGlobalValue("CHOPS")
            if cop==CHOPS.ADD1:
                new_image=ImageChops.add(self.new_image,self.other_image,self.scale,self.offset)
            elif cop==CHOPS.ADD2:
                new_image = ImageChops.add_modulo(self.new_image, self.other_image)
            elif cop==CHOPS.SUB1:
                new_image = ImageChops.subtract(self.new_image, self.other_image,self.scale,self.offset)
            elif cop==CHOPS.SUB2:
                new_image = ImageChops.subtract_modulo(self.new_image, self.other_image)
            elif cop==CHOPS.AND:
                new_image = ImageChops.logical_and(self.new_image, self.other_image)
            elif cop==CHOPS.OR:
                new_image = ImageChops.logical_or(self.new_image, self.other_image)
            elif cop==CHOPS.XOR:
                new_image = ImageChops.logical_xor(self.new_image, self.other_image)
            elif cop==CHOPS.SCREEN:
                new_image = ImageChops.screen(self.new_image, self.other_image)
            elif cop==CHOPS.LIGHTER:
                new_image = ImageChops.lighter(self.new_image, self.other_image)
            elif cop==CHOPS.DARKER:
                new_image = ImageChops.darker(self.new_image, self.other_image)
            elif cop==CHOPS.DIFF:
                new_image = ImageChops.difference(self.new_image, self.other_image)
            elif cop==CHOPS.MUL:
                new_image = ImageChops.multiply(self.new_image, self.other_image)
            new_image.save(self.filename)


class ToolsWindow(QMainWindow, Ui_ToolsWindow):
    initImg = "img/lena.bmp"
    FILE_FILTER = "*.BMP *.GIF *.JPG *.JPEG *.PNG *.PBM *.PGM *.PPM *.XBM *.XPM"

    def autoSaveTempFile(func):
        def wrapper(self, *args, **kwargs):
            print(f"[AUTO-SAVE]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs}")
            try:
                if args:
                    if args[0]==False:
                        f=func(self,  **kwargs)
                    else:
                        f = func(self,*args, **kwargs)
                else:
                    f = func(self,*args, **kwargs)
                print(f"[SAVE]:{datetime.datetime.now()} {type(self).__name__} start func **__saveTempImg** ")
                self.__setDemoImg()
                print(f"[SAVE]:{datetime.datetime.now()} {type(self).__name__} leaved func **__saveTempImg** ")
                print(f"[INFO]:{datetime.datetime.now()} {type(self).__name__} start func **__getImgInfo** ")
                self.__getImgInfo()
                print(f"[INFO]:{datetime.datetime.now()} {type(self).__name__} leaved func **__getImgInfo** ")
                return f
            except Exception as e:
                self.showError(f"{type(self).__name__}->{func.__name__}:{e.__str__()}")
        return wrapper

    def logging(func):
        def wrapper(self, *args, **kwargs):
            print(f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} entered func **{func.__name__}** args={args} kwargs={kwargs}")
            t1=time.time()
            try:
                if args:
                    if args[0]==False:
                        f=func(self,  **kwargs)
                    else:
                        f = func(self,*args, **kwargs)
                else:
                    f = func(self,*args, **kwargs)
                    t2 = time.time()
                    print(f"[TIME COST]:func **{func.__name__}** cost {round(t2 - t1,9)}ms")
                    print(f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} leaved func **{func.__name__}** args={args} kwargs={kwargs}")
                    return f
            except Exception as e:
                self.showError(f"{type(self).__name__}->{func.__name__}:{e.__str__()}")
        return wrapper



    @logging
    def __init__(self, *args, **kwargs):
        # 调用父类构造
        super(ToolsWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.demoLabel.setStBar(self.stBar)
        self.backup = []
        self.screenShotWindow = ScreenShowWindow()
        """临时图片格式"""
        # TEMP_FORMAT = self.formatBox.currentIndex()
        self.__specificConn()

        """初始化一个测试图片"""

        self.__readImg(self.initImg)
        if not os.path.exists(getGlobalValue("TEMP_DIR")):
            os.mkdir(getGlobalValue("TEMP_DIR"))
        self.tempFileName = ''
        """初始化Action"""
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
        self.copyImgBtn.clicked.connect(self.__copyImg)
        self.screenShotWindow.signals_copyImg.connect(self.__crop)
        self.changeRotBtn.clicked.connect(self.__rotateImg)

        self.withdrawBtn.clicked.connect(self.__withdraw)
        self.penBtn.clicked.connect(self.__penDownImg)
        self.penUpBtn.clicked.connect(lambda: self.demoLabel._draw(False))
        self.expandBtn.clicked.connect(self.__expandImg)
        self.chopsBtn.clicked.connect(self.__chopsImg)

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
        """图像增强"""
        self.enhanceBtn.clicked.connect(self.__enhance)
        """"""
        self.actionopen_file.triggered.connect(self.__readImg)
        self.actionsave_file.triggered.connect(self.__saveImg)

        self.formatBox.currentIndexChanged.connect(lambda: setGlobalValue("TEMP_FORMAT", self.formatBox.currentIndex()))
        "二值化时出现阈值"
        self.patternBox.currentIndexChanged.connect(lambda
                                                        index: self.thresholdBox.show() if index == CONVERT_MODE.CONVERT_MODE_1
                                                                                           or index == CONVERT_MODE.CONVERT_MODE_GAMA else self.thresholdBox.hide())
        self.patternBox.currentIndexChanged.connect(lambda idx: setGlobalValue("CONVERT_IDX", idx))
        """图像生成"""
        self.generateBtn.clicked.connect(self.__generateValidation)


        """全局参数绑定"""
        self.filterBox.currentIndexChanged.connect(lambda idx: setGlobalValue("FILTER_BOX", idx))
        self.filterBox.currentIndexChanged.connect(lambda idx: self.rankGroupBox.show()
        if idx == FILTER.RANK or idx == FILTER.MAX or idx == FILTER.MEDIAN or idx == FILTER.MIN
           or idx == FILTER.MODE else self.rankGroupBox.hide())

        self.randomEdit.textChanged.connect(lambda text: setGlobalValue("RANDOM_NOISE_NUM", int(text)))
        self.meanEdit.textChanged.connect(lambda text: setGlobalValue("GS_MEAD", float(text)))
        self.sigmaEdit.textChanged.connect(lambda text: setGlobalValue("GS_SIGMA", float(text)))
        self.saltEdit.textChanged.connect(lambda text: setGlobalValue("NOISE_PROPORTION", float(text)))
        self.rankGroupBox.hide()

        self.sizeEdit.textChanged.connect(lambda text: setGlobalValue("RANK_SIZE", int(text)))
        self.rankEdit.textChanged.connect(lambda text: setGlobalValue("RANK_LEVEL", int(text)))
        self.thresholdSlider.valueChanged.connect(lambda v: setGlobalValue("L_THRESHOLD", v))

        self.saveTempCheck.stateChanged.connect(lambda f: setGlobalValue("SAVE_TEMP", f))

        self.chopsBox.currentIndexChanged.connect(lambda idx:setGlobalValue("CHOPS", idx))
        self.chopsBox.currentIndexChanged.connect(lambda idx:self.chopParaWidget.show()
        if idx==CHOPS.ADD1 or idx==CHOPS.SUB1 else self.chopParaWidget.hide())

        self.new_image=''
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
    def __saveTempImg(self):
        fn = getTempFileName()
        self.new_image.save(fn)
        self.demoLabel.setPx(QPixmap(fn))
    @logging
    def __setDemoImg(self):
        self.demoLabel.setImg(self.new_image.toqimage())


    """
    图像编辑开始
    """
    @logging
    def __saveImg(self):
        path = QFileDialog.getSaveFileName(self, "保存路径", ".", "*."+self.formatBox.currentText())
        fn = path[0]
        if not fn:
            return
        print(fn)
        self.new_image.save(fn)
        # img=Image.fromqimage(self.demoLabel.drawImg)

        # self.demoLabel.pixmap.save(fn)
        self.stBar.showMessage("已保存到" + fn)
        pass

    @autoSaveTempFile
    @logging
    def __blendImg(self):
        new_image = self.__convertInit()
        other = QFileDialog.getOpenFileName(self, "选择另一张图片融合", ".", self.FILE_FILTER)[0]
        if other=='' or self.blendAlphaEdit.text()=='':
            return
        otherImg = Image.open(other)
        new_image = new_image.convert(otherImg.mode)

        blend = Image.blend(new_image, otherImg, float(self.blendAlphaEdit.text()))
        self.new_image=blend

    @logging
    def __withdraw(self):
        if self.backup:
            self.demoLabel.setPx(self.backup.pop())
        else:
            QMessageBox.warning(self, '警告', '没东西撤回了亲')

    def __getImgInfo(self):
        if not self.demoLabel.imgPath:
            return
        im = Image.open(self.demoLabel.imgPath)
        arr = np.array(im)
        if len(arr.shape)==2:
            width, height = arr.shape
            channels=1
        else:
            width, height, channels = arr.shape
        self.nameLabel.setText(self.demoLabel.imgPath)
        self.widthEdit.setText(str(width))
        self.heightEdit.setText(str(height))
        self.widthLabel.setText(str(width))
        self.heightLabel.setText(str(height))
        self.channelsLabel.setText(str(channels))
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
        # print(self.demoLabel.drawImg.depth(),self.demoLabel.drawImg)
        self.depthLabel.setText(str(self.demoLabel.drawImg.depth()))
        self.patternLabel.setText(str(im.mode))

    @logging
    def __readImg(self, fn=None):

        imgName = fn or QFileDialog.getOpenFileName(self, "选择一张图片", "", self.FILE_FILTER)
        fn=fn or imgName[0]
        if fn:
            self.demoLabel.imgPath = fn
            self.new_image=Image.open(fn)
            self.demoLabel.setPx(QPixmap(fn))
            self.__getImgInfo()



    # except Exception as e:
    # QMessageBox.warning(self, '错误的图片格式', "请选择正确的图片,例如:\nBMP GIF JPG JPEG PNG PBM PGM PPM XBM XPM")
    # self.showError("readImg:"+e.__str__())
    @autoSaveTempFile
    @logging
    def __crop(self, r: QRect):
        self.demoLabel.crop(r)
        self.widthEdit.setText(str(r.width()))
        self.heightEdit.setText(str(r.height()))
        self.show()


    @logging
    def __copyImg(self):
        #     将当前图片输入到screenshot
        # 注意要深拷贝
        self.backup.append(self.demoLabel.backup())
        if self.demoLabel.pixmap:
            self.hide()
            self.screenShotWindow.copyImg(self.demoLabel.pixmap)
        else:
            QMessageBox.warning(self, '警告', '图片都没有,你在裁剪nm呢')


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
    @autoSaveTempFile
    @logging
    def __resizeImg(self):
        # 调用screenshot
        self.backup.append(self.demoLabel.backup())
        new_image= self.demoLabel.pixmap.scaled(int(self.widthEdit.text()), int(self.heightEdit.text()),
                                         Qt.IgnoreAspectRatio,
                                         Qt.FastTransformation if self.checkBox_2.isChecked() else Qt.SmoothTransformation)
        self.new_image = new_image

    @autoSaveTempFile
    @logging
    def __rotateImg(self):

            new_image = self.__convertInit()
            new_image = new_image.rotate(int(self.rotatationEdit.text()))

            if self.mirrorBox.currentIndex() == MIRROR.NO_MIRROR:
                pass
            elif self.mirrorBox.currentIndex() == MIRROR.FLIP_LEFT_RIGHT:
                new_image = new_image.transpose(Image.FLIP_LEFT_RIGHT)
            elif self.mirrorBox.currentIndex() == MIRROR.FLIP_TOP_BOTTOM:
                new_image = new_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.new_image=new_image

    @autoSaveTempFile
    @logging
    def __expandImg(self):

            new_image = self.__convertInit()
            size = int(self.expandSizeEdit.text())
            color = int(self.expandColorEdit.text())
            new_image = ImageOps.expand(new_image, border=size, fill=color)
            self.new_image=new_image

    @autoSaveTempFile
    @logging
    def __chopsImg(self):
        new_image = self.__convertInit()
        other = QFileDialog.getOpenFileName(self, "选择另一张图片操作", ".", self.FILE_FILTER)[0]
        otherImg=Image.open(other)
        new_image=new_image.convert(otherImg.mode)
        thread=Convert_Thread(new_image,Convert_Thread.CHOPS_OP,otherImg)
        scale=self.scaleEdit.text()
        thread.scale=1.0 if not scale else float(scale)
        offset=self.scaleEdit.text()
        thread.offset = 1 if not scale else int(offset)
        self.__getConvertThread(thread)

    @logging
    def __penDownImg(self):
        color = QColorDialog.getColor()
        self.demoLabel.drawInit(color)
        ...

    """
    图像编辑结束
    """

    """
    图像操作开始
    """


    @logging
    def __convertInit(self):
        img = self.demoLabel.drawImg
        if not img:
            raise Exception("没有图片,你在变nm呢?")
            # QMessageBox.warning(self,'没有图片','你在变nm呢')
            return
        # 先备份
        self.backup.append(self.demoLabel.backup())
        #只能是ppm 或者png
        # return Image.fromqimage(img)
        return self.new_image

    @autoSaveTempFile
    @logging
    def __getConvertThread(self, thread):

            obj = Convert_Object()
            obj.moveToThread(thread)
            thread.started.connect(obj.process)
            obj.finished.connect(thread.quit)
            obj.finished.connect(obj.deleteLater)
            thread.finished.connect(thread.deleteLater)

            def saveImg():
                if thread.errorFlag:
                    self.showError(thread.errorFlag)
                else:
                    self.new_image = thread.new_image
                    self.demoLabel.setImg(self.new_image.toqimage())
                thread.deleteLater()

            thread.finished.connect(saveImg)
            thread.start()


    @logging
    def __convertPattern(self):
            new_image = self.__convertInit()
            thread = Convert_Thread(new_image, Convert_Thread.CONVERT_OP)
            self.__getConvertThread(thread)

    @logging
    def __customFliter(self):
        dia = CustomFilter(self)
        dia.show()

        def accepted():

                new_image = self.__convertInit()
                kernal = eval(dia.plainTextEdit.toPlainText().replace("\n", ''))
                size = 3 if dia.comboBox.currentIndex() == 0 else 5
                scale = dia.scaleEdit.text() or None
                offset = dia.offsetEdit.text()
                new_image = new_image.filter(
                    ImageFilter.Kernel((size, size), kernal, None if not scale else float(scale),
                                       0 if not offset else int(offset)))
                self.new_image=new_image


        dia.accepted.connect(accepted)


    @logging
    def __filterImg(self):
        new_image = self.__convertInit()
        thread = Convert_Thread(new_image, Convert_Thread.FILTER_OP)
        self.__getConvertThread(thread)


    @logging
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

        img = self.demoLabel.drawImg
        fn = getTempFileName()
        img.save(fn)
        new_image = Image.open(fn)
        # new_image=new_image.convert("RGB")

        r, g, b = new_image.split()

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
        plt.title(self.demoLabel.imgPath)
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

        img = self.demoLabel.drawImg

        fn = getTempFileName()
        img.save(fn)
        new_image = Image.open(fn)
        plt.subplot(221)
        plt.axis('off')
        plt.title("均衡化前")
        plt.imshow(new_image)

        # new_image=new_image.convert("RGB")
        plt.subplot(222)
        plt.xlabel("灰度值(0~255)")
        plt.ylabel("出现频率")
        hist, bins = np.histogram(np.array(new_image).flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        # 均衡后的cdf
        cdf_normalized = cdf * hist.max() / cdf.max()

        r, g, b = new_image.split()
        ar = np.array(r).flatten()
        plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
        ag = np.array(g).flatten()
        plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
        ab = np.array(b).flatten()
        plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
        plt.plot(cdf_normalized, color='y')
        plt.legend(('cdf', 'r', 'g', 'b'), loc='upper left')

        new_image = ImageOps.equalize(new_image)

        hist, bins = np.histogram(np.array(new_image).flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        # 均衡后的cdf
        cdf_normalized = cdf * hist.max() / cdf.max()

        plt.subplot(223)

        plt.axis('off')
        plt.title("均衡化后")
        plt.imshow(new_image)

        plt.subplot(224)

        plt.xlabel("灰度值(0~255)")
        plt.ylabel("出现频率")

        r, g, b = new_image.split()

        ar = np.array(r).flatten()
        plt.hist(ar, 256, [0, 256], facecolor='r', edgecolor='r')
        ag = np.array(g).flatten()
        plt.hist(ag, 256, [0, 256], facecolor='g', edgecolor='g')
        ab = np.array(b).flatten()
        plt.hist(ab, 256, [0, 256], facecolor='b', edgecolor='b')
        plt.plot(cdf_normalized, color='y')
        plt.legend(('cdf', 'r', 'g', 'b'), loc='upper left')

        plt.show()

    @logging
    def __randomNoise(self):

        new_image = self.__convertInit()

        thread = Convert_Thread(new_image, Convert_Thread.ADD_NOISE_OP)
        self.__getConvertThread(thread)
    @logging
    def __gaussianNoise(self):

        new_image = self.__convertInit()

        thread = Convert_Thread(new_image, Convert_Thread.GS_NOISE_OP)
        self.__getConvertThread(thread)
    @logging
    def __saltAndPepperNoise(self):

        new_image = self.__convertInit()

        self.__getConvertThread(Convert_Thread(new_image, Convert_Thread.SALT_NOISE_OP))
    @logging
    def __ffTransform(self):

            img = np.array(self.new_image.convert("L"))
            f = np.fft.fft2(img)
            fshift = np.fft.fftshift(f)  # 将频谱对称轴从左上角移至中心
            magnitude_spectrum = 20 * np.log(np.abs(fshift))

            rows, cols = img.shape
            crow, ccol = int(rows / 2), int(cols / 2)
            fshift[crow - 30:crow + 30, ccol - 30:ccol + 30] = 0
            f_ishift = np.fft.ifftshift(fshift)
            img_back = np.fft.ifft2(f_ishift)
            img_back = np.abs(img_back)

            plt.subplot(221), plt.imshow(img, cmap='gray')
            plt.title('输入图'), plt.xticks([]), plt.yticks([])
            plt.subplot(222), plt.imshow(magnitude_spectrum, cmap='gray')
            plt.title('幅度谱'), plt.xticks([]), plt.yticks([])
            plt.subplot(223), plt.imshow(img_back)  # 恢复图像
            plt.title('相位谱'), plt.xticks([]), plt.yticks([])
            plt.subplot(224), plt.imshow(np.angle(f_ishift), cmap='gray')
            plt.title('fft'), plt.xticks([]), plt.yticks([])
            plt.show()

    @logging
    def __hideInfoInImg(self):

            color = (255, 255, 255)
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
            plt.imshow(carrier_image)

            height, width, channels = carrier_image_arr.shape
            size = self.fontSizeEdit.text()
            fontSize = 20 if size == '' else int(size)
            font = ImageFont.truetype(r"C:\Windows\Fonts\Arial\arial.ttf", size=fontSize)

            # 自动换行
            textList = list(plainText)
            fontLength = fontSize * length

            if fontLength >= width:
                for i in range(width, fontLength, width):
                    textList.insert(i, "\n")
                plainText = ''.join(textList)

            textDraw.text((0, height // 3), plainText, fill=color, font=font)

            # plt.imshow(hide_image)
            # plt.show()
            for i in range(height):
                for j in range(width):
                    # 把整幅图的B通道全设置为偶数
                    if carrier_image_arr[i, j, 0] % 2 == 1:
                        carrier_image_arr[i, j, 0] -= 1

            hide_image_arr = np.array(hide_image)
            for i in range(height):
                for j in range(width):

                    if tuple(hide_image_arr[i, j]) == color:
                        carrier_image_arr[i, j, 0] += 1
            plt.subplot(422)
            plt.axis("off")
            plt.imshow(carrier_image_arr)

            self.new_image=Image.fromarray(carrier_image_arr)
            self.__setDemoImg()

            img = Image.new(carrier_image.mode, carrier_image.size)
            img = np.array(img)
            h, w = img.shape[:2]
            # 新建一张图用来放解出来的信息
            hideInfoImg = np.zeros((h, w, 3), np.uint8)

            for i in range(h):
                for j in range(w):
                    # 发现B通道为奇数则为信息的内容

                    if carrier_image_arr[i, j, 0] % 2 == 1:
                        hideInfoImg[i, j, 0] = 255
                        hideInfoImg[i, j, 1] = 255
                        hideInfoImg[i, j, 2] = 255
            plt.subplot(423)
            plt.axis("off")
            plt.imshow(hide_image)

            plt.subplot(424)
            plt.axis("off")
            plt.imshow(hideInfoImg)
            plt.show()



    @autoSaveTempFile
    @logging
    def __generateValidation(self):
        self.__convertInit()
        #创建一个 图片后 加入数字和英文
        fn=getTempFileName()
        color = (255, 255, 255)
        validation = Image.new("RGB", (500,500))
        textDraw = ImageDraw.Draw(validation)
        # size = 20
        fontSize = 20 #if size == '' else int(size)
        font = ImageFont.truetype(r"C:\Windows\Fonts\Arial\arial.ttf", size=fontSize)

        textDraw.text((50, 50), "abvc", fill=color, font=font)

        self.new_image=validation
        pass
    """图像增强"""

    @autoSaveTempFile
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
            self.new_image=new_image

