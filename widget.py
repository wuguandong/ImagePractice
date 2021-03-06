import numpy as np
import cv2 as cv
from PyQt5.Qt import *
from ui_widget import Ui_Widget
from imageviewer import ImageViewer
import resource
from messagedialog import MessageDialog
from util import *
from enhancement import *
from smoothing import *
from segmentation import *
from morphology import *
from edge_detection import *
from featureextraction import *


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 成员变量
        self.__menuBtnGroup = QButtonGroup(self)  # 菜单按钮组
        self.__checkedMenuBtn = None  # 当前选中的菜单按钮
        self.__openImgBtn = QPushButton('打开图片', self.ui.widget_center_container)  # 打开图片按钮
        self.__imgFileName = ''  # 图片文件名称
        self.__viewer = ImageViewer()  # 图片查看器
        self.__contrastViewer = ImageViewer()  # 原图查看器
        self.__settings = QSettings()
        self.__imgList = []  # 图片列表
        self.__redoList = []  # 重做列表
        self.__previewImgDict = {  # 预览图片字典
            'brightnessAdjust': np.ndarray([0]),
            'contrastRatioAdjust': np.ndarray([0]),
            'smoothing': np.ndarray([0]),
            'fixedThreshold': np.ndarray([0]),
            'adaptiveThreshold': np.ndarray([0]),
            'morphology': np.ndarray([0]),
            'cannyEdge': np.ndarray([0])
        }
        self.__mousePressFlag = False  # 鼠标左键是否被按下
        self.__mousePressPos = QPoint()  # 鼠标按下位置
        self.__fixedThresholdActiveFlag = False  # 固定阈值分割激活标志
        self.__cannyEdgeActiveFlag = False  # Canny边缘检测激活标志

        # 程序名称和图标
        self.setWindowTitle("图像实践")
        self.setWindowIcon(QIcon(':/image/app_icon.png'))

        # 自动填充背景色
        self.ui.widget_bg.setAutoFillBackground(True)

        # 无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # widget_center阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor('#666666'))
        self.shadow.setBlurRadius(30)
        self.ui.widget_center_container.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(False)  # 禁用阴影

        # 禁止widget_center将鼠标事件传到父级
        self.ui.widget_center.setAttribute(Qt.WA_NoMousePropagation)

        # 设置widget_imageviewer_container布局
        imageviewerContainerLayout = QHBoxLayout(self.ui.widget_imageviewer_container)
        imageviewerContainerLayout.addWidget(self.__contrastViewer)
        imageviewerContainerLayout.addWidget(self.__viewer)

        # 设置控件样式
        self.ui.widget_center.setProperty('form', 'widget_center')
        self.ui.widget_tool.setProperty('form', 'widget_tool')
        self.ui.btn_min.setProperty('form', 'btn_min')  # 窗口操作按钮
        self.ui.btn_max.setProperty('form', 'btn_max')
        self.ui.btn_close.setProperty('form', 'btn_close')
        self.__openImgBtn.setProperty('form', 'btn_open_img')  # 打开图片按钮
        self.__openImgBtn.setFixedSize(350, 50)
        self.ui.btn_save.setProperty('form', 'btn_save')  # 保存按钮
        self.ui.btn_brightness_ok.setProperty('form', 'btn_dark')  # 工具栏按钮
        self.ui.btn_undo.setProperty('form', 'btn_undo')  # 撤销重做按钮
        self.ui.btn_redo.setProperty('form', 'btn_redo')
        self.ui.btn_zoomin.setProperty('form', 'btn_zoomin')  # 图片操作按钮
        self.ui.btn_zoomout.setProperty('form', 'btn_zoomout')
        self.ui.btn_fit_display.setProperty('form', 'btn_fit_display')
        self.ui.btn_rotate.setProperty('form', 'btn_rotate')
        self.ui.btn_contrast.setProperty('form', 'btn_contrast')
        self.ui.btn_brightness_cancel.setProperty('form', 'btn_light')  # 基本页面
        self.ui.btn_contrast_ratio_ok.setProperty('form', 'btn_dark')
        self.ui.btn_contrast_ratio_cancel.setProperty('form', 'btn_light')
        self.ui.btn_color_reversal.setProperty('form', 'btn_dark_big')
        self.ui.btn_to_gray_image.setProperty('form', 'btn_dark_big')
        self.ui.btn_histogram_equalization.setProperty('form', 'btn_dark_big')
        # self.ui.btn_show_histogram.setProperty('form', 'btn_light_big')
        self.ui.btn_smoothing_cancel.setProperty('form', 'btn_light')  # 平滑页面
        self.ui.btn_smoothing_ok.setProperty('form', 'btn_dark')
        self.ui.lbl_fixed_threshold_title.setProperty('form', 'lbl_title_small')  # 分割页面
        self.ui.btn_fixed_threshold_cancel.setProperty('form', 'btn_light')
        self.ui.btn_fixed_threshold_ok.setProperty('form', 'btn_dark')
        self.ui.lbl_adaptive_threshold_title.setProperty('form', 'lbl_title_small')
        self.ui.btn_adaptive_threshold_cancel.setProperty('form', 'btn_light')
        self.ui.btn_adaptive_threshold_ok.setProperty('form', 'btn_dark')
        self.ui.lbl_otsu_threshold_title.setProperty('form', 'lbl_title_small')
        self.ui.btn_otsu_threshold.setProperty('form', 'btn_dark_big')
        self.ui.btn_morphology_cancel.setProperty('form', 'btn_light')
        self.ui.btn_morphology_ok.setProperty('form', 'btn_dark')
        self.ui.lbl_sobel_edge_detection.setProperty('form', 'lbl_title_small')  # 边缘检测页面
        self.ui.btn_sobel_edge_detection.setProperty('form', 'btn_dark_big')
        self.ui.lbl_laplacian_edge_detection.setProperty('form', 'lbl_title_small')
        self.ui.btn_laplacian_edge_detection.setProperty('form', 'btn_dark_big')
        self.ui.lbl_canny_edge_detection.setProperty('form', 'lbl_title_small')
        self.ui.btn_canny_edge_detection_cancel.setProperty('form', 'btn_light')
        self.ui.btn_canny_edge_detection_ok.setProperty('form', 'btn_dark')
        self.ui.lbl_contour_feature_title.setProperty('form', 'lbl_title_small')  # 特征提取页面
        self.ui.btn_contour_tracing.setProperty('form', 'btn_dark_big')
        self.ui.lbl_shape_feature_title.setProperty('form', 'lbl_title_small')
        self.ui.btn_hough_line_transform.setProperty('form', 'btn_dark_big')
        self.ui.lbl_point_feature_title.setProperty('form', 'lbl_title_small')
        self.ui.btn_harris_feature.setProperty('form', 'btn_dark_big')
        self.ui.btn_fast_feature.setProperty('form', 'btn_dark_big')
        self.ui.btn_orb_feature.setProperty('form', 'btn_dark_big')

        # 菜单按钮组
        self.__menuBtnGroup.setExclusive(False)
        for btn in self.ui.widget_menu.findChildren(QPushButton):
            btn.setProperty('form', 'btn_menu')
            self.__menuBtnGroup.addButton(btn)
            btn.clicked.connect(self.__menuBtnSlot)

        # 设置鼠标悬停提示
        self.ui.btn_save.setToolTip('Ctrl+S')
        self.ui.btn_undo.setToolTip('Ctrl+Z')
        self.ui.btn_redo.setToolTip('Ctrl+R')

        # 初始化窗口状态
        self.__openImgBtn.lower()
        self.ui.widget_center.move(0, 10e4)
        self.ui.widget_tool.hide()
        self.ui.widget_menu.setDisabled(True)
        self.ui.btn_save.setDisabled(True)
        self.__contrastViewer.hide()
        self.ui.btn_undo.setDisabled(True)
        self.ui.btn_redo.setDisabled(True)

        # 最小化按钮槽函数
        self.ui.btn_min.clicked.connect(self.__minBtnSlot)

        # 最大化按钮槽函数
        self.ui.btn_max.clicked.connect(self.__maxBtnSlot)

        # 关闭按钮槽函数
        self.ui.btn_close.clicked.connect(self.__closeBtnSlot)

        # 打开图片按钮槽函数
        self.__openImgBtn.clicked.connect(self.__openImgBtnSlot)

        # 保存按钮槽函数
        self.ui.btn_save.clicked.connect(self.__saveBtnSlot)

        # 撤销按钮槽函数
        self.ui.btn_undo.clicked.connect(self.__undoBtnSlot)

        # 重做按钮槽函数
        self.ui.btn_redo.clicked.connect(self.__redoBtnSlot)

        # 缩小按钮槽函数
        self.ui.btn_zoomout.clicked.connect(lambda: self.__viewer.animatedZoom(self.__viewer.propScale / 2))

        # 放大按钮槽函数
        self.ui.btn_zoomin.clicked.connect(lambda: self.__viewer.animatedZoom(self.__viewer.propScale * 2))

        # 适应显示按钮槽函数
        self.ui.btn_fit_display.clicked.connect(self.__fitDisplayBtnSlot)

        # 旋转按钮槽函数
        self.ui.btn_rotate.clicked.connect(self.__rotateBtnSlot)

        # 对比按钮槽函数
        self.ui.btn_contrast.clicked.connect(self.__contrastBtnSlot)

        # 亮度调节槽函数
        bindSpinboxAndSlider(self.ui.sb_brightness, self.ui.hs_brightness, self.__brightnessAdjustPreviewSlot)
        self.ui.btn_brightness_ok.clicked.connect(self.__brightnessAdjustOkBtnSlot)
        self.ui.btn_brightness_cancel.clicked.connect(self.__brightnessAdjustCancelBtnSlot)

        # 对比度调节槽函数
        bindSpinboxAndSlider(self.ui.sb_contrast_ratio, self.ui.hs_contrast_ratio, self.__contrastRatioAdjustPreviewSlot)
        self.ui.btn_contrast_ratio_ok.clicked.connect(self.__contrastRatioAdjustOkBtnSlot)
        self.ui.btn_contrast_ratio_cancel.clicked.connect(self.__contrastRatioAdjustCancelBtnSlot)

        # 反相按钮槽函数
        self.ui.btn_color_reversal.clicked.connect(self.__colorReversalBtnSlot)

        # 灰度化按钮槽函数
        self.ui.btn_to_gray_image.clicked.connect(self.__toGrayImageBtnSlot)

        # 直方图均衡化槽函数
        self.ui.btn_histogram_equalization.clicked.connect(self.__histogramEqualizationBtnSlot)

        # 显示直方图按钮槽函数
        # self.ui.btn_show_histogram.clicked.connect(self.__showHistogramBtnSlot)

        # 平滑操作槽函数
        bindSpinboxAndSlider(self.ui.sb_smoothing_radius, self.ui.hs_smoothing_radius, self.__smoothingPreviewSlot)
        self.ui.radio_smoothing_type_average.clicked.connect(self.__smoothingPreviewSlot)
        self.ui.radio_smoothing_type_gaussian.clicked.connect(self.__smoothingPreviewSlot)
        self.ui.radio_smoothing_type_median.clicked.connect(self.__smoothingPreviewSlot)
        self.ui.btn_smoothing_ok.clicked.connect(self.__smoothingOkBtnSlot)
        self.ui.btn_smoothing_cancel.clicked.connect(self.__smoothingCancelBtnSlot)

        # 固定阈值分割槽函数
        bindSpinboxAndSlider(self.ui.sb_fixed_threshold, self.ui.hs_fixed_threshold, self.__fixedThresholdPreviewSlot)
        self.ui.btn_fixed_threshold_ok.clicked.connect(self.__fixedThresholdOkBtnSlot)
        self.ui.btn_fixed_threshold_cancel.clicked.connect(self.__fixedThresholdCancelBtnSlot)

        # 自适应阈值分割槽函数
        bindSpinboxAndSlider(self.ui.sb_adaptive_threshold_radius, self.ui.hs_adaptive_threshold_radius, self.__adaptiveThresholdPreviewSlot)
        bindSpinboxAndSlider(self.ui.sb_adaptive_threshold_offset, self.ui.hs_adaptive_threshold_offset, self.__adaptiveThresholdPreviewSlot)
        self.ui.radio_adaptive_threshold_type_average.clicked.connect(self.__adaptiveThresholdPreviewSlot)
        self.ui.radio_adaptive_threshold_type_gaussian.clicked.connect(self.__adaptiveThresholdPreviewSlot)
        self.ui.btn_adaptive_threshold_ok.clicked.connect(self.__adaptiveThresholdOkBtnSlot)
        self.ui.btn_adaptive_threshold_cancel.clicked.connect(self.__adaptiveThresholdCancelBtnSlot)

        # OTSU阈值分割槽函数
        self.ui.btn_otsu_threshold.clicked.connect(self.__otsuThresholdBtnSlot)

        # 形态学操作槽函数
        bindSpinboxAndSlider(self.ui.sb_morphology_radius, self.ui.hs_morphology_radius, self.__morphologyPreviewSlot)
        self.ui.radio_morphology_type_dilate.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_type_erode.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_type_open.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_type_close.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_shape_rect.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_shape_circle.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.radio_morphology_type_cross.clicked.connect(self.__morphologyPreviewSlot)
        self.ui.btn_morphology_ok.clicked.connect(self.__morphologyOkBtnSlot)
        self.ui.btn_morphology_cancel.clicked.connect(self.__morphologyCancelBtnSlot)

        # 索伯边缘检测槽函数
        self.ui.btn_sobel_edge_detection.clicked.connect(self.__sobelEdgeDetectionBtnSlot)

        # 拉普拉斯边缘检测
        self.ui.btn_laplacian_edge_detection.clicked.connect(self.__laplacianEdgeDetectionBtnSlot)

        # Canny边缘检测槽函数
        bindSpinboxAndSlider(self.ui.sb_canny_low_threshold, self.ui.hs_canny_low_threshold, self.__cannyEdgePreviewSlot)
        bindSpinboxAndSlider(self.ui.sb_canny_high_threshold, self.ui.hs_canny_high_threshold, self.__cannyEdgePreviewSlot)
        self.ui.btn_canny_edge_detection_ok.clicked.connect(self.__cannyEdgeOkBtnSlot)
        self.ui.btn_canny_edge_detection_cancel.clicked.connect(self.__cannyEdgeCancelBtnSlot)

        # 轮廓跟踪槽函数
        self.ui.btn_contour_tracing.clicked.connect(self.__contourTracingSlot)

        # 霍夫直线变换槽函数
        self.ui.btn_hough_line_transform.clicked.connect(self.__houghLineTransformSlot)

        # Harris特征检测槽函数
        self.ui.btn_harris_feature.clicked.connect(self.__harrisFeatureDetectionSlot)

        # FAST特征检测槽函数
        self.ui.btn_fast_feature.clicked.connect(self.__fastFeatureDetectionSlot)

        # ORB特征检测槽函数
        self.ui.btn_orb_feature.clicked.connect(self.__orbFeatureDetectionSlot)

    # 重写绘图函数
    def paintEvent(self, event):
        # 绘制窗体阴影
        shadow_margin = 15
        shadow_pixmap = QPixmap('://image/mainWnd_shadow.png')
        painter = QPainter(self)
        pngTop = QRect(shadow_margin, 0, shadow_pixmap.width() - shadow_margin * 2, shadow_margin)
        winTop = QRect(shadow_margin, 0, self.width() - shadow_margin * 2, shadow_margin)
        painter.drawPixmap(winTop, shadow_pixmap, pngTop)
        pngBottom = QRect(shadow_margin, shadow_pixmap.height() - shadow_margin, shadow_pixmap.width() - shadow_margin * 2, shadow_margin)
        winBottom = QRect(shadow_margin, self.height() - shadow_margin, self.width() - shadow_margin * 2, shadow_margin)
        painter.drawPixmap(winBottom, shadow_pixmap, pngBottom)
        pngLeft = QRect(0, shadow_margin, shadow_margin, shadow_pixmap.height() - shadow_margin * 2)
        winLeft = QRect(0, shadow_margin, shadow_margin, self.height() - shadow_margin * 2)
        painter.drawPixmap(winLeft, shadow_pixmap, pngLeft)
        pngRight = QRect(shadow_pixmap.width() - shadow_margin, shadow_margin, shadow_margin, shadow_pixmap.height() - shadow_margin * 2)
        winRight = QRect(self.width() - shadow_margin, shadow_margin, shadow_margin, self.height() - shadow_margin * 2)
        painter.drawPixmap(winRight, shadow_pixmap, pngRight)
        pngLeftTop = QRect(0, 0, shadow_margin, shadow_margin)
        winLeftTop = QRect(0, 0, shadow_margin, shadow_margin)
        painter.drawPixmap(winLeftTop, shadow_pixmap, pngLeftTop)
        pngRightTop = QRect(shadow_pixmap.width() - shadow_margin, 0, shadow_margin, shadow_margin)
        winRightTop = QRect(self.width() - shadow_margin, 0, shadow_margin, shadow_margin)
        painter.drawPixmap(winRightTop, shadow_pixmap, pngRightTop)
        pngLeftBottom = QRect(0, shadow_pixmap.height() - shadow_margin, shadow_margin, shadow_margin)
        winLeftBottom = QRect(0, self.height() - shadow_margin, shadow_margin, shadow_margin)
        painter.drawPixmap(winLeftBottom, shadow_pixmap, pngLeftBottom)
        pngRightBottom = QRect(shadow_pixmap.width() - shadow_margin, shadow_pixmap.height() - shadow_margin, shadow_margin, shadow_margin)
        winRightBottom = QRect(self.width() - shadow_margin, self.height() - shadow_margin, shadow_margin, shadow_margin)
        painter.drawPixmap(winRightBottom, shadow_pixmap, pngRightBottom)

    # 重写改变窗口大小事件
    def resizeEvent(self, event):
        # 使用背景图片
        # palette = QPalette()
        # bgImg = QPixmap(':/image/background.jpg').scaled(self.ui.widget_bg.width(), self.ui.widget_bg.height())
        # palette.setBrush(self.backgroundRole(), QBrush(bgImg))
        # self.ui.widget_bg.setPalette(palette)

        # 使用纯色背景
        self.ui.widget_bg.setPalette(QPalette(QColor(43, 87, 154)))

        # 计算widget_center_container大小
        ownerSize = QSize(self.ui.widget_bg.width(), self.ui.widget_bg.height() - self.ui.widget_title.minimumHeight())

        # 调整打开图片按钮位置
        self.__openImgBtn.move((ownerSize.width() - self.__openImgBtn.width()) / 2, (ownerSize.height() - self.__openImgBtn.height()) / 2)

        # 调整CenterWidget的大小
        self.ui.widget_center.setFixedSize(ownerSize)

    # 重写鼠标按下事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__mousePressFlag = True
            self.__mousePressPos = event.pos()

    # 重写鼠标释放事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__mousePressFlag = False

    # 重写鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.__mousePressFlag and not self.isMaximized():
            self.move(self.pos() + event.pos() - self.__mousePressPos)

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.ui.btn_max.clicked.emit()

    # 重写键盘按下事件
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_S and not self.__openImgBtn.isEnabled():
                self.__saveBtnSlot()
            if event.key() == Qt.Key_Z and self.ui.btn_undo.isEnabled():
                self.__undoBtnSlot()
            if event.key() == Qt.Key_R and self.ui.btn_redo.isEnabled():
                self.__redoBtnSlot()

    # 最小化按钮槽函数
    def __minBtnSlot(self):
        self.showMinimized()

    # 最大化按钮槽函数
    def __maxBtnSlot(self):
        if not self.isMaximized():  # 切换至全屏状态
            self.layout().setContentsMargins(0, 0, 0, 0)
            self.showMaximized()
            self.ui.btn_max.setProperty('form', 'btn_max_back')
        else:  # 切换为窗口状态
            self.layout().setContentsMargins(15, 15, 15, 15)
            self.showNormal()
            self.ui.btn_max.setProperty('form', 'btn_max')

        self.style().polish(self.ui.btn_max)

    # 关闭按钮槽函数
    def __closeBtnSlot(self):
        self.close()

    # 菜单按钮槽函数
    def __menuBtnSlot(self):
        menu = self.sender().objectName()
        if self.__checkedMenuBtn is not None and menu == self.__checkedMenuBtn.objectName():
            self.ui.widget_tool.hide()
            self.__checkedMenuBtn = None
        else:
            # 切换page
            if menu == 'btn_menu_basic':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_basic)
            elif menu == 'btn_menu_smoothing':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_smoothing)
            elif menu == 'btn_menu_segmentation':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_segmentation)
            elif menu == 'btn_menu_morphology':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_morphology)
            elif menu == 'btn_menu_edge_detection':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_edge_detection)
            elif menu == 'btn_menu_feature_extraction':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_feature)

            if self.__checkedMenuBtn is None:
                self.ui.widget_tool.show()
            else:
                self.__checkedMenuBtn.setChecked(False)
            self.__checkedMenuBtn = self.sender()

    # 打开图片按钮槽函数
    def __openImgBtnSlot(self):
        # 防止多次点击
        self.__openImgBtn.setDisabled(True)

        # 获取桌面路径
        openDir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

        # 从QSetting中读取路径
        if self.__settings.contains('openDir'):
            openDir = self.__settings.value('openDir')

        # 打开文件选择对话框
        path, _ = QFileDialog.getOpenFileName(self, '选择图片', openDir, '图片 (*.jpg *.png *.bmp *.jpe *.jpeg *.webp *.tif *.tiff)')
        if path == '':
            return

        # 路径保存至QSetting 文件名保存至__imgFileName
        self.__settings.setValue('openDir', path[:str.rindex(path, '/')])
        self.__imgFileName = path[str.rindex(path, '/') + 1:]

        # 读取图片并添加到图片列表
        self.__imgList.append(cv.imdecode(np.fromfile(path, dtype=np.uint8), 1))

        # 显示图片
        self.__viewer.loadImage(self.__imgList[0])
        self.__contrastViewer.loadImage(self.__imgList[0])

        # 弹出中心窗体
        self.__popCenterWidget()

    # 保存按钮槽函数
    def __saveBtnSlot(self):
        # 获取保存路径
        openDir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if self.__settings.contains('openDir'):
            openDir = self.__settings.value('openDir') + '/' + self.__imgFileName
        path, _ = QFileDialog.getSaveFileName(self, '保存', openDir, '图片 (*.jpg *.png *.bmp *.jpe *.jpeg *.webp *.tif *.tiff)')
        if path == '':
            return

        # 将本次打开目录存入settings
        self.__settings.setValue('openDir', path[:str.rindex(path, '/')])

        # 保存图片
        cv.imwrite(path, self.__imgList[-1])

    # 撤销按钮槽函数
    def __undoBtnSlot(self):
        self.__redoList.append(self.__imgList.pop())
        self.__viewer.changeImage(self.__imgList[-1])

        if len(self.__imgList) == 1:
            self.ui.btn_undo.setDisabled(True)

        self.ui.btn_redo.setEnabled(True)

    # 重做按钮槽函数
    def __redoBtnSlot(self):
        self.__imgList.append(self.__redoList.pop())
        self.__viewer.changeImage(self.__imgList[-1])

        if len(self.__redoList) == 0:
            self.ui.btn_redo.setDisabled(True)

        self.ui.btn_undo.setEnabled(True)

    # 适应显示按钮槽函数
    def __fitDisplayBtnSlot(self):
        self.__viewer.fitDisplay()
        self.__contrastViewer.fitDisplay()

    # 旋转按钮槽函数
    def __rotateBtnSlot(self):
        self.__viewer.rotateImage()
        self.__contrastViewer.rotateImage()

    # 对比按钮槽函数
    def __contrastBtnSlot(self, b):
        if b:
            self.__contrastViewer.show()
        else:
            self.__contrastViewer.hide()

    # 亮度调节预览槽函数
    def __brightnessAdjustPreviewSlot(self, value):
        self.__previewImgDict['brightnessAdjust'] = adjustBrightness(self.__imgList[-1], value)
        self.__viewer.changeImage(self.__previewImgDict['brightnessAdjust'])

    # 亮度调节确定按钮槽函数
    # 说明："确定"按钮的作用是将该功能的预览图片追加到图片列表中, 如果该功能当前的参数控件为默认值则不追加
    def __brightnessAdjustOkBtnSlot(self):
        if not self.ui.hs_brightness.value() == 0:
            self.__appendImg(self.__previewImgDict['brightnessAdjust'])

            # 恢复参数控件的值
            self.ui.hs_brightness.setValue(0)

    # 亮度调节取消按钮槽函数
    def __brightnessAdjustCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['brightnessAdjust'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_brightness.setValue(0)

    # 对比度调节预览槽函数
    def __contrastRatioAdjustPreviewSlot(self, value):
        self.__previewImgDict['contrastRatioAdjust'] = adjustContrastRatio(self.__imgList[-1], np.tan(value * np.pi / 180))  # value为映射函数倾斜角
        self.__viewer.changeImage(self.__previewImgDict['contrastRatioAdjust'])

    # 对比度调节确定按钮槽函数
    def __contrastRatioAdjustOkBtnSlot(self):
        if not self.ui.hs_contrast_ratio.value() == 45:
            self.__appendImg(self.__previewImgDict['contrastRatioAdjust'])

            # 恢复参数控件的值
            self.ui.hs_contrast_ratio.setValue(45)

    # 对比度调节取消按钮槽函数
    def __contrastRatioAdjustCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['contrastRatioAdjust'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_contrast_ratio.setValue(45)

    # 反相按钮槽函数
    def __colorReversalBtnSlot(self):
        self.__appendImg(colorReversal(self.__imgList[-1]))

    # 灰度化按钮槽函数
    def __toGrayImageBtnSlot(self):
        # 如果已经是灰度图 则直接返回
        if self.__imgList[-1].ndim == 2:
            MessageDialog(self, '当前已经是灰度图像')
            return

        self.__appendImg(cv.cvtColor(self.__imgList[-1], cv.COLOR_BGR2GRAY))

    # 直方图均衡化槽函数
    def __histogramEqualizationBtnSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先进行灰度化')
            return

        self.__appendImg(histogramEqualization(self.__imgList[-1]))

    # 显示直方图按钮槽函数
    # def __showHistogramBtnSlot(self):
    #     print('待写')

    # 平滑预览槽函数
    def __smoothingPreviewSlot(self):
        radius = self.ui.hs_smoothing_radius.value()
        if self.ui.radio_smoothing_type_average.isChecked():
            self.__previewImgDict['smoothing'] = averageSmoothing(self.__imgList[-1], radius)
        elif self.ui.radio_smoothing_type_gaussian.isChecked():
            self.__previewImgDict['smoothing'] = gaussianSmoothing(self.__imgList[-1], radius)
        else:
            self.__previewImgDict['smoothing'] = medianSmoothing(self.__imgList[-1], radius)

        self.__viewer.changeImage(self.__previewImgDict['smoothing'])

    # 平滑确定按钮槽函数
    def __smoothingOkBtnSlot(self):
        if not self.ui.hs_smoothing_radius.value() == 0:
            self.__appendImg(self.__previewImgDict['smoothing'])

            # 恢复参数控件的值
            self.ui.hs_smoothing_radius.setValue(0)

    # 平滑取消按钮槽函数
    def __smoothingCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['smoothing'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_smoothing_radius.setValue(0)

    # 固定阈值分割预览函数
    def __fixedThresholdPreviewSlot(self, threshold):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            self.ui.hs_fixed_threshold.setValue(127)
            return

        self.__previewImgDict['fixedThreshold'] = fixedThresholdSegmentation(self.__imgList[-1], threshold)
        self.__viewer.changeImage(self.__previewImgDict['fixedThreshold'])
        self.__fixedThresholdActiveFlag = True  # 置为激活状态

    # 固定阈值分割确定按钮槽函数
    def __fixedThresholdOkBtnSlot(self):
        if self.__fixedThresholdActiveFlag:
            self.__appendImg(self.__previewImgDict['fixedThreshold'])

            # 恢复参数控件的值
            self.ui.hs_fixed_threshold.setValue(127)

            # 置为非激活状态
            self.__fixedThresholdActiveFlag = False

    # 固定阈值分割取消按钮槽函数
    def __fixedThresholdCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['fixedThreshold'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_fixed_threshold.setValue(127)

        # 置为非激活状态
        self.__fixedThresholdActiveFlag = False

        # 再次主动刷新显示
        self.__viewer.changeImage(self.__imgList[-1])

    # 自适应阈值分割预览函数
    def __adaptiveThresholdPreviewSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            self.ui.hs_adaptive_threshold_radius.setValue(0)
            self.ui.hs_adaptive_threshold_offset.setValue(0)
            return

        if self.ui.radio_adaptive_threshold_type_average.isChecked():
            method = 'mean'
        else:
            method = 'gaussian'
        radius = self.ui.hs_adaptive_threshold_radius.value()
        offset = self.ui.hs_adaptive_threshold_offset.value()

        if radius == 0:
            self.__previewImgDict['adaptiveThreshold'] = self.__imgList[-1]
        else:
            self.__previewImgDict['adaptiveThreshold'] = adaptiveThresholdSegmentation(self.__imgList[-1], method, radius, offset)
        self.__viewer.changeImage(self.__previewImgDict['adaptiveThreshold'])

    # 自适应阈值分割确定按钮槽函数
    def __adaptiveThresholdOkBtnSlot(self):
        if not self.ui.hs_adaptive_threshold_radius.value() == 0:
            self.__appendImg(self.__previewImgDict['adaptiveThreshold'])

            # 恢复参数控件的值
            self.ui.hs_adaptive_threshold_radius.setValue(0)
            self.ui.hs_adaptive_threshold_offset.setValue(0)

    # 自适应阈值分割取消按钮槽函数
    def __adaptiveThresholdCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['adaptiveThreshold'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_adaptive_threshold_radius.setValue(0)
        self.ui.hs_adaptive_threshold_offset.setValue(0)

    # OTSU阈值分割槽函数
    def __otsuThresholdBtnSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        self.__appendImg(otsuThresholdSegmentation(self.__imgList[-1]))

    # 形态学预览按钮槽函数
    def __morphologyPreviewSlot(self):
        # 如果当前不是二值图像 则直接返回
        if not isBinaryImage(self.__imgList[-1]):
            MessageDialog(self, '需要先在「分割」菜单中进行二值化')
            self.ui.hs_morphology_radius.setValue(0)
            return

        if self.ui.radio_morphology_shape_rect.isChecked():
            shape = 'rect'
        elif self.ui.radio_morphology_shape_circle.isChecked():
            shape = 'circle'
        else:
            shape = 'cross'
        radius = self.ui.hs_morphology_radius.value()

        if self.ui.radio_morphology_type_dilate.isChecked():
            self.__previewImgDict['morphology'] = dilateOperation(self.__imgList[-1], shape, radius)
        elif self.ui.radio_morphology_type_erode.isChecked():
            self.__previewImgDict['morphology'] = erodeOperation(self.__imgList[-1], shape, radius)
        elif self.ui.radio_morphology_type_open.isChecked():
            self.__previewImgDict['morphology'] = openOperation(self.__imgList[-1], shape, radius)
        else:
            self.__previewImgDict['morphology'] = closeOperation(self.__imgList[-1], shape, radius)

        self.__viewer.changeImage(self.__previewImgDict['morphology'])

    # 形态学确定按钮槽函数
    def __morphologyOkBtnSlot(self):
        if not self.ui.hs_morphology_radius.value() == 0:
            self.__appendImg(self.__previewImgDict['morphology'])

            # 恢复参数控件的值
            self.ui.hs_morphology_radius.setValue(0)

    # 形态学取消按钮槽函数
    def __morphologyCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['morphology'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_morphology_radius.setValue(0)

    # 索伯边缘检测槽函数
    def __sobelEdgeDetectionBtnSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        if self.ui.radio_sobel_edge_detection_axis_x.isChecked():
            axis = 'x'
        else:
            axis = 'y'
        if self.ui.radio_sobel_edge_detection_radius_1.isChecked():
            radius = 1
        elif self.ui.radio_sobel_edge_detection_radius_2.isChecked():
            radius = 2
        else:
            radius = 3

        self.__appendImg(sobelEdgeDetection(self.__imgList[-1], axis, radius))

    # 拉普拉斯边缘检测槽函数
    def __laplacianEdgeDetectionBtnSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        if self.ui.radio_laplacian_edge_detection_type_4.isChecked():
            neighbourhood = 4
        else:
            neighbourhood = 8

        self.__appendImg(laplacianEdgeDetection(self.__imgList[-1], neighbourhood))

    # Canny边缘检测预览按钮槽函数
    def __cannyEdgePreviewSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            self.ui.hs_canny_low_threshold.setValue(100)
            self.ui.hs_canny_high_threshold.setValue(200)
            return

        lowThreshold = self.ui.hs_canny_low_threshold.value()
        highThreshold = self.ui.hs_canny_high_threshold.value()

        self.__previewImgDict['cannyEdge'] = cannyEdgeDetection(self.__imgList[-1], lowThreshold, highThreshold)
        self.__viewer.changeImage(self.__previewImgDict['cannyEdge'])
        self.__cannyEdgeActiveFlag = True  # 置为激活状态

    # Canny边缘检测确定按钮槽函数
    def __cannyEdgeOkBtnSlot(self):
        if self.__cannyEdgeActiveFlag:
            self.__appendImg(self.__previewImgDict['cannyEdge'])

            # 恢复参数控件的值
            self.ui.hs_canny_low_threshold.setValue(100)
            self.ui.hs_canny_high_threshold.setValue(200)

            # 置为非激活状态
            self.__cannyEdgeActiveFlag = False

            # 再次主动刷新显示（因为滑杆恢复导致预览函数再次对图像进行Canny边缘检测）
            self.__viewer.changeImage(self.__imgList[-1])

    # Canny边缘检测取消按钮槽函数
    def __cannyEdgeCancelBtnSlot(self):
        # 重置预览图片
        self.__previewImgDict['cannyEdge'] = self.__imgList[-1]

        # 恢复参数控件的值（预览图片会刷新显示）
        self.ui.hs_canny_low_threshold.setValue(100)
        self.ui.hs_canny_high_threshold.setValue(200)

        # 置为非激活状态
        self.__cannyEdgeActiveFlag = False

        # 再次主动刷新显示
        self.__viewer.changeImage(self.__imgList[-1])

    # 轮廓跟踪槽函数
    def __contourTracingSlot(self):
        # 如果当前不是二值图像 则直接返回
        if not isBinaryImage(self.__imgList[-1]):
            MessageDialog(self, '需要先在「分割」菜单中进行二值化')
            return

        self.__appendImg(contourTracing(self.__imgList[-1]))

    # 霍夫直线变换槽函数
    def __houghLineTransformSlot(self):
        # 如果当前不是二值图像 则直接返回
        if not isBinaryImage(self.__imgList[-1]):
            MessageDialog(self, '需要先在「分割」菜单中进行二值化')
            return

        newImg, flag = houghLineTransform(self.__imgList[-1])
        if flag:
            self.__appendImg(newImg)
        else:
            MessageDialog(self, '未检测到直线')

    # Harris特征检测槽函数
    def __harrisFeatureDetectionSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        self.__appendImg(harrisFeatureDetection(self.__imgList[-1]))

    # FAST特征检测槽函数
    def __fastFeatureDetectionSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        self.__appendImg(fastFeatureDetection(self.__imgList[-1]))

    # ORB特征检测槽函数
    def __orbFeatureDetectionSlot(self):
        # 如果当前不是灰度图 则直接返回
        if not self.__imgList[-1].ndim == 2:
            MessageDialog(self, '需要先在「基本」菜单中进行灰度化')
            return

        self.__appendImg(orbFeatureDetection(self.__imgList[-1]))

    # 弹出中心窗体
    def __popCenterWidget(self):
        animation = QPropertyAnimation(self.ui.widget_center, b'pos', self)
        animation.setDuration(800)
        animation.setStartValue(QPoint(0, self.ui.widget_center_container.height()))
        animation.setEndValue(QPoint(0, 0))
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.finished.connect(lambda: self.shadow.setEnabled(True))  # 动画结束后启用阴影
        animation.start()
        self.ui.widget_menu.setEnabled(True)
        self.ui.btn_save.setEnabled(True)

    # 往图片列表中追加图片
    def __appendImg(self, img):
        # 追加图片 并刷新显示
        self.__imgList.append(img)
        self.__viewer.changeImage(self.__imgList[-1])

        # 启用撤销按钮
        self.ui.btn_undo.setEnabled(True)

        # 清空重做列表 并禁用重做按钮
        self.__redoList.clear()
        self.ui.btn_redo.setDisabled(True)

