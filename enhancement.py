import numpy as np
import cv2 as cv


# 调节亮度
def adjustBrightness(img: np.ndarray, beta) -> np.ndarray:
    return cv.addWeighted(img, 1, np.zeros(img.shape, dtype=np.uint8), 0, beta)


# 调节对比度
def adjustContrastRatio(img: np.ndarray, alpha) -> np.ndarray:
    return cv.addWeighted(img, alpha, np.zeros(img.shape, dtype=np.uint8), 0, 125 * (1 - alpha))


# 反相
def colorReversal(img: np.ndarray) -> np.ndarray:
    return cv.bitwise_not(img)


# 直方图均衡化
def histogramEqualization(img: np.ndarray) -> np.ndarray:
    return cv.equalizeHist(img)
