import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QFont, QCoreApplication
from widget import Widget


def main():
    a = QApplication(sys.argv)

    # 设置全局字体
    a.setFont(QFont('Microsoft Yahei', 9))

    # 设置组织名和程序名以便使用QSettings
    QCoreApplication.setOrganizationName('Grande')
    QCoreApplication.setApplicationName('ImagePractice')

    w = Widget()
    w.show()

    # 加载样式表
    with open('qss.css', mode='r', encoding='utf-8') as qssFile:
        qss = qssFile.read()
        a.setStyleSheet(qss)
        qssFile.close()

    sys.exit(a.exec_())


if __name__ == '__main__':
    main()
