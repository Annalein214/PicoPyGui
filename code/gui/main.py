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
    def __init__(self, parent, log, daq, settings):
        super(CentralWidget, self).__init__(parent)
        self.daq=daq
        self.log=log
        self.settings=settings

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
        self.timer.start(1000)
        # after the thread of the daq is finished, the measurement should be stopped!
        self.daq.finished.connect(self.stopMeasurement) 

    def leftSide(self):
        # left side will comprise the plot
        box = MyGui.QGroupBox(self)
        box.setMinimumSize(self.left_minimum_size[0],self.left_minimum_size[1])
        # white background is nicer for the plot
        box.setStyleSheet("background-color: rgb(255, 255, 255)")
        
        # add the plot widget
        layout=MyGui.QVBoxLayout()
        plot=plotWidget(self,self.log, self.daq)
        layout.addWidget(plot)
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
        config=configWidget(self, self.log, self.daq, self.settings)

        # BOTTOM -------------------
        self.saveLog = MyGui.QLineEdit()
        self.saveLog.setPlaceholderText("Enter log message and press ENTER")
        self.saveLog.returnPressed.connect(self.saveLogger)

        self.progress = MyGui.QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)

        self.button = MyGui.QPushButton('Start', self)
        self.button.clicked.connect(self.startMeasurement)

        # put together the right part
        layout.addWidget(config)
        layout.addWidget(self.saveLog)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)
        box.setLayout(layout)
        return box







    def saveLogger(self):
        if self.daq.out!=None:
            log=self.daq.out
        else:
            log=self.log
        try:
            log.msg("LMSG:"+str(self.saveLog.text())) # used a string here which is easily searchable
        except:
            self.log.msg("LMSG:"+str(self.saveLog.text())) # used a string here which is easily searchable
        self.saveLog.setText("")
        #self.saveLog.setPlaceholderText("Text is saved!")
        #time.sleep(0.5)
        self.saveLog.setPlaceholderText("Log Message: Press enter to save")


    def update_progressbar(self):
        pass
        ''' TODO
        if self.daq.isRunning():
            self.progress.setValue(int(self.daq.progress))#argument is changed to be int by Megumi.C
        else:
            self.progress.setValue(0)
        '''

    def startMeasurement(self):
        if self.button.text()=="Start":
            if not self.daq.isRunning():
                    self.button.setText('Stop')
                    self.daq._threadIsStopped=False
                    self.daq.start()
                    self.log.debug("Measurement started.")
            else:
                self.log.error("Measurement is  running -> you cannot start it.")
        else:
            self.stopMeasurement()

    def stopMeasurement(self):
        # this is executed twice when stopping a run somehow
        # but appart from the log print, the rest is not executed twice

        self.log.debug("Stopping measurement...")

        if self.daq.isRunning():
            '''
             measurement is running -> Stop it
            '''
            self.daq._threadIsStopped=True # this stops the next loop
            while self.daq.isRunning():
                time.sleep(0.1)
            self.log.debug("Measurement stopped.")
            '''
            if self.daq.saveMeasurement:
                self.daq.saveAll()
                #self.daq.writeToDatenbank()
                self.daq.saveMeasurement=False
                self.out=None
            else:
                #self.askToSave()
                text, ok = MyGui.QInputDialog.getText(self, 'Do you want to save?', 
                                            'Do you want to save this measurement?\n'+
                                            'You can enter a last Logbook message here:')
                if ok:
                    self.daq.out.msg("LMSG:"+str(text))
                    self.daq.saveAll()
                    #self.daq.writeToDatenbank()
                    self.daq.saveMeasurement=False
                    self.daq.out=None
                else:
                    self.daq.deleteDir()
                    self.log.info("Measurement not saved.")
            '''
        if self.button.text()=="Stop":
            self.button.setText('Start')
            self.log.debug("Stop Measurement: Measurement button set to start.")
            
        
    '''
    def askToSave(self):
       print("Ask")
       msg = MyGui.QMessageBox()
       msg.setIcon(MyGui.QMessageBox.Information)

       msg.setText("Do you want to save this measurement?")
       #msg.setInformativeText("Do you want to save this measurement?")
       msg.setWindowTitle("Save?")
       #msg.setDetailedText("blub")
       msg.setStandardButtons(MyGui.QMessageBox.Ok | MyGui.QMessageBox.Cancel)
       msg.buttonClicked.connect(self.answerSave)
       retval = msg.exec_()
       print("value of pressed message box button:", retval)

    def answerSave(self,i):
       self.log.debug("Button pressed is:%s"%i.text() )
       if i.text()=="OK":
            self.daq.saveAll()
            # reset
            self.daq.saveMeasurement=False
    '''
