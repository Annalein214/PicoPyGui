from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from code.log import log
from code.helpers import timestring_humanReadable
import time, os

# import hardware scripts # HWT
from code.sensors.dummy import Sensor
from code.sensors.hv.Caen import HV
from code.sensors.environmental_sensors.environmental_sensors import EnvSensors


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

        # check which devices should be used and don't allow switch on/off during measurement:
        useDummy=False
        useLightsensor=False
        useTempHum = False
        useTempSensors=False
        useHumidity=False
        useHV = False
        if self.dummy != None and self.settings.useDummy != False:
            useDummy=True
        if self.lightsensor!=None and self.settings.useLightsensor != False:
            useLightsensor=True
        if self.humidity!=None and self.settings.useHumidity != False:
            useHumidity=True
        if self.humtemp!=None and self.settings.useTempHum!=False:
            useTempHum = True
        if self.temperaturearray!=None and self.settings.useTempArray!=False:
            useTempSensors=True
        if self.hv!=None and self.settings.useHV != False:
            useHV=True
        


        while not self._threadIsStopped:
            self.startBlock=time.time()

            
            # -- HWT: get HW output here
            # use try to keep the thread running in case of a readout error
            if useDummy: 
                # cannot use "useDummy" here because that might be changed during run by the user in display tab and this contaminates data integrity
                val=self.dummy.readDevice()
                self.dummyVals.append(val)
            if useLightsensor: #
                try:
                    val=self.lightsensor.readDiode()
                    self.lightVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in Lightsensor reading: %s"%(str(e)))
                    self.lightVals.append(-1)
            if useTempHum or useHumidity: #
                try:
                    val=self.humtemp.readHumidity()
                    if useTempHum:
                        self.humTempVals.append(val[1])
                    if useHumidity:
                        self.humVals.append(val[0])
                except Exception as e:
                    self.log.error("ERROR in Humidity sensor reading: %s"%(str(e)))
                    self.humTempVals.append(-111)
                    self.humVals.append(-1)
            if useTempSensors: #
                try:
                    val=self.temperaturearray.readTemperature()
                    self.tempVals.append(val)
                except Exception as e:
                    self.log.error("ERROR in Temperature reading: %s"%(str(e)))
                    self.tempVals.append((-999, -999, -999, -999))
            if useHV:
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
        self.humTempVals =[]
        self.humVals = []
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

        if self.dummy!=None and self.settings.useDummy!=False: # added useDummy, because dummy is otherwise always on!
            self.save("HW_Dummy", self.dummyVals)
        if self.lightsensor!=None and self.settings.useLightsensor != False:
            self.save("HW_Lightsensor", self.lightVals)
        if self.humtemp!=None and self.settings.useTempHum!=False:
            self.save("HW_HumTemp", self.humTempVals)
        if self.hv!=None and self.settings.useHV != False:
            self.save("HW_HV", self.hvVals)
        if self.humidity!=None and self.settings.useHumidity!=False:
            self.save("HW_Humidity", self.humVals)
        if self.temperaturearray!=None and self.settings.useTempArray!=False:
            self.save("HW_Temperature", self.tempVals)
        # Update settings
        self.rounds+=1
        self.lastSaved = self.endtime
        self.saveMeasurement=True
        self.prepareAnalysis() # reset all variables

    def save(self, name, values):
        try:
           filename=self.directory+"/"+name+"_"+str(self.rounds)+".npy"
           np.save(filename, values)
           self.out.info("Save %s to file %s"%(name, filename))
        except Exception as e:
           self.log.error("Saving %s did not work, finished with error %s" %(name, str(e)))
   
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
            self.dummy = Sensor(self.log) # this should always work, so this data is always taken
        except:
            self.log.error("Cannot load hardware Dummy. Switch off.")
            self.settings.useDummy=False
            self.dummy=None


        try:
            self.lightsensor = EnvSensors(self.log)
            self.humtemp = self.lightsensor
            self.humidity = self.lightsensor
            self.temperaturearray = self.lightsensor
            if self.lightsensor.online==False:
                self.settings.useLightsensor=False
                self.settings.useTempHum = False
                self.settings.useHumidity = False
                self.settings.useTempArray = False
                self.lightsensor=None
                self.temphum=None
                self.humidity=None
                self.temperaturearray=None

                self.log.error("Photodiode and Temperatures and Humidity not online. Switch off.")
        except:
            self.log.error("Cannot load hardware Photodiode, Humidity, Temperatures. Switch off.")
            self.settings.useLightsensor=False
            self.settings.useTempHum = False
            self.settings.useHumidity = False
            self.settings.useTempArray = False
            self.lightsensor=None
            self.temphum=None
            self.humidity=None
            self.temperaturearray=None
            self.humtemp=None

        try:
            self.hv = HV(self.log)
            if self.hv.online==False:
                self.settings.useHV=False
                self.hv=None
        except:
            self.log.error("Cannot load hardware HV. Switch off.")
            self.settings.useHV=False
            self.hv=None
        

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
        self.temphum=None
        self.humidity=None
        self.temperaturearray=None
        
    def close(self):
        self.dummy.close()
        self.dummy=None

        if not self.opts.test:
            # HWT close your stuff here
            if self.lightsensor!=None or self.temphum != None or \
                self.humidity != None or self.temperaturearray != None:
                try: self.lightsensor.close()
                except: pass
                try: self.humtemp.close()
                except: pass
                try: self.humidity.close()
                except: pass
                try: self.temperaturearray.close()
                except: pass
                self.lightsensor=None
                self.temphum=None
                self.humidity=None
                self.temperaturearray=None
            if self.hv!=None:
                self.hv.close()
                self.hv=None

        self.log.info("Hardware closed. Good night!")




