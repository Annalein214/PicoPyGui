from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets

from code.gui.helper import *


class hardwareConfigWidget(MyGui.QWidget):

    def __init__(self, parent, log, daq, settings, hw):
        super(hardwareConfigWidget, self).__init__(parent)
        self.parent=parent
        self.log=log
        self.daq=daq
        self.settings=settings
        self.hw=hw

        # -------------------------------------------------
        # layout
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()
        
        labelHintChange=createLabel("Changes only take effect in \nthe next measurement.")


        # --- Sleeptime ---
        labelTime = createLabel("Time between \nmeasurements [s]")
        self.chooseTime=createTextInput(int(self.hw.HWSleepTime), 
                                          self.updateHW)

        labelHint=createLabel("Switch on available Sensors:")

        # HWT: add your options here
        # --- Dummy ----
        self.chooseDummy=createCheckbox("Dummy", # don't change name, it is processed elsewhere
                            self.hw.useDummy,
                            self.updateHW)

        # -------------------------------------------------
        # compose the layout

        c=0
        grid.addWidget(labelHintChange,       c,0)
        c+=1
        grid.addWidget(labelTime,       c,0)
        grid.addWidget(self.chooseTime,       c,1)
        c+=1
        grid.addWidget(labelHint,       c,0)
        c+=1
        # HWT add your widgets to the grid
        grid.addWidget(self.chooseDummy,       c,1)


        # -------------------------------------------------

        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()


    def updateHW(self):

        time = getTextInput(self.chooseTime)
        if time=="" or time=="-": time=1
        try:
            time=float(time)
        except:
            self.log.error("Could not convert string to float %s"%time)
            time=1
        if time<0:
            self.log.error("Choose a positive time in seconds %f"%time)
            time=1
        self.chooseTime.setText(str(time))
        self.hw.HWSleepTime=time
        # save value to settings
        self.settings.saveSetting("HWSleepTime", time)


        # HWT handle user choice here

        self.hw.useDummy=getCheckboxEnabled(self.chooseDummy)
        self.settings.saveSetting("useDummy", self.hw.useDummy)



