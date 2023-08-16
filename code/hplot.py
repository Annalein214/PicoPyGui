from code.helpers import timestring_humanReadable, dateTime_plusHours, dateTime

import matplotlib.pyplot as plt
import numpy as np
import math

class plot:

    def __init__(self,log,daq,hw, settings):
        self.log=log
        self.daq=daq
        self.hw=hw
        self.settings=settings

##########################################################################################

    def plotAll(self):
        # collect what will be plotted in which way

        
        # count
        wfmNbr=0; histNbr=0; timeNbr=0; fftNbr=0
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                if self.settings.save_wfm[channel]:
                    wfmNbr+=1
                if self.settings.save_max_amp[channel]:
                    histNbr+=1
                if self.settings.save_min_amp[channel]:
                    histNbr+=1            
                if self.settings.save_area[channel]:
                    histNbr+=1
                if self.settings.save_avg_std[channel]:
                    histNbr+=2
                    timeNbr+=2
                if self.settings.save_fft[channel]:
                    fftNbr+=1
            
        # HWT: add your hardware here
        if self.settings.useDummy:
            timeNbr+=1

        #IndisposedTimes
        histNbr+=1

        #triggerrate
        histNbr+=1
        timeNbr+=1

        #self.timewise(timeNbr)
        #self.histogram(histNbr)
        self.waveform(wfmNbr)
        

##########################################################################################

    def waveform(self, total):
        '''
        hourly plots of waveform data
        only plot a subset of available waveforms
        '''
        print("Plot waveform")

        
        # SF save until here
        # prepare plot
        rows=math.ceil(math.sqrt(total)); cols=math.ceil(total/rows)
        fig = plt.figure("Name", figsize=(3*cols,2*rows)) 
        axes=[]
        '''
        for i in range(total):
            if i<rows:
                r=i; c=0
            else:
                r=i%rows; c=i//rows
            #print(i,r,c)
            axes.append(plt.subplot2grid((rows,cols), (r,c)))
            axes[i].grid(True)


        plotI=0
        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if daq.scope.channelEnabled[channel]:
                if self.settings.save_wfm[channel]:
                    self.wfmPlot(channel, axes[plotI])
                    plotI+=1
        
        fig.suptitle("Waveform examples for Round %d. \nStart of measurement: %s. \nStart of this round: %s" %(self.daq.rounds, str(dateTime(self.daq.startthread)), str(dateTime_plusHours(self.daq.startthread, self.daq.rounds))))

        fig.subplots_adjust(top=0.75,
                            wspace=0.5, 
                            hspace=0.6, # space vertically
                            )
        '''
        filename=self.daq.directory+"/Waveforms_"+str(self.daq.rounds)+".pdf"
        fig.savefig(filename, bbox_inches='tight')
        fig.clf()
        fig.clear()
        # SF save until here
        

    def wfmPlot(self,channel, ax):
        '''
        helper
        '''
        print("Plot waveform helper", channel)

        # get y-Axis values
        values=np.array(self.daq.wfm[channel])

        if len(values)==0:
            return

        fakearray=np.arange(0,len(values),1)
        index=np.random.choice(fakearray, size=min(len(values), 20), replace=False)
        waveforms=values[index]

        unit="V"
        vRange=self.settings.voltagerange[channel]
        offSet=self.settings.offset[channel]/1000
        triggervoltage=self.settings.triggervoltage/1000
        if vRange < 1: # for convenience change to mV 
            unit="mV"
            vRange*=1000
            offSet*=1000
            triggervoltage*=1000
            waveforms*=1000

        xUnit = "sec"
        time = np.arange(0, len(values[0]), 1) * self.daq.interval
        if self.daq.interval < 1.e6: 
            time *= 1.e9
            xUnit = "ns"
        elif self.daq.interval < 1.e3:
            time *= 1.e6
            xUnit = "μs"
        elif self.daq.interval < 1:
            time *= 1.e3
            xUnit = "ms"


        # plot
        for waveform in waveforms:
            ax.plot(time, waveform, "-", linewidth=1, markersize=1, alpha=0.3, color="C0")
        ax.set_ylabel("Amplitude / %s" % unit)
        ax.set_xlabel("Time / %s" % xUnit)
        ax.set_title("Ch.%s" % channel, loc="left", pad=3, weight="bold")

        # I got a segmentation fault

##########################################################################################

    def histogram(self, total):

        '''
        hourly / end plot of timewise variables
        all plotted into the same plot
        '''

        print("Plot histogram")

        # prepare plot
        rows=math.ceil(math.sqrt(total)); cols=math.ceil(total/rows)
        #print(rows, cols)
        fig = plt.figure("Name", figsize=(4*cols,2*rows)) 
        axes=[]
        for i in range(total):
            if i<rows:
                r=i; c=0
            else:
                r=i%rows; c=i//rows
            #print(i,r,c)
            axes.append(plt.subplot2grid((rows,cols), (r,c)))
            axes[i].grid(True)

        # slowly go through all subplots with this variable
        plotI = 0

        # --------------------------------
        # get values and plot them

        # --- triggerrate ---
        values=self.daq.rate
        xlabel="Rate / Hz" # dont change name! needed in histplot
        #print(plotI,xlabel, len(values))
        self.histPlot(axes[plotI], values, xlabel)
        plotI+=1

        # --- indisposedTimes ---
        values=self.daq.indisposedTimes
        xlabel="IndisposedTimes / ?"
        #print(plotI,xlabel, len(values))
        self.histPlot(axes[plotI], values, xlabel)
        plotI+=1

        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.channelEnabled[channel]:
                # --- Amplitude --- 
                if self.settings.save_max_amp[channel]:
                    values = self.daq.max_amp[channel]
                    xlabel="Max. Ampl. Ch.%s" % channel
                    #print(plotI,xlabel, len(values))
                    self.histPlot(axes[plotI], values, xlabel, channel=channel)
                    plotI+=1

                # --- Amplitude --- 
                if self.settings.save_min_amp[channel]:
                    values = self.daq.min_amp[channel]   
                    xlabel="Min. Ampl. Ch.%s" % channel
                    #print(plotI,xlabel, len(values))
                    self.histPlot(axes[plotI], values, xlabel, channel=channel)
                    plotI+=1
                
                # --- Area ---        
                if self.settings.save_area[channel]:
                    
                    values=self.daq.area[channel]
                    xlabel="Area Ch.%s" % channel
                    #print(plotI,xlabel, len(values))
                    self.histPlot(axes[plotI], values, xlabel, channel=channel)
                    plotI+=1

                if self.settings.save_avg_std[channel]:
                    # --- Average ---
                    values=self.daq.avg[channel]
                    xlabel="Average Ch.%s" % channel
                    #print(plotI,xlabel, len(values))
                    self.histPlot(axes[plotI], values, xlabel, channel=channel)
                    plotI+=1

                    # --- std ---
                    values=self.daq.std[channel]
                    xlabel="Std.Dev. Ch.%s" % channel
                    #print(plotI,xlabel, len(values))
                    self.histPlot(axes[plotI], values, xlabel, channel=channel)
                    plotI+=1

        # --------------------------------
        # finalize

        fig.suptitle("Histograms for Round %d. \nStart of measurement: %s. \nStart of this round: %s" %(self.daq.rounds, str(dateTime(self.daq.startthread)), str(dateTime_plusHours(self.daq.startthread, self.daq.rounds))))

        fig.subplots_adjust(top=0.85,
                            wspace=0.5, 
                            hspace=0.3, # space vertically
                            )
        filename=self.daq.directory+"/Histwise_"+str(self.daq.rounds)+".pdf"
        fig.savefig(filename, bbox_inches='tight')
        fig.clf()
        fig.clear()

    def histPlot(self,ax, values, xlabel, channel=None):
        '''
        helper 
        '''

        print("Histogram helper", xlabel, len(values))
        values=np.array(values)
        if len(values)>0:
            values= np.hstack(values)
        else:
            self.log.error("No values in array of %s for histogram"%xlabel)
            print(xlabel, "no values")
            return

        if channel!=None:
            unit="V"
            vRange=self.settings.voltagerange[channel]
            offSet=self.settings.offset[channel]/1000
            triggervoltage=self.settings.triggervoltage/1000
            if vRange < 1: # for convenience change to mV 
                unit="mV"
                vRange*=1000
                offSet*=1000
                triggervoltage*=1000
                values*=1000

        unit2=""
        if "Area" in xlabel: 
            unit2+="* sec"
            # adjust unit so that you get more reasonable values
            if np.max(values)<0:
                values*=1000
                unit2="* ms"
            if np.max(values)<0:
                values*=1000
                unit2="* μs"
            if np.max(values)<0:
                values*=1000
                unit2="* ns"

        if "Amp" in xlabel:
            xBorders=(-vRange+offSet,vRange+offSet)
        else:
            mi=np.min(values)
            ma=np.max(values)
            xBorders=(mi-0.1*(ma-mi),ma+0.1*(ma-mi))

        bins=int(len(values)*0.1) # reduce number of bins to account for few values
        if bins<10: bins=10 # at least 10 bins
        bins=min(50,bins) # max 50 bins
        binning=[ i*float((xBorders[1]-xBorders[0]))/bins+xBorders[0] for i in range(bins+1)]
        binwidth=binning[1]-binning[0]
        histvals, binedges = np.histogram(values, bins=binning)

        # plot
        ax.bar(binedges[:-1], histvals, binwidth*0.9, facecolor="C0", edgecolor="C0")
        if xBorders[0]!=xBorders[1]: # only issue at the first round
            ax.set_xlim(xBorders[0],xBorders[1])

        if self.settings.triggerchannel == channel and \
           "Amp" in xlabel:
            ax.axvline(triggervoltage, color="red", 
                       linewidth=1., label="Trigger") 
            ax.legend(  loc="best",
                        frameon=False, 
                        borderaxespad=0.,
                        prop={'size': 6})

        try: ax.set_yscale("log")
        except: pass

        ax.set_ylabel("Counts", fontsize=12)
        if channel!=None:
            ax.set_xlabel("%s / %s %s" % (xlabel,unit,unit2), fontsize=12)
        else:
            ax.set_xlabel("%s" % (xlabel), fontsize=12)

##########################################################################################

    def timePlot(self,ax, xvalues, yvalues, ylabel):
        print("TimePlot helper", ylabel, len(xvalues), len(yvalues))
        if len(xvalues)!=len(yvalues):
            self.log.error("Timeplot for %s: len of x and y values does not match. Cannot plot them. %d %d"%(ylabel,len(xvalues), len(yvalues)))
        else:
            ax.plot(xvalues, yvalues, "-o", linewidth=1, markersize=1, alpha=0.7)
            ax.set_ylabel(ylabel)

    def timewise(self, total):
        '''
        hourly / end plot of timewise variables
        all plotted into the same plot
        '''
        print("Plot timewise")

        # prepare plot
        fig = plt.figure("Name", figsize=(12,2*total)) 
        axes= [plt.subplot2grid((total,1), (0, 0))]
        axes[0].grid(True)
        for i in range(total-1):
            axes.append(plt.subplot2grid((total,1), (i+1,0), sharex=axes[0]))
            axes[i+1].grid(True)
            if i<total-2:
                plt.setp(axes[i+1].get_xticklabels(), visible=False)


        # slowly go through all subplots with this variable
        plotI = 0

        # get x-Axis values
        time=(np.array(self.daq.time) - self.daq.startthread) / 60
        timeHW=(np.array(self.hw.time) - self.daq.startthread) / 60 # from unix time to minutes since measurement started

        # --------------------------------
        # get y-Axis values and plot them

        # --- triggerrate ---
        values=self.daq.rate
        ylabel="Rate / Hz"
        self.timePlot(axes[plotI], time, values, ylabel)
        plotI+=1

        for i in range(self.daq.scope.NUM_CHANNELS):
            channel=list(self.daq.scope.CHANNELS)[i][0]
            if self.settings.save_avg_std[channel]:
                if self.settings.channelEnabled[channel]:
                    # --- average ---
                    values=self.daq.avg[channel]
                    ylabel="Average Ch.%s / V" % channel
                    self.timePlot(axes[plotI], time, values, ylabel)
                    plotI+=1

                    # --- std ---
                    values=self.daq.std[channel]
                    ylabel="Std.Dev. Ch.%s / V" % channel
                    self.timePlot(axes[plotI], time, values, ylabel)
                    plotI+=1

        # --- externals ---
        if self.settings.useDummy:
            values=self.hw.dummyVals
            ylabel="Dummy / V"
            self.timePlot(axes[plotI], timeHW, values, ylabel)

        axes[0].set_title("Time development. Round %d. \nStart of measurement: %s. Start of this round: %s" %(self.daq.rounds, str(dateTime(self.daq.startthread)), str(dateTime_plusHours(self.daq.startthread, self.daq.rounds))))
        axes[-1].set_xlabel("Time / min") 

        fig.subplots_adjust(wspace=0.1, 
                            hspace=0.03, # space vertically
                            )
        filename=self.daq.directory+"/Timewise_"+str(self.daq.rounds)+".pdf"
        fig.savefig(filename, bbox_inches='tight')
        fig.clf()
        fig.clear()

        


        

