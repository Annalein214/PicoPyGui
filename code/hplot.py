import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math, os, traceback
from glob import glob
#plt.rc('xtick', labelsize=5)
#plt.rc('ytick', labelsize=5)
import matplotlib.gridspec as gridspec


from code.helpers import timestring_humanReadable, dateTime_plusHours, dateTime


class hourlyPlot:

    def __init__(self, log):
        
        self.log=log
        self.log.debug("Init hourlyPlot")
    def plotAll(self):

        self.log.debug("HourlyPlot: plotAll")

        try:# wrap so that this does not disturb normal operation
            dyrs=sorted(os.listdir("./data/"))
            hrtime=dyrs[-1] # starttime human readable
            self.directory="./data/"+hrtime
            self.outfile="./data/"+hrtime+"/"+hrtime+".out"
            #print("Directory",self.directory)
            
            # get round from file name of a file which always exists
            tfyles=sorted(glob(self.directory+"/Time_*.npy"))
            if len(tfyles)==0:
                self.log.error("No files found for plotting")
                return False
            runde = int(tfyles[-1].split("/")[-1].split(".")[0].split("_")[-1])
            #print("hourlyPlot, runde", runde)

            # get starttime from out file
            with open(self.outfile) as f:
                for line in f:
                    if "Starttime" in line:
                        unixtime=float(line.split(":")[-1].strip().split(" ")[0])
                    if "Sampling Rate" in line and "Interval" in line:
                        # Sampling Rate: %e Hz; Samples %e; MaxSamples %e; Interval %e ns
                        interval=int(float(line.split(";")[-1].strip().split(" ")[1])) # ns

            # get the time as this is shared by many variables
            time = np.load(self.directory+"/Time_"+str(runde)+".npy") 
            time-=unixtime
            time/=60. # convert to minutes

            # if exists, get the time from TimeHW_* for the external hardware
            # check if file exists
            if os.path.isfile(self.directory+"/TimeHW_"+str(runde)+".npy"):
                timeHW = np.load(self.directory+"/TimeHW_"+str(runde)+".npy") 
                timeHW-=unixtime
                timeHW/=60.

            # get all npy files
            nbr=0 # count time plots
            files = sorted(glob(self.directory+"/*_"+str(runde)+".npy"))
            #print(files)
            for fyle in files:
                if "Triggerrate" in fyle or \
                   "avg" in fyle or \
                   "std" in fyle:
                   self.plotTime(time, fyle, runde, unixtime)
                   nbr+=1
                if "HW_" in fyle.split("/")[-1][:3]:
                   self.plotTime(timeHW, fyle, runde, unixtime)
                   nbr+=1
                if "waveform" in fyle:
                    self.plotWaveform(fyle, runde, unixtime, interval)
                if "Triggerrate" in fyle or \
                   "max" in fyle or \
                   "min" in fyle or \
                   "area" in fyle or \
                   "avg" in fyle or \
                   "std" in fyle:
                   self.plotHistogram(fyle, runde, unixtime)
            self.allTimePlot(files, nbr, time, timeHW, runde, unixtime)
        except Exception as e: 
            traceback.print_exc()
            self.log.error("PlotAll failed with error %s" %str(e))

    # --------------------------------------------------------------------------------

    def allTimePlot(self,files,total, time, timeHW, runde, unixtime):

        self.log.debug("allTimePlot %d"% total)

        fig = plt.figure(dpi=100, figsize=(7, 1.5*total), facecolor='white')
        gs=gridspec.GridSpec(total, 3) # y, x devisions
        axes = [fig.add_subplot(gs[0,:]) ]
        plt.setp(axes[0].get_xticklabels(), visible=False)
        for i in range(total-1):
            axes.append(fig.add_subplot(gs[i+1,:], sharex=axes[0]))
            if i<total-2:
                plt.setp(axes[i+1].get_xticklabels(), visible=False)


        i=0
        for fylename in files:
            time2=time
            if "Triggerrate" in fylename or \
               "avg" in fylename or \
               "std" in fylename or \
               "HW_" in fylename.split("/")[-1][:3]:

                data=np.load(fylename)
                c=fylename.split("/")[-1].split(".")[0].split("_")
                if len(c)>=3:
                    channel=c[0] # A, B, ..., HW
                    mode=c[1]
                else:
                    channel="" # only for triggerrate
                    mode=c[0]

                if "Triggerrate" in mode: 
                    yUnit="Hz"
                    ma=np.max(data)
                    mi=np.min(data)
                    if min(ma, -mi) > 1000:
                        yUnit="kHz"
                        data/=1000
                elif "HW" in channel:
                    time2=timeHW
                    yUnit="?"
                    # HWT add your unit here
                    if "Lightsensor" in mode:
                        yUnit="V"
                    elif "HV" in mode:
                        yUnit="V"
                        data=data[:,1]
                    
                else: 
                    yUnit="V"
                    ma=np.max(data)
                    mi=np.min(data)
                    if max(ma, -mi) < 1:
                        yUnit="mV"
                        data*=1000

                axes[i].plot(time2,data, "-o", linewidth=1, markersize=1.5, alpha=0.7, )

                axes[i].grid(True)
                axes[i].set_ylabel("%s %s / %s" % (channel, mode, yUnit), fontsize=8)
                i+=1
        
        axes[-1].set_xlabel("Time / min",fontsize=10)

        text="Measurement started at %s"%dateTime(unixtime)
        if runde>0:
            text+="\nThis round started at %s" % dateTime_plusHours(unixtime, runde)
        axes[0].set_title(text,fontsize=10)

        fig.subplots_adjust(wspace=0.1, 
                            hspace=0.03, # space vertically
                            )

        plotname=self.directory+"/"
        plotname+="TimeAll_"+str(runde)+"_time.pdf"
        fig.savefig(plotname, bbox_inches='tight')
        fig.clf()
        fig.clear()
        plt.close(fig)
    # --------------------------------------------------------------------------------

    def plotHistogram(self,fylename, runde, unixtime):
        self.log.debug("PlotHistogram %s %d %f"%(fylename, runde, unixtime))

        data=np.load(fylename)
        data= np.hstack(data)
        c=fylename.split("/")[-1].split(".")[0].split("_")
        if len(c)>=3:
            channel=c[0] # A, B, ..., HW
            mode=c[1]
        else:
            channel="" # only for triggerrate
            mode=c[0]

        if "Triggerrate" in mode: 
            yUnit="Hz"
        elif "Area" in mode:
            yUnit="V*s"
        else: 
            yUnit="V"

        mi=np.min(data)
        ma=np.max(data)

        if "V" in yUnit:
          if max(ma, -mi) < 1:
            if not "Area" in mode: yUnit="mV"
            else: yUnit="mV*s"
            data*=1000; mi*=1000; ma*=1000
        if "Hz" in yUnit:
          if min(ma, -mi) > 1000:
            yUnit="kHz"
            data/=1000; mi/=1000; ma/=1000
        if "s" in yUnit: # area
            if max(ma, -mi) < 1e-3:
                yUnit="ms"
                data*=1e3; mi*=1e3; ma*=1e3
            if max(ma, -mi) < 1e-3:
                yUnit="μs"
                data*=1e3; mi*=1e3; ma*=1e3
            if max(ma, -mi) < 1e-3:
                yUnit="ns"
                data*=1e3; mi*=1e3; ma*=1e3

        xBorders=(mi-0.1*(ma-mi),ma+0.1*(ma-mi))
        bins=int(len(data)*0.1) # reduce number of bins to account for few values
        if bins<10: bins=10 # at least 10 bins
        bins=min(50,bins) # max 50 bins
        binning=[ i*float((xBorders[1]-xBorders[0]))/bins+xBorders[0] for i in range(bins+1)]
        binwidth=binning[1]-binning[0]
        histvals, binedges = np.histogram(data, bins=binning) 

        
        fig = plt.figure("Name", figsize=(4,3), dpi=100)         
        ax1 = plt.subplot2grid((1,1), (0, 0))

        ax1.bar(binedges[:-1], histvals, binwidth*0.9, facecolor="C0", edgecolor="C0")

        try: ax1.set_yscale("log")
        except: pass

        ax1.grid(True)
        ax1.set_xlabel("%s / %s" % (mode, yUnit))
        ax1.set_ylabel("Counts")
        text="Measurement started at %s"%dateTime(unixtime)
        if runde>0:
            text+="\nThis round started at %s" % dateTime_plusHours(unixtime, runde)
        ax1.set_title(text)

        plotname=self.directory+"/"
        if channel!="":
            plotname+=str(channel)+"_"
        plotname+=mode+"_"+str(runde)+"_hist.pdf"
        fig.savefig(plotname, bbox_inches='tight')
        fig.clf()
        fig.clear()

    # --------------------------------------------------------------------------------
    def plotWaveform(self, fylename, runde, unixtime, interval):

        self.log.debug("PlotWaveform %s %d %f %e"%( fylename, runde, unixtime, interval))

        c=fylename.split("/")[-1].split(".")[0].split("_")
        channel=c[0] # A, B, ..., HW
        mode=c[1]

        data=np.load(fylename)
        # choose only 30 datasets randomly
        waveforms=data[np.random.randint(0, data.shape[0], min(30,len(data))), :]

        time=np.arange(0, waveforms.shape[1], 1) * interval # ns

        yUnit="V"

        #improve x and y units
        ma=np.max(waveforms)
        mi=np.min(waveforms)
        if max(ma, -mi) < 1:
            yUnit="mV"
            waveforms*=1000

        xUnit="ns"
        if interval > 1000:
            time /= 1000
            interval /= 1000
            xUnit = "μs"
        if interval > 1000:
            time /= 1000
            interval /= 1000
            xUnit = "μs"   
        if interval > 1000:
            time /= 1000
            interval /= 1000
            xUnit = "s" 

        fig = plt.figure("Name", figsize=(7,3), dpi=100)         
        ax1 = plt.subplot2grid((1,1), (0, 0))

        for waveform in waveforms:
            ax1.plot(time,waveform, "-",linewidth=1, markersize=1.5, alpha=0.2)

        ax1.grid(True)
        ax1.set_ylabel("%s / %s" % (mode, yUnit))
        ax1.set_xlabel("Time / %s"%xUnit)
        text="Measurement started at %s"%dateTime(unixtime)
        if runde>0:
            text+="\nThis round started at %s" % dateTime_plusHours(unixtime, runde)
        ax1.set_title(text)

        plotname=self.directory+"/"
        if channel!="":
            plotname+=str(channel)+"_"
        plotname+=mode+"_"+str(runde)+"_wfm.pdf"
        fig.savefig(plotname, bbox_inches='tight')
        fig.clf()
        fig.clear()

    # --------------------------------------------------------------------------------

    def plotTime(self, time, fylename, runde, unixtime):

        self.log.debug("PlotTime %s %d %f"%(fylename, runde, unixtime))

        data=np.load(fylename)
        c=fylename.split("/")[-1].split(".")[0].split("_")
        if len(c)>=3:
            channel=c[0] # A, B, ..., HW
            mode=c[1]
        else:
            channel="" # only for triggerrate
            mode=c[0]

        if "Triggerrate" in mode: 
            yUnit="Hz"
            ma=np.max(data)
            mi=np.min(data)
            if min(ma, -mi) > 1000:
                yUnit="kHz"
                data/=1000
        elif "HW" in channel:
            yUnit="?"
            # HWT add your unit here and maybe the data
            if "Lightsensor" in mode:
                yUnit="V"
            elif "HV" in mode:
                yUnit="V"
                data=data[:,1]
        else: 
            yUnit="V"
            ma=np.max(data)
            mi=np.min(data)
            if max(ma, -mi) < 1:
                yUnit="mV"
                data*=1000
        # todo, merge time plots

        fig = plt.figure("Name", figsize=(7,3), dpi=100)         
        ax1 = plt.subplot2grid((1,1), (0, 0))

        ax1.plot(time,data, "-o", linewidth=1, markersize=1.5, alpha=0.7, )

        ax1.grid(True)
        ax1.set_ylabel("%s / %s" % (mode, yUnit))
        ax1.set_xlabel("Time / min")
        text="Measurement started at %s"%dateTime(unixtime)
        if runde>0:
            text+="\nThis round started at %s" % dateTime_plusHours(unixtime, runde)
        ax1.set_title(text)

        plotname=self.directory+"/"
        if channel!="":
            plotname+=str(channel)+"_"
        plotname+=mode+"_"+str(runde)+"_time.pdf"
        fig.savefig(plotname, bbox_inches='tight')
        fig.clf()
        fig.clear()
        #plt.show()


# -----------------------------------------------------------------------------
