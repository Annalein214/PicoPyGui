from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets

from code.gui.helper import *


class displayConfigWidget(MyGui.QWidget):
    '''
    trigger tab widget
    '''
    def __init__(self, parent, log, daq, settings, graph):
        super(scopeConfigWidget, self).__init__(parent)
        self.log=log
        self.daq=daq
        self.settings=settings
        self.graph=graph

    # -------------------------------------------------
        # layout
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout

		# --- Live Examples ---
        labelRaw=createLabel("Show waveforms")
        options=self.getRawOptions()
        self.chooseRaw=createSelect(options, 
                                        self.graph.raw_data_ch, 
                                        self.updateDisplay)
        labelRawNbr=createLabel("Number of waveforms")
        self.chooseRawNbr=createTextInput(self.graph.raw_data_nbr, self.updateDisplay)


        # --- Histogram ---
        labelHist=createLabel("Show histogram")
	    options=self.getHistOptions()
        self.chooseHist=createSelect(options, 
                                        self.graph.hist_ch_mode, 
                                        self.updateDisplay)


        # --- Time ---
        labelTime1=createLabel("Show time development")
	    options=self.getTimeOptions()
        self.chooseTime1=createSelect(options, 
                                        self.graph.time_ch_mode1, 
                                        self.updateDisplay)
        self.chooseTime2=createSelect(options, 
                                        self.graph.time_ch_mode2, 
                                        self.updateDisplay)


        # --- String ---
        labelStr=createLabel("Show as string")
        
	    options=self.getStrOptions()
        self.chooseStr1=createSelect(options, 
                                        self.graph.str_ch_mode1, 
                                        self.updateDisplay)
        self.chooseStr2=createSelect(options, 
                                        self.graph.str_ch_mode2, 
                                        self.updateDisplay)
        self.chooseStr3=createSelect(options, 
                                        self.graph.str_ch_mode3, 
                                        self.updateDisplay)
        self.chooseStr4=createSelect(options, 
                                        self.graph.str_ch_mode4, 
                                        self.updateDisplay)
        self.chooseStr5=createSelect(options, 
                                        self.graph.str_ch_mode5, 
                                        self.updateDisplay)
    # -------------------------------------------------
        # compose the layout

        c=0
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

        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()

    # ********************************************************************************
    # Update functions

    def updateDisplay(self):
    	'''
    	only use one function, so that it is easier to use from other widgets
    	'''

    	self.graph.raw_data_ch_type=str(getValueSelect(self.chooseRaw))
    	self.settings.saveSetting("raw_data_ch_type", self.graph.raw_data_ch_type)

    	rawNbr = str(getTextInput(self.chooseRawNbr))
        if rawNbr=="-" or rawNbr=="":# no wired effect when starting to type a negative number
            rawNbr=1
        try:
            rawNbr=int(float(rawNbr))
        except ValueError as e:
            self.log.error("Could not convert string to int %s"%rawNbr)
            rawNbr=1
            setText(self.chooseRawNbr,"1")
        self.graph.raw_data_nbr=rawNbr
        self.settings.saveSetting("raw_data_nbr", self.graph.raw_data_nbr)

        self.graph.hist_ch_mode=str(getValueSelect(self.chooseHist))
    	self.settings.saveSetting("hist_ch_mode", self.graph.hist_ch_mode)

    	self.graph.time_ch_mode1=str(getValueSelect(self.chooseTime1))
    	self.settings.saveSetting("time_ch_mode1", self.graph.time_ch_mode1)

    	self.graph.time_ch_mode2=str(getValueSelect(self.chooseTime2))
    	if self.graph.time_ch_mode2==self.graph.time_ch_mode1:
    		# prevent double work
    		self.graph.time_ch_mode2=="None"
    		setSelect(self.chooseTime2, self.graph.time_ch_mode2)
    	self.settings.saveSetting("time_ch_mode2", self.graph.time_ch_mode2)

    	# dont care about double work for strings
    	self.graph.str_ch_mode1=str(getValueSelect(self.chooseStr1))
    	self.settings.saveSetting("str_ch_mode1", self.graph.str_ch_mode1)

    	self.graph.str_ch_mode2=str(getValueSelect(self.chooseStr2))
    	self.settings.saveSetting("str_ch_mode2", self.graph.str_ch_mode2)

    	self.graph.str_ch_mode3=str(getValueSelect(self.chooseStr3))
    	self.settings.saveSetting("str_ch_mode3", self.graph.str_ch_mode3)

    	self.graph.str_ch_mode4=str(getValueSelect(self.chooseStr4))
    	self.settings.saveSetting("str_ch_mode4", self.graph.str_ch_mode4)

    	self.graph.str_ch_mode5=str(getValueSelect(self.chooseStr5))
    	self.settings.saveSetting("str_ch_mode5", self.graph.str_ch_mode5)

# ********************************************************************************
    # Update widget functions


    def updateDisplayWidget(self):
    	clearSelect(self.chooseRaw)
    	options=self.getRawOptions()
    	recreateSelect(options, self.chooseRaw, self.graph.raw_data_ch)

    	# TODO Nbr of waveforms

    	clearSelect(self.chooseHist)
    	options=self.getHistOptions()
    	recreateSelect(options, self.chooseHist, self.graph.hist_ch_mode)

    	# TODO Rest

	def getRawOptions(self):
        options=["None"]
        for i in range(self.daq.scope.NUM_CHANNELS):
        	channel=list(self.daq.scope.CHANNELS)[i][0]
        	if self.daq.save_wfm[channel]:
            	options.append(channel+": waveform")
            if self.daq.save_fft[channel]:
            	options.append(channel+": FFT")
        return options

	def getHistOptions(self):

        options=["None"]
        for i in range(self.daq.scope.NUM_CHANNELS):
        	channel=list(self.daq.scope.CHANNELS)[i][0]
        	if save_max_amp[channel]:
            	options.append(channel+": Max Amplitude")
            if save_min_amp[channel]:
            	options.append(channel+": Min Amplitude")
            if save_area[channel]:
            	options.append(channel+": Area")
            if save_avg_std[channel]:
            	options.append(channel+": Average")
            if save_avg_std[channel]:
            	options.append(channel+": Std. Deviation")
        return options

    def getTimeOptions(self):
        options=["None"]
        for i in range(self.daq.scope.NUM_CHANNELS):
        	channel=list(self.daq.scope.CHANNELS)[i][0]
        	options.append("Triggerrate")
            if save_avg_std[channel]:
            	options.append(channel+": Average")
            if save_avg_std[channel]:
            	options.append(channel+": Std. Deviation")
        # TODO external DEVICES
        return options

    def getStrOptions(self):
        options=["None"]
        for i in range(self.daq.scope.NUM_CHANNELS):
        	channel=list(self.daq.scope.CHANNELS)[i][0]
        	options.append("Latest Triggerrate")
            if save_avg_std[channel]:
            	options.append(channel+": Latest Average")
            if save_avg_std[channel]:
            	options.append(channel+": Latest Std. Dev.")
        # TODO external DEVICES
        return options