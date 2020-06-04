import numpy as np
import cv2 as cv


# 固定阈值分割
def fixedThresholdSegmentation(img: np.ndarray, threshold) -> np.ndarray:
    _, newImg = cv.threshold(img, threshold, 255, cv.THRESH_BINARY)
    return newImg


# 自适应阈值分割
def adaptiveThresholdSegmentation(img: np.ndarray, method, radius, offset) -> np.ndarray:
    if method == 'mean':
        return cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, radius * 2 + 1, offset)
    else:
        return cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, radius * 2 + 1, offset)


# OTSU
def otsuThresholdSegmentation(img: np.ndarray) -> np.ndarray:
    _, newImg = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return newImg
