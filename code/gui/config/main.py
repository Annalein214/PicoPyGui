from PyQt5 import QtWidgets, QtCore, QtGui
MyGui=QtWidgets

from code.gui.config.channel import channelConfigWidget
from code.gui.config.scope import scopeConfigWidget

##########################################################################################


class configWidget(MyGui.QWidget):
    '''
    The layout of the config widget
    '''
    def __init__(self, parent, log, daq, settings):
        super(configWidget, self).__init__(parent)
        self.daq=daq

        # copy geometry information from parent:
        self.left_minimum_size=parent.left_minimum_size
        self.right_width=parent.right_width
        self.right_tab_width=parent.right_tab_width
        self.right_tab_minimum_height=parent.right_tab_minimum_height
        self.window_position=parent.window_position
        self.window_size=parent.window_size

        config = MyGui.QTabWidget(self)
        config.setMinimumHeight(self.right_tab_minimum_height)
        config.setMinimumWidth(self.right_tab_width)
        config.setMaximumWidth(self.right_tab_width+25)

        for i in range(self.daq.scope.NUM_CHANNELS):
            tab	= channelConfigWidget(self, log, list(self.daq.scope.CHANNELS)[i][0], daq, settings, #trigger
                                        )
            config.addTab(tab,list(self.daq.scope.CHANNELS)[i][0])
        
        scope	= scopeConfigWidget(self, log, daq, settings)
        #tab6	= siggenConfigWidget(self, log, daq, settings)
        #tab7	= measurementConfigWidget(self, log, daq, settings)
        display	=displayConfigWidget(self, log, daq, settings)
        #tab8	= settingsConfigWidget(self, log, daq, settings)
        
        config.addTab(scope,"Scope")
        #config.addTab(tab6,"Sig.Gen.")
        #config.addTab(tab7,"Meas.")
        config.addTab(display,"Display")
        #config.addTab(tab8,"Sett.")
        #config.mainwindow = parent.parentWidget()

#########################################################################################

class siggenConfigWidget(MyGui.QWidget):
    '''
    signal generator tab widget
    '''
    def __init__(self, parent, log, daq, settings):
        super(siggenConfigWidget, self).__init__(parent)
        self.log=log
        self.daq=daq
        self.settings=settings

        layout=MyGui.QGridLayout()
        '''
        self.sigoffsetVoltage=0
        self.pkToPk=2 # microvolts
        self.waveType="Square"
        self.sigfrequency=1E3
        '''

        labelOffset = MyGui.QLabel()
        labelOffset.setText("Offset in mV")
        self.chooseOffset = MyGui.QLineEdit()
        self.chooseOffset.setText("0")
        self.chooseOffset.textChanged.connect(self.enable)
        # TODO read setDefault value and set it here

        labelP2P = MyGui.QLabel()
        labelP2P.setText("Peak 2 Peak in mV")
        self.chooseP2P = MyGui.QLineEdit()
        self.chooseP2P.setText("0")
        self.chooseP2P.textChanged.connect(self.enable)
        # TODO read setDefault value and set it here

        labelFreq = MyGui.QLabel()
        labelFreq.setText("Frequency in Hz")
        self.chooseFreq = MyGui.QLineEdit()
        self.chooseFreq.setText("0")
        #self.chooseFreq.setValidator(MyGui.QFloatValidator(0,20000000, 3))
        self.chooseFreq.textChanged.connect(self.enable)
        # TODO read setDefault value and set it here

        labelType = MyGui.QLabel()
        labelType.setText("Channel")
        self.chooseType = MyGui.QComboBox(self)
        for entry in list(self.daq.ps.WAVE_TYPES):
            self.chooseType.addItem(entry)
        self.chooseType.currentIndexChanged.connect(self.enable)
        
        self.sigGenEnabled=MyGui.QCheckBox("Enable signal generator")
        self.sigGenEnabled.setChecked(False)
        self.sigGenEnabled.stateChanged.connect(self.enable)
        # TODO read setDefault value and set it here

        c=0
        layout.addWidget(labelOffset,          c,0) # y, x
        layout.addWidget(self.chooseOffset,    c,1) # y, x
        c+=1
        layout.addWidget(labelP2P,              c,0) # y, x
        layout.addWidget(self.chooseP2P,        c,1) # y, x
        c+=1
        layout.addWidget(labelFreq,             c,0) # y, x
        layout.addWidget(self.chooseFreq,       c,1) # y, x
        c+=1
        layout.addWidget(labelType,            c,0) # y, x
        layout.addWidget(self.chooseType,      c,1) # y, x
        c+=1
        layout.addWidget(self.sigGenEnabled,        c,0) # y, x

        self.setLayout(layout)


    def enable(self):
        '''
        read all chosen settings
        '''

        offset = str(self.chooseOffset.text())
        if offset=="-":# no wired effect when starting to type a negative number
            offset=0
        try:
            self.daq.sigoffsetVoltage=float(offset)/1000 # mV-> V
        except ValueError as e:
            #self.log.error("Could not convert string to float %s"%offset)
            self.daq.sigoffsetVoltage=0
            self.chooseOffset.setText("0")
            
        p2p = str(self.chooseP2P.text())
        if p2p=="-":# no wired effect when starting to type a negative number
            p2p=0
        try:
            self.daq.pkToPk=float(p2p)/1000 # mV-> V
        except ValueError as e:
            #self.log.error("Could not convert string to float %s"%p2p)
            self.daq.pkToPk=0
            self.chooseP2P.setText("0")
        
        freq = str(self.chooseFreq.text())
        try:
            self.daq.sigfrequency=float(freq)
        except ValueError as e:
            #self.log.error("Could not convert string to float %s"%freq)
            self.daq.sigfrequency=0
            self.chooseFreq.setText("0")

        self.daq.waveType = str(self.chooseType.currentText())
                
        try:
            if self.sigGenEnabled.isChecked():
                self.log.info("Enable Signal Generator")
                self.daq.setSignalGenerator(disable=False)
                self.daq.sigGenEnabled=True
            elif not self.sigGenEnabled.isChecked() and self.daq.sigGenEnabled:
                self.log.info("Disable Signal Generator")
                self.daq.setSignalGenerator(disable=True)
                self.daq.sigGenEnabled=False
        except Exception as e:
            print(e)
            
        self.settings.saveSettings()
		
##########################################################################################

      
        
##########################################################################################

        
class displayConfigWidget(MyGui.QWidget):
    '''
    The master of the channel config widgets
    '''
    def __init__(self, parent, log, daq, settings):
        super(displayConfigWidget, self).__init__(parent)
        self.log=log
        self.daq=daq
        self.settings=settings
        
        wrapperLayout = MyGui.QVBoxLayout(self)
        grid=MyGui.QGridLayout()
        
        '''
        default=self.daq.showArea
        self.showArea=MyGui.QCheckBox("Show Charge")
        self.showArea.setChecked(default)
        self.showArea.stateChanged.connect(self.enable)

        labelTime = MyGui.QLabel()
        labelTime.setText("Measurement time [min]")
        self.chooseTime = MyGui.QLineEdit()
        self.chooseTime.setText(str(float(self.daq.measurementduration))) # disabled
        self.chooseTime.textChanged.connect(self.enable)

        labelWaveforms = MyGui.QLabel()
        labelWaveforms.setText("Waveforms to show/save")
        self.chooseWaveforms = MyGui.QLineEdit()
        if qt==4:
        	self.chooseWaveforms.setValidator(MyGui.QIntValidator(0,1000)) # min max stellenzahl nach komma
        else:
        	self.chooseWaveforms.setValidator(QtGui.QIntValidator(0,1000)) # min max stellenzahl nach komma
        self.chooseWaveforms.setText(str(int(self.daq.nowaveforms)))
        self.chooseWaveforms.textChanged.connect(self.enable)
        
        labelXTicks = MyGui.QLabel()
        labelXTicks.setText("Xtick Nbr.")
        self.labelXTicks = MyGui.QLineEdit()
        if qt==4:
        	self.labelXTicks.setValidator(MyGui.QIntValidator(0,20)) # min max stellenzahl nach komma
        else:
        	self.labelXTicks.setValidator(QtGui.QIntValidator(0,20)) # min max stellenzahl nach komma
        self.labelXTicks.setText(str(int(self.daq.xticks))) # disabled
        self.labelXTicks.textChanged.connect(self.enable)
        
        

        c=0
        c+=1
        grid.addWidget(labelTime,             c,0) # y, x
        grid.addWidget(self.chooseTime,       c,1) # y, x
        c+=1
        grid.addWidget(labelWaveforms,        c,0) # y, x
        grid.addWidget(self.chooseWaveforms,  c,1) # y, x
        c+=1
        grid.addWidget(labelXTicks,        c,0) # y, x
        grid.addWidget(self.labelXTicks,  c,1) # y, x
        c+=1
        grid.addWidget(self.showArea,        c,0) # y, x
        c+=1
        '''
        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()


    def enable(self):
        '''
        read all chosen settings
        '''

        measurementduration = str(self.chooseTime.text())
        try:
            self.daq.measurementduration=float(measurementduration)
        except ValueError as e:
            #self.log.error("Could not convert string to float %s"%measurementduration)
            self.daq.measurementduration=0
            #self.chooseTime.setText("0")
            
        nowaveforms = str(self.chooseWaveforms.text())
        try:
            self.daq.nowaveforms=int(nowaveforms)
        except ValueError as e:
            #self.log.error("Could not convert string to int %s"% nowaveforms)
            self.daq.nowaveforms=0
        
        xticks=str(self.labelXTicks.text())
        try:
            self.daq.xticks=int(xticks)
        except ValueError as e:
            #self.log.error("Could not convert string to int %s"% xticks)
            self.daq.xticks=5
        
        
        self.daq.showArea=self.showArea.isChecked()  
        
         
                     
        self.settings.saveSettings()

##########################################################################################

class settingsConfigWidget(MyGui.QWidget):
    '''
    settings tab widget
    '''
    def __init__(self, parent, log, daq, settings):
        super(settingsConfigWidget, self).__init__(parent)
        self.log=log
        self.daq=daq
        self.settings=settings

        layout=MyGui.QGridLayout()

        #self.enabled=MyGui.QCheckBox("Enabled")
        #self.enabled.setChecked(False)
        #self.enabled.stateChanged.connect(self.enable)
        
        default=self.daq.led
        self.led=MyGui.QCheckBox("LED on")
        self.led.setChecked(default)
        self.led.stateChanged.connect(self.enable)
        
        labelSource = MyGui.QLabel()
        labelSource.setText("Source")
        self.chooseSource = MyGui.QComboBox(self)
        default=self.daq.source
        for entry in ["None", "Am241_stud","Am241_katrin", "Ba133","Sr90"]:
            self.chooseSource.addItem(entry)
        index = self.chooseSource.findText(default, QtCore.Qt.MatchFixedString)
        if index >= 0: self.chooseSource.setCurrentIndex(index)
        self.chooseSource.currentIndexChanged.connect(self.enable)
        
        labelPMT = MyGui.QLabel()
        labelPMT.setText("PMT")
        self.choosePMT = MyGui.QComboBox(self)
        default=str(self.daq.pmt)
        for entry in ["6","1","3"]:
            self.choosePMT.addItem(entry)
        index = self.choosePMT.findText(default, QtCore.Qt.MatchFixedString)
        if index >= 0: self.choosePMT.setCurrentIndex(index)
        self.choosePMT.currentIndexChanged.connect(self.enable)
        
        labelSzin = MyGui.QLabel()
        labelSzin.setText("Szintillator")
        self.chooseSzin = MyGui.QComboBox(self)
        default=self.daq.szint
        for entry in ["None","EJ212","EJ440","Uwe"]:
            self.chooseSzin.addItem(entry)
        index = self.chooseSzin.findText(default, QtCore.Qt.MatchFixedString)
        if index >= 0: self.chooseSzin.setCurrentIndex(index)
        self.chooseSzin.currentIndexChanged.connect(self.enable)
        
        labelWater = MyGui.QLabel()
        labelWater.setText("Water Quality")
        self.chooseWater = MyGui.QComboBox(self)
        default=self.daq.water
        for entry in ["None","Ultra-Purified", "De-Ionized", "Mineral", "Tab", "Contamined"]:
            self.chooseWater.addItem(entry)
        index = self.chooseWater.findText(default, QtCore.Qt.MatchFixedString)
        if index >= 0: self.chooseWater.setCurrentIndex(index)
        self.chooseWater.currentIndexChanged.connect(self.enable)
        
        default=self.daq.degased
        self.degased=MyGui.QCheckBox("Water is degased")
        self.degased.setChecked(default)
        self.degased.stateChanged.connect(self.enable)
        
        #labelDistance = MyGui.QLabel()
        #labelDistance.setText("Distance PMT to water / source")
        #self.chooseDistance = MyGui.QLineEdit()
        #self.chooseDistance.setText(str(self.daq.dist))
        #self.chooseDistance.textChanged.connect(self.enable)

        c=0
        layout.addWidget(labelSource,    c,0) # y, x
        layout.addWidget(self.chooseSource,    c,1) # y, x
        c+=1
        layout.addWidget(labelPMT,    c,0) # y, x
        layout.addWidget(self.choosePMT,    c,1) # y, x
        c+=1
        layout.addWidget(labelSzin,    c,0) # y, x
        layout.addWidget(self.chooseSzin,    c,1) # y, x
        c+=1
        layout.addWidget(labelWater,    c,0) # y, x
        layout.addWidget(self.chooseWater,    c,1) # y, x
        c+=1
        layout.addWidget(self.degased,    c,0) # y, x
        c+=1
        #layout.addWidget(labelDistance,    c,0) # y, x
        #layout.addWidget(self.chooseDistance,    c,1) # y, x
        #c+=1
        layout.addWidget(self.led,    c,0) # y, x
        
        c+=1
        wrapperLayout.addLayout(grid)
        wrapperLayout.addStretch()


    def enable(self):
        '''
        read all chosen settings
        '''
        self.daq.led=self.led.isChecked()   
        self.daq.source = str(self.chooseSource.currentText())
        self.daq.pmt = int(str(self.choosePMT.currentText()))
        self.daq.szint = str(self.chooseSzin.currentText())
        self.daq.water = str(self.chooseWater.currentText())
        #self.daq.dist = str(self.chooseDistance.text())
        self.daq.degased = self.degased.isChecked()
        
        self.settings.saveSettings()

##########################################################################################
