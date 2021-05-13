# import pyqtgraph.examples
# pyqtgraph.examples.run()

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

img_man = np.array(Image.open('微信图片_20210510212749.jpg').convert("L")) #直接读为灰度图像
# plt.subplot(121),plt.imshow(img_man,'gray'),plt.title('origial')
# plt.xticks([]),plt.yticks([])
# #--------------------------------
# rows,cols = img_man.shape
# mask = np.ones(img_man.shape,np.uint8)
# mask[rows//2-30:rows//2+30,cols//2-30:cols//2+30] = 0
# #--------------------------------
# f1 = np.fft.fft2(img_man)
# f1shift = np.fft.fftshift(f1)
# f1shift = f1shift*mask
# f2shift = np.fft.ifftshift(f1shift) #对新的进行逆变换
# img_new = np.fft.ifft2(f2shift)
# #出来的是复数，无法显示
# img_new = np.abs(img_new)
# #调整大小范围便于显示
# img_new = (img_new-np.amin(img_new))/(np.amax(img_new)-np.amin(img_new))
# plt.subplot(122),plt.imshow(img_new,'gray'),plt.title('Highpass')
# plt.xticks([]),plt.yticks([])
# plt.show()

# img_man = cv2.imread('woman.jpg',0) #直接读为灰度图像
plt.subplot(121),plt.imshow(img_man,'gray'),plt.title('origial')
plt.xticks([]),plt.yticks([])
#--------------------------------
rows,cols = img_man.shape
mask = np.zeros(img_man.shape,np.uint8)
mask[rows//2-20:rows//2+20,cols//2-20:cols//2+20] = 1
#--------------------------------
f1 = np.fft.fft2(img_man)
f1shift = np.fft.fftshift(f1)
f1shift = f1shift*mask
f2shift = np.fft.ifftshift(f1shift) #对新的进行逆变换
img_new = np.fft.ifft2(f2shift)
#出来的是复数，无法显示
img_new = np.abs(img_new)
#调整大小范围便于显示
img_new = (img_new-np.amin(img_new))/(np.amax(img_new)-np.amin(img_new))
plt.subplot(122),plt.imshow(img_new,'gray'),plt.title('lowpass')
plt.xticks([]),plt.yticks([])
plt.show()