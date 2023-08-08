from PyQt5 import QtWidgets, QtCore
MyGui=QtWidgets

# ----- Create ----------------------------------

def createLabel(text):
    label=MyGui.QLabel()
    label.setText(str(text))
    return label

def createSelect(options, default, updateFct):
    select = MyGui.QComboBox()# self as argument?
    for entry in options:
        select.addItem(entry)
    index = select.findText(default, QtCore.Qt.MatchFixedString)
    if index >= 0:
         select.setCurrentIndex(index)        
    select.currentIndexChanged.connect(updateFct)
    return select

def createCheckbox(text,default, updateFct):
        
            box=MyGui.QCheckBox(text)
            box.setChecked(default)
            box.stateChanged.connect(updateFct)
            return box

def createTextInput(default, updateFct):
            box=MyGui.QLineEdit()
            box.setText(str(default))
            box.textChanged.connect(updateFct)
            return box

# ----- Get Value ----------------------------------

def getValueSelect(obj):
    return obj.currentText()

def getTextInput(obj):
    return str(obj.text())

def getCheckboxValue(obj):
    return str(obj.text())

# ----- Set Value ----------------------------------

def setText(box,value):
    box.setText(str(value))

def setCheckbox(box, value):
    box.setChecked(bool(value))