import numpy as np
import cv2 as cv


# 创建结构元素
def createStructuringElement(shape, radius):
    width = 2 * radius + 1
    if shape == 'rect':
        return cv.getStructuringElement(cv.MORPH_RECT, (width, width))
    elif shape == 'circle':
        return cv.getStructuringElement(cv.MORPH_ELLIPSE, (width, width))
    else:
        return cv.getStructuringElement(cv.MORPH_CROSS, (width, width))


# 膨胀
def dilateOperation(img: np.ndarray, shape, radius) -> np.ndarray:
    return cv.dilate(img, createStructuringElement(shape, radius), iterations=1)


# 腐蚀
def erodeOperation(img: np.ndarray, shape, radius) -> np.ndarray:
    return cv.erode(img, createStructuringElement(shape, radius), iterations=1)


# 开运算
def openOperation(img: np.ndarray, shape, radius) -> np.ndarray:
    return cv.morphologyEx(img, cv.MORPH_OPEN, createStructuringElement(shape, radius))


# 闭运算
def closeOperation(img: np.ndarray, shape, radius) -> np.ndarray:
    return cv.morphologyEx(img, cv.MORPH_CLOSE, createStructuringElement(shape, radius))
