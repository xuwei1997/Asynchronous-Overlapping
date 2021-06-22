#运用多个图像，寻找最优函数

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
# from multiprocessing.dummy import Pool as ThreadPool
import os
from functools import partial
from statistics import mean

def out_log(string):
    f = "log.txt"
    with open(f, "a") as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
        file.write(string + "\n")

def find_path_one_img(img_PATH,COOL, laplace_w, direction_w, magnitude_w):
    img_G, img_RGB=img_PATH

    img_G_path = os.path.join(r'/tmp/pycharm_project_836/gary1', img_G)
    img_RGB_path = os.path.join(r'/tmp/pycharm_project_836/rbg1', img_RGB)
    img_mark_path = os.path.join(r'/tmp/pycharm_project_836/mark_or', img_RGB)

    # print(img_G_path, img_RGB_path)

    contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)  # 获取初始二值化路径。返回路径和rgb图
    # 高斯滤波后生成特征图
    img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
    scissors = Scissors(img_rgb_gaussian, laplace_w=laplace_w, direction_w=direction_w, magnitude_w=magnitude_w,
                        use_dynamic_features=False)

    # 灰度图寻找较大边缘
    contours_g_out = []
    # scissors_list = []
    # cool_list = []
    for k in contours_g:
        if len(k) > 150:
            # print(len(k))
            contours_g_out.append(k)
            # scissors_list.append(scissors)
            # cool_list.append(COOL)

    # 叠加显示
    img_rgb_c = cv2.drawContours(img_rgb, contours_g_out, -1, (0, 255, 0), 3)

    # #  单线进程方法2！！
    Intelligent_scissors_par = partial(Intelligent_scissors, scissors=scissors, cool_number=COOL)
    # print('map')
    out_end = list(map(Intelligent_scissors_par, contours_g_out))
    # print(out_end)

    # 画边缘
    img_out = cv2.drawContours(img_rgb_c, out_end, -1, (255, 0, 0), 3)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    #处理路径并保存
    path_mask = str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w)
    # path_out = str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w)
    mask_dire=os.path.join(r'/tmp/pycharm_project_836/',path_mask)
    out_dire=os.path.join(mask_dire,'out_rgb/')
    if os.path.exists(mask_dire) == False:  # 查看是否有文件夹
        os.mkdir(mask_dire)
    if os.path.exists(out_dire) == False:  # 查看是否有文件夹
        os.mkdir(out_dire)

    img_out_path = os.path.join(out_dire, img_RGB)
    mask_out_path = os.path.join(mask_dire, img_RGB)

    cv2.imwrite(img_out_path, img_out)
    cv2.imwrite(mask_out_path, mask_out)

    # iou
    iou, pa = eval(mask_out_path, img_mark_path)

    return -iou  # 最优化取最小值！！取负数！！

def find_path_func(X):  # COOL缩放过
    COOL, laplace_w, direction_w, magnitude_w = X
    print(COOL, laplace_w, direction_w, magnitude_w)
    COOL = int(COOL * 100)

    path_gary = r'/tmp/pycharm_project_836/gary1'
    path_rgb = r'/tmp/pycharm_project_836/rbg1'

    # 按文件名排列
    f_gary = os.listdir(path_gary)
    f_rgb = os.listdir(path_rgb)
    f_gary = sorted(f_gary)
    f_rgb = sorted(f_rgb)
    f_zip=zip(f_gary,f_rgb)

    find_path_one_img_par=partial(find_path_one_img,COOL=COOL, laplace_w=laplace_w, direction_w=direction_w, magnitude_w=magnitude_w)
    niou=list(map(find_path_one_img_par,f_zip))
    print("niou")
    print(niou)

    log=str(niou)+'_'+str(mean(niou)) +str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w)
    out_log(log)
    print(log)

    return mean(niou)

if __name__ == '__main__':
    # X=[0.2,0.3,0.2,0.2]
    # iou=find_path_func(X)
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

