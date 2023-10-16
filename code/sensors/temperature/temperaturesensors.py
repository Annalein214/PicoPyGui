'''
Temperature sensors driven with an arduino
'''

import serial, sys, glob, traceback, time

TAG = "TS"

class TempSensors:

    def readDevice(self, debug=False, test=False):
        # get the data
        #self.initialise() # seems to be no issue if this is done repeatedly
        if self.device==None:
            self.online=False
            return False

        # you need to do this twice in order to get a result at the first time
        i=0
        repeat=True
        while repeat:
            
            self.device.write(b'1')
            raw = self.device.readline()
            if debug: print(i, raw, test, repeat)
            string = str(raw, 'utf-8').strip()
            if debug: print(string)
            if "Found " in string: 
                    repeat = True
            else: 
                repeat = False
                i+=1
            # stop loop
            i+=1
            if i>5: 
                if debug: print("break because of i")
                break
            if "Temperature" in string:
                if debug: print("break because temperature found")
                break
            #if not test: 
            #    print("break because of test")
            #    repeat=False
            if not repeat: 
                if debug: print("break because of repeat")
                repeat=False
            

        # --- Standard output: ---
        # --- Setup ---
        #Locating devices...Found 1 devices.
        #Found device 0 with addreLocating devices...Found 1 devices.
        #Found device 0 with address: 283023E70D00009A
        #  --- send "1" per serial and you get:
        #Device: 0, Temperature: 25.87;Device: 0, Temperature: 25.87;
        
        string = str(raw, 'utf-8').strip()

        #string = string.replace("\\r", "").replace("\\n", "").replace("b'", "").replace("'", "")
        #self.log.debug(TAG+": Raw3: %s"% string)

        if not "Temperature" in str(string):
            raise RuntimeError(TAG+": Value not from Temperature sensor: %s" % raw)
        devices=string.split(";")
        temperatures=[]
        for dev in devices:
            if dev != "":
                temperatures.append(dev.split(":")[-1])

        #self.log.debug(TAG+": Voltage [mV]: %f"% voltage)
        #self.device.close()
        return temperatures

    def initialise(self,):
        # start connection to device, used by test()
        self.device=serial.Serial(str(self.port), 9600,timeout=2, write_timeout = 1)

    def test(self, port, debug=False):
        # tests a port and initializes it => stop once port found, otherwise wrong device will get initialized
        try:
            self.log.info(TAG+": Test Port %s for temperature sensor"% port)
            self.port=port
            self.initialise()
            if self.device==None:
                raise Exception("No device initialised!")
            voltage=self.readDevice(debug, True)
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


    def __init__(self, log,port=None, debug=False):
        '''
        - test port given to function
        - list all possible ports
        - test the ports
        - initilaizes the working port
        '''
        self.port=port
        self.log=log
        self.log.info(TAG+": Port given: %s"%port)

        
        self.findPort(port, debug)
        
    
    def findPort(self, port, debug=False):
        if port != None:
            test=self.test(port, debug)
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

                test=self.test(port, debug)
                if test==True:
                    self.port=port
                    break
                    #print "Port found", port
                    
        if self.port==None:
            self.log.error(TAG+": No port found. Measurement switched off!")
            self.online=False
        else:
            self.log.warning(TAG+": Using device at port %s for temperature" % self.port)
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
    t=TempSensors(log, debug=True)
    while t.online:
        print (t.readDevice())
        print (t.readDevice())
        print (t.readDevice())
        sleep(1)




