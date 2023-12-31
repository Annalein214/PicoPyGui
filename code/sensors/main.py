from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from code.log import log
from code.helpers import timestring_humanReadable
import time, os

# import hardware scripts
from code.sensors.dummy import Sensor
from code.sensors.lightsensor.photodiode import Photodiode
from code.sensors.hv.Caen import HV
from code.sensors.temperature.temperaturesensors import TempSensors

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

        self.rounds=0 # how many times does the measurement saveAll and restart before stopped

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

        self.out.debug("HW measurement started "+str(self._threadIsStopped))
        
        while not self._threadIsStopped:
            self.startBlock=time.time()

            
            # -- HWT: get HW output here
            # use try to keep the thread running in case of a readout error
            if self.dummy!=None: # cannot use "useDummy" here because that might be changed during run by the user in display tab
                val=self.dummy.readDevice()
                self.dummyVals.append(val)
            if self.lightsensor!=None: #
                try:
                    val=self.lightsensor.readDevice()
                    self.lightVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in Lightsensor reading: %s"%(str(e)))
                    self.lightVals.append(-1)
            if self.roomtemp!=None: #
                try:
                    val=self.roomtemp.readTemperature()
                    self.roomVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in Roomtemp sensor reading: %s"%(str(e)))
                    self.roomVals.append(-1)
            if self.temperaturesensors!=None: #
                try:
                    val=self.temperaturesensors.readDevice()
                    self.tempVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in Temperature reading: %s"%(str(e)))
                    self.tempVals.append((-999, -999, -999, -999))
            if self.hv!=None:
                try:               
                    val=self.hv.readDevice()
                    self.hvVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in HV reading: %s"%(str(e)))
                    self.hvVals.append((-1,-1,-1))
            # ---
            self.endtime=time.time()
            self.analysis()
            
            time.sleep(self.settings.HWSleepTime)

        self.out.debug("HW measurement stopped")


    # ****** Analysis **********************************************************

    def prepareAnalysis(self):
        '''
        produce all variables, could be more efficient if you would restrict to actually used variables
        but I don't think this really matters

        initialize variables here, which need to be reset every hour after saving!
        HWT
        '''
        self.dummyVals = []
        self.lightVals = []
        self.roomVals =[]
        self.hvVals = []
        self.tempVals = []
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

        self.save("TimeHW", self.time)

        '''
        HWT save all values here
        '''

        if self.dummy!=None:
            self.save("HW_Dummy", self.dummyVals)
        if self.lightsensor!=None:
            self.save("HW_Lightsensor", self.lightVals)
        if self.roomtemp!=None:
            self.save("HW_Roomtemp", self.roomVals)
        if self.hv!=None:
            self.save("HW_HV", self.hvVals)
        if self.temperaturesensors!=None:
            self.save("HW_Temperature", self.tempVals)
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
        # always initialize here even if user switches off later

        try:
            self.dummy = Sensor(self.log)
        except:
            self.log.error("Cannot load hardware Dummy. Switch off.")
            self.settings.useDummy=False
            self.dummy=None


        try:
            self.lightsensor = Photodiode(self.log)
            self.roomtemp = self.lightsensor
            if self.lightsensor.online==False:
                self.settings.useLightsensor=False
                self.settings.useRoomtemp = False
                self.lightsensor=None
                self.roomtemp=None
                self.log.error("Photodiode and Roomtemperature not online. Switch off.")
        except:
            self.log.error("Cannot load hardware Photodiode and Roomtemperature. Switch off.")
            self.settings.useLightsensor=False
            self.lightsensor=None
            self.settings.useRoomtemp = False
            self.roomtemp=None

        try:
            self.hv = HV(self.log)
            if self.hv.online==False:
                self.settings.useHV=False
                self.hv=None
        except:
            self.log.error("Cannot load hardware Photodiode. Switch off.")
            self.settings.useHV=False
            self.hv=None

        try:
            self.temperaturesensors = TempSensors(self.log)
            if self.temperaturesensors.online==False:
                self.settings.useTemp=False
                self.temperaturesensors=None
                self.log.error("Temperature sensor offline. Switch off.")
        except:
            self.log.error("Cannot load hardware Temperature. Switch off.")
            self.settings.useTemp=False
            self.temperaturesensors=None
        

    def setDefault(self):
        # --- thread variables -----
        self.out=None # log object, needs to be initialized for saveLogger 
        self._progress=0 # progress of thread
        self._threadIsStopped=True # use this to stop the thread (effect is not directly!)
        # --- run -----
        self.startthread=0 # time when thread started
        # HWT initialize variable which points to the device
        self.dummy=None
        self.lightsensor=None
        self.hv=None
        self.temperaturesensors=None
        self.roomtemp=None
        
    def close(self):
        self.dummy.close()
        self.dummy=None

        if not self.opts.test:
            # HWT close your stuff here
            if self.lightsensor!=None or self.roomtemp != None:
                try: self.lightsensor.close()
                except: pass
                try: self.roomtemp.close()
                except: pass
                self.lightsensor=None
                self.roomtemp=None
            if self.hv!=None:
                self.hv.close()
                self.hv=None
            if self.temperaturesensors!=None:
                self.temperaturesensors.close()
                self.temperaturesensors=None

        self.log.info("Hardware closed. Good night!")




