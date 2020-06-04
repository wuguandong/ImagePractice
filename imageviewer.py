import numpy as np
import cv2 as cv
from PyQt5.Qt import *
from PyQt5.QtCore import pyqtProperty


class ImageViewer(QWidget):
    # 类常量
    MIN_SCALE = 0.1  # 最小的缩放比例
    MAX_SCALE = 30  # 最大的缩放比例
    ANTI_MOVE_OUT_WIDTH = 250  # 防止地图移出窗口的最小边缘宽度

    # 类变量
    __offset = QPointF()  # 绘图偏移量
    __scale = 1.0  # 绘图缩放比例
    __rotateAngle = 0.0  # 旋转角度（角度制）

    def __init__(self, parent=None):
        super().__init__(parent)

        # 成员变量
        self.img = QImage()
        self.__mousePosF = QPointF  # 鼠标的位置
        self.__zoomCenterOnCursor = False  # 是否以鼠标为中心缩放

        # 临时
        self.setPalette(QPalette(QColor(0, 255, 0, 80)))
        self.setAutoFillBackground(True)

    # 重写绘图事件
    def paintEvent(self, event):
        if self.img.isNull():
            return

        # 如果可以完整显示图片 则居中显示
        if self.__canFullDisplay():
            ImageViewer.__offset = QPointF((self.width() - self.img.width() * ImageViewer.__scale) / 2, (self.height() - self.img.height() * ImageViewer.__scale) / 2)

        painter = QPainter(self)
        painter.translate(ImageViewer.__offset)
        painter.scale(ImageViewer.__scale, ImageViewer.__scale)
        painter.drawImage(0, 0, self.img)

    # 重写窗口大小改变事件
    def resizeEvent(self, event):
        # 如果处于隐藏状态 则直接返回
        if self.isHidden():
            return

        # 如果resize前能完整显示 则resize后重新适应窗口显示
        # oldSize = event.oldSize()
        # if oldSize.width() >= self.img.width() * ImageViewer.__scale and oldSize.height() >= self.img.height() * ImageViewer.__scale:
        #     self.fitDisplay()
        self.fitDisplay()  # 只要resize就重新适应窗口显示

    # 重写鼠标按下事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__mousePosF = event.localPos()  # 记录鼠标左键按下的位置
            self.setCursor(Qt.OpenHandCursor)  # 设置光标样式为小手

    # 重写鼠标释放事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # 设置光标样式箭头

    # 重写鼠标移动事件
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # 计算偏移量的变化值
            deltaOffset: QPointF = event.localPos() - self.__mousePosF

            # 在保证地图不移出窗口的情况下 更新偏移量
            if ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.width() * ImageViewer.__scale <= ImageViewer.__offset.x() + deltaOffset.x() <= self.width() - ImageViewer.ANTI_MOVE_OUT_WIDTH:
                ImageViewer.__offset.setX(ImageViewer.__offset.x() + deltaOffset.x())
            if ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.height() * ImageViewer.__scale <= ImageViewer.__offset.y() + deltaOffset.y() <= self.height() - ImageViewer.ANTI_MOVE_OUT_WIDTH:
                ImageViewer.__offset.setY(ImageViewer.__offset.y() + deltaOffset.y())

            # 更新__mousePosF
            self.__mousePosF = event.localPos()

            # 刷新所有viewer
            self.__updateAll()

    # 重写鼠标滚轮事件
    def wheelEvent(self, event):
        # 记录鼠标的位置
        self.__mousePosF = event.posF()

        # 以鼠标为中心缩放
        self.__zoomCenterOnCursor = True

        if event.angleDelta().y() > 0:  # 向上滚动 即放大
            self.setProperty('propScale', ImageViewer.__scale * 1.1)
        else:  # 向下滚动 即缩小
            self.setProperty('propScale', ImageViewer.__scale / 1.1)

    # 加载图片
    def loadImage(self, npImg: np.ndarray):
        npImg = cv.cvtColor(npImg, cv.COLOR_BGR2RGB)
        self.img = QImage(npImg, npImg.shape[1], npImg.shape[0], npImg.shape[1] * 3, QImage.Format_RGB888)
        self.fitDisplay()  # 适应窗口显示

    # 更换图片
    def changeImage(self, npImg: np.ndarray):
        if npImg.ndim == 3:
            npImg = cv.cvtColor(npImg, cv.COLOR_BGR2RGB)
            self.img = QImage(npImg, npImg.shape[1], npImg.shape[0], npImg.shape[1] * 3, QImage.Format_RGB888)
        else:
            self.img = QImage(npImg, npImg.shape[1], npImg.shape[0], npImg.shape[1], QImage.Format_Grayscale8)

        # 根据__rotateAngle旋转图片
        if not self.__rotateAngle == 0:
            tf = QTransform()
            tf.rotate(self.__rotateAngle)
            self.img = self.img.transformed(tf)

        self.update()

    # 适应窗口显示
    def fitDisplay(self):
        # 如果处于隐藏状态 则直接返回
        if self.isHidden():
            return

        # 如果图片大于窗口 则缩小至窗口大小
        if self.img.width() > self.width() or self.img.height() > self.height():
            ImageViewer.__scale = min(self.width() / self.img.width(), self.height() / self.img.height())
        else:
            ImageViewer.__scale = 1.0

        self.update()

    # 有动画效果的缩放
    # 注：只需要调用一个实例的该方法即可缩放全部实例
    def animatedZoom(self, scale):
        # 以窗口为中心缩放
        self.__zoomCenterOnCursor = False

        # 设置动画
        animation = QPropertyAnimation(self, b'propScale', self)
        animation.setDuration(500)
        animation.setStartValue(ImageViewer.__scale)
        animation.setEndValue(scale)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.start()

    # 旋转图片 向右旋转90°
    # 注：只需要调用一个实例的该方法即可缩放全部实例
    def rotateImage(self):
        tf = QTransform()
        tf.rotate(-90)
        self.img = self.img.transformed(tf)

        # 将当前旋转角度保存到__rotateAngle
        self.__rotateAngle -= 90
        self.__rotateAngle %= 360

        # 适应窗口显示
        self.fitDisplay()

        self.update()

    # 是否可以完整显示图像
    def __canFullDisplay(self):
        return self.width() >= self.img.width() * ImageViewer.__scale and self.height() >= self.img.height() * ImageViewer.__scale

    # 刷新所有ImageViewer的实例
    def __updateAll(self):
        for viewer in self.parent().findChildren(ImageViewer):
            if not viewer.isHidden():
                viewer.update()

    # 自定义属性propScale的get方法
    @pyqtProperty(float)
    def propScale(self):
        return ImageViewer.__scale

    # 自定义属性propScale的set方法
    @propScale.setter
    def propScale(self, scale):
        # 如果缩放比例超出允许的范围，直接返回
        if scale < ImageViewer.MIN_SCALE or scale > ImageViewer.MAX_SCALE:
            return

        # 计算缩放中心
        if self.__zoomCenterOnCursor:
            pos = self.__mousePosF - ImageViewer.__offset
        else:
            pos = QPointF(self.width() / 2, self.height() / 2) - ImageViewer.__offset

        # 计算新的偏移量
        newOffset: QPointF = ImageViewer.__offset - QPointF((scale - ImageViewer.__scale) * pos.x() / ImageViewer.__scale, (scale - ImageViewer.__scale) * pos.y() / ImageViewer.__scale)

        # 更新__scale
        ImageViewer.__scale = scale

        # 防止地图缩放后移出窗口
        if newOffset.x() < ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.width() * ImageViewer.__scale:
            ImageViewer.__offset.setX(ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.width() * ImageViewer.__scale)
        elif newOffset.x() > self.width() - ImageViewer.ANTI_MOVE_OUT_WIDTH:
            ImageViewer.__offset.setX(self.width() - ImageViewer.ANTI_MOVE_OUT_WIDTH)
        else:
            ImageViewer.__offset.setX(newOffset.x())
        if newOffset.y() < ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.height() * ImageViewer.__scale:
            ImageViewer.__offset.setY(ImageViewer.ANTI_MOVE_OUT_WIDTH - self.img.height() * ImageViewer.__scale)
        elif newOffset.y() > self.height() - ImageViewer.ANTI_MOVE_OUT_WIDTH:
            ImageViewer.__offset.setY(self.height() - ImageViewer.ANTI_MOVE_OUT_WIDTH)
        else:
            ImageViewer.__offset.setY(newOffset.y())

        # 刷新所有viewer
        self.__updateAll()
