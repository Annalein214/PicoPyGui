'''
Environmental sensors driven with an arduino

Output of arduino:
[BOOTUP]
Found 4 devices.
Found device 0 with address: 283023E70D00009A
Found device 1 with address: 28E1F2E70D0000FA
Found device 2 with address: 285140E70D000031
Found device 3 with address: 2817AFE60D0000CC
[PRESS 1]
Diode 127.08
[PRESS 2]
Temperatures: 283023E70D00009A 26.37; 28E1F2E70D0000FA 25.69; 285140E70D000031 25.94; 2817AFE60D0000CC 26.19; 
[PRESS 3]
Humidity 48.00; Temperature 26.80

'''

import serial, sys, glob, traceback, time

TAG = "ES"

class EnvSensors:

    def readDevice(self, debug=False):
        for i in range(10):
            raw = self.device.readline()
            if debug: print(i, raw)
            if raw == b'':
                return True
        return False
    
    def readHumidity(self, debug=False):
        # get the data of diode
        # also accounts for bootup stuff

        if self.device==None:
            self.online=False
            return False

            
        self.device.write(b'3')
        raw = self.device.readline()
        if debug: print(raw)
        string = str(raw, 'utf-8').strip()

        if not "Humidity" in str(string):
            raise RuntimeError(TAG+": Value not from Humidity sensor: %s" % raw)
        devices=string.split(";")
        humidity=float(devices[0].split(" ")[-1])
        if debug: print("Humidity", humidity)
        humTemp=float(devices[1].split(" ")[-1])
        if debug: print("Humidity Temperature", humTemp)
        return humidity,humTemp

    def readDiode(self, debug=False):
        # get the data of diode
        # also accounts for bootup stuff

        if self.device==None:
            self.online=False
            return False

            
        self.device.write(b'1')
        raw = self.device.readline()
        if debug: print(raw)
        string = str(raw, 'utf-8').strip()

        if not "Diode" in str(string):
            raise RuntimeError(TAG+": Value not from Diode sensor: %s" % raw)
        devices=string.split(" ")
        diode=float(string.split(" ")[-1])
        if debug: print("Diode", diode)
        #self.log.debug(TAG+": Voltage [mV]: %f"% voltage)
        #self.device.close()
        return diode

    def readTemperature(self, debug=False, test=False):
        # get the data of temperature

        if self.device==None:
            self.online=False
            return False

        # you need to do this twice in order to get a result at the first time
        
        
        self.device.write(b'2')
        raw = self.device.readline()
        if debug: print(1,raw, test)        
        string = str(raw, 'utf-8').strip()

        if not "Temperatures" in str(string):
            raise RuntimeError(TAG+": Value not from Temperature sensors: %s" % raw)
        # Temperatures: 283023E70D00009A 26.37; 28E1F2E70D0000FA 25.69; 
        #               285140E70D000031 25.94; 2817AFE60D0000CC 26.19; 

        temperatures=[]
        devices=string.strip().split(";")
        for dev in devices:
            if dev!="":
                if debug: print(dev)
                temp=dev.split(" ")[-1]
                temp=float(temp)
                if debug: print("temp", temp)
                temperatures.append(temp)
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
            result=self.readDevice(debug)
            if result==False:
                raise Exception("Device is talking too much!")
            diodeValue=self.readDiode(debug)
            self.device.close()
            return True
        except Exception as e:
            if debug:
                e2=str(traceback.print_exc())
                print(e2)
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
        self.readDevice(debug)
        
    
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
            self.log.warning(TAG+": Using device at port %s for temperature array, humidity + temperature and photodiode" % self.port)
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
    debug=False
    t=EnvSensors(log, debug=debug)
    #exit()
    while t.online:
        print (t.readDiode(debug=debug))
        print (t.readTemperature(debug=debug))
        sleep(1)




