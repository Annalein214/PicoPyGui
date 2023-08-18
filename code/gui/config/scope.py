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

        labelHintChange=createLabel("Changes only take effect in \nthe next measurement.")

        # --- Channel ---
        labelChannel=createLabel("Trigger Channel")
        options=[]
        for i in range(self.daq.scope.NUM_CHANNELS):
            options.append(list(self.daq.scope.CHANNELS)[i][0])
        self.chooseChannel=createSelect(options, 
                                        self.settings.triggerchannel, 
                                        self.updateChannel)

        # --- Mode ---
        labelMode = createLabel("Trigger Mode")
        options=[]
        for entry in self.daq.scope.THRESHOLD_TYPE.items():
            options.append(entry[0])
        self.chooseMode=createSelect(options,
                                    self.settings.triggermode,
                                    self.updateMode)
        # --- min suggested Voltage ---
        labelMinVoltage = createLabel("Min. Voltage [mV]")
        self.minVoltage = createLabel(self.daq.scope.MINTRIGGER[self.settings.voltagerange[self.settings.triggerchannel]])


        # --- Voltage ---
        labelVoltage = createLabel("Tr. Voltage [mV]  ")
        self.chooseVoltage=createTextInput(self.settings.triggervoltage,self.updateVoltage)

        # --- Delay ---
        labelDelay = createLabel("Tr. Delay [Sampling Interval]")
        self.chooseDelay = createTextInput(self.settings.triggerdelay, self.updateDelay)

        # --- Pretriggersamples ---
        labelPretrig = createLabel("Pre-trigger Samples [%]")
        self.choosePreTrig = createTextInput(self.settings.nopretriggersamples, self.updatePretrig)
        
        
        # --- Timeout ---
        labelTimeout = createLabel("Timeout [ms]")
        self.chooseTimeout=createTextInput(self.settings.triggertimeout,self.updateTimeout)

        # --- Frequency ---
        labelFreq = createLabel("Sampling frequency [Hz]")
        self.chooseFreq = createTextInput("%e"%self.settings.samplefreq, self.updateFrequency)

        labelInt= createLabel("Sampling Interval [ns]")
        self.labelIntVal=createLabel("%e"%(1.0/self.settings.samplefreq*1.e9))

        # --- Samples ---
        labelSample = createLabel("Number of samples")
        self.chooseSample = createTextInput(str(int(self.settings.nosamples)), self.updateSampleNumer)

        labelWvl= createLabel("Length of Capture [ns]")
        self.labelWvlVal=createLabel("%e"%(int(self.settings.nosamples)/self.settings.samplefreq*1.e9))

        # --- Captures ---
        labelCaptures = createLabel("Number of captures")
        self.chooseCaptures = createTextInput(str(int(self.settings.captures)), self.updateCaptures)

        # --- Choose channels

        labelAdj= createLabel("Switch on / off:")
        self.chEnabled=[]
        self.chEnNum=0
        for i in range(self.daq.scope.NUM_CHANNELS):
            chName=list(self.daq.scope.CHANNELS)[i][0]
            en=bool(self.settings.channelEnabled[chName])
            if chName==self.settings.triggerchannel and not en:
                self.log.error("Trigger channel (%s) is not enabled." % chName)
                en=True
            self.chEnNum+=en
            wid=createCheckbox("Channel %s"%chName, # don't change name, it is processed elsewhere
                                       en,
                                       self.updateChEn)
            self.chEnabled.append(wid)
        # --- Measurement time
        labelTime = createLabel("Measurement time [min]")
        self.chooseTime=createTextInput(self.settings.measurementduration, self.updateTime)

        # -------------------------------------------------
        # compose the layout

        c=0
        grid.addWidget(labelHintChange,       c,0)
        c+=1
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
        grid.addWidget(labelPretrig,            c,0) 
        grid.addWidget(self.choosePreTrig,      c,1) 
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
        #self.settings.measurementduration=duration
        self.settings.saveSetting("measurementduration", duration)
 

    def updateFrequency(self):
        freq = str(getTextInput(self.chooseFreq))
        if freq=="" or freq==0:
            freq=1.e9
        try:
            samplefreq=int(float(freq))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%freq)
            samplefreq=1.e9
            setText(self.chooseFreq,"1.e9")

        if samplefreq==0: samplefreq=1.e9
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
        setText(self.labelWvlVal,"%e"%(newInterval*int(self.settings.nosamples)*1e9))

        if abs(newFreq-samplefreq)>0.1:
            self.log.warning("Chosen frequency (%e) was changed to match Scope settings: %e"%(samplefreq, newFreq))
            samplefreq=newFreq
            setText(self.chooseFreq,"%e"%newFreq)

        #self.settings.samplefreq=samplefreq
        self.settings.saveSetting("samplefreq", samplefreq)

    def updateSampleNumer(self):
        nosamples = str(self.chooseSample.text())
        try:
            nosamples=int(nosamples)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"% nosamples)
            nosamples=0
            setText(self.chooseSample,"1.e9")


        setText(self.labelWvlVal,"%e"%(float(nosamples)/self.settings.samplefreq*1e9))

        self.settings.nosamples=nosamples
        self.settings.saveSetting("nosamples", nosamples)

    def updateCaptures(self):

        captures = str(self.chooseCaptures.text())
        try:
            captures=int(captures)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%captures)
            captures=0
            setText(self.chooseCaptures,"0")
        #self.settings.captures=captures
        self.settings.saveSetting("captures", captures)
        # connection between samples and captures can only be done during runtime!        

    def updateChannel(self):
        '''
        read all chosen settings
        '''

        triggerchannel = str(getValueSelect(self.chooseChannel))
        setText(self.minVoltage,str(self.daq.scope.MINTRIGGER[self.settings.voltagerange[triggerchannel]]))
        self.settings.saveSetting("triggerchannel", triggerchannel)

        self.updateChEn()
    def updateMode(self):
        triggermode = str(getValueSelect(self.chooseMode))
        self.settings.saveSetting("triggermode", triggermode)

    def updateTimeout(self):
        triggertimeout =str(getTextInput(self.chooseDelay))
        self.settings.saveSetting("triggertimeout", triggertimeout)

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
        if triggervoltage/1000 > float(self.settings.voltagerange[self.settings.triggerchannel]) - self.settings.offset[self.settings.triggerchannel]/1000 or \
           triggervoltage/1000 < -float(self.settings.voltagerange[self.settings.triggerchannel]) - self.settings.offset[self.settings.triggerchannel]/1000:
            self.log.error("Triggervoltage (%f V) outside voltagerange (%f - %f V) for channel %s" % (
                                triggervoltage/1000, 
                                -self.settings.voltagerange[self.settings.triggerchannel]- self.settings.offset[self.settings.triggerchannel]/1000,
                                self.settings.voltagerange[self.settings.triggerchannel]- self.settings.offset[self.settings.triggerchannel]/1000,
                                self.settings.triggerchannel))
        #self.settings.triggervoltage=triggervoltage
        self.settings.saveSetting("triggervoltage", triggervoltage)

    def updateDelay(self):
        delay = str(getTextInput(self.chooseDelay))
        if delay=="-" or delay=="":# no wired effect when starting to type a negative number
            delay=0
        try:
            triggerdelay=int(float(delay))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%delay)
            triggerdelay=0
            setText(self.choosePreTrig,"0")
        #self.settings.triggerdelay=triggerdelay
        self.settings.saveSetting("triggerdelay", triggerdelay)


    def updatePretrig(self):
        pretrig = str(getTextInput(self.choosePreTrig))
        if pretrig=="-" or pretrig=="":# no wired effect when starting to type a negative number
            pretrig=0.1
        try:
            pretrigger=float(pretrig)
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%delay)
            pretrigger=0.1
            setText(self.choosePreTrig,"0.1")
        if pretrigger<0 or pretrigger > 1: 
            self.log.error("Pre Trigger sample fraction needs to be between 0 and 1. I recommend 0.1")
            setText(self.choosePreTrig,"0.1")
        self.settings.saveSetting("nopretriggersamples", pretrigger)


    # --- Pretriggersamples ---
        labelPretrig = createLabel("Pre-trigger Samples\n[Sampling Interval]")
        self.choosePreTrig = createTextInput(self.settings.nopretriggersamples, self.updatePretrig)
        


    def updateChEn(self):

        i=0
        self.chEnNum=0
        for entry in self.chEnabled:
            chName=getCheckboxValue(entry)
            chName=chName.split(" ")[1]
            en=entry.isChecked()
            if chName==self.settings.triggerchannel and not en:
                self.log.error("Trigger channel (%s) is not enabled." % chName)
                en=True
            setCheckbox(entry,en)
            self.chEnNum+=en
            #self.settings.channelEnabled[chName]=en
        
            if ":" in self.settings.hist_ch_mode:
                ch,mode=self.settings.hist_ch_mode.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("hist_ch_mode", "None")
            if ":" in self.settings.time_ch_mode1:
                ch,mode=self.settings.time_ch_mode1.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("time_ch_mode1", "None")
            if ":" in self.settings.time_ch_mode2:
                ch,mode=self.settings.time_ch_mode2.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("time_ch_mode2", "None")
            if ":" in self.settings.str_ch_mode1:
                ch,mode=self.settings.str_ch_mode1.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("str_ch_mode1", "None")
            if ":" in self.settings.str_ch_mode2:
                ch,mode=self.settings.str_ch_mode2.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("str_ch_mode2", "None")
            if ":" in self.settings.str_ch_mode3:
                ch,mode=self.settings.str_ch_mode3.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("str_ch_mode3", "None")
            if ":" in self.settings.str_ch_mode4:
                ch,mode=self.settings.str_ch_mode4.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("str_ch_mode4", "None")
            if ":" in self.settings.str_ch_mode5:
                ch,mode=self.settings.str_ch_mode5.split(":")
                if ch==chName and en==False:
                    self.settings.saveSetting("str_ch_mode5", "None")

            #print("Enabled", chName, en)
            self.settings.saveSetting("channelEnabled.%s"%chName,en)
        
        self.updateFrequency()
        # TODO bug: if you press the trigger channel twice, the check actually disappears!
        # This is only in GUI, the variable is still set correctly