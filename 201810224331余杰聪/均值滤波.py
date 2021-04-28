from PIL import Image,ImageFilter
from matplotlib import pyplot as plt
import numpy as np
img=Image.open('woman.bmp')
blur=img.filter(ImageFilter.BLUR)
imgarr=np.array(img)

plt.imshow(imgarr,cmap='gray')
plt.show()