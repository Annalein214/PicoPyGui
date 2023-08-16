'''
You have to execute this script with python 3 to start the application
'''

# general libraries
import faulthandler
import sys, os
from optparse import OptionParser
# custom
from code.helpers import green, nc, red, yellow, lila, pink, blue
from code.log import log
from code.settings import Settings
from code.hplot2 import hourlyPlot

# load gui libraries
from PyQt5 import QtWidgets
MyGui=QtWidgets
# custom
from code.gui.window import ApplicationWindow
from code.gui.graph import graph

# load hardware
from code.daq import daq
from code.sensors.main import external


# -----------------------------------------------------------------------------
def main(opts, log):
    '''
    function to boot up the program
    '''

    connect=bool(~opts.test)
    if connect:
        # start external hardware
        pass
    else:
        # set references to None
        pass

    # load settings from settings.cfg and save them into the daq class
    settings=Settings(log) 

    # initialize picoscope class (handles connect variable itself)
    # connect all external hardware with picoscope
    scope=daq(log, opts, settings) 
    # this function might set opts.test to true if no device is found
    # this function later also gets a reference to hw

    # initialize graph class (stores some important variables which are also used by GUI)
    graf=graph(log, opts, settings)

    # initialize external hardware class
    hw = external(log, opts, settings, scope)

    # initialize class for plotting the data automatically
    hplot = hourlyPlot(log)

    # start GUI or terminal
    if opts.konsole==False:
        app = MyGui.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)

        # Set up the GUI part
        gui=ApplicationWindow(scope, 
                                log, 
                                opts, 
                                settings,
                                graf,
                                hw,
                                hplot
                                )
        gui.show()
        log.debug("Window is set up")

        sys.exit(app.exec_())
        # here nothing is executed anymore
    elif opts.konsole==True:
        log.info("Starting in Konsole Mode. Directly starting data taking.")
        scope._threadIsStopped=False
        scope.startRapidMeasurement()
        scope.close()
        log.endLogging()

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    '''
    get the user input from command line and start up
    '''

    faulthandler.enable()

    # define and get program options
    usage="""

            %prog [options]

            This program is dedicated for use with PicoScope  6404B or 3406DMSO

            -d : directory to store data. All Files will be stored in ./data if not otherwise set.
            -t : don't use an actual picoscope but fakedata for testing, does not work for all functions!
            -k : use only terminal, do not start GUI

            """

    parser = OptionParser(usage=usage)
    parser.add_option("-t","--test", action="store_true",dest="test", help="Do not connect to device.", default=False)
    parser.add_option("-d","--dir",dest="directory", help="Directory to store data", default=False)
    parser.add_option("-k", "--konsole", action="store_true", dest="konsole", help="Start from terminal without GUI", default=False)
    opts, args = parser.parse_args()

    # deal with program options
    if not opts.directory:
        opts.directory="./data/" # also works on windows
    if opts.directory[-1]!="/":
        opts.directory+="/"
    os.makedirs(opts.directory, exist_ok=True)

    # start logging, set logging level
    log=log(save=True, level="debug", directory=opts.directory)
    log.debug("Arguments:"+" ".join(sys.argv))

    # make it so!
    main(opts, log)













