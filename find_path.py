import cv2
from feature_extraction_recompose import Scissors
# from scissors.feature_extraction import Scissors
import numpy as np
from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool as Pool
# from functools import partial

MAX_cou = 1000
COOL = 20


def list_logical_and(list_a, list_b):  # b长a短
    # print(list_a)
    # print(list_b)
    if list_a == []:
        list_a = [[0, 0]]
    if list_b == []:
        list_b = [[0, 0]]
    np_a = np.array(list_a)
    np_b = np.array(list_b)
    xa, ya = np_a.shape
    xb, yb = np_b.shape
    if xb >= xa:
        np_a_c = np.pad(np_a, ((0, xb - xa), (0, yb - ya)))  # 填充至长度相同
        and_np = np_a_c == np_b
    else:
        np_b_c = np.pad(np_b, ((0, xa - xb), (0, ya - yb)))  # 填充至长度相同
        and_np = np_b_c == np_a
    # print(and_np)
    return np.logical_and(and_np[:, 0], and_np[:, 1])


def findContours_g(img_G_path, img_RGB_path):
    # 读灰度图与RGB
    print(img_G_path)
    print(img_RGB_path)
    img_g = cv2.imread(img_G_path, 0)
    img_rgb = cv2.imread(img_RGB_path)
    img_rgb2g = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    # 灰度图二值化
    ret, img_b = cv2.threshold(img_g, 0, 255, cv2.THRESH_OTSU)
    # 闭开运算
    kernel_CLOSE = np.ones((13, 13), np.uint8)
    kernel_OPEN = np.ones((9, 9), np.uint8)
    img_b = cv2.morphologyEx(img_b, cv2.MORPH_CLOSE, kernel_CLOSE)
    img_b = cv2.morphologyEx(img_b, cv2.MORPH_OPEN, kernel_OPEN)
    # 灰度图寻找边缘
    contours_g, hierarchy = cv2.findContours(img_b, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours_g, img_rgb  # 返回img_rgb以便画图,contours_g的shape是list里面装着(1,n,2)


def Intelligent_scissors(contour, scissors):
    # reshape
    contour = contour.reshape(contour.shape[0], 2)
    # print(contour.shape)

    # 初始化指针
    # seed_pointer = 0
    free_pointer = 1

    # 初始化队列
    list_a = [[0, 0]]
    list_b = []
    list_cou = np.zeros(MAX_cou)  # 计数器,50位
    # print(list_cou)
    list_contours = []  # 最终边界

    seed_x, seed_y = contour[0]  # 初始化seed
    # 不让初始点贴在边缘
    seed_x = seed_x + 3
    seed_y = seed_y + 3

    for free_pointer in range(0, contour.shape[0]):
        print('\nfree_pointer=%d' % free_pointer)

        # 取free seed并寻路
        free_x, free_y = contour[free_pointer]
        # seed_x, seed_y = contour[seed_pointer]
        # print(free_x, free_y, seed_x, seed_y)
        print('free_x_y=(%d,%d) seed_x_y=(%d,%d)' % (free_x, free_y, seed_x, seed_y))
        if free_x > 4 and free_y > 4:  # 不是边界
            list_b = scissors.find_path(seed_x, seed_y, free_x, free_y)
            # list_b = scissors.find_path(seed_x, seed_y, free_x, free_y)  # 输出的是(y,x),从free到seed.
            list_b = list(reversed(list_b))  # 翻转，从seed到free

            # list_and
            list_and = list_logical_and(list_a, list_b)

            # 处理计数器
            for i, b in enumerate(list_and):
                if b:
                    list_cou[i] = list_cou[i] + 1  # 若路径与之前一致则计数器加1
                else:
                    list_cou[i:] = 0  # 若路径与之前不一致，不一致及之后清零
                    break

            # 出栈大于COOL的点
            for p in range(MAX_cou):
                if list_cou[p] >= COOL:
                    seed_y, seed_x = list_b.pop(0)
                    list_contours.append([seed_y, seed_x])  # 不将x,y转正！
                    list_cou[p] = 0
                    # seed_pointer=seed_pointer+1 #冻结
                else:
                    break
            # 去除list_cou前面的0
            list_cou = list_cou[list_cou > 0]
            # print(list_cou.shape[0])
            list_cou = np.pad(list_cou[list_cou > 0], ((0, MAX_cou - list_cou.shape[0])))
            list_a = list_b
        else:  # 边界全部出栈
            seed_y = free_y
            seed_x = free_x
            list_b.append([free_y, free_x])
            list_contours = list_contours + list_b
            list_b = [0, 0]
            # 重新初始化
            list_a = [[0, 0]]
            list_b = []
            list_cou = np.zeros(MAX_cou)  # 计数器,50位

        # print(list_cou)
        # print(list_contours)

    # 剩余的list_b加入最终队列中
    list_contours = list_contours + list_b
    print(list_contours)

    out=np.array(list_contours).reshape(-1, 1, 2)
    out=out[:, :, [1, 0]]
    return out

def path_multi():
    pass

if __name__ == '__main__':
    print('test1')

    img_G_path = 'gary.jpg'
    img_RGB_path = 'rbg.jpg'
    contours_g, img_rgb = findContours_g(img_G_path, img_RGB_path)

    #特征图
    scissors = Scissors(img_rgb, use_dynamic_features=False)

    # 灰度图寻找较大边缘
    contours_g_out = []
    scissors_list=[]
    for k in contours_g:
        if len(k) > 150:
            print(len(k))
            contours_g_out.append(k)
            scissors_list.append(scissors)


    # 叠加显示
    img_rgb_c = cv2.drawContours(img_rgb, contours_g_out, -1, (0, 255, 0), 3)
    cv2.imwrite('img_rgb_c.jpg', img_rgb_c)


    # scissors = Scissors(img_rgb, use_dynamic_features=True)

    #找边缘
    # mult_list=[]
    # out_end=[]
    p = Pool()

    # for c in contours_g_out:
    #     print('\n######mult######')
    #     # contour = Intelligent_scissors(c, scissors)  # 以第0个轮廓为例

    # partial_func = partial(Intelligent_scissors, scissors=scissors)
    out_end=p.map(Intelligent_scissors,contours_g_out,scissors_list)
    print(out_end)


    #画边缘
    img_out = cv2.drawContours(img_rgb_c, out_end, -1, (255, 0, 0), 3)

    # 创造一个遮罩
    mask = np.zeros(img_rgb.shape).astype(img_rgb.dtype)
    mask_out = cv2.drawContours(mask, out_end, -1, (255, 255, 255), -1)  # 画边缘

    cv2.imwrite('20-cl.jpg', img_out)
    cv2.imwrite('20m-cl.jpg', mask_out)
