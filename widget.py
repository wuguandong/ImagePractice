import numpy as np
import cv2 as cv
from PyQt5.Qt import *
from ui_widget import Ui_Widget
from imageviewer import ImageViewer
import resource


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 成员变量
        self.__menuBtnGroup = QButtonGroup(self)  # 菜单按钮组
        self.__checkedMenuBtn = None  # 当前选中的菜单按钮
        self.__openImgBtn = QPushButton('打开图片', self.ui.widget_center_container)  # 打开图片按钮
        self.__viewer = ImageViewer()  # 图片查看器
        self.__contrastViewer = ImageViewer()  # 原图查看器
        self.__settings = QSettings()
        self.__imgList = []  # 图片列表

        # 程序名称和图标
        self.setWindowTitle("图像实践")
        self.setWindowIcon(QIcon(':/image/app_icon.png'))

        # 自动填充背景色
        self.ui.widget_bg.setAutoFillBackground(True)

        # 无边框窗口
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # widget_center阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor('#666666'))
        self.shadow.setBlurRadius(30)
        self.ui.widget_center_container.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(False)  # 禁用阴影

        # 设置widget_imageviewer_container布局
        imageviewerContainerLayout = QHBoxLayout(self.ui.widget_imageviewer_container)
        imageviewerContainerLayout.addWidget(self.__contrastViewer)
        imageviewerContainerLayout.addWidget(self.__viewer)

        # 设置控件样式
        self.ui.widget_center.setProperty('form', 'widget_center')
        self.ui.widget_tool.setProperty('form', 'widget_tool')
        self.ui.btn_min.setProperty('form', 'btn_min')
        self.ui.btn_max.setProperty('form', 'btn_max')
        self.ui.btn_close.setProperty('form', 'btn_close')

        # 菜单按钮组
        self.__menuBtnGroup.setExclusive(False)
        for btn in self.ui.widget_menu.findChildren(QPushButton):
            btn.setProperty('form', 'btn_menu')
            self.__menuBtnGroup.addButton(btn)
            btn.clicked.connect(self.__menuBtnSlot)

        # 初始化窗口状态
        self.__openImgBtn.lower()
        self.ui.widget_center.move(0, 10e4)
        self.ui.widget_tool.hide()
        self.ui.widget_menu.setDisabled(True)
        self.__contrastViewer.hide()

        # 打开图片按钮槽函数
        self.__openImgBtn.clicked.connect(self.__openImgBtnSlot)

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

    # 重写改变窗口大小事件
    def resizeEvent(self, event):
        # 背景图片大小自适应
        # palette = QPalette()
        # bgImg = QPixmap(':/image/background.jpg').scaled(self.ui.widget_bg.width(), self.ui.widget_bg.height())
        # palette.setBrush(self.backgroundRole(), QBrush(bgImg))
        # self.ui.widget_bg.setPalette(palette)
        self.ui.widget_bg.setPalette(QPalette(QColor(43, 87, 154)))  # 临时用纯色背景

        # 计算widget_center_container大小
        ownerSize = QSize(self.ui.widget_bg.width(), self.ui.widget_bg.height() - self.ui.widget_title.minimumHeight())

        # 调整打开图片按钮位置
        self.__openImgBtn.move((ownerSize.width() - self.__openImgBtn.width()) / 2, (ownerSize.height() - self.__openImgBtn.height()) / 2)

        # 调整CenterWidget的大小
        self.ui.widget_center.setFixedSize(ownerSize)

    # 菜单按钮槽函数
    def __menuBtnSlot(self):
        menu = self.sender().objectName()
        if self.__checkedMenuBtn is not None and menu == self.__checkedMenuBtn.objectName():
            self.ui.widget_tool.hide()
            self.__checkedMenuBtn = None
        else:
            if menu == 'btn_menu_enhancement':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_enhancement)
            elif menu == 'btn_menu_smoothing':
                self.ui.widget_tool.setCurrentWidget(self.ui.page_smoothing)
            if self.__checkedMenuBtn is None:
                self.ui.widget_tool.show()
            else:
                self.__checkedMenuBtn.setChecked(False)
            self.__checkedMenuBtn = self.sender()

    # 打开图片按钮槽函数
    def __openImgBtnSlot(self):
        # 获取桌面路径
        openDir = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

        # 从QSetting中读取路径
        if self.__settings.contains('openDir'):
            openDir = self.__settings.value('openDir')

        # 打开文件选择对话框
        path, _ = QFileDialog.getOpenFileName(self, '选择图片', openDir, '图片 (*.jpg *.png)')
        if path == '':
            return

        # 路径保存至QSetting
        self.__settings.setValue('openDir', path)

        # 读取图片并添加到图片列表
        self.__imgList.append(cv.imdecode(np.fromfile(path, dtype=np.uint8), 1))

        # 显示图片
        self.__viewer.loadImage(self.__imgList[0])
        self.__contrastViewer.loadImage(self.__imgList[0])

        # 弹出中心窗体
        self.__popCenterWidget()

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

        # 适应窗口显示
        self.__viewer.fitDisplay()
        self.__contrastViewer.fitDisplay()

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
