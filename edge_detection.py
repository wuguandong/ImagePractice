import numpy as np
import cv2 as cv


# 索伯
def sobelEdgeDetection(img: np.ndarray, axis, radius) -> np.ndarray:
    if axis == 'x':
        img_16S = cv.Sobel(img, cv.CV_16S, 1, 0, ksize=radius * 2 + 1)
    else:
        img_16S = cv.Sobel(img, cv.CV_16S, 0, 1, ksize=radius * 2 + 1)
    img_abs_16S = np.absolute(img_16S)
    return np.uint8(img_abs_16S)


# 拉普拉斯
def laplacianEdgeDetection(img: np.ndarray, neighbourhood) -> np.ndarray:
    if neighbourhood == 4:
        img_16S = cv.Laplacian(img, cv.CV_16S, ksize=1)
    else:
        img_16S = cv.Laplacian(img, cv.CV_16S, ksize=3)
    img_abs_16S = np.absolute(img_16S)
    return np.uint8(img_abs_16S)


# Canny
def cannyEdgeDetection(img: np.ndarray, lowThreshold, highThreshold) -> np.ndarray:
    return cv.Canny(img, lowThreshold, highThreshold)
