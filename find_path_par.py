#寻找最优参数

from feature_extraction_recompose_2 import Scissors #更改参数
import numpy as np
from find_path import Intelligent_scissors, findContours_g
import cv2
import os
from evaluation import eval

def find_path_fun(COOL=20,laplace_w=0.3, direction_w=0.2,magnitude_w=0.2):
    img_G_path='gary.jpg'
    img_RGB_path='rbg.jpg'
    contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)

    # 高斯滤波后生成特征图
    img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
    scissors = Scissors(img_rgb_gaussian,laplace_w=laplace_w, direction_w=direction_w,magnitude_w=magnitude_w, use_dynamic_features=False)

    # 灰度图寻找较大边缘
    contours_g_out = []
    for k in contours_g:
        if len(k) > 150:
            contours_g_out.append(k)

    # 单线进程方法！！
    out_end = []
    for c in contours_g_out:
        o = Intelligent_scissors(c, scissors, COOL)
        out_end.append(o)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    # 画
    mask_out_path = str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w) + '_' + img_RGB_path
    cv2.imwrite(mask_out_path, mask_out)


    #iou
    act_path = 'rbg_1.jpg'
    iou, pa = eval( mask_out_path, act_path)

    return iou




if __name__ == '__main__':
    iou=find_path_fun(20,0.3,0.2,0.2)
    print(iou)
