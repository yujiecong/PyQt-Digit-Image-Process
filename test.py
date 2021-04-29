from decorator import decorator
# def decorater(func):
#     print('outer')
#     def mainFunc():
#         print(f"[DEBUG]:enter {func.__name__}")
#         return func(*args,**kwargs)
#     print('inner')
#     return mainFunc


@logging
def test():
    print('测试')
test()
# import sys
#
# import numpy as np
# from PIL import Image, ImageFilter
# from PyQt5.QtGui import QImage, QPixmap, QMovie
# import matplotlib.pyplot as plt
# from PyQt5.QtWidgets import QLabel, QApplication
#
# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
# fn='img/lena.bmp'
# im=Image.open(fn)
# new_image = im.filter(
#     ImageFilter.Kernel((3, 3), [1,1,1,
#                                 -3,-1,1,
#                                 1,1,1]))
#
# plt.imshow(new_image,cmap="gray")
# plt.show()
#
# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #
# #     ql=QLabel()
# #     mov=QMovie(fn)
# #     ql.setMovie(mov)
# #     mov.start()
# #     ql.show()
# #
# #
# #     sys.exit(app.exec_())
#
#
#
# # img=img.convert("1")
# # img.save("rgbMoon.jpg")
# # QPixmap.fromImage(img.toqimage()).save("moonPix","jpg")

