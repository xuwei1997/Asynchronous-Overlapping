# 寻找最优参数

from feature_extraction_recompose_2 import Scissors  # 更改参数
import numpy as np
from find_path import Intelligent_scissors, findContours_g
import cv2
from evaluation import eval
from sko.PSO import PSO
from sko.tools import set_run_mode
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool as Pool
# from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import os
from functools import partial


def find_path_func(X):  # COOL缩放过
    COOL, laplace_w, direction_w, magnitude_w = X
    print(COOL, laplace_w, direction_w, magnitude_w)
    COOL = int(COOL * 100)
    img_G_path = 'gary.jpg'
    img_RGB_path = 'rbg.jpg'
    contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)

    # 高斯滤波后生成特征图
    img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
    scissors = Scissors(img_rgb_gaussian, laplace_w=laplace_w, direction_w=direction_w, magnitude_w=magnitude_w,
                        use_dynamic_features=False)

    # 灰度图寻找较大边缘
    contours_g_out = []
    scissors_list = []
    cool_list = []
    for k in contours_g:
        if len(k) > 150:
            contours_g_out.append(k)
            scissors_list.append(scissors)
            cool_list.append(COOL)

    # #  单线进程方法！！
    # out_end = []
    # for c in contours_g_out:
    #     o = Intelligent_scissors(c, scissors, COOL)
    #     out_end.append(o)

    # #  单线进程方法2！！
    Intelligent_scissors_par = partial(Intelligent_scissors, scissors=scissors, cool_number=COOL)
    print('map')
    out_end =list(map(Intelligent_scissors_par,contours_g_out))
    print(out_end)

    # # 找边缘,多进程
    # p = Pool()
    # out_end = p.map(Intelligent_scissors, contours_g_out, scissors_list, cool_list)
    # print(out_end)

    #找边缘,多进程,偏函数
    # Intelligent_scissors_par=partial(Intelligent_scissors,scissors=scissors,cool_number=COOL)
    # p = Pool(14)
    # out_end = p.map(Intelligent_scissors_par, contours_g_out)
    # p.join()
    # print(out_end)

    # # 找边缘,多线程,偏函数
    # Intelligent_scissors_par=partial(Intelligent_scissors,scissors=scissors,cool_number=COOL)
    # p =ThreadPool()
    # out_end = p.map(Intelligent_scissors_par, contours_g_out)
    # p.join()
    # print(out_end)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    # 画
    mask_out_path = str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(
        magnitude_w) + '_' + img_RGB_path
    mask_out_path = os.path.join(r'/tmp/pycharm_project_836/img_out', mask_out_path)
    cv2.imwrite(mask_out_path, mask_out)

    # iou
    act_path = 'rbg_1.jpg'

    iou, pa = eval(mask_out_path, act_path)

    return -iou  # 最优化取最小值！！取负数！！


if __name__ == '__main__':
    # iou=find_path_func(20,0.3,0.2,0.2)
    # print(iou)

    set_run_mode(find_path_func, 'multiprocessing')
    print("pao1")
    pso = PSO(func=find_path_func, n_dim=4, pop=15, max_iter=30, lb=[0.1, 0.1, 0.1, 0.1], ub=[0.28, 0.8, 0.8, 0.8],
              w=0.8, c1=0.5, c2=0.5)
    print("pao2")
    pso.record_mode = True
    print("pao3")

    #5
    print("pao4")
    pso.run(5)
    print('best_x is ', pso.gbest_x, 'best_y is', pso.gbest_y)
    plt.plot(pso.gbest_y_hist)
    plt.savefig('5.png')
    record_dict = pso.record_value
    f = open('5.txt', 'w')
    f.write(str(record_dict) + '\n' + 'best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y))
    f.close()

    #10
    pso.run(5)
    print('best_x is ', pso.gbest_x, 'best_y is', pso.gbest_y)
    plt.plot(pso.gbest_y_hist)
    plt.savefig('10.png')
    record_dict = pso.record_value
    f = open('10.txt', 'w')
    f.write(str(record_dict) + '\n' + 'best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y))
    f.close()

    #15
    pso.run(5)
    print('best_x is ', pso.gbest_x, 'best_y is', pso.gbest_y)
    plt.plot(pso.gbest_y_hist)
    plt.savefig('15.png')
    record_dict = pso.record_value
    f = open('15.txt', 'w')
    f.write(str(record_dict) + '\n' + 'best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y))
    f.close()

    #20
    pso.run(5)
    print('best_x is ', pso.gbest_x, 'best_y is', pso.gbest_y)
    plt.plot(pso.gbest_y_hist)
    plt.savefig('20.png')
    record_dict = pso.record_value
    f = open('20.txt', 'w')
    f.write(str(record_dict) + '\n' + 'best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y))
    f.close()

    print(pso.record_value)
