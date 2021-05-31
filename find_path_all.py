# 循环寻找文件夹中所有文件边界

import cv2
from find_path import Intelligent_scissors, findContours_g
from feature_extraction_recompose import Scissors
# from scissors.feature_extraction import Scissors
from pathos.multiprocessing import ProcessingPool as Pool
import numpy as np
import os


def find_path_one_img(img_G, img_RGB):
    COOL = 24

    img_G_path = os.path.join(r'./gary', img_G)
    img_RGB_path = os.path.join(r'./rbg', img_RGB)
    print(img_G_path, img_RGB_path)

    contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)  # 获取初始二值化路径。返回路径和rgb图
    # 高斯滤波后生成特征图
    img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
    scissors = Scissors(img_rgb_gaussian, use_dynamic_features=False)  # 特征图！！

    # 灰度图寻找较大边缘
    contours_g_out = []
    scissors_list = []
    cool_list = []
    for k in contours_g:
        if len(k) > 150:
            print(len(k))
            contours_g_out.append(k)
            scissors_list.append(scissors)
            cool_list.append(COOL)

    # 叠加显示
    img_rgb_c = cv2.drawContours(img_rgb, contours_g_out, -1, (0, 255, 0), 3)
    # cv2.imwrite('img_rgb_c.jpg', img_rgb_c)

    # scissors = Scissors(img_rgb, use_dynamic_features=True)

    # 找边缘,多进程
    # p = Pool()
    # out_end = p.map(Intelligent_scissors, contours_g_out, scissors_list, cool_list)
    # print(out_end)

    # 单线进程方法！！
    out_end = []
    for c in contours_g_out:
        o = Intelligent_scissors(c, scissors, COOL)
        out_end.append(o)

    # 画边缘
    img_out = cv2.drawContours(img_rgb_c, out_end, -1, (255, 0, 0), 3)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    # 画
    img_out_path = os.path.join(r'./c24-030103', img_RGB)
    mask_out_path = os.path.join(r'./c24-030103m', img_RGB)
    cv2.imwrite(img_out_path, img_out)
    cv2.imwrite(mask_out_path, mask_out)


if __name__ == '__main__':
    # path_gary = r'D:\python3test\Intelligent_Scissors\gary'
    # path_rgb=r'D:\python3test\Intelligent_Scissors\rbg'
    path_gary = r'/tmp/pycharm_project_836/gary'
    path_rgb = r'/tmp/pycharm_project_836/rbg'

    f_gary = os.listdir(path_gary)
    f_rgb = os.listdir(path_rgb)
    #按文件名排列
    f_gary=sorted(f_gary)
    f_rgb = sorted(f_rgb)
    print(f_gary)
    print(f_rgb)

    # find_path_one_img(f_gary[0],f_rgb[0])
    p0 = Pool()
    p0.map(find_path_one_img, f_gary, f_rgb)
