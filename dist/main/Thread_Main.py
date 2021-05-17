"""
警告 线程是不安全的
"""

# class Convert_Object(QObject):
import random
import time

import numpy as np
from PIL import Image, ImageFilter, ImageChops, ImageStat
from PIL import ImageDraw
from PIL import ImageFont
from PyQt5.QtCore import QObject, pyqtSignal

import datetime

from PyQt5.QtWidgets import QFileDialog

import Global_Main


class Convert_Object(QObject):
    """

    """
    CONVERT_OP = 0
    FILTER_OP = 1
    ADD_NOISE_OP = 2
    GS_NOISE_OP = 3
    SALT_NOISE_OP = 4
    CHOPS_OP = 5
    UPDATE_OP=6
    FFT_OP=7
    IFFT_OP=71


    HIDE_INFO_OP=8
    HIDE_INFO_OP2=82
    DEHIDE_INFO_OP=81
    DEBUG = False
    finished = pyqtSignal()
    para = {"GS_MEAD": .1,
            "GS_SIGMA": .1,
            "RANDOM_NOISE_NUM": 5000,
            "NOISE_PROPORTION": 0.1,
            "CONVERT_IDX": 0,
            "L_THRESHOLD": 127,
            "FILTER_BOX": 0,
            "RANK_SIZE": 3,
            "RANK_LEVEL": 3,
            "CHOPS": 0,
            "BLUR_RADIUS":2,
            "GAMA_C":1,
            "GAMMA":1,
            }


    def thread_logging(func):
        def wrapper(self, *args, **kwargs):
            print(
                f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} entered thread-func **{func.__name__}** args={args} kwargs={kwargs}")
            t1 = time.time()
            # print(f"[START TIMER]:{t1}")
            try:
                if args:
                    if args[0] == False:
                        f = func(self, **kwargs)
                    else:
                        f = func(self, *args, **kwargs)
                else:
                    f = func(self, *args, **kwargs)

                t2 = time.time()
                print(f"[THREAD TIME COST]:{t2 - t1}s")
                print(
                    f"[DEBUG]:{datetime.datetime.now()} {type(self).__name__} leaved thread-func **{func.__name__}** args={args} kwargs={kwargs}")
                return f
            except Exception as e:
                self.errorFlag = f"{type(self).__name__}->{func.__name__}:{e.__str__()}"
                self.parent().showError(self.errorFlag)

        return wrapper

    @staticmethod
    def setGlobalValue(k,v):

        Convert_Object.para[k]=v


    @staticmethod
    def getGlobalValue(s):
        return Convert_Object.para[s]
    @thread_logging
    def __init__(self, new_image, op, other_image=None, parent=None):
        """
        线程不安全的
        """
        super(Convert_Object, self).__init__(parent)

        self.other_image = other_image
        self.new_image = new_image
        self.filename = ''

        self.mean = self.getGlobalValue("GS_MEAD")
        self.sigma = self.getGlobalValue("GS_SIGMA")
        self.randomNum = self.getGlobalValue("RANDOM_NOISE_NUM")
        self.proportion = self.getGlobalValue("NOISE_PROPORTION")
        self.threshold = self.getGlobalValue("L_THRESHOLD")
        self.blurRadius=self.getGlobalValue("BLUR_RADIUS")
        self.errorFlag = ''
        # 烦死了
        self.scale = 0
        self.offset = 0

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
        elif self.__op == self.CHOPS_OP:
            self.chops()
        elif self.__op==self.UPDATE_OP:
            self.update()
        elif self.__op==self.HIDE_INFO_OP:
            self.hideTextInfo()
        elif self.__op==self.HIDE_INFO_OP2:
            self.hideImgInfo()
        elif self.__op==self.DEHIDE_INFO_OP:
            self.deHideInfo()
        elif self.__op==self.FFT_OP:
            self.fft()
        self.finished.emit()
    @thread_logging
    def ifft(this):
        self=this.parent()

        fn = self.getGlobalValue("FFT_DIR") + "outfft.txt"
        fftArr = np.loadtxt(fn).view(complex).T
        ifftArr=np.fft.ifftshift(fftArr)
        ifftArr=np.fft.ifft2(ifftArr)
        ifftArr=np.abs(ifftArr)

        ifftArr = ifftArr.astype('uint8')

        ifftImg=Image.fromarray(ifftArr)

        this.new_image=ifftImg
    @thread_logging
    def fft(this):
        self=this.parent()
        new_image=this.new_image
        img = np.array(new_image.convert("L"))
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)  # 将频谱对称轴从左上角移至中心
        self.fftImg=fshift
        magnitude_spectrum = 20 * np.log(np.abs(fshift)) #提高亮度
        # self.formatBox.setCurrentIndex(FORMAT_MODE.modeDict["tiff"])
        fn=self.getGlobalValue("FFT_DIR")+"outfft.txt"
        np.savetxt(fn,fshift.T.view(float))
        magnitude_spectrum=magnitude_spectrum.astype('uint8')
        this.new_image=Image.fromarray(magnitude_spectrum)
    @thread_logging
    def deHideInfo(this):
        # 开始还原]
        self=this.parent()
        hide_image = this.new_image
        hide_image_arr = np.array(hide_image)
        channels = int(self.channelsLabel.text())
        if channels >= 3:
            decoded=np.bitwise_and(hide_image_arr[:,:,2], 1)
        else:
            decoded=np.bitwise_and(hide_image_arr, 1)

        where=np.where( np.array(decoded) ==1, 255, 0).astype(np.uint8)
        this.new_image = Image.fromarray(where)



        # channels = int(self.channelsLabel.text())
        # height, width = hide_image_arr.shape[:2]
        # color = 255
        # h, w = height,width
        # if channels >= 3:
        #     hideInfoImg = np.zeros((h, w,3), np.uint8)
        # else:
        #     hideInfoImg = np.zeros((h, w), np.uint8)
        #
        #
        # if channels >= 3:
        #     for i in range(h):
        #         for j in range(w):
        #             if hide_image_arr[i, j, 2] % 2 == 1:
        #                 hideInfoImg[i, j,0] = color
        #                 hideInfoImg[i, j,1] = color
        #                 hideInfoImg[i, j,2] = color
        #
        # else:
        #     for i in range(h):
        #         for j in range(w):
        #             # 发现B通道为奇数则为信息的内容
        #             if hide_image_arr[i, j] % 2 == 1:
        #                 hideInfoImg[i, j] = color

    @thread_logging
    def hideImgInfo(self):
        parent=self.parent()
        parent.formatBox.setCurrentIndex(Global_Main.FORMAT_MODE.modeDict["png"])
        carrier_image = self.new_image
        path = QFileDialog.getOpenFileName(parent, "选择一张照片隐藏", ".", "*.*")
        fn = path[0]
        if not fn:
            return
        hide_image=Image.open(fn).resize((carrier_image.height,carrier_image.width))
        hide_image=hide_image.convert("L")

        hide_img_1= np.where(np.array(hide_image) > 128, 1, 0).astype(np.uint8)
        # hide_image.show()
        # Image.fromarray(hide_img_1).show()
        # 最低位变为 0
        lsb = np.bitwise_and(carrier_image, 0xFE)
        channels = int(parent.channelsLabel.text())
        if channels >= 3:
            lsb[:,:,2]+= hide_img_1
        else:
            lsb += hide_img_1
        self.new_image = Image.fromarray(lsb)
        # 将 logo 拼接到最低位(其中一个通道，也可以保留3个通道)


    @thread_logging
    def hideTextInfo(self):
        parent=self.parent()
        carrier_image = self.new_image

        hide_image = Image.new('RGB', carrier_image.size)
        # carrier_image_arr = np.array(carrier_image)

        plainText = parent.hideInfoEdit.toPlainText()

        textDraw = ImageDraw.Draw(hide_image)
        height, width = carrier_image.height,carrier_image.width

        size = parent.fontSizeEdit.text()
        fontSize = 50 if size == '' else int(size)
        font = ImageFont.truetype(r"C:\Windows\Fonts\微软雅黑\msyhbd.ttc", size=fontSize)
        color = 255
        textDraw.text((0, height // 3), plainText, font=font, fill=color)

        hide_img_1= np.where(np.array(hide_image) > 128, 1, 0).astype(np.uint8)

        lsb = np.bitwise_and(carrier_image, 0xFE)

        parent.formatBox.setCurrentIndex(Global_Main.FORMAT_MODE.modeDict["png"])


        lsb+= hide_img_1

        self.new_image = Image.fromarray(lsb)
        # if channels >= 3:
        #     parent.formatBox.setCurrentIndex(Global_Main.FORMAT_MODE.modeDict["png"])
        #     textDraw.text((0, height // 3), plainText, font=font, fill=(color, color, color))
        # else:
        #     textDraw.text((0, height // 3), plainText, font=font, fill=color)
        #
        # if channels >= 3:
        #     for i in range(height):
        #         for j in range(width):
        #             # 把整幅图的B通道全设置为偶数
        #             if carrier_image_arr[i, j, 2] % 2 == 1:
        #                 carrier_image_arr[i, j, 2] -= 1
        #
        # else:
        #     for i in range(height):
        #         for j in range(width):
        #             # 把整幅图的灰度通道全设置为偶数
        #             if carrier_image_arr[i, j] % 2 == 1:
        #                 carrier_image_arr[i, j] -= 1
        #
        # hide_image_arr = np.array(hide_image)
        # if channels >= 3:
        #     for i in range(height):
        #         for j in range(width):
        #
        #             if tuple(hide_image_arr[i, j, :3]) == (color, color, color):
        #                 carrier_image_arr[i, j, 2] += 1
        # else:
        #     for i in range(height):
        #         for j in range(width):
        #
        #             if hide_image_arr[i, j] == color:
        #                 carrier_image_arr[i, j] += 1


    @thread_logging
    def update(this):

        self=this.parent()

        im = this.new_image

        arr = np.array(im)

        if len(arr.shape) == 2:
            width, height = arr.shape
            channels = 1
        else:
            width, height, channels = arr.shape


        self.widthLabel.setText(str(height))
        self.heightLabel.setText(str(width))
        self.channelsLabel.setText(str(channels))
        self.nameLabel.setText(self.demoLabel.imgPath.split('/')[-1])
        self.formatLabel.setText(self.demoLabel.format)
        stat = ImageStat.Stat(im)
        self.extremaLabel.setText(str(stat._getextrema()))
        self.pixelsNumLabel.setText(str(stat._getcount()))
        self.pixelsSumLabel.setText(str(stat._getsum()))

        self.averageLabel.setText(str(stat._getmean()))

        #根据平均rgb 设置背景颜色
        if len(stat._getmean())>=3:
            rgb=stat._getmean()[:3]
            rgb=list(map(int,rgb))

            fontColor = (255 - rgb[0], rgb[1], 255 - rgb[2])

            rgba=f"background-color:rgba{(rgb[0],rgb[1],rgb[2],50)};"
            self.scrollAreaWidgetContents_3.setStyleSheet(rgba)
            style="QWidget#scrollAreaWidgetContents{%s}QLabel{%s}"%(rgba,f"color:rgb{fontColor};")
            self.scrollAreaWidgetContents.setStyleSheet(style)
            self.stBar.setStyleSheet(rgba+f"color:rgb{fontColor};")

            self.scrollArea.setStyleSheet("QScrollBar:vertical{%s}"%rgba)
            dockstyle="""
            QDockWidget::title {
                %s
            }
            """%rgba
            self.dockWidget.setStyleSheet(dockstyle)
            self.dockWidget_2.setStyleSheet(dockstyle)
            self.dockWidget_3.setStyleSheet(dockstyle)
            # self._3DWidget.w.setBackgroundColor(rgb)
            # self.centralwidget.setStyleSheet(rgba)
        else:
            g=stat._getmean()[0]
            g=int(g)
            # self._3DWidget.w.setBackgroundColor((g, g, g,100))
            self.scrollAreaWidgetContents_3.setStyleSheet(f"background-color:rgba{(g, g, g,100)}")
            ga=f"background-color:rgba{(255-g, 255-g, 255-g,100)}"
            style="QWidget#scrollAreaWidgetContents{%s}QLabel{%s}"%(ga,f"color:rgb{ga};")
            self.scrollAreaWidgetContents.setStyleSheet(style)
            self.scrollArea.setStyleSheet("QScrollBar:vertical{%s}" % ga)
            self.stBar.setStyleSheet(ga)

            docks="""
            QDockWidget::title {
                %s
            }
            """ % ga
            self.dockWidget.setStyleSheet(docks)
            self.dockWidget_2.setStyleSheet(docks)
            self.dockWidget_3.setStyleSheet(docks)

        self.medianLabel.setText(str(stat._getmedian()))
        self.rmsLabel.setText(str(stat._getrms()))
        self.varLabel.setText(str(stat._getvar()))
        self.stddevLabel.setText(str(stat._getstddev()))

        self.depthLabel.setText(str(self.demoLabel.drawImg.depth()))
        self.patternLabel.setText(str(im.mode))
        self.sizeLabel.setText(f"({width},{height})")

        self._3DWidget.w.clear()
        self._3DWidget.setData(im)

        hist =im.histogram() #np.reciprocal(np.array(),dtype=)
        # im.getpi
        if channels >= 3:

            self.graphicsView_6.hide()
            self.graphicsView_3.show()
            self.graphicsView_3.plot.clear()
            self.graphicsView_3.plot.setXRange(0, 256)
            self.graphicsView_3.setData(hist[:256],'r')
            self.graphicsView_3.setData(hist[256:512],'g')
            self.graphicsView_3.setData(hist[512:768],'b')


        elif channels == 1:
            self.graphicsView_3.hide()
            self.graphicsView_6.show()
            self.graphicsView_6.plot.clear()
            self.graphicsView_6.plot.setXRange(0, 256)

            self.graphicsView_6.setData(hist,(200,200,200))

    @thread_logging
    def convert(self):

        convertIdx = self.getGlobalValue("CONVERT_IDX")

        if convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_1bit:
            self.new_image = self.new_image.convert("L")
            arr = np.array(self.new_image)
            # for i in range(self.new_image.height):
            #     for j in range(self.new_image.width):
            #         arr[i][j] = 255 if arr[i][j] >= self.threshold else 0
            arr = np.where(arr> self.threshold, 255, 0).astype(np.uint8)
            self.new_image = Image.fromarray(arr)

        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_L:
            self.new_image = self.new_image.convert("L")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_P:
            self.new_image = self.new_image.convert("P")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_RGB:
            self.new_image = self.new_image.convert("RGB")

        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_RGBA:
            self.new_image = self.new_image.convert("RGBA")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_CMYK:
            self.new_image = self.new_image.convert("CMYK")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_YCbCr:
            self.new_image = self.new_image.convert("YCbCr")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_I:
            self.new_image = self.new_image.convert("I")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_F:
            self.new_image = self.new_image.convert("F")
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_REVERSE:
            arr = np.array(self.new_image)

            if len(arr.shape) >= 3:
                height, width, channels = arr.shape
                for i in range(height):
                    for j in range(width):
                        for k in range(channels):
                            arr[i, j, k] = 255 - arr[i, j, k]
            else:
                height, width = arr.shape
                for i in range(height):
                    for j in range(width):
                        arr[i, j] = 255 - arr[i, j]
            self.new_image = Image.fromarray(arr)
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_LOG:
            """
                改变换将输入中范围较窄的低灰度值映射为输出中较宽范围的灰度值。相反的，对高的输入灰度值也是如此。我们使用这种类型的变换来扩展图像中暗像素的值，同时压缩更高灰度级的值。反对数变换的作用与此相反。
                """
            arr = np.array(self.new_image)
            output = self.threshold * np.log(1.0 + arr)
            output = np.uint8(output + 0.5)
            self.new_image = Image.fromarray(output)
        elif convertIdx == Global_Main.CONVERT_MODE.CONVERT_MODE_GAMA:
            c=self.getGlobalValue("GAMA_C")
            gamma=self.getGlobalValue("GAMMA")
            self.new_image=np.array(self.new_image)
            self.new_image = Image.fromarray(np.uint8(c * np.power(self.new_image, gamma)))



    @thread_logging
    def filter(self):

        filterIdx = self.getGlobalValue("FILTER_BOX")
        if filterIdx == Global_Main.FILTER.GaussianBlur:
            self.new_image = self.new_image.filter(ImageFilter.GaussianBlur(self.blurRadius))
        elif filterIdx == Global_Main.FILTER.BLUR:
            self.new_image = self.new_image.filter(ImageFilter.BLUR)
        elif filterIdx == Global_Main.FILTER.EDGE_ENHANCE:
            self.new_image = self.new_image.filter(ImageFilter.EDGE_ENHANCE)
        elif filterIdx == Global_Main.FILTER.FIND_EDGES:
            self.new_image = self.new_image.filter(ImageFilter.FIND_EDGES)
        elif filterIdx == Global_Main.FILTER.EMBOSS:
            self.new_image = self.new_image.filter(ImageFilter.EMBOSS)
        elif filterIdx == Global_Main.FILTER.CONTOUR:
            self.new_image = self.new_image.filter(ImageFilter.CONTOUR)
        elif filterIdx == Global_Main.FILTER.SHARPEN:
            self.new_image = self.new_image.filter(ImageFilter.SHARPEN)
        elif filterIdx == Global_Main.FILTER.SMOOTH:
            self.new_image = self.new_image.filter(ImageFilter.SMOOTH)
        elif filterIdx == Global_Main.FILTER.DETAIL:
            self.new_image = self.new_image.filter(ImageFilter.DETAIL)
        elif filterIdx == Global_Main.FILTER.RANK:
            self.new_image = self.new_image.filter(
                ImageFilter.RankFilter(self.getGlobalValue("RANK_SIZE"),
                                       self.getGlobalValue("RANK_LEVEL")))
        elif filterIdx == Global_Main.FILTER.MEDIAN:
            self.new_image = self.new_image.filter(ImageFilter.MedianFilter(self.getGlobalValue("RANK_SIZE")))

        elif filterIdx == Global_Main.FILTER.MIN:
            self.new_image = self.new_image.filter(ImageFilter.MinFilter(self.getGlobalValue("RANK_SIZE")))

        elif filterIdx == Global_Main.FILTER.MAX:
            self.new_image = self.new_image.filter(ImageFilter.MaxFilter(self.getGlobalValue("RANK_SIZE")))
        elif filterIdx == Global_Main.FILTER.MODE:

            self.new_image = self.new_image.filter(ImageFilter.ModeFilter(self.getGlobalValue("RANK_SIZE")))

    @thread_logging
    def addRandomNoise(self):
        arr = np.array(self.new_image)
        # print(self.randomNum)

        if len(arr.shape) >= 3:
            rows, cols, dims = arr.shape
            for i in range(self.randomNum):
                x = np.random.randint(0, rows)
                y = np.random.randint(0, cols)

                arr[x, y, :] = random.randint(0, 255)

        else:
            rows, cols = arr.shape
            for i in range(self.randomNum):
                x = np.random.randint(0, rows)
                y = np.random.randint(0, cols)

                arr[x, y] = random.randint(0, 255)
        self.new_image = Image.fromarray(arr)

    @thread_logging
    def addSaltNoise(self):

        imageArr = np.array(self.new_image)
        # 求得其高宽
        if (len(imageArr.shape)==2):
            img_Y, img_X = imageArr.shape
            img_Z=1
        else:
            img_Y, img_X, img_Z = imageArr.shape
        # 噪声点的 X 坐标
        X = np.random.randint(img_X, size=(int(self.proportion * img_X * img_Y * img_Z),))
        # 噪声点的 Y 坐标
        Y = np.random.randint(img_Y, size=(int(self.proportion * img_X * img_Y * img_Z),))
        if len(imageArr.shape)>=3:
            Z = np.random.randint(img_Z, size=(int(self.proportion * img_X * img_Y * img_Z),))
        # 噪声点的坐标赋值
            imageArr[Y, X, Z] = np.random.choice([0, 255], size=(int(self.proportion * img_X * img_Y * img_Z),))
        else:
            imageArr[Y, X] = np.random.choice([0, 255], size=(int(self.proportion * img_X * img_Y),))
        # 噪声容器
        # sp_noise_plate = np.ones_like(image_copy) * 127
        # 将噪声给噪声容器
        # sp_noise_plate[Y, X] = image_copy[Y, X]

        # new_image=Image.fromarray()

        self.new_image = Image.fromarray(imageArr)

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
        # print(self.mean, self.sigma,)
        noise = np.random.normal(self.mean, self.sigma, img.shape)
        # 将噪声和图片叠加
        gaussian_out = img + noise
        # 将超过 1 的置 1，低于 0 的置 0
        gaussian_out = np.clip(gaussian_out, 0, 1)
        # 将图片灰度范围的恢复为 0-255
        gaussian_out = np.uint8(gaussian_out * 255)
        # 将噪声范围搞为 0-255
        # noise = np.uint8(noise*255)

        self.new_image = Image.fromarray(gaussian_out)

    @thread_logging
    def chops(self):
        cop = self.getGlobalValue("CHOPS")
        if cop == Global_Main.CHOPS.ADD1:
            new_image = ImageChops.add(self.new_image, self.other_image, self.scale, self.offset)
        elif cop == Global_Main.CHOPS.ADD2:
            new_image = ImageChops.add_modulo(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.SUB1:
            new_image = ImageChops.subtract(self.new_image, self.other_image, self.scale, self.offset)
        elif cop == Global_Main.CHOPS.SUB2:
            new_image = ImageChops.subtract_modulo(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.AND:
            new_image = ImageChops.logical_and(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.OR:
            new_image = ImageChops.logical_or(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.XOR:
            new_image = ImageChops.logical_xor(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.SCREEN:
            new_image = ImageChops.screen(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.LIGHTER:
            new_image = ImageChops.lighter(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.DARKER:
            new_image = ImageChops.darker(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.DIFF:
            new_image = ImageChops.difference(self.new_image, self.other_image)
        elif cop == Global_Main.CHOPS.MUL:
            new_image = ImageChops.multiply(self.new_image, self.other_image)
        self.new_image = new_image
