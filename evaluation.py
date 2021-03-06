import cv2
import numpy as np


def eval(pre_path,act_path):
    pre = cv2.imread(pre_path, 0)
    act = cv2.imread(act_path, 0)

    # pre = cv2.resize(pre, (640, 360), interpolation=cv2.INTER_AREA)
    # act = cv2.resize(act, (640, 360), interpolation=cv2.INTER_AREA)

    # 因为有高斯模糊的边界，所以还得二值化一下ps里出来的照片
    ret, act = cv2.threshold(act, 127, 255, cv2.THRESH_BINARY)

    pre_and_act = cv2.bitwise_and(pre, act)  # 交集,真阳性
    pre_or_act = cv2.bitwise_or(pre, act)  # 并集

    # 取反后取交集，为真阴性
    npre = cv2.bitwise_not(pre)
    nact = cv2.bitwise_not(act)
    npre_and_nact = cv2.bitwise_and(npre, nact)

    # print(pre_and_act==255)
    # print(np.sum(pre_and_act==255))

    # print('iou:')
    iou = np.sum(pre_and_act == 255) / np.sum(pre_or_act == 255)
    # print(iou)

    # print('pa')
    all = pre.shape[0] * pre.shape[1]
    pa = (np.sum(pre_and_act == 255) + np.sum(npre_and_nact == 255)) / all
    # print(pa)

    return iou,pa


if __name__ == '__main__':
    pre_path='20m-cl.jpg'
    # pre_path = 'gary_otsu.jpg'
    # pre_path='gary-th-oc.jpg'
    act_path = 'rbg_1.jpg'

    iou,pa=eval(pre_path,act_path)
    print(iou,pa)

