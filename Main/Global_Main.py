import os

from PIL import ImageEnhance
import time

class MIRROR:
    NO_MIRROR = 0
    FLIP_LEFT_RIGHT = 1
    FLIP_TOP_BOTTOM = 2

class CHOPS:
    ADD1=0
    ADD2=1
    SUB1=2
    SUB2=3
    AND=4
    OR=5
    XOR=6
    SCREEN=7
    LIGHTER=8
    DARKER=9
    DIFF=10
    MUL=11

class FILTER:
    """
    举一个滤波在我们生活中的应用：美颜的磨皮功能。如果将我们脸上坑坑洼洼比作是噪声的话，那么滤波算法就是来取出这些噪声，使我们自拍的皮肤看起来很光滑。
    """
    GaussianBlur = 0
    BLUR = 1
    EDGE_ENHANCE = 2
    FIND_EDGES = 3
    EMBOSS = 4
    CONTOUR = 5
    SHARPEN = 6
    SMOOTH = 7
    DETAIL = 8
    RANK=9
    MEDIAN=10
    MIN=11
    MAX=12
    MODE=13



class CONVERT_MODE:
    CONVERT_MODE_1bit = 0
    CONVERT_MODE_8bit=-1
    CONVERT_MODE_L = 1
    CONVERT_MODE_P = 2
    CONVERT_MODE_RGB = 3
    CONVERT_MODE_RGBA = 4
    CONVERT_MODE_CMYK = 5
    CONVERT_MODE_YCbCr = 6
    CONVERT_MODE_I = 7
    CONVERT_MODE_F = 8
    CONVERT_MODE_REVERSE = 9
    CONVERT_MODE_LOG = 10
    CONVERT_MODE_GAMA = 11


class FORMAT_MODE:

    modeDict = {
        "jpg": 0,
        "bmp": 1,
        "png": 2,
        "ppm": 3,
        "gif": 4,
    }

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