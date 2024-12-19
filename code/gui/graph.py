import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, FormatStrFormatter



from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
MyGui=QtWidgets

from code.helpers import linestyles
    
import random, time, traceback
import numpy as np

##########################################################################################

class graph():
    '''
    used for data storage and maybe to do 
    heavy calculation in a thread as preparation for plot widget
    '''
    def __init__(self, log, opts, settings):
        self.log=log 
        self.opts=opts
        self.settings=settings

        # load variables from settings
        self.setDefault()
    
    def setDefault(self):    
        self.raw_data_ch=self.settings.attr["raw_data_ch"]
        self.raw_data_nbr=self.settings.attr["raw_data_nbr"]
        self.hist_ch_mode=self.settings.attr["hist_ch_mode"]
        self.time_ch_mode1=self.settings.attr["time_ch_mode1"]
        self.time_ch_mode2=self.settings.attr["time_ch_mode2"]
        self.str_ch_mode1=self.settings.attr["str_ch_mode1"]
        self.str_ch_mode2=self.settings.attr["str_ch_mode2"]
        self.str_ch_mode3=self.settings.attr["str_ch_mode3"]
        self.str_ch_mode4=self.settings.attr["str_ch_mode4"]
        self.str_ch_mode5=self.settings.attr["str_ch_mode5"]

##########################################################################################
# draw figure (general stuff)

class plotWidget(FigureCanvas):
    """A canvas that updates itself every 
        interval with a new plot.
    """

    def __init__(self, parent, log, daq, settings, hw):

        self.log = log
        self.daq = daq
        self.settings = settings
        self.hw = hw
        
        # initialize the figure, needs to be done first!
        self.fig = Figure(dpi=100, facecolor='white')
        gs=gridspec.GridSpec(5, 4) # y, x devisions
        self.axH = self.fig.add_subplot(gs[0:2,2:])# histogram; oben links
        self.axW = self.fig.add_subplot(gs[0:2,:2])# waveform; oben rechts
        self.axT1 = self.fig.add_subplot(gs[3,:])# time development; unten links
        self.axT2 = self.fig.add_subplot(gs[4,:], sharex=self.axT1)# time development; unten links

        # for later
        # self.ax4 = self.ax2.twinx()
        # self.ax4.yaxis.set_label_position("right")

        self.fig.subplots_adjust(left=0.2,right=0.92,
                                 bottom=0.07,top=0.97,
                                 wspace=1.2, # space between horizontally arranged plots
                                 hspace=0.03, # space vertically
                                 )

        # setup canvas
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   MyGui.QSizePolicy.Expanding,
                                   MyGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.axW.set_title("Waveforms", fontsize=8, loc="left", pad=3, weight="bold")
        self.axW.set_xlabel("Time")
        self.axW.set_ylabel("Amplitude")
        
        self.axH.set_title("Histogram", fontsize=8, loc="left", pad=3, weight="bold")
        self.axH.set_ylabel("Counts")
        self.axH.set_xlabel(r"Amplitude")

        self.axT1.set_title("Time development", fontsize=8, loc="left", pad=3, weight="bold")
        self.axT1.set_ylabel("Value ") # todo unit
        self.axT2.set_ylabel("Value ") # todo unit
        self.axT2.set_xlabel("Time / min") 
        plt.setp(self.axT1.get_xticklabels(), visible=False)
        self.axT1.yaxis.set_major_locator(MaxNLocator(nbins="auto",prune='lower'))

        self.axW.text(0.1, -0.25, "Latest values:", 
                          weight="bold", fontsize=8,
                          transform=self.axW.transAxes, 
                          horizontalalignment="left", verticalalignment="top",
                          )
        self.axW.text(0.1, -0.25-0.05, "Value: None", 
                        fontsize=8,
                        transform=self.axW.transAxes, 
                          horizontalalignment="left", verticalalignment="top",)

        self.axH.grid()
        self.axW.grid()
        self.axT1.grid()
        self.axT2.grid()

        # update is triggered from daq, but make sure this is not too often
        self.minUpdateTime=1 # sec, ensure that it is larger than time required to make data
        self.lastUpdate=int(time.time()) - (2*self.minUpdateTime) # ensure that an update will be done directly

        self.log.debug("Init Figure")
        

    # -------------------------------------------------------------------------

    def update_figure(self): 

        if not self.daq.isRunning():
            self.log.error("Daq not running. Maybe slow PC?")
            return
        try:
            # pack into try to avoid nasty crash just because of plotting
            now=time.time()
            #print(self.minUpdateTime, (now-self.lastUpdate))
            if (now-self.lastUpdate)>self.minUpdateTime:
                #self.log.debug("Update Figure")
                self.lastUpdate=now

                # clear everything
                self.axH.clear()
                self.axW.clear()
                self.axT1.clear()
                self.axT2.clear()

                # formatting

                self.axH.grid()
                self.axW.grid()
                self.axT1.grid()
                self.axT2.grid()

                plt.setp(self.axT1.get_xticklabels(), visible=False)
                self.axT1.yaxis.set_major_locator(MaxNLocator(nbins="auto",prune='lower'))


                # plot data
                self.plotWaveform()
                self.plotHistogram()
                for i in range(2):
                    self.plotTime(i+1)
                for i in range(5):
                    self.plotText(i+1)
                

                # draw everything
                self.draw()
            else:
                pass
                #self.log.debug("Min time did not elapse")
        except Exception as e:
            traceback.print_exc()
            self.log.error("Graph exception: %s"%(str(e)))

        
        
##########################################################################################
# draw figure (data stuff)


    def plotText(self,nbr):
        str_ch_mode = [self.settings.str_ch_mode1, 
                       self.settings.str_ch_mode2,
                       self.settings.str_ch_mode3,
                       self.settings.str_ch_mode4,
                       self.settings.str_ch_mode5,][nbr-1]

        if nbr==1:  # only execute once
            self.axW.text(0.1, -0.25, "Latest values:", 
                          weight="bold", fontsize=8,
                          transform=self.axW.transAxes, 
                          horizontalalignment="left", verticalalignment="top",
                          )

        if str_ch_mode != "None":

            #print(str_ch_mode)

            if ":" in  str_ch_mode:
                channel=str_ch_mode.split(":")[0]
                mode=str_ch_mode.split(":")[1]
            else:
                channel=""
                mode=""

            #print(channel, mode)

            if "Triggerrate" in str_ch_mode:
                if len(self.daq.rate)>0:
                    value = "%.2e" % self.daq.rate[-1]
                else:
                    value= "00"
                title = "Triggerrate"
                yUnit = "Hz"
            elif "Std" in mode:
                if len(self.daq.std[channel][-1])>0:
                    value = "%.2e" % self.daq.std[channel][-1]
                else:
                    value= "00"
                title = "Std. Dev. Ch. %s" % channel
                yUnit = "V"
            elif "Average" in mode:
                if self.daq.avg[channel][-1]>0:
                    value = "%.2e" % self.daq.avg[channel][-1]
                else:
                    value=np.nan
                title = "Average Ch. %s" % channel
                yUnit = "V"
            # HWT add custom instructions for hardware
            elif "Dummy" in mode:
                if self.hw.dummyVals[-1]>0:
                    value = "%.2e" % self.hw.dummyVals[-1]
                else:
                    value=np.nan
                title = "Ext. Dummy"
                yUnit = "V"
            elif "Lightsensor" in mode:
                if self.hw.lightVals[-1]>0:
                   value = "%.2e" % self.hw.lightVals[-1]
                else:
                    value=np.nan
                title = "Lightsensor"
                yUnit = "V"
            elif "Humidity" in mode:
                if self.hw.humVals[-1]>0:
                   value = "%.2e" % self.hw.humVals[-1]
                else:
                    value=np.nan
                title = "Humidity"
                yUnit = "%"
            elif "HumTemp" in mode:
                if len(self.hw.humTempVals)>0:
                    value = "%.1f" % self.hw.humTempVals[-1]
                else:
                    value=np.nan
                title = "HumTemp"
                yUnit = "°C"
            elif "HV" in mode:
                if self.hw.hvVals[-1]>0:
                    value = "%.2e" % self.hw.hvVals[-1][1]
                else:
                    value=np.nan
                title = "HV"
                yUnit = "V"
            elif "Temperature" in mode:
                if len(self.hw.tempVals)>0:
                    values = self.hw.tempVals[-1]
                else:
                    values=[np.nan, np.nan, np.nan]
                title = "Temps"
                yUnit = "°C"
                value = ""
                for v in values:
                    value+="%.1f %s; " % (float(v), yUnit)
                value=value[:-(len(yUnit))]

            text="%s: %s %s" % (title,value,yUnit)

            if nbr < 3:
                ax=self.axW
                nbr2=nbr; dx=0
            else:
                ax=self.axH
                nbr2=nbr-3; dx=-0.2
            
            ax.text(0.1+dx, -0.25-(0.05*nbr2), text, 
                        fontsize=8,
                        transform=ax.transAxes, 
                          horizontalalignment="left", verticalalignment="top",)


    def plotTime(self,nbr):


        # first check which of the variables and settings to choose:
        if nbr==1:
            time_ch_mode=self.settings.time_ch_mode1
            ax=self.axT1
        else:
            time_ch_mode=self.settings.time_ch_mode2
            ax=self.axT2

        # no prepare plotting
        if time_ch_mode != "None":

            if ":" in  time_ch_mode:
                channel=time_ch_mode.split(":")[0]
                mode=time_ch_mode.split(":")[1]
            else:
                channel=""
                mode=time_ch_mode

            #print(time_ch_mode, channel, mode)

            if "Triggerrate" in time_ch_mode:
                values = self.daq.rate
                title = time_ch_mode
                yLabel="Rate"
                yUnit = "Hz"
            elif "Std" in mode:
                values = self.daq.std[channel]
                title = "Standard deviation Ch. %s" % channel
                yUnit = "V"
                yLabel="Std. Deviation"
            elif "Average" in mode:
                values = self.daq.avg[channel]
                title = "Average Ch. %s" % channel
                yUnit = "V"
                yLabel="Average"
            # HWT add custom instructions for hardware
            elif "Dummy" in mode:
                values = self.hw.dummyVals
                title = "External Dummy"
                yUnit = "V"
                yLabel="Value"
            elif "Lightsensor" in mode:
                values = self.hw.lightVals
                title = "Lightsensor"
                yUnit = "V"
                yLabel="Value"
            elif "Humidity" in mode:
                values = self.hw.humVals
                title = "Humidity"
                yUnit = "%"
                yLabel="Percentage"
            elif "HumTemp" in mode:
                values = self.hw.humTempVals
                title = "HumTemp"
                yUnit = "°C"
                yLabel="Temperature"
            elif "HV" in mode:
                values= np.array(self.hw.hvVals)
                #print(values)
                # get the second column in a 2d numpy array named values
                values = values[:,1]
                #print(values)
                title = "HV"
                yUnit = "V"
                yLabel="Voltage"
            elif "Temperature" in mode:
                values_temp= np.array(self.hw.tempVals)
                # get all temperatures separately and make a legend added to the title
                values=[]
                title = "Temps: "
                if len(values_temp)>0:
                    for i in range(len(values_temp[0])):
                        values.append(values_temp[:,i])
                        title+="%s (%s); " % ("Sensor "+str(i), linestyles[i]) 
                yUnit = "°C"
                yLabel="Temperature"

            # select correct x values for the time
            if "HW" == channel:
                time=(np.array(self.hw.time) - self.daq.startthread) / 60 # from unix time to minutes since measurement started
                # self.daq.startthread is common start point!
            else:
                time=(np.array(self.daq.time) - self.daq.startthread) / 60 # from unix time to minutes since measurement started

            # strange mismatch of len(time) and len(values) only happens few times
            # handle it like this for now, but need to investigate - TOD()
            if len(time)!=len(values) and abs(len(time)-len(values))<2 and not "Temperature" in mode:
                #self.log.warning("Lengths of arrays do not match! %s %s %d %d"%( channel, mode, len(time), len(values)))
                time=list(time)
                values=list(values)
                if len(time)>len(values):
                    time=time[:-1]
                else:
                    values=values[:-1]
                #print("CORRECTED:", len(time), len(values))
            else:

              #print("DEBUG", type(values), type(time))
              #print("DEBUG", type(values[0]))
              if len(values)>0 and type(values[0])!=float and type(values[0])!=np.float64 and len(time)!=len(values[0]) and abs(len(time)-len(values[0]))<2:
                self.log.warning("Lengths of arrays do not match! %s %s %d %d"%( channel, mode, len(time), len(values[0])))
                time=list(time)
                values0=list(values[0])
                if len(time)>len(values0):
                    time=time[:-1]
                else:
                    for i in range(len(values)):
                        values[i]=values[i][:-1]
                #print("CORRECTED:", len(time), len(values[0]))
            #print(values)
            if not "Temperature" in mode:
                ax.plot(time, values, "-o", 
                        linewidth=1, markersize=1, 
                        alpha=0.7, color="C%d"%nbr)
            else:
                #print(time, values, channel, mode)
                for i in range(len(values)):
                    ax.plot(time, values[i], marker="o", 
                        linewidth=1, markersize=1, 
                        alpha=0.7, color="C%d"%nbr, linestyle=linestyles[i], label="Sensor "+str(i))

            #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))

            if nbr==1:
                ax.set_title(title, fontsize=8, weight="bold",loc="left", pad=3,)
            else:
                ax.text(0.01, 0.99, title, 
                        transform=ax.transAxes, 
                        horizontalalignment="left",
                        verticalalignment="top",
                        fontsize=8, 
                        weight="bold",)
            ax.set_ylabel("%s / %s" % (yLabel,yUnit))
            ax.set_xlabel("Time / min") 
        else: # nothing chosen
            if nbr==1:
                ax.set_title("Time development: No data chosen", fontsize=8, weight="bold",loc="left", pad=3,)
            else:
                ax.text(0.01, 0.99, "Time development: No data chosen", 
                        transform=ax.transAxes, 
                        horizontalalignment="left",
                        verticalalignment="top",
                        fontsize=8, 
                        weight="bold",)
            ax.set_ylabel("Value ")
            ax.set_xlabel("Time / min") 


    def plotHistogram(self):
        if self.settings.hist_ch_mode != "None":

            if self.settings.hist_ch_mode != "Triggerrate":
                channel=self.settings.hist_ch_mode.split(":")[0]
                mode=self.settings.hist_ch_mode.split(":")[1]
            else:
                channel=""
                mode="Triggerrate"

            if "Max" in mode:
                values = self.daq.max_amp[channel]
            elif "Min" in mode:
                values = self.daq.min_amp[channel]
            elif "Std" in mode:
                values = self.daq.std[channel]
            elif "Average" in mode:
                values = self.daq.avg[channel]
            elif "Area" in mode:
                values = self.daq.area[channel]
            elif "Triggerrate" in mode:
                values = self.daq.rate
                

            if len(values) > 0:
                values=np.array(values)
                values= np.hstack(values)

                if not mode in ["Triggerrate"]:
                    # choose units
                    xUnit="V"
                    vRange=self.settings.voltagerange[channel]
                    offSet=self.settings.offset[channel]/1000
                    triggervoltage=self.settings.triggervoltage/1000
                    if vRange < 1: # for convenience change to mV 
                        xUnit="mV"
                        vRange*=1000
                        offSet*=1000
                        triggervoltage*=1000
                        values*=1000
                else:
                    xUnit = "Hz"
                xUnit2=""
                if "Area" in mode: 
                    xUnit2+="* sec"
                    # adjust unit so that you get more reasonable values
                    if np.max(values)<0:
                        values*=1000
                        xUnit2+="* ms"
                    if np.max(values)<0:
                        values*=1000
                        xUnit2+="* μs"
                    if np.max(values)<0:
                        values*=1000
                        xUnit2+="* ns"

                if mode in ["Max.Amplitude", "Min.Amplitude"]:
                    # prepare histogram
                    xBorders=(-vRange-offSet,vRange-offSet) # correct ylim for offset
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
                self.axH.bar(binedges[:-1], histvals, binwidth*0.9, facecolor="C0", edgecolor="C0")

                if xBorders[0]!=xBorders[1]: # only issue at the first round
                    self.axH.set_xlim(xBorders[0],xBorders[1])
                #self.axH.set_ylim(1.e-1, max(histvals)+max(histvals)*0.1)

                # trigger
                if self.settings.triggerchannel == channel:
                    self.axH.axvline(triggervoltage, color="red", linewidth=1., label="Trigger") 
                    self.axH.legend(bbox_to_anchor=(0.65, 0.97, 0.35, 0.10), 
                                ncol=1, mode="expand", frameon=False, 
                                borderaxespad=0.,prop={'size': 6})



                try: self.axH.set_yscale("log")
                except: pass

                if channel!="":
                    self.axH.set_title("Hist. %s Ch. %s" % (mode,channel), fontsize=8, loc="left", pad=3, weight="bold")
                else:
                    self.axH.set_title("Hist. of Rate", fontsize=8, loc="left", pad=3, weight="bold")

                self.axH.set_ylabel("Counts")
                self.axH.set_xlabel("%s / %s %s" % (mode,xUnit, xUnit2))

            else:
                self.log.warn("No data in array")

        else: # no data to plot
            self.axH.set_title("Histogram: no channel chosen", fontsize=8, weight="bold",loc="left", pad=3,)
            self.axH.set_ylabel("Counts")
            self.axH.set_xlabel(r"Amplitude")


    def plotWaveform(self):

        # todo separate waveform and fft, because code has little overlap
        
        if self.settings.raw_data_ch != "None":
            channel=self.settings.raw_data_ch.split(":")[0]
            mode=self.settings.raw_data_ch.split(":")[1]

            if "waveform" in mode:
                title="Waveform"
                ylabel="Amplitude"
                values=self.daq.lastWfm[channel]
                # x-Axis / waveform duration
                xUnit = "sec"
                xLabel="Time"
                wfmTime = np.arange(0, len(values[0]), 1) * self.daq.interval
                if self.daq.interval < 1.e6: 
                    wfmTime *= 1.e9
                    xUnit = "ns"
                elif self.daq.interval < 1.e3:
                    wfmTime *= 1.e6
                    xUnit = "μs"
                elif self.daq.interval < 1:
                    wfmTime *= 1.e3
                    xUnit = "ms"

                xvalues=wfmTime

                # choose units
                yUnit="V"
                vRange=self.settings.voltagerange[channel]
                offSet=self.settings.offset[channel]/1000
                triggervoltage=self.settings.triggervoltage/1000
                if vRange < 1: # for convenience change to mV 
                    yUnit="mV"
                    vRange*=1000
                    offSet*=1000
                    triggervoltage*=1000
                    
            else:
                title="FFT"
                ylabel="Amplitude"
                values=np.array(self.daq.fft[channel][-1])
                xUnit = "Hz"
                xLabel="Frequency"
                yUnit="V"
                xvalues=self.daq.xfreq

            # choose which waveforms to plot from the last round of waveforms
            fakearray=np.arange(0,len(values), 1)
            index=np.random.choice(fakearray, size=min(self.settings.raw_data_nbr, len(values)), replace=False)
            vals=values[index]
            #print(len(values), np.min(values), np.max(values))
            #print(len(vals), np.min(vals), np.max(vals))
            if yUnit=="mV": vals*=1000

            

            # plot
            for wfm in vals:
                #print(wfmTime)
                #print(wfm)
                self.axW.plot(xvalues, wfm, 
                                linestyle="-", linewidth=1.0, alpha=0.5)

            # trigger
            if self.settings.triggerchannel == channel and title!="FFT":
                self.axW.axhline(triggervoltage, color="red", linewidth=1., label="Trigger") 
                self.axW.legend(bbox_to_anchor=(0.65, 0.97, 0.35, 0.10), 
                            ncol=1, mode="expand", frameon=False, 
                            borderaxespad=0.,prop={'size': 6})

            # label
            self.axW.set_title("%s Ch. %s" % (title,channel), 
                                fontsize=8, loc="left", pad=3, weight="bold")
            
            self.axW.set_xlabel("%s / %s" % (xLabel,xUnit))
            self.axW.set_ylabel("%s / %s" % (ylabel,yUnit))

            # keep lims constant
            if "waveform" in mode:
                yBorders=(-vRange-offSet,vRange-offSet) # correct ylim for offset
                self.axW.set_ylim(tuple(yBorders))
                self.axW.set_xlim(0, wfmTime[-1])
            else:
                try: self.axW.set_xscale("log")
                except: pass

            
        else: # no data to plot
            self.axW.set_title("Waveforms: No data chosen", fontsize=8, weight="bold",loc="left", pad=3,)
            self.axW.set_xlabel("Time")
            self.axW.set_ylabel("Amplitude")
    # -------------------------------------------------------------------------


