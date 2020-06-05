import numpy as np
import cv2 as cv


# 轮廓跟踪
# img: 二值图像
def contourTracing(img: np.ndarray) -> np.ndarray:
    contours, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    newImg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.drawContours(newImg, contours, -1, (0, 0, 255), 2)
    return newImg


# 霍夫直线变换
# img: 二值图像
def houghLineTransform(img: np.ndarray):
    lines = cv.HoughLines(img, 1, np.pi / 180, 200)
    newImg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv.line(newImg, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return newImg, True
    else:
        return img, False


# Harris特征检测
# img: 灰度图像
def harrisFeatureDetection(img: np.ndarray) -> np.ndarray:
    img_float32 = np.float32(img)
    dst = cv.cornerHarris(img_float32, 2, 3, 0.04)
    dst = cv.dilate(dst, None)
    newImg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    newImg[dst > 0.01 * dst.max()] = [0, 0, 255]
    return newImg


# FAST特征检测
# img: 灰度图像
def fastFeatureDetection(img: np.ndarray) -> np.ndarray:
    fast = cv.FastFeatureDetector_create()
    points = fast.detect(img, None)
    newImg = cv.drawKeypoints(img, points, None, color=(0, 0, 255))
    return newImg


# ORB特征检测
# img: 灰度图像
def orbFeatureDetection(img: np.ndarray) -> np.ndarray:
    orb = cv.ORB_create()
    points = orb.detect(img, None)
    points, _ = orb.compute(img, points)
    newImg = cv.drawKeypoints(img, points, None, color=(0, 0, 255))
    return newImg
