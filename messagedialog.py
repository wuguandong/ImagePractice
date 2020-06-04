from PyQt5.Qt import *


class MessageDialog(QDialog):
    def __init__(self, parent: QWidget, text: str):
        super().__init__(parent)

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 总在最前
        self.setWindowFlags(Qt.WindowDoesNotAcceptFocus)  # 不获取焦点
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭后自动删除自身
        self.setModal(False)  # 非模态

        # 背景颜色
        self.setStyleSheet('background:rgba(255,0,0,0.7);'
                           'border-radius: 5px;'
                           'font-size: 11pt;'
                           '')

        # 设置布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        lblText = QLabel(text)
        lblText.setAlignment(Qt.AlignCenter)
        lblText.setStyleSheet('color: white;')
        layout.addWidget(lblText)
        self.setLayout(layout)

        # 设置窗口大小和位置
        self.setFixedSize(max(len(text) * 15 + 120, 100), 80)
        self.move(int((parent.width() - self.width()) / 2), int((parent.height() - self.height()) / 2))

        # 设置定时器
        timer = QTimer(self)
        timer.timeout.connect(self.close)

        # 显示
        self.show()
        timer.start(3000)
