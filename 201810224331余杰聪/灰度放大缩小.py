from PIL import Image
from matplotlib import pyplot as plt
import numpy as np

img = Image.open('lena.bmp')
img = np.array(img)
# print(img.ndim)
fig1=plt.figure(1)
ax1=fig1.add_subplot(221);
ax1.imshow(img)
ax2=fig1.add_subplot(222); ax2.imshow(img, cmap ='gray')
ax3=fig1.add_subplot(223); ax3.imshow(img, cmap = plt.cm.gray)
ax4=fig1.add_subplot(224); ax4.imshow(img, cmap = plt.cm.gray_r)

fig2=plt.figure()
img=Image.fromarray(img)
img=img.resize((128,128))
ax1=fig2.add_subplot(211);ax1.imshow(img)
img=img.resize((1024,1024))
ax2=fig2.add_subplot(212);ax2.imshow(img)
# fig2.show()

plt.show()



