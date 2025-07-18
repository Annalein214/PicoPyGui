'''
HV driven and read out with an arduino

not yet adjusted for 2 HV devices. You need to choose manually here
'''

DEVICE=2 # 1 for HV, 2 for HV2

import serial, sys, glob, traceback

TAG = "HV"

class HV:

    def readDevice(self):
        # get the data
        #self.initialise() # seems to be no issue if this is done repeatedly
        if self.device==None:
            return False
        # Note: cannot try because I rely on this failing for wrong ports
            
        self.device.write(b'%d'%DEVICE)
        raw = self.device.readline()
        self.device.write(b'%d'%DEVICE)
        raw = self.device.readline()
        string = str(raw, 'utf-8').strip()

        if not "Vmon" in str(string):
            raise RuntimeError(TAG+": Value not from HV: %s" % raw)
        
        values=string.split(" ")
        monVoltage=float(values[1]) # mV
        HVVoltage=float(values[4]) # mV
        HVError=float(values[7]) # mV

        #self.log.debug(TAG+": Voltage [mV]: %f"% voltage)
        #self.device.close()
        return monVoltage, HVVoltage, HVError
       
       
    def readSwitch(self, nbr):
    	# 3 for micro
    	# 4 for macro
    
        if self.device==None:
            return False
        
        # note: here only one attempt is allowed!
        self.device.write(b'%d'%nbr)
        raw = self.device.readline()
        
        string = str(raw, 'utf-8').strip()  
        if string=="":
            self.device.write(b'%d'%nbr)
            raw = self.device.readline()
        
            string = str(raw, 'utf-8').strip()  
          
        if not "SW-" in str(string):
            raise RuntimeError(TAG+": Value not from Switch: %s" % raw)
            
        values=string.replace(".","").split(":")[-1]
        vals = []
        for v in vals:
            try:
               vv=float(v)
               vals.append(vv)
            except: 
                print("not converting:", v)
                #pass
        return vals

    def initialise(self,):
        # start connection to device, used by test()
        self.device=serial.Serial(str(self.port), 115200,timeout=3)

    def test(self, port):
        # tests a port and initializes it => stop once port found, otherwise wrong device will get initialized
        try:
            self.log.info(TAG+": Test Port %s for device"% port)
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
                #test=self.test(port)
                if test==True:
                    self.port=port
                    break
                    #print "Port found", port
                    
        if self.port==None:
            self.log.error(TAG+": No port found. Measurement switched off!")
            self.online=False
        else:
            self.log.warning(TAG+": Using device at port %s for HV" % self.port)
            self.initialise()
            self.online=True


    def close(self):
        self.device.close()


if __name__ == "__main__":

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
    t=HV(log)
    #print (t.readDevice())
    print(t.readSwitch(3))
    print(t.readSwitch(4))




