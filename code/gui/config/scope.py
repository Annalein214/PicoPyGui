from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets


from code.gui.helper import *


class scopeConfigWidget(MyGui.QWidget):
    '''
    trigger tab widget
    '''
    def __init__(self, parent, log, daq, settings):
        super(scopeConfigWidget, self).__init__(parent)
        self.log=log
        self.daq=daq
        self.settings=settings

        # -------------------------------------------------
        # layout
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()

        # --- Channel ---
        labelChannel=createLabel("Trigger Channel")
        options=[]
        for i in range(self.daq.scope.NUM_CHANNELS):
            options.append(list(self.daq.scope.CHANNELS)[i][0])
        self.chooseChannel=createSelect(options, 
                                        self.daq.triggerchannel, 
                                        self.updateChannel)

        # --- Mode ---
        labelMode = createLabel("Trigger Mode")
        options=[]
        for entry in self.daq.scope.THRESHOLD_TYPE.items():
            options.append(entry[0])
        self.chooseMode=createSelect(options,
                                    self.daq.triggermode,
                                    self.updateMode)
        # --- min suggested Voltage ---
        labelMinVoltage = createLabel("Min. Voltage [mV]")
        self.minVoltage = createLabel(self.daq.scope.MINTRIGGER[self.daq.voltagerange[self.daq.triggerchannel]])


        # --- Voltage ---
        labelVoltage = createLabel("Tr. Voltage [mV]  ")
        self.chooseVoltage=createTextInput(self.daq.triggervoltage,self.updateVoltage)

        # --- Delay ---
        labelDelay = createLabel("Tr. Delay [Sampling Interval]")
        self.chooseDelay = createTextInput(self.daq.triggerdelay, self.updateDelay)
        
        labelHintDelay = createLabel("Note: + will shift trigger to left. \n"+\
                                     "Default at 0 is a 10% shift to right. \n"+\
                                     "Make sure you don't choose a value \n"+\
                                     "larger than 10% otherwise the \n"+\
                                     "waveform is shifted out of the \n"+\
                                     "analysis window.")
        # --- Timeout ---
        labelTimeout = createLabel("Timeout [ms]")
        self.chooseTimeout=createTextInput(self.daq.triggertimeout,self.updateTimeout)

        # --- Frequency ---
        labelFreq = createLabel("Sampling frequency [Hz]")
        self.chooseFreq = createTextInput("%e"%self.daq.samplefreq, self.updateFrequency)

        labelInt= createLabel("Sampling Interval [ns]")
        self.labelIntVal=createLabel("%e"%(1.0/self.daq.samplefreq*1.e9))

        # --- Samples ---
        labelSample = createLabel("Number of samples")
        self.chooseSample = createTextInput(str(int(self.daq.nosamples)), self.updateSampleNumer)

        labelWvl= createLabel("Length of Capture [ns]")
        self.labelWvlVal=createLabel("%e"%(int(self.daq.nosamples)/self.daq.samplefreq*1.e9))

        # --- Captures ---
        labelCaptures = createLabel("Number of captures")
        self.chooseCaptures = createTextInput(str(int(self.daq.captures)), self.updateCaptures)

        # --- Choose channels

        labelAdj= createLabel("Switch on / off:")
        self.chEnabled=[]
        self.chEnNum=0
        for i in range(self.daq.scope.NUM_CHANNELS):
            chName=list(self.daq.scope.CHANNELS)[i][0]
            en=bool(self.daq.channelEnabled[chName])
            if chName==self.daq.triggerchannel and not en:
                self.log.error("Trigger channel (%s) is not enabled." % chName)
                en=True
            self.chEnNum+=en
            wid=createCheckbox("Channel %s"%chName, # don't change name, it is processed elsewhere
                                       en,
                                       self.updateChEn)
            self.chEnabled.append(wid)
        # --- Measurement time
        labelTime = createLabel("Measurement time [min]")
        self.chooseTime=createTextInput(self.daq.measurementduration, self.updateTime)

        # -------------------------------------------------
        # compose the layout

        c=0
        grid.addWidget(labelChannel,          c,0) # y, x
        grid.addWidget(self.chooseChannel,    c,1) 
        c+=1
        grid.addWidget(labelMinVoltage,          c,0) 
        grid.addWidget(self.minVoltage,    c,1)         
        c+=1
        grid.addWidget(labelVoltage,          c,0) 
        grid.addWidget(self.chooseVoltage,    c,1) 
        c+=1
        grid.addWidget(labelMode,             c,0) 
        grid.addWidget(self.chooseMode,       c,1) 
        c+=1
        grid.addWidget(labelDelay,            c,0) 
        grid.addWidget(self.chooseDelay,      c,1) 
        c+=1
        grid.addWidget(labelHintDelay,            c,1)
        c+=1
        grid.addWidget(labelFreq,           c,0) 
        grid.addWidget(self.chooseFreq,     c,1) 
        c+=1
        grid.addWidget(labelInt,           c,0) 
        grid.addWidget(self.labelIntVal,     c,1) 
        c+=1
        grid.addWidget(labelSample,           c,0) 
        grid.addWidget(self.chooseSample,     c,1) 
        c+=1
        grid.addWidget(labelWvl,           c,0) 
        grid.addWidget(self.labelWvlVal,     c,1) 
        c+=1
        grid.addWidget(labelCaptures,         c,0) 
        grid.addWidget(self.chooseCaptures,   c,1)
        c+=1
        grid.addWidget(labelAdj,             c,0)
        for entry in self.chEnabled:
            c+=1
            grid.addWidget(entry,            c,1)  
        c+=1
        grid.addWidget(labelTime,         c,0) 
        grid.addWidget(self.chooseTime,   c,1)

        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()

    # ********************************************************************************
    # Update functions

    def updateTime(self):

        duration = str(self.chooseTime.text())
        if duration=="": duration=0
        try:
            duration=int(duration)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%duration)
            duration=0
            setText(self.chooseTime,"0")
        self.daq.measurementduration=duration
        self.settings.saveSetting("measurementduration", self.daq.measurementduration)
 

    def updateFrequency(self):
        freq = str(getTextInput(self.chooseFreq))
        if freq=="":
            freq=1.e9
        try:
            samplefreq=int(float(freq))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%freq)
            samplefreq=1.e9
            setText(self.chooseFreq,"1.e9")

        sampleInterval = 1.0 / samplefreq
        timebase=self.daq.scope.getTimeBaseNum(sampleInterval)
        ntimebase=timebase
        if timebase==0 and self.chEnNum==2:
            ntimebase=1
        elif timebase<=1 and self.chEnNum>2:
            ntimebase=2
        if timebase<=2 and self.chEnNum>4:
            ntimebase=3
        if timebase!=ntimebase:
            self.log.error("Adjusted timebase from %d to %d due to too many channels being enabled: %d" % (timebase, 
                                                ntimebase, 
                                                self.chEnNum))
            timebase=ntimebase

        newInterval=self.daq.scope.getTimestepFromTimebase(timebase)
        newFreq=1.0/newInterval

        setText(self.labelIntVal,"%e"%(newInterval*1e9))
        setText(self.labelWvlVal,"%e"%(newInterval*int(self.daq.nosamples)*1e9))

        if abs(newFreq-samplefreq)>0.1:
            self.log.warning("Chosen frequency (%e) was changed to match Scope settings: %e"%(samplefreq, newFreq))
            samplefreq=newFreq
            setText(self.chooseFreq,"%e"%newFreq)

        self.daq.samplefreq=samplefreq
        self.settings.saveSetting("samplefreq", self.daq.samplefreq)

    def updateSampleNumer(self):
        nosamples = str(self.chooseSample.text())
        try:
            nosamples=int(nosamples)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"% nosamples)
            nosamples=0
            setText(self.chooseSample,"1.e9")


        setText(self.labelWvlVal,"%e"%(float(nosamples)/self.daq.samplefreq*1e9))

        self.daq.nosamples=nosamples
        self.settings.saveSetting("nosamples", self.daq.nosamples)

    def updateCaptures(self):

        captures = str(self.chooseCaptures.text())
        try:
            captures=int(captures)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%captures)
            captures=0
            setText(self.chooseCaptures,"1.e9")
        self.daq.captures=0
        self.settings.saveSetting("captures", self.daq.captures)
        # connection between samples and captures can only be done during runtime!        

    def updateChannel(self):
        '''
        read all chosen settings
        '''

        self.daq.triggerchannel = str(getValueSelect(self.chooseChannel))
        setText(self.minVoltage,str(self.daq.scope.MINTRIGGER[self.daq.voltagerange[self.daq.triggerchannel]]))
        self.settings.saveSetting("triggerchannel", self.daq.triggerchannel)

        self.updateChEn()
    def updateMode(self):
        self.daq.triggermode = str(getValueSelect(self.chooseMode))
        self.settings.saveSetting("triggermode", self.daq.triggermode)

    def updateTimeout(self):
        self.daq.triggertimeout =str(getTextInput(self.chooseDelay))
        self.settings.saveSetting("triggertimeout", self.daq.triggertimeout)

    def updateVoltage(self):
        triggervoltage = str(self.chooseVoltage.text())
        if triggervoltage=="-" or triggervoltage=="":# no wired effect when starting to type a negative number
            triggervoltage=0
        try:
            triggervoltage=float(triggervoltage)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%triggervoltage)
            triggervoltage=0
            setText(self.chooseVoltage,"0")
        if abs(triggervoltage)/1000>self.daq.voltagerange[self.daq.triggerchannel]:
            self.log.error("Triggervoltage (%d V) outside voltagerange (%s V) for channel %s" % (
                                triggervoltage/1000, 
                                self.daq.voltagerange[self.daq.triggerchannel], 
                                self.daq.triggerchannel))
        self.daq.triggervoltage=triggervoltage
        self.settings.saveSetting("triggervoltage", self.daq.triggervoltage)

    def updateDelay(self):
        delay = str(getTextInput(self.chooseDelay))
        if delay=="-" or delay=="":# no wired effect when starting to type a negative number
            delay=0
        try:
            triggerdelay=int(float(delay))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%delay)
            triggerdelay=0
            setText(self.chooseVoltage,"0")
        self.daq.triggerdelay=triggerdelay
        self.settings.saveSetting("triggerdelay", self.daq.triggerdelay)


    def updateChEn(self):

        i=0
        self.chEnNum=0
        for entry in self.chEnabled:
            chName=getCheckboxValue(entry)
            chName=chName.split(" ")[1]
            en=entry.isChecked()
            if chName==self.daq.triggerchannel and not en:
                self.log.error("Trigger channel (%s) is not enabled." % chName)
                en=True
            setCheckbox(entry,en)
            self.chEnNum+=en
            self.daq.channelEnabled[chName]=en
        
        self.settings.saveSetting("channelEnabled.%s"%chName, 
                                self.daq.channelEnabled[chName])
        
        self.updateFrequency()
        # TODO bug: if you press the trigger channel twice, the check actually disappears!
        # This is only in GUI, the variable is still set correctly