from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets

from code.gui.helper import *


class channelConfigWidget(MyGui.QWidget):
    '''
    The master of the channel config widgets
    '''
    def __init__(self, parent, log, channel, daq, settings, #trigger
        ):
        super(channelConfigWidget, self).__init__(parent)
        self.log=log
        self.channel=channel # this widget is used several times, dependent on the number of available channels
        self.daq=daq # this config tab is connected with the daq
        self.settings=settings # save changes to the general settings too
        #self.trigger=trigger # changes in this config also influence the trigger
        
        # -------------------------------------------------
        # layout 
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()
       
        # --- Voltage ---
        labelVoltage=createLabel("Voltage Range")
        options=[]
        for entry in self.daq.scope.CHANNEL_RANGE:
            options.append(entry["rangeStr"])
            if self.daq.voltagerange[self.channel]==entry["rangeV"]:
                default=entry["rangeStr"]
        self.chooseVoltage=createSelect(options, default, self.updateVoltage)

        # --- Voltage ---
        labelCoupling = createLabel("Coupling")
        self.chooseCoupling=createSelect(self.daq.scope.CHANNEL_COUPLINGS,          
                                         self.daq.coupling[self.channel], 
                                         self.updateCoupling)

        # --- Offset ---
        labelOffset = createLabel("Offset [mV]")
        self.chooseOffset=createTextInput(int(self.daq.offset[self.channel]), 
                                          self.updateOffset)
        
        # --- Hint for Offset ---
        labelMaxOffset = createLabel("Max.Offset [mV]")
        self.maxOffset = createLabel(str(int(self.daq.scope.maxOffset(self.daq.coupling[self.channel], self.daq.voltagerange[self.channel]))
))

        # -------------------------------------------------
        # compose the layout
        c=0
        grid.addWidget(labelVoltage,          c,0) # y, x
        grid.addWidget(self.chooseVoltage,    c,1) 
        c+=1
        grid.addWidget(labelCoupling,         c,0) 
        grid.addWidget(self.chooseCoupling,   c,1) 
        c+=1
        grid.addWidget(labelOffset,           c,0) 
        grid.addWidget(self.chooseOffset,     c,1) 
        c+=1
        grid.addWidget(labelMaxOffset,           c,0) 
        grid.addWidget(self.maxOffset,     c,1) 
        
        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()

    # ********************************************************************************
    # Update functions

    def updateOffsetHint(self):
        maxOffset=int(self.daq.scope.maxOffset(self.daq.coupling[self.channel], self.daq.voltagerange[self.channel]))
        self.maxOffset.setText(str(maxOffset))
        return maxOffset

    def updateOffset(self):
        offset = getTextInput(self.chooseOffset)
        if offset=="" or offset=="-": offset=0
        try:
            offset=int(float(offset))
        except:
            self.log.error("Could not convert string to integer %s"%offset)
            offset=0

        maxOffset=self.updateOffsetHint()
        if abs(offset)>maxOffset:
            self.log.error("Offset (%d mV) exceeding max Offset (%d mV)\n"%(offset,maxOffset)+\
                           "\tfor this choice of Coupling (%s) and Voltage Range (%s)."\
                           %(
                            str(self.daq.coupling[self.channel]), 
                            str(self.daq.voltagerange[self.channel])))
            offset=maxOffset

        self.chooseOffset.setText(str(offset))
        self.daq.offset[self.channel]=0
        # save value to settings
        self.settings.saveSetting("offset."+self.channel, offset)

    def updateVoltage(self):
        # get current chosen value
        voltageStr=getValueSelect(self.chooseVoltage)
        # save value to daq attributes
        for entry in self.daq.scope.CHANNEL_RANGE:
            if voltageStr==entry["rangeStr"]:
                voltagerange=entry["rangeV"]
                self.daq.voltagerange[self.channel]=voltagerange
        # save value to settings
        self.settings.saveSetting("voltagerange."+self.channel, voltagerange)
        # update info about offset, as this depends on voltagerange
        self.updateOffsetHint()
        self.updateOffset()
        

    def updateCoupling(self):
        # get current chosen value
        coupling=getValueSelect(self.chooseCoupling)
        # save value to daq attributes
        self.daq.coupling[self.channel] = coupling
        # save value to settings
        self.settings.saveSetting("coupling."+self.channel, coupling)
        # update info about offset, as this depends on coupling
        self.updateOffsetHint()
        self.updateOffset()

    #def enable(self):
        # TODO: why was this done?
        #if voltagerange!=self.daq.voltagerange[self.channel]:
        #    self.log.error("Required Voltage range not available: %f\n"+\
        #                   "Chose %f instead"%(voltagerange, self.daq.voltagerange))
        
        # update trigger minimum
        #self.trigger.minVoltage.setText(str(self.daq.suggestedMinVoltage())) # after all other settings have been done!!
    