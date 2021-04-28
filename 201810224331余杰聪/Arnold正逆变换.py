from PIL import Image,ImageFilter
from matplotlib import pyplot as plt
import numpy as np
def arnold(img):
    r, c = img.shape
    p = np.zeros((r, c), np.uint8)
    a = 1
    b = 1
    for i in range(r):
        for j in range(c):
            x = (i + b * j) % r
            y = (a * i + (a * b + 1) * j) % c
            p[x, y] = img[i, j]
    return p

def dearnold(img):
    r, c = img.shape
    p = np.zeros((r, c), np.uint8)
    a = 1
    b = 1
    for i in range(r):
        for j in range(c):
            x = ((a * b + 1) * i - b * j) % r
            y = (-a * i + j) % c
            p[x, y] = img[i, j]
    return p

img=Image.open('moon.jpg')
imgarr=np.array(img)
imgarnold=arnold(imgarr)
plt.imshow(imgarnold,cmap='gray')
plt.title("1 times of arnold")
plt.show()
for i in range(3):
    imgarnold=arnold(imgarnold)
    plt.title(f"{i+2} times of arnold")
    plt.imshow(imgarnold, cmap='gray')
    plt.show()

imgdearnold=dearnold(imgarnold)
plt.imshow(imgdearnold,cmap='gray')
plt.show()
