from PyQt5.Qt import QSpinBox, QSlider


# 绑定整数输入框和滑块
def bindSpinboxAndSlider(editor: QSpinBox, slider: QSlider, slot):
    # 联动
    editor.valueChanged.connect(lambda value: slider.setValue(value))
    slider.valueChanged.connect(lambda value: editor.setValue(value))

    # 绑定槽函数
    slider.valueChanged.connect(slot)
