from PyQt5.QtCore import QThread, pyqtSignal

import time, os, sys, shutil
import numpy as np
from code.helpers import timestring_humanReadable
from code.picoscope.device import deviceShelf
from code.log import log
from code.hplot import plot

class daq(QThread):
    '''
    Master of this Thread: CentralWidget (in gui/main)
    I use instantiation of QThread instead of moveToThread
    because this was originally written for QT4. 
    This also means, that only the code in run() is in the new thread.
    All other functions are outside. 
    Also variables from the constructor are outside.
    Caviat: you have to make sure that the state of variables is safe between different threads
    '''

    data_updated = pyqtSignal() # signals and slots need to be in class declaration and not constructor!

 
    #def __del__(self):
    #    self.wait()


# ****** Measurement **********************************************************

    def prepareAdministration(self):
        '''
        prepare what you need for the measurement, apart from setting up the scope
        initialize variables, which will not be reset every hour
        '''
        self.startthread=time.time() # required for filenames and analysis
        st=str(timestring_humanReadable(self.startthread))
        # make a new directory to save all files of this run in there
        self.directory=self.opts.directory+"/"+str(st)+"/"
        os.makedirs(self.directory, exist_ok=True)

        # make a new log file and save all info of this run in there
        self.out=log(save=True, level="debug", directory=self.directory, end="out")
        self.out.info("Starttime: %s %s"%(self.startthread, st))
        self.out.info("Main log file: %s"%self.log.filename) # save info about main logfile name
        self.out.info("\tSleep Time %fs"% self.sleeptime)

        self.log.info("Measurement log file in %s" % (self.out.filename))

        self.saveMeasurement=False # reset to false so that the user can decide 

        # link to plot class for hourly plots (only possible here if you want to use same log file)
        self.hourlyPlot = plot(self.out, self, self.hw)

        # needed for the first round
        self.endtime = time.time() # need this value for the first loop
        self.lastSaved = self.endtime # keep track of saving the data every hour, here this is just for the first round

    def setupScope(self):
        '''
        set up all scope properties
        '''
        # at least one channel must be enabled, this is already ensured in GUI and by triggering
        
        # enable channels
        for i in range(self.scope.NUM_CHANNELS):
            channel=list(self.scope.CHANNELS)[i][0]
            self.setChannel(channel, self.channelEnabled[channel])

        # setup trigger
        ok=self.setTrigger()
        if not ok: return False

        # setup sampling frequency
        self.setSampling()
        # setup rapid block
        ok=self.setCaptures()
        if not ok: return False
        return True

    def showProgress(self):
        if self.measurementduration!=0:
            self._progress = float(self.endtime-self.startthread)/(self.measurementduration*60)*100
        else:
            # since the measurement is reset every hour use this value for the progress bar
            self._progress = float(self.endtime-self.startthread)/(60*60)*100
        sys.stdout.write("\r \t %.2f %%" % (self._progress) ); sys.stdout.flush()

    def run(self):
        self.log.info("DAQ runs. See output in separate ~.out file")
        #self.prepareAdministration() # don't execute here, but from GUI so that prepared values can be accessed before actual run starts
        ok=self.setupScope()
        if not ok: return # stop the run
        # prepare varibles needed for analysis, reset these every hour
        self.prepareAnalysis()     
        

        # --- start the loop ---
        # loop until chose time elapsed or STOP button is pressed
        while not self._threadIsStopped:

            self.showProgress()

            # ---- THE BLOCK -----
            # do not change anything in here 
            if not self.opts.test: # scope is connected
                startBlock=time.time_ns() # the last command before block starts!
                it=self.scope.runBlock(pretrig=self.nopretriggersamples)
                #print ("run")
                self.indisposedTimes.append(it)
                while(self.scope.isReady() == False):
                    '''
                    if self._threadIsStopped: break TODO check if this is ok to be done
                    '''
                    time.sleep(self.sleeptime) # on unix nanosecond resolution is possible: https://docs.python.org/3/library/time.html
                endBlock=time.time_ns()
            else: # no scope connected
                startBlock=time.time_ns()
                for i in range(2):
                    #print(".",)
                    time.sleep(1)
                endBlock=time.time_ns()
            self.endtime=endBlock/1e9
            self.measurementtime = endBlock-startBlock # ns
            #print("time",endBlock-startBlock)
            self.startblock=startBlock
            
            # ---- BLOCK END -----
            
            if not self.opts.test:
                data=self.scope.getDataVBulk()
            else:
                # make data: TODO mind OFFSET!
                data=[]
                for i in range(self.scope.NUM_CHANNELS):
                    channel=list(self.scope.CHANNELS)[i][0]
                    vRange=self.voltagerange[channel]*1000*0.5

                    waveforms=[]
                    for i in range(100):
                        A=np.random.randint(-vRange,vRange)
                        x=np.arange(0,self.nosamples,1)/self.nosamples*np.pi*np.random.randint(0,5)
                        x=x-np.pi/10*np.random.randint(0,10)
                        wfm=A*np.sin(x)+self.offset[channel]
                        waveforms.append(wfm/1000)
                    data.append(waveforms)


            # DO ANALYSIS
            # decided to keep it in the same thread, as there would be no improvement anyhow
            self.analysis(data)

            if self.endtime - self.lastSaved > (60*60):
                self.out.info("Reset run after %d seconds"%(self.endtime - self.lastSaved)) 
                #self.hourlyPlot.plotAll()
                self.saveAll()

            # --- stop the loop ---
            #print(self.endtime - self.startthread, self.measurementduration*60)
            if self.measurementduration!=0 and ((self.measurementduration*3) < (self.endtime - self.startthread)):
                # segmentation code when I switch on the following line 
                self.hourlyPlot.plotAll() 
                self.saveAll()
                self.copyLogfile()
                self.out.info("Stop the measurement after elapsed time, chosen by the user, is reached: %d min"%self.measurementduration)
                self._threadIsStopped=True
       
        # after the loop
        # save all the last time: this is done by CentralWidget-StopMeasurement 
        # in order to have it outside the thread and also to have access to the GUI options

    # ****** Analysis **********************************************************

    def prepareAnalysis(self):
        '''
        produce all variables, could be more efficient if you would restrict to actually used variables
        but I don't think this really matters

        initialize variables here, which need to be reset every hour after saving!
        '''

        self.wfm={}
        self.lastWfm={} # need to save last waveforms separately for live plotting
        self.max_amp={}
        self.min_amp={}
        self.area={}
        self.avg={}
        self.std={}
        self.xfreq=[]
        self.fft={}
        self.indisposedTimes=[] # save the values returned by runBlock, whatever they are
        self.measurementtime=0
        self.rate=[]
        self.time=[] # absolute time of a loop start in unix time
        self.duration=[] # duration of one loop (inverse of rate)

        for i in range(self.scope.NUM_CHANNELS):
            channel=list(self.scope.CHANNELS)[i][0]
            self.wfm[channel]=[]
            self.max_amp[channel]=[]
            self.min_amp[channel]=[]
            self.area[channel]=[]
            self.avg[channel]=[]
            self.std[channel]=[]
            self.fft[channel]=[]

    def analysis(self,data):

        # go through the channels
        for i in range(len(data)):
            channel=list(self.scope.CHANNELS)[i][0]
            if self.channelEnabled[channel]:
                if self.save_wfm[channel]:
                    arrai=self.getWFM(data[i], channel)
                    self.wfm[channel].extend(arrai)# use extend since the number of wfm per capture is known
                    self.lastWfm[channel]=np.array(arrai)
                if self.save_max_amp[channel]:
                    arrai=self.max_amplitude(data[i])
                    self.max_amp[channel].extend(arrai)
                if self.save_min_amp[channel]:
                    arrai=self.min_amplitude(data[i])
                    self.min_amp[channel].extend(arrai)
                if self.save_area[channel]:
                    arrai=self.calcArea(data[i])
                    self.area[channel].extend(arrai)
                if self.save_avg_std[channel]:
                    arrai=self.average(data[i])
                    self.avg[channel].append(arrai)
                    arrai=self.calcStd(data[i])
                    self.std[channel].append(arrai)
                if self.save_fft[channel]:
                    arrai=self.calcFft(data[i], channel)
                    self.fft[channel].append(arrai)

        rate = self.captures/self.measurementtime*1.e9
        #print("Rate", rate, self.captures, self.captures/self.measurementtime)
        self.rate.append(rate)
        self.duration.append(self.measurementtime)
        self.time.append(self.startblock/1.e9) # ns -> sec

        self.data_updated.emit() # you could also send data here
       
    def getWFM(self,dataX, channel):
        dx=np.array(dataX)
        if self.save_wfm_nbr[channel]>0:
            fakearray=np.arange(0,len(dx),1)
            index=np.random.choice(fakearray, size=self.save_wfm_nbr[channel], replace=False)
            arrai=dx[index]
        else:
            arrai=dataX
        return arrai

    def max_amplitude(self, dataX):
        arrai=np.max(dataX, axis=1) # first axis: column, second axis: row
        return arrai

    def min_amplitude(self, dataX):
        arrai=np.min(dataX, axis=1) # first axis: column, second axis: row
        return arrai

    def average(self, dataX):
        arrai=np.mean(dataX) # first axis: column, second axis: row
        return arrai

    def calcStd(self, dataX):
        arrai=np.std(dataX) # first axis: column, second axis: row
        return arrai

    def calcArea(self, dataX):
        areas=[]
        for waveform in dataX:
            baseline=0 # so far I got much worse results, if I tried to improve area
            area=waveform - baseline # you could make the waveform much shorter here
            area=sum(area)
            area*=self.interval
            areas.append(area)
        return areas

    def calcFft(self, dataX, channel):
        '''
        long time no use,
        no idea if this is correct!
        '''

        # downsample first!
        dx=np.array(dataX)
        if self.save_fft_nbr[channel]>0:
            fakearray=np.arange(0,len(dx),1)
            index=np.random.choice(fakearray, size=self.save_fft_nbr[channel], replace=False)
            arrai=dx[index]
        else:
            arrai=dx
        freqs=[]
        for waveform in arrai:
            Y = np.fft.fft(waveform)
            # correct for mirroring at the end
            N = int(len(Y)/2+1)
            # leakage effect
            hann = np.hanning(len(waveform))
            Yhann = np.fft.fft(hann*waveform)
            freq=2*np.abs(Yhann[:N])/N
            
            
            if self.xfreq==[]: # always the same?
                # x values
                dt = 500 * self.interval
                fa = 1.0/dt # scan frequency
                X = np.linspace(0, fa/2, N, endpoint=True)
                self.xfreq=X
            freqs.append(np.array(freq))
        return freqs

    # ****** Save **********************************************************

    def saveAll(self):
        '''
        executed when
        - stop button is pressed and user wants to save
        - every hour
        '''
        self.out.info("Save all in round %d"%(self.rounds))
        
        # go through the channels
        for i in range(self.scope.NUM_CHANNELS):
            channel=list(self.scope.CHANNELS)[i][0]
            if self.channelEnabled[channel]:
                if self.save_wfm[channel]:
                    self.save(channel+"_"+"waveform",self.wfm[channel])
                if self.save_max_amp[channel]:
                    self.save(channel+"_"+"max_amplitude",self.max_amp[channel])
                if self.save_min_amp[channel]:
                    self.save(channel+"_"+"min_amplitude",self.min_amp[channel])
                if self.save_area[channel]:
                    self.save(channel+"_"+"area",self.area[channel])
                if self.save_avg_std[channel]:
                    self.save(channel+"_"+"std",self.std[channel])
                    self.save(channel+"_"+"avg",self.avg[channel])
                if self.save_fft[channel]:
                    self.save(channel+"_"+"fft",self.fft[channel])
        
        # TODO: check if needed
        self.save("IndisposedTimes", self.indisposedTimes)

        # save always
        self.save("Triggerrate", self.rate)
        self.save("Time", self.time)
        self.save("Duration", self.duration)
        # TODO devices

        # Update settings
        self.rounds+=1
        self.lastSaved = self.endtime
        self.saveMeasurement=True
        self.prepareAnalysis() # reset all variables
        
    def save(self, name, values):
        filename=self.directory+"/"+name+"_"+str(self.rounds)+".npy"
        np.save(filename, values)
        self.out.info("Save %s to file %s"%(name, filename))

    def deleteDir(self):
        self.log.info("Deleting directory %s" % self.directory)

        try:
            if os.path.isfile(self.out.filename):
                os.remove(self.out.filename)
            if os.path.exists(self.directory):
                os.rmdir(self.directory)
        except Exception as e:
            self.log.error("Deleting of directory %s didn't work with error %s" % (self.directory, str(e)))

    def copyLogfile(self):
        # copy general log file here
        shutil.copyfile(self.log.filename, 
                        self.directory+"/"+self.log.filename.split("/")[-1]) 
        # use this module instead of os module to be compatible with windows

    # ****** Scope functions **********************************************************

    def setChannel(self, channel, enable=True):
        '''
        wrapper function to manage the channel properties of the picoscope
        '''

        VRange=self.scope.setChannel(channel=channel,
                                      coupling=self.coupling[channel],
                                      VRange=self.voltagerange[channel],
                                      VOffset=self.offset[channel]/1000, # offset is saved in mV, so convert to V here
                                      enabled=enable,
                                      )
        if VRange!=self.voltagerange[channel]:
            self.out.warning("Voltagerange of Channel %s was changed from %s to %s"% (channel, 
                                                                                          self.voltagerange[channel], 
                                                                                          VRange))
            self.voltagerange[channel]=VRange
        self.out.info("Channel %s: Mode %s, Voltage %fV, Offset %fmV, Enabled %d" % (channel,
                                                                        self.coupling[channel],
                                                                        self.voltagerange[channel]/1000,
                                                                        self.offset[channel],
                                                                        int(self.channelEnabled[channel]),
                                                                        ))

    def setTrigger(self):
    
        '''
        wrapper function to manage the trigger settings of the picoscope
        the trigger works on 1 channel
        There are some thresholds below which the trigger does not function well dependent
        on the channel range setting
        '''

        
        # ensure channel is enabled
        self.setChannel(self.triggerchannel, enable=True)

        ret=self.scope.setSimpleTrigger(self.triggerchannel,
                                    threshold_V=self.triggervoltage/1000, # in gui in mV here in V
                                    direction=self.triggermode,
                                    delay=self.triggerdelay,
                                    timeout_ms=self.triggertimeout,
                                    enabled=True)

        if ret:
            self.out.info("Trigger: Channel %s, " %  (self.triggerchannel) +\
                          "Voltage %fV, " % (self.triggervoltage/1000) +\
                          "Mode %s, "% (self.triggermode) +\
                          "Delay %f, "% (self.triggerdelay) +\
                          "Timeout %f, "% (self.triggertimeout))
            return True
        else:
            self.out.error("WARNING: Setting trigger failed!")
            return False # stop the run

    def setSampling(self):
        if self.opts.test: 
            self.interval=1./self.samplefreq
            return
        samplingRate, maxSamples, samples = self.scope.setSamplingFrequency(self.samplefreq, self.nosamples) # sample frequency, number of samples
        #maxSamples comes from the device, i.e. in test mode it is not known
        if self.samplefreq!=samplingRate:
            self.out.warning("Sampling rate was changed from %e to %e"%(self.samplefreq, samplingRate))
            self.samplefreq=samplingRate
        if self.nosamples!=samples:
            self.out.warning("Sample number was changed from %e to %e"%(self.nosamples, samples))
            self.nosamples=samples
        self.interval=1./self.samplefreq

        self.out.info("Sampling Rate: %e Hz; Samples %e; MaxSamples %e; Interval %e ns"%(self.samplefreq, 
                                                                    self.nosamples, 
                                                                    maxSamples,
                                                                    self.interval*1e9))

        # todo: anything with maxSamples

    def setCaptures(self):
        # number of memory segments must be equal or larger than self.captures
        if self.captures!=0:
            if self.opts.test: 
                return True
            maxSamples_per_Segment = self.scope.memorySegments(self.captures) 
            # otherwise the sample number got reduced
            if maxSamples_per_Segment<self.nosamples:
                self.out.error( "Reduce sample number per capture to maximum number")
                self.nosamples=maxSamples_per_Segment
                return False # stop run
            self.scope.setNoOfCaptures(self.captures)

            self.out.info("Captures: %e"%(self.captures, maxSamples_per_Segment))
            return True
        else:
            self.out.error("Capture number needs to be larger than zero")
            return False


    # ****** Class functions **********************************************************
    def __init__(self, log, opts, settings):
        '''
        initialise and prepare data taking
        - search for available picoscopes
        '''
        QThread.__init__(self)

        self.log=log
        self.opts=opts
        self.settings=settings

        # search picoscope devices and let the user decide which one to use
        # might return a dummy device: bool(self.scope.dummy)
        ds=deviceShelf(log,self.opts.test)
        self.scope=ds.select_and_start_device()
        self.opts.test=ds.test

        self.hw=None # will be set by GUI when first run starts
        self.setDefault() # load settings from file and set local variables


    def setDefault(self):
        # --- thread variables -----
        self.out=None # log object, needs to be initialized for saveLogger 
        self._progress=0 # progress of thread
        self._threadIsStopped=True # use this to stop the thread (effect is not directly!)
        
        # --- settings -----
        # (stuff which is remembered after re-launch)
        # channel settings
        self.voltagerange=self.settings.attr["voltagerange"]
        self.coupling=self.settings.attr["coupling"] # dc or ac
        self.offset=self.settings.attr["offset"] # voltage for offset of channel
        self.channelEnabled=self.settings.attr["channelEnabled"]
        # trigger settings
        self.triggerchannel=self.settings.attr["triggerchannel"]
        self.triggermode=self.settings.attr["triggermode"]
        self.triggervoltage=self.settings.attr["triggervoltage"]
        self.triggerdelay=self.settings.attr["triggerdelay"]
        self.triggertimeout=self.settings.attr["triggertimeout"]
        # block settings
        self.samplefreq=self.settings.attr["samplefreq"]
        self.captures=self.settings.attr["captures"]
        self.nosamples=self.settings.attr["nosamples"]
        self.measurementduration=self.settings.attr["measurementduration"]
        # save and analysis settings
        self.save_wfm=self.settings.attr["save_wfm"]
        self.save_max_amp=self.settings.attr["save_max_amp"]
        self.save_min_amp=self.settings.attr["save_min_amp"]
        self.save_area=self.settings.attr["save_area"]
        self.save_avg_std=self.settings.attr["save_avg_std"]
        self.save_fft=self.settings.attr["save_fft"]
        self.save_wfm_nbr=self.settings.attr["save_wfm_nbr"]
        self.save_fft_nbr=self.settings.attr["save_fft_nbr"]
        # --- run -----
        self.sleeptime=0.0001 # time interval after which the thread asks the scope if it is done. 1ms should be ok if you make the measurement longer than 1s
        self.saveMeasurement=False # default is false, so the user can decide. After 1h automatically set to true though
        self.rounds=0 # how many times does the measurement saveAll and restart before stopped
        '''
        self.starttime # starttime of thread (not start time of scope execution!)
        self.endtime # end time of the last block in seconds after 1970
        
        self.interval=0 # inverse of samplefreq
        ### for saving
        self.indisposedTimes=[]
        self.lastSaved=time.time()
        self.measurementtime
        '''