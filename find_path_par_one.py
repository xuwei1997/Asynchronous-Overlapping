#运用单个图像，寻找最优函数

from feature_extraction_recompose_2 import Scissors  # 更改参数
import numpy as np
from find_path import Intelligent_scissors, findContours_g
import cv2
from evaluation import eval
from sko.PSO import PSO
from sko.tools import set_run_mode
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool as Pool_pa
# from pathos.multiprocessing import Pool
from multiprocessing import Pool
# from multiprocessing.dummy import Pool as ThreadPool
import os
from functools import partial
# from statistics import mean

def out_log(string):
    f = "log.txt"
    with open(f, "a") as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
        file.write(string + "\n")

def find_path_one_img(img_PATH,COOL, laplace_w, direction_w, magnitude_w):
    print('find_path_one_img')
    try:
        img_G, img_RGB=img_PATH
        print(img_RGB,COOL, laplace_w, direction_w, magnitude_w)

        #读取的路径
        img_G_path = os.path.join(r'./gary1', img_G)
        img_RGB_path = os.path.join(r'./rbg1', img_RGB)
        img_mark_path = os.path.join(r'./mark_or', img_RGB)

        # 保存的路径
        path_mask = str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w)
        mask_dire = os.path.join(r'./', path_mask)
        out_dire = os.path.join(mask_dire, 'out_rgb/')
        if os.path.exists(mask_dire) == False:  # 查看是否有文件夹
            os.mkdir(mask_dire)
        if os.path.exists(out_dire) == False:  # 查看是否有文件夹
            os.mkdir(out_dire)

        img_out_path = os.path.join(out_dire, img_RGB)
        mask_out_path = os.path.join(mask_dire, img_RGB)

        #判断是否已经存在生成的图像
        if os.path.exists(mask_out_path) == False:  # 查看是否有文件，没有才需要生成

            # print(img_G_path, img_RGB_path)

            contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)  # 获取初始二值化路径。返回路径和rgb图
            # 高斯滤波后生成特征图
            img_rgb_gaussian = cv2.GaussianBlur(img_rgb, (5, 5), 0)  # 高斯滤波
            scissors = Scissors(img_rgb_gaussian, laplace_w=laplace_w, direction_w=direction_w, magnitude_w=magnitude_w,
                                use_dynamic_features=False)

            # 叠加显示
            img_rgb_c = cv2.drawContours(img_rgb, contours_g, -1, (0, 255, 0), 3)

            # # #  单线进程方法2！！
            Intelligent_scissors_par = partial(Intelligent_scissors, scissors=scissors, cool_number=COOL)
            # print('map')
            out_end = list(map(Intelligent_scissors_par, contours_g))
            # # print(out_end)

            #多进程方法!
            # print('map')
            # print("p2=Pool_pa()")
            # p2 = Pool_pa()
            # out_end = p2.map(Intelligent_scissors_par, contours_g)

            # 画边缘
            img_out = cv2.drawContours(img_rgb_c, out_end, -1, (255, 0, 0), 3)

            # 创造一个遮罩
            mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
            mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

            # 保存
            cv2.imwrite(img_out_path, img_out)
            cv2.imwrite(mask_out_path, mask_out)

        # iou
        iou, pa = eval(mask_out_path, img_mark_path)

    except BaseException as e:
        print('except:', e)
        iou=0
        print("iou=0")

    return -iou  # 最优化取最小值！！取负数！！


def find_path_func(X):  # COOL缩放过
    COOL, laplace_w, direction_w, magnitude_w = X
    # COOL = int(COOL*100)
    COOL = int(COOL)
    print(COOL, laplace_w, direction_w, magnitude_w)


    img_g_name = '1_2021-01-30_18.jpg'
    img_rgb_name = '1_2021-01-30_15.jpg'
    img_PATH=(img_g_name,img_rgb_name)
    niou=find_path_one_img(img_PATH,COOL,laplace_w,direction_w,magnitude_w)

    log=str(niou)+'_' +str(COOL) + '_' + str(laplace_w) + '_' + str(direction_w) + '_' + str(magnitude_w)
    out_log(log)
    # print(log)

    return niou


if __name__ == '__main__':
    # 防止线程错误！
    cv2.setNumThreads(1)

    set_run_mode(find_path_func, 'multiprocessing')
    # set_run_mode(find_path_func, 'multithreading')

    print("pso1")
    max_i = 60
    # pso = PSO(func=find_path_func, n_dim=4, pop=20, max_iter=1, lb=[0.12, 0.1, 0.1, 0.1], ub=[0.28, 0.8, 0.8, 0.8],  w=0.8, c1=0.5, c2=0.5)
    pso = PSO(func=find_path_func, n_dim=4, pop=14, max_iter=1, lb=[10, 0.1, 0.1, 0.1], ub=[40, 0.9, 0.9, 0.9],
              w=1.1, c1=0.5, c2=0.5)
    print("pso2")
    pso.record_mode = True

    print("pso3")
    for i in range(max_i):
        pso.run(1)
        # print('best_x is ', pso.gbest_x, 'best_y is', pso.gbest_y)
        plt.plot(pso.gbest_y_hist)
        plt.title('NO:'+str(i))
        plt.savefig('NO:'+str(i)+'_pso.png',dpi=300)
        record_dict = pso.record_value
        #pso.txt
        # print('pso.txt')
        f = open('pso.txt', 'w')
        f.write('NO:'+str(i)+'_'+str(record_dict) + '\n' + 'best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y))
        f.close()
        #pso_hist.txt
        # print('pso_hist.txt')
        f = open('pso_hist.txt', 'a')
        f.write('NO:' + str(i) +'_best_x is ' + str(pso.gbest_x) + 'best_y is' + str(pso.gbest_y) + '\n')
        f.close()

    print(pso.record_value)