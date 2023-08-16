from PyQt5 import QtWidgets, QtCore
MyGui=QtWidgets

from code.gui.graph import plotWidget
from code.gui.config.main import configWidget

import time

class CentralWidget(MyGui.QWidget):
    '''
    The inner layout of the application window
    initializes all sub-widgets and gives settings to those
    '''
    def __init__(self, parent, log, daq, settings, graph, hw):
        super(CentralWidget, self).__init__(parent)
        self.daq=daq
        self.log=log
        self.settings=settings
        self.graph=graph
        self.hw=hw
        self.parent=parent

        # copy geometry information from parent:
        self.left_minimum_size=parent.left_minimum_size
        self.right_width=parent.right_width
        self.right_tab_width=parent.right_tab_width
        self.right_tab_minimum_height=parent.right_tab_minimum_height
        self.window_position=parent.window_position
        self.window_size=parent.window_size

        # main layout which will devided horizontally (=> 2 spaces next to each other horizontally)
        layout=MyGui.QHBoxLayout()

        # make the basic layout of the left and right sides
        left=self.leftSide()
        right=self.rightSide()

        # put together the central widget
        layout.addWidget(left)
        layout.addWidget(right)
        self.setLayout(layout)

        # connect threads
        self.setConnections()

    def setConnections(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_progressbar)
        self.timer.start(1000) # milliseconds?
        # after the thread of the daq is finished, the measurement should be stopped!
        self.daq.finished.connect(self.stopMeasurement) 
        # scope tells the graph to update
        self.daq.data_updated.connect(self.plot.update_figure)

    def leftSide(self):
        # left side will comprise the plot
        box = MyGui.QGroupBox(self)
        box.setMinimumSize(self.left_minimum_size[0],self.left_minimum_size[1])
        # white background is nicer for the plot
        box.setStyleSheet("background-color: rgb(255, 255, 255)")
        
        # add the plot widget
        layout=MyGui.QVBoxLayout()
        self.plot=plotWidget(self,self.log, self.daq, self.graph, self.hw)
        layout.addWidget(self.plot)
        box.setLayout(layout)
        return box

    def rightSide(self):
        # right side will comprise the config and buttons to start/stop the measurement
        box = MyGui.QGroupBox(self)
        box.setMinimumWidth(self.right_width)
        box.setMaximumWidth(self.right_width+50)

        # right side is devided into the upper part (config) and bottom part (start/stop button)
        layout=MyGui.QVBoxLayout()

        # TOP -------------------
        # the config widget is complicated therefore in another class
        config=configWidget(self, self.log, self.daq, self.settings, self.graph, self.hw)

        # BOTTOM -------------------

        label=MyGui.QLabel()
        label.setText("Logbook")
        self.saveLog = MyGui.QLineEdit()
        self.logPlaceholder="Enter log message and press ENTER"
        self.saveLog.setPlaceholderText(self.logPlaceholder)
        self.saveLog.returnPressed.connect(self.saveLogger)

        label2=MyGui.QLabel()
        label2.setText("Progress")
        self.progress = MyGui.QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)

        self.button = MyGui.QPushButton('Start', self)
        self.button.clicked.connect(self.startMeasurement)

        # put together the right part
        layout.addWidget(config)
        layout.addWidget(label)
        layout.addWidget(self.saveLog)
        layout.addWidget(label2)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)
        box.setLayout(layout)
        return box

    def saveLogger(self):
        # if measurement is running, save to measurement log
        if self.daq.out!=None:
            log=self.daq.out
        else: # otherwise save to general log
            log=self.log
        log.msg("LMSG: "+str(self.saveLog.text())) # used a string here which is easily searchable
        # reset
        self.saveLog.setText("")
        self.saveLog.setPlaceholderText(self.logPlaceholder)


    def update_progressbar(self):
        pass
        if self.daq.isRunning():
            self.progress.setValue(int(self.daq._progress))#argument is changed to be int by Megumi.C
        else:
            self.progress.setValue(0)

    def startMeasurement(self):
        if self.button.text()=="Start":            
            # link hw to daq here, cannot be done at initalization due to an egg and henn issue
            self.daq.hw=self.hw
            if not self.daq.isRunning():
                    self.button.setText('Stop')
                    self.daq._threadIsStopped=False
                    if not self.hw.isRunning():
                        self.hw._threadIsStopped=False
                        self.daq.prepareAdministration() 
                        self.hw.prepareAdministration()
                        self.daq.start()
                        self.hw.start()
                        self.log.debug("Measurement started.")
                        self.parent.statusBar().showMessage("Measurement running")

                    else: 
                        self.log.error("HW Measurement is running -> you cannot start it")
            else:
                self.log.error("Measurement is  running -> you cannot start it.")
        else:
            self.stopMeasurement()

    def stopMeasurement(self):
        # this is executed twice when stopping a run somehow
        # but appart from the log print, the rest is not executed twice

        self.log.debug("Stopping measurement. Please wait...")
        self.daq.out.debug("Stopping measurement with STOP button.")
        self.hw.out.debug("Stopping HW measurement with STOP button.")
        self.parent.statusBar().showMessage("Stopping measurement. Please wait...")

        if self.daq.isRunning():

            # -- measurement is running -> Stop it
            self.daq._threadIsStopped=True # this stops the next loop
            # wait until daq is finally stopped
            while self.daq.isRunning():
                time.sleep(0.1)
            self.log.debug("Measurement stopped.")
            
            # --- check if it should be saved
            if not self.daq.saveMeasurement:
                text, ok = MyGui.QInputDialog.getText(self, 'Do you want to save?', 
                                            'Do you want to save this measurement?\n'+
                                            'You can enter a last Logbook message here:')
                if ok: 
                    self.daq.saveMeasurement=True
                    self.hw.saveMeasurement=True
                    self.daq.out.msg("LMSG:"+str(text))
                    self.hw.out.msg("LMSG:"+str(text))

            # --- stop HW
            if self.hw.isRunning():
                self.hw._threadIsStopped=True
                while self.daq.isRunning():
                    time.sleep(0.1)
            self.log.debug("HW Measurement stopped.")

            # --- save or not
            if self.daq.saveMeasurement==True:
                self.daq.hourlyPlot.plotAll()
                self.daq.saveAll()
                self.hw.saveAll()
                self.daq.copyLogfile()
            else:
                self.hw.deleteFile()
                self.daq.deleteDir()
                self.log.info("Measurement not saved.")

        if self.hw.isRunning():
            # this happens if the elapsed time has passed in daq
            self.hw._threadIsStopped=True  # this stops the next loop
 
            # wait until daq is finally stopped
            while self.hw.isRunning():
                time.sleep(0.1)
            self.log.debug("HW Measurement stopped.")
            if self.daq.saveMeasurement==True:
                self.hw.saveAll()
            else:
                self.hw.deleteFile()
                self.log.info("HW Measurement not saved.")

        # reset start button
        if self.button.text()=="Stop":
            self.button.setText('Start')
            self.log.debug("Stop Measurement: Measurement button set to start.")
            self.parent.statusBar().showMessage("")

