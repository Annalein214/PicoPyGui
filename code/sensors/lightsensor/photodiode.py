'''
Photodiode driven with an arduino
'''

import serial, sys, glob, traceback, time

TAG = "PD"

class Photodiode:

    def readDevice(self):
        # get the data
        #self.initialise() # seems to be no issue if this is done repeatedly
        if self.device==None:
            return False

        # you need to do this twice in order to get a result at the first time
        self.device.write(b'1')
        raw = self.device.readline()
        self.device.write(b'1')
        raw = self.device.readline()

        # the device gives a float value in millivoltage after the string "Diode "
        
        #raw=self.reader.readline()
        #self.log.debug(TAG+": Raw1: %s"% raw)
        string = str(raw, 'utf-8').strip()
        #self.log.debug(TAG+": Raw2: %s"% string)

        #string = string.replace("\\r", "").replace("\\n", "").replace("b'", "").replace("'", "")
        #self.log.debug(TAG+": Raw3: %s"% string)

        if not "Diode" in str(string):
            raise RuntimeError(TAG+": Value not from Diode: %s" % raw)
        voltage=float(string.split(" ")[1])

        #self.log.debug(TAG+": Voltage [mV]: %f"% voltage)
        #self.device.close()
        return voltage

    def readTemperature(self):
        # get the data
        #self.initialise() # seems to be no issue if this is done repeatedly
        if self.device==None:
            return False

        # you need to do this twice in order to get a result at the first time
        self.device.write(b'2')
        raw = self.device.readline()
        self.device.write(b'2')
        raw = self.device.readline()

        # the device gives a float value in millivoltage after the string "Diode "
        
        #raw=self.reader.readline()
        #self.log.debug(TAG+": Raw1: %s"% raw)
        string = str(raw, 'utf-8').strip()
        #self.log.debug(TAG+": Raw2: %s"% string)

        #string = string.replace("\\r", "").replace("\\n", "").replace("b'", "").replace("'", "")
        #self.log.debug(TAG+": Raw3: %s"% string)

        if not "Temperature" in str(string):
            raise RuntimeError(TAG+": Value not from DiodeTemperature: %s" % raw)
        voltage=float(string.split(" ")[1])

        #self.log.debug(TAG+": Voltage [mV]: %f"% voltage)
        #self.device.close()
        return voltage

    def initialise(self,):
        # start connection to device, used by test()
        self.device=serial.Serial(str(self.port), 9600,timeout=2, write_timeout = 1)

    def test(self, port):
        # tests a port and initializes it => stop once port found, otherwise wrong device will get initialized
        try:
            self.log.info(TAG+": Test Port %s for photodiode"% port)
            self.port=port
            self.initialise()
            if self.device==None:
                raise Exception("No device initialised!")
            voltage=self.readDevice()
            self.device.close()
            return True
        except Exception as e:
            #e2=str(traceback.print_exc())
            #print(e2)
            self.port=None
            try: self.device.close() 
            except: pass
            self.device=None
            self.log.info(TAG+": Error testing port %s: %s" %( port, e))
            return False


    def __init__(self, log,port=None):
        '''
        - test port given to function
        - list all possible ports
        - test the ports
        - initilaizes the working port
        '''
        self.port=port
        self.log=log
        self.log.info(TAG+": Port given: %s"%port)

        

        self.findPort(port)
        
    
    def findPort(self, port):
        if port != None:
            test=self.test(port)
            if test == False:
                self.port=None

        if self.port==None:

            # find a port 
            self.log.info(TAG+": No port given. Try to find port for platform "+sys.platform)
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
            self.log.error(TAG+": No port found. Measurement switched off!")
            self.online=False
        else:
            self.log.warning(TAG+": Using device at port %s for photodiode" % self.port)
            self.initialise()
            self.online=True


    def close(self):
        self.device.close()


if __name__ == "__main__":
    from time import sleep

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
        def warning(self,str):
            print("WARN: "+str)
    log=log()
    t=Photodiode(log)
    while True:
        print ("Diode value [V]", t.readDevice())
        print ("Temperature value [C]",t.readTemperature())
        sleep(1)




