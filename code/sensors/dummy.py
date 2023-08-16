'''
Dummy of a sensor which can be read out by serial communication
'''

import serial, sys, glob, traceback
import numpy as np # for dummy values

TAG="HWD: " # unique tag for this hardware for the log entries

class Sensor:

    # -----------------------------------------------------------------------------
    # do work

    def readDevice(self):
        # get the data
        if not self.online:
            voltage=np.random.random()
        return voltage

    # -----------------------------------------------------------------------------
    # Initialize and find ports 
    def __init__(self, log, port = None):
        '''
        - test port given to function
        - list all possible ports
        - test the ports
        - initilaizes the working port
        '''

        self.port=port
        self.log=log
        self.log.info(TAG+"Port given: %s"%port)

        self.findPort(port)

    def findPort(self, port):
        if port != None:
            test=self.test(port)
            if test == False:
                self.port=None
    
        if self.port==None:

            # find a port 
            self.log.info(TAG+"No port given. Try to find port for platform "+sys.platform)
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
                # not tested!
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                # access to serial ports is given by
                # sudo usermod -a -G dialout USERNAME
                ports = glob.glob('/dev/ttyUSB*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
                # not tested!
            else:
                raise EnvironmentError('Unsupported platform')

            #print "Test ports", ports
            for port in ports:
                if "Bluetooth" in port: continue
                if "BLTH" in port: continue

                test=self.test(port)
                if test==True:
                    self.port=port
                    break
                    #print "Port found", port
                    
        if self.port==None:
            self.log.error(TAG+"No port found. Measurement switched off!")
            self.online=False
        else:
            self.log.info(TAG+"Using device at port %s for photodiode" % self.port)
            self.online=True

    def initialise(self,):
        # start connection to device, used by test()
        self.device=serial.Serial(str(self.port), 9600,timeout=2)


    def test(self, port):
        # tests a port and initializes it => stop once port found, otherwise wrong device will get initialized
        try:
            self.log.info(TAG+"Test Port %s for photodiode"% port)
            self.port=port
            self.initialise()
            if self.device==None:
                raise Exception(TAG+"No device initialised!")
            voltage=self.readDevice()
            self.device.close()
            return True
        except Exception as e:
            self.port=None
            try: self.device.close() 
            except: pass
            self.device=None
            self.log.info(TAG+"Error testing port %s: %s" %( port, e))
            return False


# -----------------------------------------------------------------------------
# test

if __name__ == "__main__":
    '''
    make it possible to run/test independently 
    '''

    # make a dummy log class
    class log:
        def __init__(self):
            pass
        def error(self, str):
            print("ERROR: "+str)
        def debug(self,str):
            print("DEBUG: "+str)
        def info(self,str):
            print("INFO: "+str)

    log=log()
    t=Sensor(log)
    print (t.readDevice())
