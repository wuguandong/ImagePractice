import numpy as np
import cv2 as cv


# 均值平滑
def averageSmoothing(img: np.ndarray, radius) -> np.ndarray:
    width = 2 * radius + 1
    return cv.blur(img, (width, width))


# 高斯平滑
def gaussianSmoothing(img: np.ndarray, radius) -> np.ndarray:
    width = 2 * radius + 1
    return cv.GaussianBlur(img, (width, width), 0)


# 中值平滑
def medianSmoothing(img: np.ndarray, radius) -> np.ndarray:
    return cv.medianBlur(img, 2 * radius + 1)
