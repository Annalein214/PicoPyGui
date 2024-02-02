if 0:
    from code.picoscope.picoscope3000 import picoscope as p3000
    from code.picoscope.picoscope5000 import picoscope as p5000
    from code.picoscope.picoscope6000 import picoscope as p6000 # ADDPICO in order to add another type of picoscope, add the library here
    from code.picoscope.dummy import dummyScope
    from code.helpers import *
    from code.log import log
else:
    from picoscope3000 import picoscope as p3000
    from picoscope5000 import picoscope as p5000
    from picoscope6000 import picoscope as p6000 # ADDPICO in order to add another type of picoscope, add the library here
    from dummy import dummyScope
    red='\033[31;1m' # for errors
    green='\033[32;1m' #
    yellow='\033[33;1m' #
    lila='\033[34m' #
    pink='\033[35;1m' #
    blue='\033[36;1m' #
    nc='\033[0m'

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
            print("WARNING: "+str)

    log=log()

import traceback


'''
Find different devices and enable choice of device.
Limitations:
- only one device of each type will be listed for now (change is possible)
- only one device can be used at a time (change is possible)
- only some device types are implemented:
    - 3xxxD (not ABC) MSO not yet available
    - 5xxxx 
    - 6xxxx probably outdated code, need to check a few small changes made for 3xxxD

    
SDK is installed to /Library/Frameworks/PicoSDK.framework
'''


drivers = [p3000, p5000, p6000] # ADDPICO in order to add another type of picoscope, add the library here

class deviceShelf():
    def __init__(self,log, test):
        self.log=log
        self.test=test

    def find_units(self):
        # Search for, open and return all devices for supported picoscope drivers
        devices = []
        for driver in drivers:
            try: 
                device = driver() # worked
                device.open() # no ide 
                devices.append(device)
            except Exception as e:
                print("ERROR: ",e)
                continue
        return devices

    def getDeviceName(self,device):
        # get the device type from the device info, see other available info in this example
        '''
        DriverVersion                 : PS3000A MacOSX Driver, 2.1.105.3345
        USBVersion                    : 3.0
        HardwareVersion               : 1
        VariantInfo                   : 3406DMSO
        BatchAndSerial                : JY908/0114
        CalDate                       : 07Sep22
        KernelVersion                 : 0.0
        DigitalHardwareVersion        : 1
        AnalogueHardwareVersion       : 1
        PicoFirmwareVersion1          : 1.7.5.0
        PicoFirmwareVersion2          : 1.0.67.0
        '''
        info=device.getAllUnitInfo()
        vinfo=info
        details=info.split("\n")
        for detail in details:
            if "VariantInfo" in detail:
                vinfo=detail.split(":")[-1].replace(" " ,"")
            if "BatchAndSerial" in detail:
                serial=detail.split(":")[-1].replace(" " ,"")
        return vinfo+" "+serial

    def select_unit(self,devices):
        # give the choice on command line to select one of the devices found by find_units
        # if there is only one unit, automatically choose this unit
        if len(devices)==0:
            raise RuntimeError(red+"Could not find any devices on any drivers."+nc)
        elif len(devices)==1:
            self.log.msg("Only one device found. Automatically choose this device:")
            chosen_device=devices[0]
            vinfo=self.getDeviceName(chosen_device)
        else:
            self.log.msg(green+"Please select a device: The following devices are available (type, batch, serial)."+nc)
            i=1
            for device in devices:
                vinfo=getDeviceName(device)
                self.log.msg("%02d: "%i,vinfo)
            text=input(green+"Please enter the number of the device which should be initialized: "+nc)
            try:
                nbr=int(text)
                if nbr < len(devices)+1:
                    chosen_device=devices[nbr-1]
                else:
                    raise RuntimeError("Number not listed.")
            except:
                for device in devices:
                    device.close()
                traceback.print_exc()
                raise RuntimeError("Invalid number")
            # close other devices
            i=1
            for device in devices:
                if i!=nbr:
                    self.log.msg("Close",i)
                    device.close()
        self.log.info("The chosen device is called (type, batch, serial): %s"%vinfo)
        return chosen_device

    def select_and_start_device(self, test):
        devices=self.find_units()
        if devices:
            device=self.select_unit(devices)
        if not devices or test:
            self.log.warning("No picoscope found, start in test mode")
            self.test=True
            device = dummyScope()
        return device


if __name__ == "__main__":
    test=False
    ds=deviceShelf(log, test)
    device=ds.select_and_start_device(test)
    device.close()
