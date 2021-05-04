from PIL import Image,ImageFilter
from matplotlib import pyplot as plt
import numpy as np
def arnold(image):
    arnold_image = np.zeros(shape=image.shape,dtype=np.uint8)
    a=b=1
    # 2：计算N
    h, w = image.shape[0], image.shape[1]
    N = h  # 或N=w

    # 3：遍历像素坐标变换

    for ori_x in range(h):
        for ori_y in range(w):
            # 按照公式坐标变换
            new_x = (1 * ori_x + b * ori_y) % N
            new_y = (a * ori_x + (a * b + 1) * ori_y) % N

            arnold_image[new_x, new_y, :] = image[ori_x, ori_y, :]

    return arnold_image

def dearnold(image):
    decode_image = np.zeros(shape=image.shape,dtype=np.uint8)
    a=b=1

    h, w = image.shape[0], image.shape[1]
    N = h
    for ori_x in range(h):
        for ori_y in range(w):
            # 按照公式坐标变换
            new_x = ((a * b + 1) * ori_x + (-b) * ori_y) % N
            new_y = ((-a) * ori_x + ori_y) % N
            decode_image[new_x, new_y, :] = image[ori_x, ori_y, :]
    return decode_image

img=Image.open('QQ截图20210428202605.png')
imgarr=np.array(img)
imgarnold=arnold(imgarr)
plt.imshow(imgarnold,cmap='gray')
plt.title("1 times of arnold")
plt.show()


imgarnold=dearnold(imgarnold)
plt.title(f"{1} times of dearnold")
plt.imshow(imgarnold, cmap='gray')
plt.show()

