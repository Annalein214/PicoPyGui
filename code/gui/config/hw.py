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
        self.hw=hw # TODO not needed?

        # -------------------------------------------------
        # layout
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()
        
        labelHintChange=createLabel("Changes only take effect in \nthe next measurement.")


        # --- Sleeptime ---
        labelTime = createLabel("Time between \nmeasurements [s]")
        self.chooseTime=createTextInput(int(self.settings.HWSleepTime), 
                                          self.updateHW)

        labelHint=createLabel("Switch on available Sensors:")

        # HWT: add your options here
        # --- Dummy ----
        self.chooseDummy=createCheckbox("Dummy", # don't change name, it is processed elsewhere
                            self.settings.useDummy,
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
        #self.settings.HWSleepTime=time
        # save value to settings
        self.settings.saveSetting("HWSleepTime", time)


        # HWT handle user choice here

        useDummy=getCheckboxEnabled(self.chooseDummy)
        if ":" in self.settings.time_ch_mode1:
                ch,mode=self.settings.time_ch_mode1.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("time_ch_mode1", "None")
        if ":" in self.settings.time_ch_mode2:
                ch,mode=self.settings.time_ch_mode2.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("time_ch_mode2", "None")
        if ":" in self.settings.str_ch_mode1:
                ch,mode=self.settings.str_ch_mode1.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("str_ch_mode1", "None")
        if ":" in self.settings.str_ch_mode2:
                ch,mode=self.settings.str_ch_mode2.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("str_ch_mode2", "None")
        if ":" in self.settings.str_ch_mode3:
                ch,mode=self.settings.str_ch_mode3.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("str_ch_mode3", "None")
        if ":" in self.settings.str_ch_mode4:
                ch,mode=self.settings.str_ch_mode4.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("str_ch_mode4", "None")
        if ":" in self.settings.str_ch_mode5:
                ch,mode=self.settings.str_ch_mode5.split(":")
                if mode=="Dummy" and not useDummy:
                    self.settings.saveSetting("str_ch_mode5", "None")
        # todo the handling of all these settings could be made easier somehow
        self.settings.saveSetting("useDummy", useDummy)



