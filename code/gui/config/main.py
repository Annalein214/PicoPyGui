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
        display	=displayConfigWidget(self, log, daq, settings)
        
        config.addTab(scope,"Scope")
        config.addTab(display,"Display")
        
        config.mainwindow = parent.parentWidget()

#########################################################################################

'''
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
'''		