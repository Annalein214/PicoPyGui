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

        # --- Lightsensor ----
        self.chooseLight=createCheckbox("Lightsensor", # don't change name, it is processed elsewhere
                            self.settings.useLightsensor,
                            self.updateHW)

        # --- HV ----
        self.chooseHV=createCheckbox("HV", # don't change name, it is processed elsewhere
                            self.settings.useHV,
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
        c+=1
        grid.addWidget(self.chooseLight,       c,1)
        c+=1
        grid.addWidget(self.chooseHV,       c,1)

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


        # HWT handle user choice here, also handle the impact on possible choices in the display tab
        self.simpleChoice(self.settings.useDummy, "Dummy", self.chooseDummy, "useDummy")         
        self.simpleChoice(self.settings.useLightsensor, "Lightsensor", self.chooseLight, "useLightsensor")        
        self.simpleChoice(self.settings.useHV, "HV", self.chooseHV, "useHV")        


    def simpleChoice(self,mode, modeName, selectMode, varName):
        mode=getCheckboxEnabled(selectMode)
        self.settings.saveSetting(varName, mode)
        self.switchOption(modeName, mode, self.settings.time_ch_mode1, "time_ch_mode1")
        self.switchOption(modeName, mode,self.settings.time_ch_mode2, "time_ch_mode2")
        self.switchOption(modeName, mode,self.settings.str_ch_mode1, "str_ch_mode1")
        self.switchOption(modeName, mode,self.settings.str_ch_mode2, "str_ch_mode2")
        self.switchOption(modeName, mode,self.settings.str_ch_mode3, "str_ch_mode3")
        self.switchOption(modeName, mode,self.settings.str_ch_mode4, "str_ch_mode4")
        self.switchOption(modeName, mode,self.settings.str_ch_mode5, "str_ch_mode5")
        

    def switchOption(self,modeName, mode, selection, varName):
            if ":" in selection:
                ch,mode=selection.split(":")
                if mode==modeName and not mode:
                    self.settings.saveSetting(varName, "None")

