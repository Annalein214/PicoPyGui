from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets

from code.gui.helper import *


class displayConfigWidget(MyGui.QWidget):
    '''
    display tab widget
    '''
    def __init__(self, parent, log, daq, settings, graph, hw):
        super(displayConfigWidget, self).__init__(parent)
        self.parent=parent
        self.log=log
        self.daq=daq
        self.settings=settings
        #self.graph=graph todo remove
        #self.hw=hw todo remove

    # -------------------------------------------------
        # layout
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()

        labelHintChange=createLabel("Changes can be done during \nmeasurement.")

        # --- Live Examples ---
        labelRaw=createLabel("Show waveforms")
        options=self.getRawOptions()
        self.chooseRaw=createSelect(options, 
                                        self.settings.raw_data_ch, 
                                        self.updateDisplay)
        labelRawNbr=createLabel("Number of waveforms")
        self.chooseRawNbr=createTextInput(self.settings.raw_data_nbr, self.updateDisplay)


        # --- Histogram ---
        labelHist=createLabel("Show histogram")
        options=self.getHistOptions()
        self.chooseHist=createSelect(options, 
                                        self.settings.hist_ch_mode, 
                                        self.updateDisplay)


        # --- Time ---
        labelTime1=createLabel("Show time development")
        options=self.getTimeOptions()
        self.chooseTime1=createSelect(options, 
                                        self.settings.time_ch_mode1, 
                                        self.updateDisplay)
        self.chooseTime2=createSelect(options, 
                                        self.settings.time_ch_mode2, 
                                        self.updateDisplay)


        # --- String ---
        labelStr=createLabel("Show as string")
        
        options=self.getStrOptions()
        self.chooseStr1=createSelect(options, 
                                        self.settings.str_ch_mode1, 
                                        self.updateDisplay)
        self.chooseStr2=createSelect(options, 
                                        self.settings.str_ch_mode2, 
                                        self.updateDisplay)
        self.chooseStr3=createSelect(options, 
                                        self.settings.str_ch_mode3, 
                                        self.updateDisplay)
        self.chooseStr4=createSelect(options, 
                                        self.settings.str_ch_mode4, 
                                        self.updateDisplay)
        self.chooseStr5=createSelect(options, 
                                        self.settings.str_ch_mode5, 
                                        self.updateDisplay)

        labelHelp=createLabel("If you miss options, maybe channel is \nnot enabled?")
    # -------------------------------------------------
        # compose the layout

        c=0
        grid.addWidget(labelHintChange,       c,0)
        c+=1
        grid.addWidget(labelRaw,          c,0) # y, x
        grid.addWidget(self.chooseRaw,    c,1) 
        c+=1
        grid.addWidget(labelRawNbr,          c,0) # y, x
        grid.addWidget(self.chooseRawNbr,    c,1)
        c+=1
        grid.addWidget(labelHist,          c,0) # y, x
        grid.addWidget(self.chooseHist,    c,1)
        c+=1
        grid.addWidget(labelTime1,          c,0) # y, x
        grid.addWidget(self.chooseTime1,    c,1)
        c+=1
        grid.addWidget(self.chooseTime2,    c,1) 
        c+=1
        grid.addWidget(labelStr,          c,0) # y, x
        grid.addWidget(self.chooseStr1,    c,1)
        c+=1
        grid.addWidget(self.chooseStr2,    c,1) 
        c+=1
        grid.addWidget(self.chooseStr3,    c,1) 
        c+=1
        grid.addWidget(self.chooseStr4,    c,1) 
        c+=1
        grid.addWidget(self.chooseStr5,    c,1) 
        c+=1
        grid.addWidget(labelHelp,       c,0)
        

        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()

    # ********************************************************************************
    # Update functions

    def updateDisplay(self):
        '''
        only use one function, so that it is easier to use from other widgets
        '''

        #self.log.debug("Update Display")

        #self.settings.raw_data_ch=str(getValueSelect(self.chooseRaw))
        raw_data_ch=str(getValueSelect(self.chooseRaw))
        self.settings.saveSetting("raw_data_ch", raw_data_ch)

        rawNbr = str(getTextInput(self.chooseRawNbr))
        if rawNbr=="-" or rawNbr=="":# no wired effect when starting to type a negative number
            rawNbr=1
        try:
            rawNbr=int(float(rawNbr))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%rawNbr)
            rawNbr=1

        # should be below saved number of WFM
        #if self.settings.raw_data_ch!="None":
        if self.settings.raw_data_ch!="None":
            #if rawNbr>self.settings.save_wfm_nbr[self.settings.raw_data_ch.split(":")[0]]:
            #    rawNbr=self.settings.save_wfm_nbr[self.settings.raw_data_ch.split(":")[0]]
            if rawNbr>self.settings.save_wfm_nbr[self.settings.raw_data_ch.split(":")[0]]:
                rawNbr=self.settings.save_wfm_nbr[self.settings.raw_data_ch.split(":")[0]]
                self.log.debug("Prevent choosing more than available")
        
        if rawNbr<=0:
            self.log.error("Number of waveforms must be at least 1, you chose %d"%rawNbr)
            rawNbr=1
            
        setText(self.chooseRawNbr,rawNbr)
        raw_data_nbr=rawNbr
        self.settings.saveSetting("raw_data_nbr", raw_data_nbr)

        hist_ch_mode=str(getValueSelect(self.chooseHist))
        self.settings.saveSetting("hist_ch_mode", hist_ch_mode)

        time_ch_mode1=str(getValueSelect(self.chooseTime1))
        self.settings.saveSetting("time_ch_mode1", time_ch_mode1)

        time_ch_mode2=str(getValueSelect(self.chooseTime2))
        if time_ch_mode2==self.settings.time_ch_mode1:
            # prevent double work
            self.log.debug("Prevent double work, set Time 2 to None")
            time_ch_mode2=="None"
            setSelect(self.chooseTime2, "None")# use string instead of variable, seems to not have been set in that time
        self.settings.saveSetting("time_ch_mode2", time_ch_mode2)

        # dont care about double work for strings
        str_ch_mode1=str(getValueSelect(self.chooseStr1))
        self.settings.saveSetting("str_ch_mode1", str_ch_mode1)

        str_ch_mode2=str(getValueSelect(self.chooseStr2))
        self.settings.saveSetting("str_ch_mode2", str_ch_mode2)

        str_ch_mode3=str(getValueSelect(self.chooseStr3))
        self.settings.saveSetting("str_ch_mode3", str_ch_mode3)

        str_ch_mode4=str(getValueSelect(self.chooseStr4))
        self.settings.saveSetting("str_ch_mode4", str_ch_mode4)

        str_ch_mode5=str(getValueSelect(self.chooseStr5))
        self.settings.saveSetting("str_ch_mode5", str_ch_mode5)


# ********************************************************************************
    # Update widget functions


    def renewDisplayWidget(self, index):

        #self.log.debug("Renew Display? %d %s"%(index, self.parent.tabText(index)))
        # only update if this tab is opened
        if self.parent.tabText(index)!="Display":
            return

        #self.log.debug("Renew Display!")

        # prevent updateDisplay from firing due to changing the select options
        self.chooseRaw.blockSignals(True)
        self.chooseRawNbr.blockSignals(True)
        self.chooseHist.blockSignals(True)
        self.chooseTime1.blockSignals(True)
        self.chooseTime2.blockSignals(True)
        self.chooseStr1.blockSignals(True)
        self.chooseStr2.blockSignals(True)
        self.chooseStr3.blockSignals(True)
        self.chooseStr4.blockSignals(True)
        self.chooseStr5.blockSignals(True)

        clearSelect(self.chooseRaw)
        options=self.getRawOptions()
        index=recreateSelect(options, self.chooseRaw, self.settings.raw_data_ch)

        if self.settings.raw_data_ch!="None":
            self.settings.raw_data_nbr=min(self.settings.raw_data_nbr,self.settings.save_wfm_nbr[self.settings.raw_data_ch.split(":")[0]])
        setText(self.chooseRawNbr,self.settings.raw_data_nbr)

        clearSelect(self.chooseHist)
        options=self.getHistOptions()
        recreateSelect(options, self.chooseHist, self.settings.hist_ch_mode)

        clearSelect(self.chooseTime1)
        clearSelect(self.chooseTime2)
        options=self.getTimeOptions()
        recreateSelect(options, self.chooseTime1, self.settings.time_ch_mode1)
        recreateSelect(options, self.chooseTime2, self.settings.time_ch_mode2)

        clearSelect(self.chooseStr1)
        clearSelect(self.chooseStr2)
        clearSelect(self.chooseStr3)
        clearSelect(self.chooseStr4)
        clearSelect(self.chooseStr5)
        options=self.getStrOptions()
        recreateSelect(options, self.chooseStr1, self.settings.str_ch_mode1)
        recreateSelect(options, self.chooseStr2, self.settings.str_ch_mode2)
        recreateSelect(options, self.chooseStr3, self.settings.str_ch_mode3)
        recreateSelect(options, self.chooseStr4, self.settings.str_ch_mode4)
        recreateSelect(options, self.chooseStr5, self.settings.str_ch_mode5)

        # revive signals
        self.chooseRaw.blockSignals(False)
        self.chooseRawNbr.blockSignals(False)
        self.chooseHist.blockSignals(False)
        self.chooseTime1.blockSignals(False)
        self.chooseTime2.blockSignals(False)
        self.chooseStr1.blockSignals(False)
        self.chooseStr2.blockSignals(False)
        self.chooseStr3.blockSignals(False)
        self.chooseStr4.blockSignals(False)
        self.chooseStr5.blockSignals(False)

        self.updateDisplay()

    def getRawOptions(self):
        options=["None"]
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            #print(channel,self.settings.channelEnabled[channel], self.settings.save_wfm[channel])
            if self.settings.channelEnabled[channel]:
                if self.settings.save_wfm[channel]:
                    options.append(channel+":waveform")
                #if self.settings.save_fft[channel]:
                #    options.append(channel+":FFT")
        return options

    def getHistOptions(self):

        options=["None", "Triggerrate"]
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                if self.settings.save_max_amp[channel]:
                    options.append(channel+":Max.Amplitude") # no spaces here! otherwise issue in settings.py:126
                if self.settings.save_min_amp[channel]:
                    options.append(channel+":Min.Amplitude")
                if self.settings.save_area[channel]:
                    options.append(channel+":Area")
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Average")
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Std. Deviation")
        return options

    def getTimeOptions(self):
        options=["None", "Triggerrate"]
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Average")
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Std.Deviation")
        # HWT add external hardware options here
        if self.settings.useDummy: 
            options.append("HW:Dummy")
        if self.settings.useLightsensor: 
            options.append("HW:Lightsensor")
        if self.settings.useHV: 
            options.append("HW:HV")
        return options

    def getStrOptions(self):
        options=["None", "Triggerrate"]
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Average")
                if self.settings.save_avg_std[channel]:
                    options.append(channel+":Std.Dev.")
        # HWT add external hardware options here
        if self.settings.useDummy: 
            options.append("HW:Dummy")
        if self.settings.useLightsensor: 
            options.append("HW:Lightsensor")
        if self.settings.useHV: 
            options.append("HW:HV")
        return options
