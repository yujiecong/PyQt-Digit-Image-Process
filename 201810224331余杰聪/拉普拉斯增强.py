from PIL import Image,ImageFilter
from matplotlib import pyplot as plt
import numpy as np
img=Image.open('moon.jpg')
kernal=[1,1,1,1,-8,1,1,1,1]
img.filter(ImageFilter.Kernel((3,3),kernal))
imgarr=np.array(img,dtype="int8")

plt.imshow(imgarr,cmap='gray')
plt.show()