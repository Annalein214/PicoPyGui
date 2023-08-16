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
       
        labelHintChange=createLabel("Changes only take effect in \nthe next measurement.")

        # --- Voltage ---
        labelVoltage=createLabel("Voltage Range")
        options=[]
        for entry in self.daq.scope.CHANNEL_RANGE:
            options.append(entry["rangeStr"])
            if self.settings.voltagerange[self.channel]==entry["rangeV"]:
                default=entry["rangeStr"]
        self.chooseVoltage=createSelect(options, default, self.updateVoltage)

        # --- Coupling ---
        labelCoupling = createLabel("Coupling")
        self.chooseCoupling=createSelect(self.daq.scope.CHANNEL_COUPLINGS,          
                                         self.settings.coupling[self.channel], 
                                         self.updateCoupling)

        # --- Offset ---
        labelOffset = createLabel("Offset [mV]")
        self.chooseOffset=createTextInput(int(self.settings.offset[self.channel]), 
                                          self.updateOffset)
        
        # --- Hint for Offset ---
        labelMaxOffset = createLabel("Max.Offset [mV]")
        self.maxOffset = createLabel(str(int(self.daq.scope.maxOffset(self.settings.coupling[self.channel], self.settings.voltagerange[self.channel]))
))

        # --- Analysis ------
        labelAdj= createLabel("Save:")
        self.chooseWfm=createCheckbox("Waveform (data heavy!)", # don't change name, it is processed elsewhere
                            self.settings.save_wfm[self.channel],
                            self.updateAnalysis)
        labelWFMnbr= createLabel("Number of Waveforms to save")
        self.chooseWfmNbr=createTextInput(self.settings.save_wfm_nbr[self.channel], self.updateAnalysis)
        self.chooseMaxAmp=createCheckbox("Max. Amplitude", # don't change name, it is processed elsewhere
                            self.settings.save_max_amp[self.channel],
                            self.updateAnalysis)
        self.chooseMinAmp=createCheckbox("Min. Amplitude", # don't change name, it is processed elsewhere
                            self.settings.save_min_amp[self.channel],
                            self.updateAnalysis)
        self.chooseMaxArea=createCheckbox("Area above baseline", # don't change name, it is processed elsewhere
                            self.settings.save_area[self.channel],
                            self.updateAnalysis)
        self.chooseAvgStd=createCheckbox("Average, standard deviation", # don't change name, it is processed elsewhere
                            self.settings.save_avg_std[self.channel],
                            self.updateAnalysis)
        #self.chooseFFT=createCheckbox("Simple FFT (data+CPU heavy!)", # don't change name, it is processed elsewhere
        #                    self.settings.save_fft[self.channel],
        #                    self.updateAnalysis)
        #labelFFTnbr= createLabel("Number of FFT to save")
        #self.chooseFFTNbr=createTextInput(self.settings.save_fft_nbr[self.channel], self.updateAnalysis)

        labelNbrHint = createLabel("If you choose 0 waveforms \nor fft to save, all will be \nsaved. This is very data/CPU \nheavy!")

        # -------------------------------------------------
        # compose the layout
        c=0
        grid.addWidget(labelHintChange,       c,0)
        c+=1
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
        c+=1
        grid.addWidget(labelAdj,             c,0)
        c+=1
        grid.addWidget(self.chooseWfm,             c,1)
        c+=1
        grid.addWidget(labelWFMnbr,             c,0)
        grid.addWidget(self.chooseWfmNbr,             c,1)

        c+=1
        grid.addWidget(self.chooseMaxAmp,             c,1)
        c+=1
        grid.addWidget(self.chooseMinAmp,             c,1)
        c+=1
        grid.addWidget(self.chooseMaxArea,             c,1)
        c+=1
        grid.addWidget(self.chooseAvgStd,             c,1)
        c+=1
        #grid.addWidget(self.chooseFFT,             c,1)
        #c+=1
        #grid.addWidget(labelFFTnbr,             c,0)
        #grid.addWidget(self.chooseFFTNbr,             c,1)
        c+=1
        grid.addWidget(labelNbrHint,             c,1)
        c+=1

        #---
        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()

    # ********************************************************************************
    # Update functions

    def updateAnalysis(self):
        # todo a bit repetitive
        save_wfm=getCheckboxEnabled(self.chooseWfm)
        # prevent issue if values are changed at runtime in channel but display is not executed before run starts
        if not save_wfm and self.settings.raw_data_ch.split(":")[0]==self.channel:
            self.settings.saveSetting("raw_data_ch", "None")
        self.settings.saveSetting("save_wfm."+self.channel, save_wfm)



        save_max_amp=getCheckboxEnabled(self.chooseMaxAmp)
        if ":" in self.settings.hist_ch_mode:
            ch,mode=self.settings.hist_ch_mode.split(":")
            if not save_max_amp and ch==self.channel and "Max" in mode:
                self.settings.saveSetting("hist_ch_mode", "None")
        self.settings.saveSetting("save_max_amp."+self.channel, save_max_amp)


        save_min_amp=getCheckboxEnabled(self.chooseMinAmp)
        if ":" in self.settings.hist_ch_mode:
            ch,mode=self.settings.hist_ch_mode.split(":")
            if not save_min_amp and ch==self.channel and "Min" in mode:
                self.settings.saveSetting("hist_ch_mode", "None")
        self.settings.saveSetting("save_min_amp."+self.channel, save_min_amp)

        save_area=getCheckboxEnabled(self.chooseMaxArea)
        if ":" in self.settings.hist_ch_mode:
            ch,mode=self.settings.hist_ch_mode.split(":")
            if not save_area and ch==self.channel and "Area" in mode:
                self.settings.saveSetting("hist_ch_mode", "None")
        self.settings.saveSetting("save_area."+self.channel, save_area)

        save_avg_std=getCheckboxEnabled(self.chooseAvgStd)
        if ":" in self.settings.hist_ch_mode:
            ch,mode=self.settings.hist_ch_mode.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("hist_ch_mode", "None")
        if ":" in self.settings.time_ch_mode1:
            ch,mode=self.settings.time_ch_mode1.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("time_ch_mode1", "None")
        if ":" in self.settings.time_ch_mode2:
            ch,mode=self.settings.time_ch_mode2.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("time_ch_mode2", "None")
        if ":" in self.settings.str_ch_mode1:
            ch,mode=self.settings.str_ch_mode1.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("str_ch_mode1", "None")
        if ":" in self.settings.str_ch_mode2:
            ch,mode=self.settings.str_ch_mode2.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("str_ch_mode2", "None")
        if ":" in self.settings.str_ch_mode3:
            ch,mode=self.settings.str_ch_mode3.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("str_ch_mode3", "None")
        if ":" in self.settings.str_ch_mode4:
            ch,mode=self.settings.str_ch_mode4.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("str_ch_mode4", "None")
        if ":" in self.settings.str_ch_mode5:
            ch,mode=self.settings.str_ch_mode5.split(":")
            if not save_avg_std and ch==self.channel and ("Std" in mode or "Average" in mode):
                self.settings.saveSetting("str_ch_mode5", "None")
        self.settings.saveSetting("save_avg_std."+self.channel, save_avg_std)
        
        #self.settings.save_fft[self.channel]=getCheckboxEnabled(self.chooseFFT)
        #self.settings.saveSetting("save_fft."+self.channel, self.settings.save_fft[self.channel])



        wfmnbr=int(getTextInput(self.chooseWfmNbr))
        if wfmnbr=="-" or wfmnbr=="":
            wfmnbr=1
        try:
            wfmnbr=int(float(wfmnbr))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%wfmnbr)
            wfmnbr=1

        if wfmnbr<1:
            self.log.error("Save at least one waveform or disable waveforms")
            wfmnbr=1
        setText(self.chooseWfmNbr,wfmnbr)
        #self.settings.save_wfm_nbr[self.channel]=wfmnbr
        #self.settings.save_fft_nbr[self.channel]=int(getTextInput(self.chooseFFTNbr))

        self.settings.saveSetting("save_wfm_nbr."+self.channel, wfmnbr)
        #self.settings.saveSetting("save_fft_nbr."+self.channel, self.settings.save_fft_nbr[self.channel])



    def updateOffsetHint(self):
        maxOffset=int(self.daq.scope.maxOffset(self.settings.coupling[self.channel], self.settings.voltagerange[self.channel]))
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
                            str(self.settings.coupling[self.channel]), 
                            str(self.settings.voltagerange[self.channel])))
            offset=maxOffset

        self.chooseOffset.setText(str(offset))
        #self.settings.offset[self.channel]=offset
        # save value to settings
        self.settings.saveSetting("offset."+self.channel, offset)

    def updateVoltage(self):
        # get current chosen value
        voltageStr=getValueSelect(self.chooseVoltage)
        # save value to daq attributes
        for entry in self.daq.scope.CHANNEL_RANGE:
            if voltageStr==entry["rangeStr"]:
                voltagerange=entry["rangeV"]
                break
                #self.settings.voltagerange[self.channel]=voltagerange
        # save value to settings
        self.settings.saveSetting("voltagerange."+self.channel, voltagerange)
        # update info about offset, as this depends on voltagerange
        self.updateOffsetHint()
        self.updateOffset()
        

    def updateCoupling(self):
        # get current chosen value
        coupling=getValueSelect(self.chooseCoupling)
        # save value to daq attributes
        #self.settings.coupling[self.channel] = coupling
        # save value to settings
        self.settings.saveSetting("coupling."+self.channel, coupling)
        # update info about offset, as this depends on coupling
        self.updateOffsetHint()
        self.updateOffset()

    #def enable(self):
        # TODO: why was this done?
        #if voltagerange!=self.settings.voltagerange[self.channel]:
        #    self.log.error("Required Voltage range not available: %f\n"+\
        #                   "Chose %f instead"%(voltagerange, self.settings.voltagerange))
        
        # update trigger minimum
        #self.trigger.minVoltage.setText(str(self.daq.suggestedMinVoltage())) # after all other settings have been done!!
    