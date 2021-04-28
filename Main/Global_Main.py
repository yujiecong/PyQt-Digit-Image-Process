import os

global_dict = {
    "TEMP_DIR":os.getcwd()+ "/cache_img/",
    "TEMP_FORMAT": 0,
    "GS_MEAD":1,
    "GS_SIGMA":1,
    "RANDOM_NOISE_NUM":1000,
    "NOISE_PROPORTION":0.1,
    "CONVERT_IDX":0,
    "L_THRESHOLD":127,
    "FILTER_BOX":0,
    "RANK_SIZE":3,
    "RANK_LEVEL":3,
    "SAVE_TEMP":0,

}


def setGlobalValue(s: str, v):
    global_dict[s] = v
    print(s,v)


def getGlobalValue(s: str):
    return global_dict[s]


import time


def getTempFileName():
    return f"{getGlobalValue('TEMP_DIR')}{time.time()}.{FORMAT_MODE.modeDict[getGlobalValue('TEMP_FORMAT')]}"


class MIRROR:
    NO_MIRROR = 0
    FLIP_LEFT_RIGHT = 1
    FLIP_TOP_BOTTOM = 2


class FILTER:
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
    CONVERT_MODE_1 = 0
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
    FORMAT_JPG = 0
    FORMAT_PNG = 1
    FORMAT_PPM = 2
    FORMAT_GIF = 3

    modeDict = {
        FORMAT_JPG: "jpg",
        FORMAT_PNG: "png",
        FORMAT_PPM: "ppm",
        FORMAT_GIF: "gif",
    }
