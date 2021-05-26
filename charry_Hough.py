import numpy as np
import cv2
from math import cos, sin, pi
import math
from find_path import Intelligent_scissors
# from scissors.feature_extraction import Scissors
from feature_extraction_recompose import Scissors

if __name__ == '__main__':
    path = '10.jpg'
    img_rgb = cv2.imread(path)
    img_rgb = cv2.resize(img_rgb, (1296, 864), interpolation=cv2.INTER_CUBIC)
    res = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    # 显示
    # cv2.namedWindow("img_b", cv2.WINDOW_NORMAL)
    # cv2.imshow("img_b", res)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 将图进行中值模糊
    res = cv2.medianBlur(res, 5)
    cimg = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
    t = 0

    # 圆检测，第一个参数源图像的灰度图，第二个参数霍夫梯度法，
    # 第四个参数圆与圆心之间的最小距离，param1传递给canny边缘检测算子的高阈值，
    # 而低阈值为高阈值的一半。它表示在检测阶段圆心的累加器阈值。它越小的话，
    # 就可以检测到更多根本不存在的圆，而它越大的话，能通过检测的圆就更加接近完美的圆形了。
    circles = cv2.HoughCircles(res, cv2.HOUGH_GRADIENT, 1, 5000,
                               param1=29, param2=55, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))

    # 绘制圆

    # for (x, y, r) in circles[0, :]:
    #     # 绘制外圆
    #     cv.circle(cimg, (x, y), r, (0, 255, 0), 10)
    #     # 绘制圆心
    #     cv.circle(cimg, (x, y), 2, (0, 0, 255), 3)

    # 输出圆的信息以及圆上所有点的坐标
    for circle in circles[0]:
        # 输出圆的基本信息
        print(circle[2])
        # 坐标行列
        x = int(circle[0])
        y = int(circle[1])
        # 半径
        r = int(circle[2])
        print(x, y, r)
    # 计算边缘点集
    contour_cir = []
    for i in range(1, 360):
        angle = 57.3 * i
        # x1 = x + r * cos(angle * pi / 180)
        # y1 = y + r * sin(angle * pi / 180)
        # print('%.2f' % x1,',''%.2f' % y1)
        x1 = x + r * cos(math.radians((angle * pi / 180)))
        y1 = y + r * sin(math.radians((angle * pi / 180)))
        i += 1
        contour_cir.append([int(x1), int(y1)])
        # print([int(x1), int(y1)])
    contour_cir=np.array(contour_cir).reshape(-1, 1, 2)
    print(contour_cir.shape)
    # print(contour_cir)

    # 叠加显示
    img_rgb_c = cv2.drawContours(img_rgb, [contour_cir], -1, (0, 255, 0), 2)

    # 高斯滤波后生成特征图
    img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
    scissors = Scissors(img_rgb_gaussian, use_dynamic_features=False)  # 特征图！！

    # 单线程方法！！
    j = Intelligent_scissors(contour_cir, scissors,20)  # c为一个轮廓，scissors为特征图
    out_end = [j]



    # 画边缘
    img_out = cv2.drawContours(img_rgb_c , out_end, -1, (255, 0, 0), 2)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    # 画
    cv2.imwrite('h10-28.jpg', img_out)
    cv2.imwrite('h10m-28 .jpg', mask_out)
