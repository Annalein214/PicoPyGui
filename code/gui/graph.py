from __future__ import print_function
from __future__ import absolute_import

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


try:
    from PyQt4 import QtGui, QtCore
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    MyGui=QtGui
except ImportError as e:
    from PyQt5 import QtWidgets, QtCore
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    MyGui=QtWidgets
    
import random
from matplotlib.figure import Figure

import numpy as np
##########################################################################################


class plotWidget(FigureCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, parent, log, daq):

        self.log = log
        self.daq= daq

        dpi=100

        self.fig = Figure(dpi=dpi, facecolor='white')
        '''
        #self.ax1 = self.fig.add_subplot(221) # oben rechts
        #self.ax2 = self.fig.add_subplot(212) # unten
        #self.ax3 = self.fig.add_subplot(222) # oben links
        gs=gridspec.GridSpec(2, 4)
        self.ax1 = self.fig.add_subplot(gs[0,:2])# oben rechts
        self.ax3 = self.fig.add_subplot(gs[0,2:])# oben links
        self.ax2 = self.fig.add_subplot(gs[1,:-1])# oben links
        
        self.ax4 = self.ax2.twinx()
        self.ax5 = self.ax3.twinx()
        self.ax4.yaxis.set_label_position("right") # strange bug that the label is on the left side otherwise
        self.ax5.yaxis.set_label_position("right")

        self.fig.subplots_adjust(left=0.13,
                                 right=0.86,
                                 bottom=0.1,
                                 top=0.97,
                                 wspace=0.9,
                                 hspace=0.4,
                                 )

        self.layout()
        
        # test text at start
        text="Temperatures:\n"+r" $-^{\circ} \,\,\,-^{\circ}$"+"\n"+"$-^{\circ} \,\,\, -^{\circ}$"+"\n\n"
        text+="Room light: - mV"+"\n\n"
        text+="Freq/Int: \n"+" - Hz "+"\n"+" - ns \n\n"
        text+="Rate: " + " - Hz \n\n"
        text+="Ch B: " + " - V \n\n"
        text+="Ch C:\n - mV\n\n"
        self.ax2.text(1.25,1., 
                         text, 
                         transform=self.ax4.transAxes,
                         horizontalalignment='left',
                         verticalalignment='top',
                         fontsize=7)
        '''
        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   MyGui.QSizePolicy.Expanding,
                                   MyGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        '''
        # counter of updates
        self.i=0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(self.daq.loopduration)
        '''
##########################################################################################

    def layout(self):
        # this has to be done for every re-draw

        # common for all axes
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.ax3.grid(True)

        # specific for axes

        # labels
        if not self.daq.showArea:
            self.ax1.set_xlabel(r"Amplitude / mV")
        else:
            self.ax1.set_xlabel(r"Charge / pC")
        self.ax1.set_ylabel("Counts")
        self.ax2.set_xlabel(r"Time / s")
        self.ax2.set_ylabel("Rate / 1/s", color="blue")
        self.ax3.set_xlabel(r"Time / ns")
        self.ax5.set_ylabel("Amplitude / mV")
        self.ax4.set_ylabel("Ch B / V", color="green")
        self.ax4.yaxis.set_label_position("right") # repetition needed so that label keeps on the right, strange bug with new matplotlib version
        self.ax5.yaxis.set_label_position("right")
        
        xloc = matplotlib.pyplot.MaxNLocator(self.daq.xticks)
        self.ax1.xaxis.set_major_locator(xloc)

    def gain(self,x):
        # PMT 6 by Pieper
       return 4.3820810269624345e-9*x**(0.50531132059975381*10)

##########################################################################################
    def update_figure(self):
        negativePulse=True

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.ax5.clear()

        
        if self.daq.isRunning() and len(self.daq.rate)>0:

            self.i+=1

            try:
                # this fails the first time, but then it works
                if self.i%2==0:
                    self.log.debug("Set timer interval to %f seconds"%(self.daq.loopduration/1000)) # todo info in window
                    self.timer.setInterval(int(self.daq.loopduration)) # adjust interval dynamically so that it stays at a useful level
                    #argument is changed to be int by Megumi.C
            except AttributeError as e:
                self.log.debug( "WARNING: plotWidget has no timer")
                
            # ----------------
            # update timelike data here (otherwise problems might occur 
            # when the array changes while this code executes
            time=np.array(self.daq.blocktimes)-self.daq.blocktimes[0]
            
            # noise ###############################################################
            
            # put this before channel A to have it drawn in background
            if self.daq.channelEnabled["D"]:
                
                try:
                    noiseWfm=self.daq.savedNoise
                    i=0
                    for waveform in noiseWfm:
                            wfmtime=(np.arange(0,len(waveform),1))* 1./self.daq.sampleRate*1e9
                            self.ax5.plot(wfmtime, np.array(waveform)*1000, "-",
                                          linewidth=1,
                                          alpha=0.3,
                                          color="gray"
                                         )
                            i+=1
                            if i> self.daq.nowaveforms:
                                break
                    self.ax5.set_xlim(0,np.max(wfmtime))
                    self.ax5.set_ylim(-self.daq.voltagerange["D"]*1000-(self.daq.offset["D"]*1000), self.daq.voltagerange["D"]*1000-(self.daq.offset["D"]*1000))
                except AttributeError as e:
                    #self.log.error(str(e))
                    pass
            # HV ###############################################################
            
            def monitorToHV(monitor):
                return 1000*monitor # switch off calculation of high voltage to use this channel more generic, just convert to volts from millivolts
                #return 3000.*monitor/5.

            
            if self.daq.channelEnabled["B"]:
              channelB=self.daq.channelB
              if type(channelB)==list or type(channelB)==np.ndarray:
                timeB=time[:len(channelB)]
                channelB=channelB[:len(timeB)] 
                #cB=channelB
                cB=[]
                for capture in channelB:
                    cB.append(np.mean(capture))
                #print ("HV",np.mean(cB))
                channelB=np.array(cB)
                channelB=monitorToHV(channelB)
                self.ax4.plot(timeB, channelB, "-o", color="green", linewidth=1, markersize=1, alpha=0.7)
                from matplotlib.ticker import FormatStrFormatter
                #self.ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f')) # make more generic
                #self.ax4.set_ylim(-self.daq.voltagerange["B"]-self.daq.offset["B"], self.daq.voltagerange["B"]-self.daq.offset["B"])
                meanHV=np.mean(channelB)
            else: 
                meanHV=1096.5 # 1.840 monitor voltage
                meanHV=0 # use the channel more generic
            
            
            # PMT ###############################################################
            if self.daq.channelEnabled["A"]: 
                rate=self.daq.rate
                savedCaptures=self.daq.savedCaptures
                #print(len(savedCaptures), "savedCaptures")
                if not self.daq.showArea: #-------- Amplitude ------------------------
                    if negativePulse:
                        borders=(-self.daq.voltagerange["A"]*1000+self.daq.offset["A"]*1000,
                             self.daq.voltagerange["A"]*1000+self.daq.offset["A"]*1000) # change from positive to negative offset for negative / positive pulses
                    else:
                        borders=(-self.daq.voltagerange["A"]*1000-self.daq.offset["A"]*1000,
                             self.daq.voltagerange["A"]*1000-self.daq.offset["A"]*1000) # change from positive to negative offset for negative / positive pulses
                    bins=50 # twice the resolution
                    binning=[ i*float((borders[1]-borders[0]))/bins+borders[0] for i in range(bins+1)]
                    binwidth=binning[1]-binning[0]

                    # amplitude
                    #self.ax1.axvline(-self.daq.triggervoltage*1000, color="k", linewidth=1.) # TODO nur wenn trigger auf channel A
                    amplitudes = np.array(self.daq.amplitudes)
                    if len(amplitudes)>0:
                        amplitudes= np.hstack(amplitudes)
                        if negativePulse:
                            amplitudes= -np.array(amplitudes)*1000
                        else:
                            amplitudes= np.array(amplitudes)*1000 # -Volt -> +mVolt # change from negative to positive for negative / positive pulses
                        histvals, binedges = np.histogram(np.array(amplitudes), bins=binning)
                        self.ax1.bar(binedges[:-1], histvals, binwidth*0.9, facecolor="b", edgecolor="b")
                        self.ax1.set_xlim(borders[0],borders[1])
                        self.ax1.set_ylim(1.e-1, max(histvals)+max(histvals)*0.1)
                        try: self.ax1.set_yscale("log", nonpositive="clip")
                        except: pass
                        # TODO error bars

                else: #-------- Area ------------------------
                    
                    

                    areas = np.array(self.daq.areas)
                    #print (areas)
                    if len(areas)>0:
                        areas= np.hstack(areas)
                        #print("Gain:",self.gain(meanHV))# 10073680.8734
                        #gain=1.e7 # generic, can be corrected more easily but gives nicer numbers -> TODO change to charge in pC instead
                        #areas=np.float64(areas) /50./(1.602*1e-19)/gain #/self.gain(meanHV) # change from negative to positive for negative / positive pulses
                        areas=np.float64(areas)/50*1.e12 # -> convert to charge in pC
                        #print(areas)
                        if negativePulse:
                            areas=-areas
                        
                        #print ("Areas graph",np.min(areas), np.max(areas))
                        
                        # good for a first guess:
                        #borders=(0,np.max(areas)+np.max(areas)*0.1) 
                        borders=(-1,5)
                        # hard coded because it is hard to estimate a useful value from data, best option would be to correlate it with a known  which is hard if the PMT gain isn't known yet
                       
                        #borders=(-2e7,5e7) # pmt 1 for ampl PE
                        #borders=(-1e7,2e7) # pmt 6 for ampl PE
                        # borders=(-2e10,5e10) # pmt 6 for pure area
                        #borders=(-1e-7, 5e-7)
                        bins=128 # twice the resolution
                        binning=[ i*float((borders[1]-borders[0]))/bins+borders[0] for i in range(bins+1)]
                        binwidth=binning[1]-binning[0]
                        
                        histvals, binedges = np.histogram(np.array(areas), bins=binning)
                        self.ax1.bar(binedges[:-1], histvals, binwidth*0.9, facecolor="b", edgecolor="b")
                        '''
                        self.ax1.set_xlim(borders[0],borders[1])
                        self.ax1.set_ylim(1.e-1, max(histvals)+max(histvals)*0.1)                        
                        '''
                        try: self.ax1.set_yscale("log", nonpositive="clip")
                        except: pass
                        
                        #for label in self.ax1.get_xticklabels()[::2]:
                        #    label.set_visible(False)
                        # TODO error bars
                        

                #--- rate -------------------------------------------

                ratetime=time[:len(rate)]
                rate=rate[:len(ratetime)]
                ##print (len(ratetime), len(rate))
                if len(rate)>0:
                    self.ax2.plot(ratetime, rate, "-o", color="blue", linewidth=1, markersize=1, alpha=0.7)
                    xlim1=0
                    xlim2=max(ratetime)+max(ratetime)*0.1
                    if xlim2 == xlim1:
                        xlim2=1 # avoid an annoying error on the first entry after bootup
                    self.ax2.set_xlim(0,xlim2)
                    self.ax2.set_ylim(min(rate)-min(rate)*0.1,max(rate)+max(rate)*0.1)

                #--- waveform -------------------------------------------
                self.ax3.axhline(self.daq.triggervoltage*1000, color="k", linewidth=1.)
                i=0
                for waveform in savedCaptures:
                        wfmtime=(np.arange(0,len(waveform),1))* 1./self.daq.sampleRate*1e9
                        #print("Sampling Rate %0.1e" % self.daq.sampleRate)
                        #print("Max wfmtime %d %d" % (np.max(wfmtime), len(wfmtime)))
                        self.ax3.plot(wfmtime, np.array(waveform)*1000, "-",
                                      linewidth=1,
                                      alpha=0.5
                                     )
                        i+=1
                        if i> self.daq.nowaveforms:
                            break
                self.ax3.set_ylim(-self.daq.voltagerange["A"]*1000-(self.daq.offset["A"]*1000), 
                                   self.daq.voltagerange["A"]*1000-(self.daq.offset["A"]*1000))
                self.ax3.set_xlim(0, np.max(wfmtime))
            
            

            # 4th Channel  ###############################################################
            #if self.daq.channelEnabled["C"]:
            #  channelC=self.daq.channelC
            #  if type(channelC)==list or type(channelC)==np.ndarray:
            #    timeC=time[:len(channelC)]
            #    channelC=channelC[:len(timeC)] 
            #    channelC=np.array(channelC)
                #self.ax4.plot(timeC, channelC, "-o", color="green", linewidth=1, markersize=1)
                #self.ax4.set_ylim(-self.daq.voltagerange["C"]+self.daq.offset["C"], self.daq.voltagerange["C"]+self.daq.offset["C"])


            # Text Info  ###############################################################

            # TODO area outside the graphs for the text info stuff
            if True:#try:
                text=""
                if self.daq.measureTemp and len(self.daq.temperatures)>0:

                    if len(self.daq.temperatures[-1])==5:
                        text+="Temperatures: \n"
                        # show ERR if sensor offline (values above 4000 celsius)
                        if self.daq.temperatures[-1][1]<50: text+=r"$%.1f^{\circ}$ " % self.daq.temperatures[-1][1]
                        else: text+="ERR "
                        if self.daq.temperatures[-1][2]<50: text+=r"$%.1f^{\circ}$ " % self.daq.temperatures[-1][2]
                        else: text+="ERR "
                        text+="\n"
                        if self.daq.temperatures[-1][3]<50: text+=r"$%.1f^{\circ}$ " % self.daq.temperatures[-1][3]
                        else: text+="ERR "
                        if self.daq.temperatures[-1][4]<50: text+=r"$%.1f^{\circ}$ " % self.daq.temperatures[-1][4]
                        else: text+="ERR "
                        text+="\n\n"
                    else:
                        self.log.error("Not all temperature sensors read out. One might be broken or you have to disconnect and connect the USB Hygrosens device! %s" % (str(self.daq.temperatures[-1])))
                        text+="Temperatures:\n"+r" $-^{\circ} \,\,\,-^{\circ}$"+\
                            "\n"+"$-^{\circ} \,\,\, -^{\circ}$"+"\n\n"
                else:
                    text+="Temperatures:\n"+r" $-^{\circ} \,\,\,-^{\circ}$"+\
                            "\n"+"$-^{\circ} \,\,\, -^{\circ}$"+"\n\n"


                if self.daq.measureLight and len(self.daq.lightsensor)>0:
                    text+="Room Light:\n"+"%.1f mV \n\n" % self.daq.lightsensor[-1][1]
                else:
                    text+="Room light: - mV"+"\n\n"

                
                text+="Freq/Int:\n"+\
                        r" %.1e Hz /" % (self.daq.sampleRate) + \
                        "\n"+ \
                        "%.1e ns" %(1./self.daq.sampleRate*1e9) +\
                        "\n\n"

                if len(rate)>0:
                    text+="Rate: " + " %d Hz \n\n" % (rate[-1])
                try:
                    if len(channelB)>0:
                        text+="Ch B: " + " %.1e V \n\n" % (channelB[-1]) # make more generic
                except: pass

                if self.daq.channelEnabled["C"] and len(self.daq.channelC)>0:
                        text+="Ch C:\n"+ \
                                r" %.1f mV" % (self.daq.channelC[-1]*1000) +\
                                "\n\n"
                else:
                        text+="Ch C:\n - mV\n\n"

                self.ax2.text(1.35,1., 
                                 text, 
                                 transform=self.ax4.transAxes,
                                 horizontalalignment='left',
                                 verticalalignment='top',
                                 fontsize=7)
            #except Exception as e:
            #    self.log.error(str(e))
            
            self.layout()
            self.draw()
        






