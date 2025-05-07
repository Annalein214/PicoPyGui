from PyQt5.QtCore import QThread, pyqtSignal

import time, os, sys, shutil
import numpy as np
from code.helpers import timestring_humanReadable
from code.picoscope.device import deviceShelf
from code.log import log

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
    data_saved = pyqtSignal()
 
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
        self.log.outfile=self.out.filename # save the name of the logfile in the main log class

        self.settings.saveMeasurement=False # reset to false so that the user can decide 

        # how many times does the measurement saveAll and restart before stopped
        self.rounds=0 

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
            ok=self.setChannel(channel, self.settings.channelEnabled[channel])
            if not ok: return False

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
        if self.settings.measurementduration!=0:
            self._progress = float(self.endtime-self.startthread)/(self.settings.measurementduration*60)*100
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
                it=self.scope.runBlock(pretrig=self.settings.nopretriggersamples)
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
                    vRange=self.settings.voltagerange[channel]*1000*0.5

                    waveforms=[]
                    for i in range(100):
                        A=np.random.randint(-vRange,vRange)
                        x=np.arange(0,self.settings.nosamples,1)/self.settings.nosamples*np.pi*np.random.randint(0,5)
                        x=x-np.pi/10*np.random.randint(0,10)
                        wfm=A*np.sin(x)-self.settings.offset[channel]
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
            #print(self.endtime - self.startthread, self.settings.measurementduration*60)
            if self.settings.measurementduration!=0 and ((self.settings.measurementduration*60) < (self.endtime - self.startthread)):
                # stop hw thread to ensure data integrity => no solution for segmentation fault
                # keep it anyhow
                self.hw._threadIsStopped=True
                while self.hw.isRunning():
                    time.sleep(0.1)
                # extra time before or after executing next line => no solution for segmentation fault
                # remove all self.hw from hplot.py => no solution
                # remove all out/log frmo hplot.py => no solution
                # only waveform and w/o helper => no solution
                # tried upgrade of pip3 matplotlib from 3.7.0 to 3.7.2
                #self.hourlyPlot.plotAll()
                self.saveAll()
                self.copyLogfile()
                self.out.info("Stop the measurement after elapsed time, chosen by the user, is reached: %d min"%self.settings.measurementduration)
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
        self.pulses={}
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
            self.pulses[channel]=[]

    def analysis(self,data):

        # go through the channels
        for i in range(len(data)):
            channel=list(self.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                if self.settings.save_wfm[channel]:
                    arrai=self.getWFM(data[i], channel)
                    self.wfm[channel].extend(arrai)# use extend since the number of wfm per capture is known
                    self.lastWfm[channel]=np.array(arrai)
                if self.settings.save_max_amp[channel]:
                    arrai=self.max_amplitude(data[i])
                    self.max_amp[channel].extend(arrai)
                if self.settings.save_min_amp[channel]:
                    arrai=self.min_amplitude(data[i])
                    self.min_amp[channel].extend(arrai)
                if self.settings.save_area[channel]:
                    arrai=self.calcArea(data[i])
                    self.area[channel].extend(arrai)
                if self.settings.save_avg_std[channel]:
                    arrai=self.average(data[i])
                    self.avg[channel].append(arrai)
                    arrai=self.calcStd(data[i])
                    self.std[channel].append(arrai)
                if self.settings.save_fft[channel]:
                    arrai=self.calcFft(data[i], channel)
                    self.fft[channel].append(arrai)
                if channel=="A": # force identification of pulses
                    arrai= self.calcPulses(data[i])
                    self.pulses[channel].append(arrai)

        rate = self.settings.captures/self.measurementtime*1.e9
        #print("Rate", rate, self.settings.captures, self.settings.captures/self.measurementtime)
        self.rate.append(rate)
        self.duration.append(self.measurementtime)
        self.time.append(self.startblock/1.e9) # ns -> sec

        self.data_updated.emit() # you could also send data here
       
    def calcPulses(self, dataX):
        '''
        calculate the number of pulses in the waveform
        - go through every waveform in the capture
        - find zero crossings (in reference to a trigger value)
        - find the minimum in between the zero crossings
        '''

        #Set Trigger
        trigger = 0.002 # needs to be the opposite sign of the real trigger value

        #create lists 
        peak_loc=[] 
        peak_amp=[]
        peak_loc_sub=np.zeros(30)*np.NaN # in order to get a matrix with fixed size
        peak_amp_sub=np.zeros(30)*np.NaN
        

        for wfm in dataX:  #index (idx) is added to each element (wfm) in data, starting at 0 
            zero_crossings = np.where(np.diff(np.sign(wfm+trigger)))[0] #Finds index, where sign wfm + index changes from positive to negative or vice versa 
            #[0::2] means even indexed zero crossing (0,2,4,...), begin of window 
            max_loc = [z1 + np.argmin(wfm[z1:z2+1]) for z1,z2 in zip(zero_crossings[0::2],zero_crossings[1::2])]  
            peak_loc_sub[0:len(max_loc)]=max_loc
            peak_amp_sub[0:len(max_loc)]=wfm[max_loc]
            peak_loc.append(peak_loc_sub)
            peak_amp.append(peak_amp_sub)
            #peak_num.append(len(max_loc))

        arrai= np.array(peak_loc, peak_amp)
        return arrai
        


    def getWFM(self,dataX, channel):
        dx=np.array(dataX)
        if self.settings.save_wfm_nbr[channel]>0:
            fakearray=np.arange(0,len(dx),1)
            index=np.random.choice(fakearray, size=self.settings.save_wfm_nbr[channel], replace=False)
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
        if self.settings.save_fft_nbr[channel]>0:
            fakearray=np.arange(0,len(dx),1)
            index=np.random.choice(fakearray, size=self.settings.save_fft_nbr[channel], replace=False)
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
            if self.settings.channelEnabled[channel]:
                if self.settings.save_wfm[channel]:
                    self.save(channel+"_"+"waveform",self.wfm[channel])
                if self.settings.save_max_amp[channel]:
                    self.save(channel+"_"+"max_amplitude",self.max_amp[channel])
                if self.settings.save_min_amp[channel]:
                    self.save(channel+"_"+"min_amplitude",self.min_amp[channel])
                if self.settings.save_area[channel]:
                    self.save(channel+"_"+"area",self.area[channel])
                if self.settings.save_avg_std[channel]:
                    self.save(channel+"_"+"std",self.std[channel])
                    self.save(channel+"_"+"avg",self.avg[channel])
                if self.settings.save_fft[channel]:
                    self.save(channel+"_"+"fft",self.fft[channel])
                if channel=="A": # save forced identification of pulses
                    self.save(channel+"_"+"pulses",self.pulses[channel])
        
        # TODO: check if needed
        #self.save("IndisposedTimes", self.indisposedTimes)

        # save always
        self.save("Triggerrate", self.rate)
        self.save("Time", self.time)
        self.save("Duration", self.duration)
        # TODO devices
        self.hw.saveAll()

        # Update settings
        self.rounds+=1
        self.lastSaved = self.endtime
        self.settings.saveMeasurement=True
        self.prepareAnalysis() # reset all variables
        self.data_saved.emit()
        
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

        try:
            VRange=self.scope.setChannel(channel=channel,
                                          coupling=self.settings.coupling[channel],
                                          VRange=self.settings.voltagerange[channel],
                                          VOffset=self.settings.offset[channel]/1000, # offset is saved in mV, so convert to V here
                                          enabled=enable,
                                          )

            if VRange!=self.settings.voltagerange[channel]:
                self.out.warning("Voltagerange of Channel %s was changed from %s to %s"% (channel, 
                                                                                          self.settings.voltagerange[channel], 
                                                                                          VRange))
                self.settings.voltagerange[channel]=VRange
            self.out.info("Channel %s: Mode %s, Voltage %.3fV, Offset %.1fmV, Enabled %d" % (channel,
                                                                        self.settings.coupling[channel],
                                                                        self.settings.voltagerange[channel],
                                                                        self.settings.offset[channel],
                                                                        int(self.settings.channelEnabled[channel]),
                                                                        ))
            return True
        except Exception as e:
            self.log.error("ERROR settings channel %s: %s"%(channel,str(e)))
            return False

        

    def setTrigger(self):
    
        '''
        wrapper function to manage the trigger settings of the picoscope
        the trigger works on 1 channel
        There are some thresholds below which the trigger does not function well dependent
        on the channel range setting
        '''

        
        # ensure channel is enabled
        ok=self.setChannel(self.settings.triggerchannel, enable=True)
        
        self.out.info("Trigger: Channel %s, " %  (self.settings.triggerchannel) +\
                              "Voltage %fV, " % (self.settings.triggervoltage/1000) +\
                              "Mode %s, "% (self.settings.triggermode) +\
                              "Delay %f, "% (self.settings.triggerdelay) +\
                              "Timeout %f, "% (self.settings.triggertimeout) +\
                             "Pretrigger Ratio %.2f"% self.settings.nopretriggersamples )
                              
        if not ok: return False

        try:
            ret=self.scope.setSimpleTrigger(self.settings.triggerchannel,
                                    threshold_V=self.settings.triggervoltage/1000, # in gui in mV here in V
                                    direction=self.settings.triggermode,
                                    delay=self.settings.triggerdelay,
                                    timeout_ms=self.settings.triggertimeout,
                                    enabled=True)

            if ret:
                self.out.info("Trigger: Channel %s, " %  (self.settings.triggerchannel) +\
                              "Voltage %fV, " % (self.settings.triggervoltage/1000) +\
                              "Mode %s, "% (self.settings.triggermode) +\
                              "Delay %f, "% (self.settings.triggerdelay) +\
                              "Timeout %f, "% (self.settings.triggertimeout))
                return True
            else:
                self.out.error("WARNING: Setting trigger failed!")
                return False # stop the run
        except Exception as e:
            self.log.error("ERROR setting trigger: %s" %(str(e)))

    def setSampling(self):
        if self.opts.test: 
            self.interval=1./self.settings.samplefreq
            self.out.info("Sampling Rate: %e Hz; Samples %e; MaxSamples %e; Interval %e ns; Pre-trigger %d"%(self.settings.samplefreq, 
                                                                    self.settings.nosamples, 
                                                                    0,
                                                                    self.interval*1e9, 
                                                                    int(self.settings.nopretriggersamples * self.settings.nosamples)))

            return
        samplingRate, maxSamples, samples = self.scope.setSamplingFrequency(self.settings.samplefreq, self.settings.nosamples) # sample frequency, number of samples
        #maxSamples comes from the device, i.e. in test mode it is not known
        if self.settings.samplefreq!=samplingRate:
            self.out.warning("Sampling rate was changed from %e to %e"%(self.settings.samplefreq, samplingRate))
            self.settings.samplefreq=samplingRate
        if self.settings.nosamples!=samples:
            self.out.warning("Sample number was changed from %e to %e"%(self.settings.nosamples, samples))
            self.settings.nosamples=samples
        self.interval=1./self.settings.samplefreq

        self.out.info("Sampling Rate: %e Hz; Samples %e; MaxSamples %e; Interval %e ns"%(self.settings.samplefreq, 
                                                                    self.settings.nosamples, 
                                                                    maxSamples,
                                                                    self.interval*1e9))

        # todo: anything with maxSamples

    def setCaptures(self):
        # number of memory segments must be equal or larger than self.settings.captures
        if self.settings.captures!=0:
            if self.opts.test: 
                self.out.info("Captures: %e; max Samples per Segment %e"%(self.settings.captures, 0))
                return True
            maxSamples_per_Segment = self.scope.memorySegments(self.settings.captures) 
            # otherwise the sample number got reduced
            if maxSamples_per_Segment<self.settings.nosamples:
                self.out.error( "Reduce sample number per capture to maximum number")
                self.settings.nosamples=maxSamples_per_Segment
                return False # stop run
            self.scope.setNoOfCaptures(self.settings.captures)

            self.out.info("Captures: %e; max Samples per Segment %e"%(self.settings.captures, maxSamples_per_Segment))
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
        self.scope=ds.select_and_start_device(opts.test)
        self.opts.test=ds.test

        self.hw=None # will be set by GUI when first run starts
        self.setDefault() # load settings from file and set local variables


    def setDefault(self):
        # --- thread variables -----
        self.out=None # log object, needs to be initialized for saveLogger 
        self._progress=0 # progress of thread
        self._threadIsStopped=True # use this to stop the thread (effect is not directly!)

        # --- run -----
        self.sleeptime=0.0001 # time interval after which the thread asks the scope if it is done. 1ms should be ok if you make the measurement longer than 1s
        self.settings.saveMeasurement=False # default is false, so the user can decide. After 1h automatically set to true though
        '''
        self.starttime # starttime of thread (not start time of scope execution!)
        self.endtime # end time of the last block in seconds after 1970
        
        self.interval=0 # inverse of samplefreq
        ### for saving
        self.indisposedTimes=[]
        self.lastSaved=time.time()
        self.measurementtime
        '''


    def close(self):
        if not self.opts.test:
            self.scope.close()
            self.scope=None
        self.log.info("Picoscope closed. Good night!")


