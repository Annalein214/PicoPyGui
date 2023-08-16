from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from code.log import log
from code.helpers import timestring_humanReadable
import time, os

# import hardware scripts
from code.sensors.dummy import Sensor

class external(QThread):

    data_updated = pyqtSignal() # signals and slots need to be in class declaration and not constructor!

    # ****** Prepare run **********************************************************

    def prepareAdministration(self):
        '''
        copy settings from daq
        start your own log file!
        '''
        self.startthread=self.daq.startthread
        st=str(timestring_humanReadable(self.startthread))
        self.directory=self.daq.directory

        # make a new log file and save all info of this run in there
        self.out=log(save=True, level="debug", directory=self.directory, end="hw.out")
        self.out.info("Starttime: %s %s"%(self.startthread, st))
        self.out.info("Main log file: %s"%self.log.filename) # save info about main logfile name

        self.log.info("Measurement log file in %s" % (self.out.filename))

        self.saveMeasurement=self.settings.saveMeasurement # reset to false so that the user can decide 

        # needed for the first round
        self.endtime = time.time() # need this value for the first loop
        self.lastSaved = self.endtime # keep track of saving the data every hour, here this is just for the first round

    def setupHardware(self):
        '''
        HWT: in here comes everything that has to be done once before run, 
        i.e. cannot be done repeatedly but cannot only be done in __init__
        '''
        pass

    # ****** Run **********************************************************

    def run(self):

        self.setupHardware()
        self.prepareAnalysis()

        self.out.debug("HW measurement started"+str(self._threadIsStopped))
        
        while not self._threadIsStopped:
            self.startBlock=time.time()

            # -- HWT: get HW output here
            if self.dummy!=None: # cannot use "useDummy" here because that might be changed during run by the user in display tab
                val=self.dummy.readDevice()
                self.dummyVals.append(val)

            # ---
            self.endtime=time.time()
            self.analysis()
            
            time.sleep(self.settings.HWSleepTime)
            

            # save after one our
            if self.endtime - self.lastSaved > (60*60):
                self.out.info("Reset HW run after %d seconds"%(self.endtime - self.lastSaved)) 
                self.saveAll()

        self.out.debug("HW measurement stopped")
        self.saveAll()


    # ****** Analysis **********************************************************

    def prepareAnalysis(self):
        '''
        produce all variables, could be more efficient if you would restrict to actually used variables
        but I don't think this really matters

        initialize variables here, which need to be reset every hour after saving!
        HWT
        '''
        self.dummyVals = []
        self.time=[]

    def analysis(self):
        self.time.append(self.startBlock)
        # self.dummyVals #directly added data to array in block. Don't need to treat it here
        
        '''
        HWT: here you can treat your data every cycle
        '''

        self.data_updated.emit() # you could also send data here

    # ****** Save **********************************************************
    def saveAll(self):
        
        self.out.info("HW Save all in round %d"%(self.rounds))

        '''
        HWT save all values here
        '''

        if self.dummy!=None:
            self.save("Dummy", self.dummyVals)

        # Update settings
        self.rounds+=1
        self.lastSaved = self.endtime
        self.saveMeasurement=True
        self.prepareAnalysis() # reset all variables

    def save(self, name, values):
        filename=self.directory+"/"+name+"_"+str(self.rounds)+".npy"
        np.save(filename, values)
        self.out.info("Save %s to file %s"%(name, filename))

    def deleteFile(self):
        self.log.info("Deleting log file %s" % self.directory)
        try:
            if os.path.isfile(self.out.filename):
                os.remove(self.out.filename)
        except Exception as e:
            self.log.error("Deleting of directory %s didn't work with error %s" % (self.directory, str(e)))

    # ****** Class stuff **********************************************************

    def __init__(self, log, opts, settings, daq):
        QThread.__init__(self)

        self.log=log
        self.opts=opts
        self.settings=settings
        self.daq=daq

        self.setDefault()

        #--- HWT: initialise hardware here
        if self.settings.useDummy: 
            try:
                self.dummy = Sensor(self.log)
            except:
                self.log.error("Cannot load hardware Dummy. Switch off.")
                self.settings.useDummy=False
                self.dummy=None

        

    def setDefault(self):
        # --- thread variables -----
        self.out=None # log object, needs to be initialized for saveLogger 
        self._progress=0 # progress of thread
        self._threadIsStopped=True # use this to stop the thread (effect is not directly!)
        # --- run -----
        self.rounds=0 # how many times does the measurement saveAll and restart before stopped
        self.startthread=0 # time when thread started
        self.dummy=None
        
    def close(self):
        self.dummy.close()
        self.dummy=None

        if not self.opts.test:
            # HWT close your stuff here
            pass
        self.log.info("Hardware closed. Good night!")




