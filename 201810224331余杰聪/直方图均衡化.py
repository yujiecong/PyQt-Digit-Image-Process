import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
gray_level = 256  # 灰度级


def pixel_probability(img):
    """
    计算像素值出现概率
    :param img:
    :return:
    """
    assert isinstance(img, np.ndarray)

    prob = np.zeros(shape=(256))

    for rv in img:
        for cv in rv:
            prob[cv] += 1

    r, c = img.shape
    prob = prob / (r * c)

    return prob


def probability_to_histogram(img, prob):
    """
    根据像素概率将原始图像直方图均衡化
    :param img:
    :param prob:
    :return: 直方图均衡化后的图像
    """
    prob = np.cumsum(prob)  # 累计概率

    img_map = [int(i * prob[i]) for i in range(256)]  # 像素值映射

   # 像素值替换
    assert isinstance(img, np.ndarray)
    r, c = img.shape
    for ri in range(r):
        for ci in range(c):
            img[ri, ci] = img_map[img[ri, ci]]

    return img


def plot(y, name):
    """
    画直方图，len(y)==gray_level
    :param y: 概率值
    :param name:
    :return:
    """
    plt.figure(num=name)
    plt.bar([i for i in range(gray_level)], y, width=1)


if __name__ == '__main__':

    img = Image.open('rice.bmp')  # 读取灰度图
    img=np.array(img)
    prob = pixel_probability(img)
    plot(prob, "原图直方图")

    # 直方图均衡化
    img = probability_to_histogram(img, prob)

    prob = pixel_probability(img)
    plot(prob, "直方图均衡化结果")

    plt.show()