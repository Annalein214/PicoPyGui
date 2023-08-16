'''
adopted the picoscope 6000 code for the 3000a scopes
'''
# run with python 3

import time, math, inspect, sys
import numpy as np

from ctypes import byref, POINTER, create_string_buffer, c_float, \
    c_int16, c_int32, c_uint32, c_uint64, c_void_p, Structure, c_int64
from ctypes import c_int32 as c_enum
from ctypes.util import find_library

import platform

##########################################################################################
'''
Changes to picoscope6000:
IMPORTANT: only valid for 3000D MSO not ABC
- replaced all ps6000 with ps3000a
- remove DC50
- add setDigitalPort
- change numbers in timebase functions


TODO: 
- setDigitalPort issue
Traceback (most recent call last):
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 791, in <module>
    LogicLevel=mps.setDigitalPort(0, # 0 or 1
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 342, in setDigitalPort
    self.checkResult(m) # 0 if all ok
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 280, in checkResult
    raise IOError('Error calling %s: %s (%s)' % (str(inspect.stack()[1][3]), ecName, ecDesc))
OSError: Error calling setDigitalPort:  ()


- in normal mode issue 
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 511, in getDataV
    self.checkResult(m) # 0 if all ok(m)
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 261, in checkResult
    raise IOError('Error calling %s: %s (%s)' % (str(inspect.stack()[1][3]), ecName, ecDesc))
  OSError: Error calling getDataV: PICO_RATIO_MODE_NOT_SUPPORTED (The selected downsampling mode (used for data reduction) is not allowed.)

'''
##########################################################################################

class picoscope:

    # ps3000a properties
    LIBNAME = "ps3000a"
    NUM_CHANNELS = 4
    CHANNELS     = {"A": 0, "B": 1, "C": 2, "D": 3,
                    "External": 4, "MaxChannels": 4, "TriggerAux": 5}
    NUM_PORTS=2
    PORTS = {"0": 0x80, "1":0x81}
    PORTRANGE=5000 # -5V to 5V
    CHANNEL_COUPLINGS = {"DC": 1, "AC": 0} # just save play to use dc instead of dc50 because the latter does not exist # TODO
    CHANNEL_RANGE = [{"rangeV": 50E-3,  "apivalue": 2, "rangeStr": "50 mV"},
                     {"rangeV": 100E-3, "apivalue": 3, "rangeStr": "100 mV"},
                     {"rangeV": 200E-3, "apivalue": 4, "rangeStr": "200 mV"},
                     {"rangeV": 500E-3, "apivalue": 5, "rangeStr": "500 mV"},
                     {"rangeV": 1.0,    "apivalue": 6, "rangeStr": "1 V"},
                     {"rangeV": 2.0,    "apivalue": 7, "rangeStr": "2 V"},
                     {"rangeV": 5.0,    "apivalue": 8, "rangeStr": "5 V"},
                     {"rangeV": 10.0,   "apivalue": 9, "rangeStr": "10 V"},
                     {"rangeV": 20.0,   "apivalue": 10, "rangeStr": "20 V"},
                     ]
    MAXOFFSETDC={50E-3: 2000, # V, mV
                100E-3: 2000,
                200E-3: 2000,
                500E-3: 5000,
                1.0: 4500,
                2.0: 3500,
                5.0: 500,
                10.0: 0,
                20.0: 0,
                }   
    MAXOFFSETAC={50E-3: 2000, # V, mV
                100E-3: 2000,
                200E-3: 2000,
                500E-3: 10000,
                1.0: 10000,
                2.0: 10000,
                5.0: 35000,
                10.0: 30000,
                20.0: 20000,
                } 
    MINTRIGGER={50E-3: 4, # V, mV
                100E-3: 8,
                200E-3: 10,
                500E-3: 25,
                1.0: 50,
                2.0: 100,
                5.0: 250,
                10.0: 500,
                20.0: 1000,
                }
    THRESHOLD_TYPE = {"Above": 0,"Below": 1,"Rising": 2,"Falling": 3,"RiseOrFall": 4}
    MAX_VALUE = 32764 #32768-256
    MIN_VALUE = -32764 # -32768
    EXT_MAX_VALUE = 32767
    EXT_MIN_VALUE = -32767
    EXT_RANGE_VOLTS = 20
    
    WAVE_TYPES = {"Sine": 0, "Square": 1, "Triangle": 2,
                  "RampUp": 3, "RampDown": 4,
                  "Sinc": 5, "Gaussian": 6, "HalfSine": 7, "DCVoltage": 8,
                  "WhiteNoise": 9}
                  
    SIGGEN_TRIGGER_TYPES = {"Rising": 0, "Falling": 1,
                            "GateHigh": 2, "GateLow": 3}
    SIGGEN_TRIGGER_SOURCES = {"None": 0, "ScopeTrig": 1, "AuxIn": 2,
                              "ExtIn": 3, "SoftTrig": 4, "TriggerRaw": 5}
    
    ### getUnitInfo parameter types
    UNIT_INFO_TYPES = {"DriverVersion"          : 0x0,
                       "USBVersion"             : 0x1,
                       "HardwareVersion"        : 0x2,
                       "VariantInfo"             : 0x3,
                       "BatchAndSerial"         : 0x4,
                       "CalDate"                : 0x5,
                       "KernelVersion"          : 0x6,
                       "DigitalHardwareVersion" : 0x7,
                       "AnalogueHardwareVersion": 0x8,
                       "PicoFirmwareVersion1"   : 0x9,
                       "PicoFirmwareVersion2"   : 0xA}
    
    ###Error codes - copied from ps6000 programmers manual.
    ERROR_CODES = [[0x00 , "PICO_OK", "The PicoScope XXXX is functioning correctly."],
        [0x01 , "PICO_MAX_UNITS_OPENED", "An attempt has been made to open more than PSXXXX_MAX_UNITS."],
        [0x02 , "PICO_MEMORY_FAIL", "Not enough memory could be allocated on the host machine."],
        [0x03 , "PICO_NOT_FOUND", "No PicoScope XXXX could be found."],
        [0x04 , "PICO_FW_FAIL", "Unable to download firmware."],
        [0x05 , "PICO_OPEN_OPERATION_IN_PROGRESS"],
        [0x06 , "PICO_OPERATION_FAILED"],
        [0x07 , "PICO_NOT_RESPONDING", "The PicoScope XXXX is not responding to commands from the PC."],
        [0x08 , "PICO_CONFIG_FAIL", "The configuration information in the PicoScope XXXX has become corrupt or is missing."],
        [0x09 , "PICO_KERNEL_DRIVER_TOO_OLD", "The picopp.sys file is too old to be used with the device driver."],
        [0x0A , "PICO_EEPROM_CORRUPT", "The EEPROM has become corrupt, so the device will use a default setting."],
        [0x0B , "PICO_OS_NOT_SUPPORTED", "The operating system on the PC is not supported by this driver."],
        [0x0C , "PICO_INVALID_HANDLE", "There is no device with the handle value passed."],
        [0x0D , "PICO_INVALID_PARAMETER", "A parameter value is not valid."],
        [0x0E , "PICO_INVALID_TIMEBASE", "The timebase is not supported or is invalid."],
        [0x0F , "PICO_INVALID_VOLTAGE_RANGE", "The voltage range is not supported or is invalid."],
        [0x10 , "PICO_INVALID_CHANNEL", "The channel number is not valid on this device or no channels have been set."],
        [0x11 , "PICO_INVALID_TRIGGER_CHANNEL", "The channel set for a trigger is not available on this device."],
        [0x12 , "PICO_INVALID_CONDITION_CHANNEL", "The channel set for a condition is not available on this device."],
        [0x13 , "PICO_NO_SIGNAL_GENERATOR", "The device does not have a signal generator."],
        [0x14 , "PICO_STREAMING_FAILED", "Streaming has failed to start or has stopped without user request."],
        [0x15 , "PICO_BLOCK_MODE_FAILED", "Block failed to start", "a parameter may have been set wrongly."],
        [0x16 , "PICO_NULL_PARAMETER", "A parameter that was required is NULL."],
        [0x18 , "PICO_DATA_NOT_AVAILABLE", "No data is available from a run block call."],
        [0x19 , "PICO_STRING_BUFFER_TOO_SMALL", "The buffer passed for the information was too small."],
        [0x1A , "PICO_ETS_NOT_SUPPORTED", "ETS is not supported on this device."],
        [0x1B , "PICO_AUTO_TRIGGER_TIME_TOO_SHORT", "The auto trigger time is less than the time it will take to collect the pre-trigger data."],
        [0x1C , "PICO_BUFFER_STALL", "The collection of data has stalled as unread data would be overwritten."],
        [0x1D , "PICO_TOO_MANY_SAMPLES", "Number of samples requested is more than available in the current memory segment."],
        [0x1E , "PICO_TOO_MANY_SEGMENTS", "Not possible to create number of segments requested."],
        [0x1F , "PICO_PULSE_WIDTH_QUALIFIER", "A null pointer has been passed in the trigger function or one of the parameters is out of range."],
        [0x20 , "PICO_DELAY", "One or more of the hold-off parameters are out of range."],
        [0x21 , "PICO_SOURCE_DETAILS", "One or more of the source details are incorrect."],
        [0x22 , "PICO_CONDITIONS", "One or more of the conditions are incorrect."],
        [0x23 , "PICO_USER_CALLBACK", "The driver's thread is currently in the psXXXXBlockReady callback function and therefore the action cannot be carried out."],
        [0x24 , "PICO_DEVICE_SAMPLING", "An attempt is being made to get stored data while streaming. Either stop streaming by calling psXXXXStop, or use psXXXXGetStreamingLatestValues."],
        [0x25 , "PICO_NO_SAMPLES_AVAILABLE", "because a run has not been completed."],
        [0x26 , "PICO_SEGMENT_OUT_OF_RANGE", "The memory index is out of range."],
        [0x27 , "PICO_BUSY", "Data cannot be returned yet."],
        [0x28 , "PICO_STARTINDEX_INVALID", "The start time to get stored data is out of range."],
        [0x29 , "PICO_INVALID_INFO", "The information number requested is not a valid number."],
        [0x2A , "PICO_INFO_UNAVAILABLE", "The handle is invalid so no information is available about the device. Only PICO_DRIVER_VERSION is available."],
        [0x2B , "PICO_INVALID_SAMPLE_INTERVAL", "The sample interval selected for streaming is out of range."],
        [0x2D , "PICO_MEMORY", "Driver cannot allocate memory."],
        [0x2E , "PICO_SIG_GEN_PARAM", "Incorrect parameter passed to signal generator."],
        [0x34 , "PICO_WARNING_AUX_OUTPUT_CONFLICT", "AUX cannot be used as input and output at the same time."],
        [0x35 , "PICO_SIGGEN_OUTPUT_OVER_VOLTAGE", "The combined peak to peak voltage and the analog offset voltage exceed the allowable voltage the signal generator can produce."],
        [0x36 , "PICO_DELAY_NULL", "NULL pointer passed as delay parameter."],
        [0x37 , "PICO_INVALID_BUFFER", "The buffers for overview data have not been set while streaming."],
        [0x38 , "PICO_SIGGEN_OFFSET_VOLTAGE", "The analog offset voltage is out of range."],
        [0x39 , "PICO_SIGGEN_PK_TO_PK", "The analog peak to peak voltage is out of range."],
        [0x3A , "PICO_CANCELLED", "A block collection has been cancelled."],
        [0x3B , "PICO_SEGMENT_NOT_USED", "The segment index is not currently being used."],
        [0x3C , "PICO_INVALID_CALL", "The wrong GetValues function has been called for the collection mode in use."],
        [0x3F , "PICO_NOT_USED", "The function is not available."],
        [0x40 , "PICO_INVALID_SAMPLERATIO", "The aggregation ratio requested is out of range."],
        [0x41 , "PICO_INVALID_STATE", "Device is in an invalid state."],
        [0x42 , "PICO_NOT_ENOUGH_SEGMENTS", "The number of segments allocated is fewer than the number of captures requested."],
        [0x43 , "PICO_DRIVER_FUNCTION", "You called a driver function while another driver function was still being processed."],
        [0x45 , "PICO_INVALID_COUPLING", "An invalid coupling type was specified in psXXXXSetChannel."],
        [0x46 , "PICO_BUFFERS_NOT_SET", "An attempt was made to get data before a data buffer was defined."],
        [0x47 , "PICO_RATIO_MODE_NOT_SUPPORTED", "The selected downsampling mode (used for data reduction) is not allowed."],
        [0x49 , "PICO_INVALID_TRIGGER_PROPERTY", "An invalid parameter was passed to psXXXXSetTriggerChannelProperties."],
        [0x4A , "PICO_INTERFACE_NOT_CONNECTED", "The driver was unable to contact the oscilloscope."],
        [0x4D , "PICO_SIGGEN_WAVEFORM_SETUP_FAILED", "A problem occurred in psXXXXSetSigGenBuiltIn or psXXXXSetSigGenArbitrary."],
        [0x4E , "PICO_FPGA_FAIL"],
        [0x4F , "PICO_POWER_MANAGER"],
        [0x50 , "PICO_INVALID_ANALOGUE_OFFSET", "An impossible analogue offset value was specified in psXXXXSetChannel."],
        [0x51 , "PICO_PLL_LOCK_FAILED", "Unable to configure the PicoScope XXXX."],
        [0x52 , "PICO_ANALOG_BOARD", "The oscilloscope's analog board is not detected, or is not connected to the digital board."],
        [0x53 , "PICO_CONFIG_FAIL_AWG", "Unable to configure the signal generator."],
        [0x54 , "PICO_INITIALISE_FPGA", "The FPGA cannot be initialized, so unit cannot be opened."],
        [0x56 , "PICO_EXTERNAL_FREQUENCY_INVALID", "The frequency for the external clock is not within +/-5% of the stated value."],
        [0x57 , "PICO_CLOCK_CHANGE_ERROR", "The FPGA could not lock the clock signal."],
        [0x58 , "PICO_TRIGGER_AND_EXTERNAL_CLOCK_CLASH", "You are trying to configure the AUX input as both a trigger and a reference clock."],
        [0x59 , "PICO_PWQ_AND_EXTERNAL_CLOCK_CLASH", "You are trying to configure the AUX input as both a pulse width qualifier and a reference clock."],
        [0x5A , "PICO_UNABLE_TO_OPEN_SCALING_FILE", "The scaling file set can not be opened."],
        [0x5B , "PICO_MEMORY_CLOCK_FREQUENCY", "The frequency of the memory is reporting incorrectly."],
        [0x5C , "PICO_I2C_NOT_RESPONDING", "The I2C that is being actioned is not responding to requests."],
        [0x5D , "PICO_NO_CAPTURES_AVAILABLE", "There are no captures available and therefore no data can be returned."],
        [0x5E , "PICO_NOT_USED_IN_THIS_CAPTURE_MODE", "The capture mode the device is currently running in does not support the current request."],
        [0x103 , "PICO_GET_DATA_ACTIVE", "Reserved"],
        [0x104 , "PICO_IP_NETWORKED", "The device is currently connected via the IP Network socket and thus the call made is not supported."],
        [0x105 , "PICO_INVALID_IP_ADDRESS", "An IP address that is not correct has been passed to the driver."],
        [0x106 , "PICO_IPSOCKET_FAILED", "The IP socket has failed."],
        [0x107 , "PICO_IPSOCKET_TIMEDOUT", "The IP socket has timed out."],
        [0x108 , "PICO_SETTINGS_FAILED", "The settings requested have failed to be set."],
        [0x109 , "PICO_NETWORK_FAILED", "The network connection has failed."],
        [0x10A , "PICO_WS2_32_DLL_NOT_LOADED", "Unable to load the WS2 dll."],
        [0x10B , "PICO_INVALID_IP_PORT", "The IP port is invalid."],
        [0x10C , "PICO_COUPLING_NOT_SUPPORTED", "The type of coupling requested is not supported on the opened device."],
        [0x10D , "PICO_BANDWIDTH_NOT_SUPPORTED", "Bandwidth limit is not supported on the opened device."],
        [0x10E , "PICO_INVALID_BANDWIDTH", "The value requested for the bandwidth limit is out of range."],
        [0x10F , "PICO_AWG_NOT_SUPPORTED", "The device does not have an arbitrary waveform generator."],
        [0x110 , "PICO_ETS_NOT_RUNNING", "Data has been requested with ETS mode set but run block has not been called, or stop has been called."],
        [0x111 , "PICO_SIG_GEN_WHITENOISE_NOT_SUPPORTED", "White noise is not supported on the opened device."],
        [0x112 , "PICO_SIG_GEN_WAVETYPE_NOT_SUPPORTED", "The wave type requested is not supported by the opened device."],
        [0x116 , "PICO_SIG_GEN_PRBS_NOT_SUPPORTED", "Siggen does not generate pseudorandom bit stream."],
        [0x117 , "PICO_ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS", "When a digital port is enabled, ETS sample mode is not available for use."],
        [0x118 , "PICO_WARNING_REPEAT_VALUE", "Not applicable to this device."],
        [0x119 , "PICO_POWER_SUPPLY_CONNECTED", "The DC power supply is connected."],
        [0x11A , "PICO_POWER_SUPPLY_NOT_CONNECTED", "The DC power supply is not connected."],
        [0x11B , "PICO_POWER_SUPPLY_REQUEST_INVALID", "Incorrect power mode passed for current power source."],
        [0x11C , "PICO_POWER_SUPPLY_UNDERVOLTAGE", "The supply voltage from the USB source is too low."],
        [0x11D , "PICO_CAPTURING_DATA", "The device is currently busy capturing data."],
        [0x11F , "PICO_NOT_SUPPORTED_BY_THIS_DEVICE", "A function has been called that is not supported by the current device variant."],
        [0x120 , "PICO_INVALID_DEVICE_RESOLUTION", "The device resolution is invalid (out of range)."],
        [0x121 , "PICO_INVALID_NUMBER_CHANNELS_FOR_RESOLUTION", "The number of channels which can be enabled is limited in 15 and 16-bit modes"],
        [0x122 , "PICO_CHANNEL_DISABLED_DUE_TO_USB_POWERED", "USB Power not sufficient to power all channels."]]

    def __init__(self):
        print("DEBUG: Init 3000")
        self.dummy=False
        self.CHRange = [5.0] * self.NUM_CHANNELS
        self.CHOffset = [0.0] * self.NUM_CHANNELS
        self.ProbeAttenuation = [1.0] * self.NUM_CHANNELS
        self.ChEnabled= [0] * self.NUM_CHANNELS
        self.PortEnabled = [0] * self.NUM_PORTS
        self.handle = None
        
        # to load the proper dll
        
        
        if platform.system() == 'Linux':
            from ctypes import cdll
            self.lib = cdll.LoadLibrary("lib" + self.LIBNAME + ".so.2")
        elif  platform.system()=="Darwin":
            from ctypes import cdll
            print("\tYou seem to be on a Mac."+\
                  "If the following fails do: Link the libraries from Application/Picoscope/Content/Resources per $ln -s *dylib to /usr/local/lib/ ")
            print("\tFor PicoScope 7: $export DYLD_FALLBACK_LIBRARY_PATH=/Applications/PicoScope 7 T&M.app/Contents/Resources/")
            self.lib = cdll.LoadLibrary("lib" + self.LIBNAME + ".dylib")	
        else:
            from ctypes import windll
            #import os
            #print ("dir",os.path.isdir("C:/Program Files/Pico Technology/SDK/lib/"))
            self.lib = windll.LoadLibrary(self.LIBNAME + ".dll")
    
    def open(self):
        c_handle = c_int16()
        serialNullTermStr = None # Passing None is the same as passing NULL
        m = self.lib.ps3000aOpenUnit(byref(c_handle), serialNullTermStr)
        self.checkResult(m)
        self.handle = c_handle.value
        self.name = 3000
      
    def close(self):
        if not self.handle is None:
            m = self.lib.ps3000aStop(c_int16(self.handle))
            self.checkResult(m)
            m = self.lib.ps3000aCloseUnit(c_int16(self.handle))
            self.checkResult(m)
            self.handle = None
        
    def checkResult(self, ec):
        """ Check result of function calls, raise exception if not 0. """
        if ec == 0:
            return
        else:
            ecName=""
            for t in self.ERROR_CODES:
                if t[0] == ec:
                    ecName= t[1]
                    break   
            ecDesc=""
            for t in self.ERROR_CODES:
                if t[0] == ec:
                    try:
                        ecDesc=t[2]
                    except IndexError:
                        ecDesc=""
            raise IOError('Error calling %s: %s (%s)' % (str(inspect.stack()[1][3]), ecName, ecDesc))

    def getAllUnitInfo(self):
        """ Return: human readible unit information as a string. """
        s = ""
        for key in sorted(self.UNIT_INFO_TYPES.keys(), key=self.UNIT_INFO_TYPES.get):
            s += key.ljust(30) + ": " + self.getUnitInfo(key) + "\n"

        s = s[:-1]
        return s
        
    def getUnitInfo(self, info):
        """ Return: A string containing the requested information. """
        if not isinstance(info, int):
            info = self.UNIT_INFO_TYPES[info]
        
        s = create_string_buffer(256)
        requiredSize = c_int16(0)
        m = self.lib.ps3000aGetUnitInfo(c_int16(self.handle), byref(s),
                                       c_int16(len(s)), byref(requiredSize),
                                       c_enum(info))
        self.checkResult(m)
        if requiredSize.value > len(s):
            s = create_string_buffer(requiredSize.value + 1)
            m = self.lib.ps3000aGetUnitInfo(c_int16(self.handle), byref(s),
                                           c_int16(len(s)),
                                           byref(requiredSize), c_enum(info))
            self.checkResult(m)

        return s.value.decode('utf-8')

    def maxOffset(self, coupling, voltagerange):

        if coupling=="DC50" or coupling=="DC":
            return self.MAXOFFSETDC[voltagerange]
        else:
            return self.MAXOFFSETAC[voltagerange]

    def setDigitalPort(self, port, # 0 or 1
                         logiclevel_V=0, # -5v to 5v
                         enabled=True):
        '''
        PS3000A_DIGITAL_PORT0 = 0x80 (digital channels 0–7) 
        PS3000A_DIGITAL_PORT1 = 0x81 (digital channels 8–15)

        '''

        # ensure integer type 
        enabled = int(bool(enabled))

        # get the integer representing the port
        if not isinstance(port, int):
            portNum = self.PORTS[port]
        else:
            portNum = port

        # convert from volts to adc
        a2v = self.PORTRANGE / self.MAX_VALUE # 5V / 32767
        logiclevel = int(logiclevel_V / a2v)

        if logiclevel >= self.MAX_VALUE or logiclevel <= self.MIN_VALUE: 
            raise IOError("Logic level of %fV outside allowed range (%f, %f)" % (
                    logiclevel_V, -self.PORTRANGE,
                    self.PORTRANGE))

        m = self.lib.ps3000aSetDigitalPort(c_int16(self.handle), 
                                           c_enum(portNum), 
                                           c_int16(enabled), 
                                           c_int16(logiclevel))
        self.checkResult(m) # 0 if all ok

        self.PortEnabled[portNum] = enabled
        self.PortLevel[portNum]= logiclevel

        return logiclevel
        
    def setChannel(self,channel='A', coupling="AC", VRange=2.0, VOffset=0.0, enabled=True,
                   BWLimited=False, probeAttenuation=1.0):
        
        # ensure integer type 
        enabled = int(bool(enabled))
        BWLimited=int(BWLimited) # 2 for 6404, 1 for 6402/6403 
        
        # get the integer representing the channel
        if not isinstance(channel, int):
            chNum = self.CHANNELS[channel]
        else:
            chNum = channel

        # get the integer representing the coupling
        if not isinstance(coupling, int):
            coupling = self.CHANNEL_COUPLINGS[coupling.replace("\r","")]# TODO warum \r in coupling???

        # finds the next largest range accounting for small floating point errors
        VRangeAPI = None
        for item in self.CHANNEL_RANGE:
            if item["rangeV"] - VRange / probeAttenuation > -1E-4:
                if VRangeAPI is None:
                    VRangeAPI = item
                elif VRangeAPI["rangeV"] > item["rangeV"]:
                    VRangeAPI = item

        if VRangeAPI is None:
            raise ValueError("Desired range %f is too large. Maximum range is %f." %
                             (VRange, self.CHANNEL_RANGE[-1]["rangeV"] * probeAttenuation))

        # store the actually chosen range of the scope
        VRange = VRangeAPI["rangeV"] * probeAttenuation
        
        # set the channel 
        m = self.lib.ps3000aSetChannel(c_int16(self.handle), c_enum(chNum),
                                      c_int16(enabled), c_enum(coupling),
                                      c_enum(VRangeAPI["apivalue"]), c_float(VOffset/probeAttenuation),
                                      c_enum(BWLimited))
        self.checkResult(m) # 0 if all ok

        # if all was successful, save the parameters
        self.ChEnabled[chNum] = enabled
        self.CHRange[chNum] = VRange
        self.CHOffset[chNum] = VOffset
        self.ProbeAttenuation[chNum] = probeAttenuation

        return VRange
        
    def setSimpleTrigger(self, trigSrc, threshold_V=0, direction="Rising", delay=0, timeout_ms=100,
                         enabled=True):
       
        if not isinstance(trigSrc, int):
            trigSrc = self.CHANNELS[trigSrc]

        if not isinstance(direction, int):
            direction = self.THRESHOLD_TYPE[direction]

        if trigSrc >= self.NUM_CHANNELS:
            threshold_adc = int((threshold_V / self.EXT_RANGE_VOLTS) * self.EXT_MAX_VALUE)
            threshold_adc = min(threshold_adc, self.EXT_MAX_VALUE)
            threshold_adc = max(threshold_adc, self.EXT_MIN_VALUE)
        else:
            a2v = self.CHRange[trigSrc] / self.MAX_VALUE
            threshold_adc = int((threshold_V + self.CHOffset[trigSrc]) / a2v)

            if threshold_adc >= self.MAX_VALUE or threshold_adc <= self.MIN_VALUE: 
                raise IOError("Trigger Level of %fV outside allowed range (%f, %f)" % (
                    threshold_V, -self.CHRange[trigSrc] - self.CHOffset[trigSrc],
                    self.CHRange[trigSrc] - self.CHOffset[trigSrc]))

        enabled = int(bool(enabled))

        m = self.lib.ps3000aSetSimpleTrigger(
            c_int16(self.handle), c_int16(enabled),
            c_enum(trigSrc), c_int16(threshold_adc),
            c_enum(direction), c_uint32(delay), c_int16(timeout_ms))
        self.checkResult(m) # 0 if all ok(m)



        return True
        
    def getTimeBaseNum(self, sampleTimeS):
        """ Return sample time in seconds to timebase as int for API calls. """
        maxSampleTime = (((2 ** 32 - 1) - 2) / 125000000) ## obi change to 3000 D
        if sampleTimeS < 8E-9:
            timebase = math.floor(math.log(sampleTimeS * 1E9, 2)) ## obi change for 3000 D
            timebase = max(timebase, 0) # ergibt 2. wenn sampleTimeS=1e-9
        else:
            #Otherwise in range 2^32-1
            if sampleTimeS > maxSampleTime:
                sampleTimeS = maxSampleTime
            timebase = math.floor((sampleTimeS * 125000000) + 2) ## obi change to 3000 D
        timebase = int(timebase)
        return timebase


    def getTimestepFromTimebase(self, timebase):
        """ Return timebase to sampletime as seconds. """
        if timebase < 3: ## obi change to 3000 D
            dt = 2. ** timebase / 1E9 ## obi change to 3000 D
        else:
            dt = (timebase - 2.) / 125000000. ## obi change to 3000 D
        return dt


    def setSamplingFrequency(self, sampleFreq, noSamples, oversample=0, segmentIndex=0):
        sampleInterval = 1.0 / sampleFreq
        duration = noSamples * sampleInterval        
        self.oversample = oversample
        self.timebase = self.getTimeBaseNum(sampleInterval) # 2.0 fuer 1.0ns interval
        timebase_dt = self.getTimestepFromTimebase(self.timebase) # 8e-10 fuer 1.0ns interval
        noSamples = int(round(duration / timebase_dt))
            
        maxSamples = c_int32()
        sampleRate = c_float()
        m = self.lib.ps3000aGetTimebase2(c_int16(self.handle), c_uint32(self.timebase),
                                        c_uint32(noSamples), byref(sampleRate),
                                        c_int16(oversample), byref(maxSamples),
                                        c_uint32(segmentIndex))
        self.checkResult(m) # 0 if all ok(m)

        self.sampleInterval=sampleRate.value / 1.0E9
        self.maxSamples=maxSamples.value

        # remove changing the nosample -> no this is only to save them, do not remove this line
        self.noSamples =noSamples
        self.sampleRate = 1.0 / self.sampleInterval
        
        return (self.sampleRate, self.maxSamples, noSamples)
        
    def memorySegments(self, noSegments):
        nMaxSamples = c_uint32()
        m = self.lib.ps3000aMemorySegments(c_int16(self.handle),
                                          c_uint32(noSegments), byref(nMaxSamples))
        self.checkResult(m) # 0 if all ok(m)
        self.maxSamples = nMaxSamples.value
        self.noSegments = noSegments
        return self.maxSamples
        
    def setNoOfCaptures(self, noCaptures):
        m = self.lib.ps3000aSetNoOfCaptures(c_int16(self.handle), c_uint32(noCaptures))
        self.checkResult(m) # 0 if all ok(m)
        
    def runBlock(self, pretrig=0.0, segmentIndex=0):
        nSamples = min(self.noSamples, self.maxSamples)
        numPreTrigSamples=int(round(nSamples * pretrig))
        numPostTrigSamples=int(round(nSamples * (1 - pretrig)))
        timeIndisposedMs = c_int32()
        m = self.lib.ps3000aRunBlock(
            c_int16(self.handle), c_uint32(numPreTrigSamples),
            c_uint32(numPostTrigSamples), c_uint32(self.timebase),
            c_int16(self.oversample), byref(timeIndisposedMs),
            c_uint32(segmentIndex), c_void_p(), c_void_p())
        self.checkResult(m) # 0 if all ok(m)
        return timeIndisposedMs.value
        
    def isReady(self):
        ready = c_int16()
        m = self.lib.ps3000aIsReady(c_int16(self.handle), byref(ready))
        self.checkResult(m) # 0 if all ok(m)
        if ready.value:
            return True
        else:
            return False
            
    def getDataRaw(self, channel='A', numSamples=0, startIndex=0, downSampleRatio=1,
                   downSampleMode=0, segmentIndex=0, data=None):
        if not isinstance(channel, int):
            channel = self.CHANNELS[channel]

        if numSamples == 0:
            numSamples = min(self.maxSamples, self.noSamples)

        if data is None:
            data = np.empty(numSamples, dtype=np.int16)
        
        # set buffer
        dataPtr = data.ctypes.data_as(POINTER(c_int16))
        numSamples = len(data)
        m = self.lib.ps3000aSetDataBuffer(c_int16(self.handle), c_enum(channel),
                                         dataPtr, c_uint32(numSamples),
                                         c_enum(downSampleMode))
        self.checkResult(m) # 0 if all ok(m)

        # get the values
        numSamplesReturned = c_uint32()
        numSamplesReturned.value = numSamples
        overflow = c_int16()
        m = self.lib.ps3000aGetValues(
            c_int16(self.handle), c_uint32(startIndex),
            byref(numSamplesReturned), c_uint32(downSampleRatio),
            c_enum(downSampleMode), c_uint32(segmentIndex),
            byref(overflow))
        self.checkResult(m) # 0 if all ok(m)
        
        numSamplesReturned=numSamplesReturned.value
        overflow=overflow.value
        overflow = bool(overflow & (1 << channel))
        
        # clear buffer!
        m = self.lib.ps3000aSetDataBuffer(c_int16(self.handle), c_enum(channel),
                                         c_void_p(), c_int32(0), c_uint32(0), c_enum(0))
        self.checkResult(m) # 0 if all ok(m)
        
        return data
        
    def getDataV(self, numSamples=0, startIndex=0, downSampleRatio=1,
                   downSampleMode=0, segmentIndex=0, data=None):
        # TODO set buffer for MSO

        if numSamples == 0:
            numSamples = min(self.maxSamples, self.noSamples)            
        
        # set buffer
        data=[0] * self.NUM_CHANNELS # array to hold all buffers
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                data[ch] = np.empty(numSamples, dtype=np.int16)
                dataPtr = data[ch].ctypes.data_as(POINTER(c_int16))
                dataPtr2 = data[ch].ctypes.data_as(POINTER(c_int16)) # dummy, not used
                numSamples = len(data[ch])
                #m = self.lib.ps3000aSetDataBuffer(c_int16(self.handle), 
                #                                  c_enum(ch),
                #                                  dataPtr, 
                #                                  c_int32(numSamples),# bufferLth
                #                                  c_uint32(1), # segmentIndex # TODO new with MSO
                #                                   c_enum(downSampleMode)                     , # mode
                #                                  )
                m = self.lib.ps3000aSetDataBuffers(c_int16(self.handle), 
                                             c_enum(ch), 
                                             dataPtr, 
                                             dataPtr2, 
                                             c_int32(numSamples), 
                                             0, 
                                             0)

                self.checkResult(m) # 0 if all ok(m)

        # get the values
        numSamplesReturned = c_uint32()
        numSamplesReturned.value = numSamples
        overflow = c_int16()
        m = self.lib.ps3000aGetValues(
            c_int16(self.handle), c_uint32(startIndex),
            byref(numSamplesReturned), c_uint32(downSampleRatio),
            c_enum(downSampleMode), c_uint32(segmentIndex),
            byref(overflow))
        self.checkResult(m) # 0 if all ok(m)
                
        # clear buffer!
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                m = self.lib.ps3000aSetDataBuffers(c_int16(self.handle), c_enum(ch),
                                         c_void_p(),c_void_p(), 0,0,0)
        self.checkResult(m) # 0 if all ok(m)
        
        dataV=[0] * self.NUM_CHANNELS
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                dataV[ch]=self.rawToV(ch, data[ch])
        
        return np.array(dataV)
        
    def rawToV(self, channel, dataRaw):
        if not isinstance(channel, int):
            channel = self.CHANNELS[channel]
                        
        if  type(dataRaw[0])==np.ndarray: # this is for rapid block mode
            dataV = np.ascontiguousarray(
                        np.zeros((len(dataRaw), len(dataRaw[0])), dtype=np.float64)
                    )
        else: # normal block mode
            dataV = np.empty(dataRaw.size)
                
        a2v = self.CHRange[channel] / float(self.MAX_VALUE)
        np.multiply(dataRaw, a2v, dataV)
        np.subtract(dataV, self.CHOffset[channel], dataV)

        return dataV
        
    def SetDataBufferBulk(self, channel, buffer, waveform, downSampleRatioMode):
        # only for rapid block mode
        bufferPtr = buffer.ctypes.data_as(POINTER(c_int16))
        bufferPtr2 = buffer.ctypes.data_as(POINTER(c_int16)) # dummy
        bufferLth = len(buffer)

        m = self.lib.ps3000aSetDataBuffers(c_int16(self.handle),
                                              c_enum(channel), 
                                              bufferPtr, 
                                              bufferPtr2,
                                              c_uint32(bufferLth), 
                                              c_uint32(waveform), 
                                              c_enum(downSampleRatioMode)
                                              )
        self.checkResult(m) # 0 if all ok(m)
        
    def ClearDataBufferBulk(self, channel):
        m = self.lib.ps3000aSetDataBuffers(
            c_int16(self.handle),c_enum(channel), 
            c_void_p(), c_void_p(), c_uint32(0), c_uint32(0), c_enum(0))
        self.checkResult(m) # 0 if all ok(m)

    def getDataVBulk(self, numSamples=0, fromSegment=0,
        toSegment=None, downSampleRatio=1, downSampleMode=0):

        if toSegment is None:
            toSegment = self.noSegments - 1
        if numSamples == 0:
            numSamples = min(self.maxSamples, self.noSamples)
        numSegmentsToCopy = toSegment - fromSegment + 1
        

        # set up each row in the data array as a buffer for one of
        # the memory segments in the scope
        data=[0] * self.NUM_CHANNELS # array to hold all buffers
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                # buffer
                data[ch] = np.ascontiguousarray(
                    np.zeros((numSegmentsToCopy, numSamples), dtype=np.int16)
                    )
                for i, segment in enumerate(range(fromSegment, toSegment+1)):
                    self.SetDataBufferBulk(ch,data[ch][i],segment,downSampleMode)
            
        overflow = np.ascontiguousarray(
            np.zeros(numSegmentsToCopy, dtype=np.int16)
            )
            
        noOfSamples = c_uint32(numSamples)
        
        m = self.lib.ps3000aGetValuesBulk(
                    c_int16(self.handle),
                    byref(noOfSamples),
                    c_uint32(fromSegment), c_uint32(toSegment),
                    c_uint32(downSampleRatio), c_enum(downSampleMode),
                    overflow.ctypes.data_as(POINTER(c_int16))
                    )
        self.checkResult(m) # 0 if all ok(m)
        numSamples=noOfSamples.value
        
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                for i, segment in enumerate(range(fromSegment, toSegment+1)):
                    self.ClearDataBufferBulk(ch)
                    
        # get physical values from adc counts
        
        dataV=[0] * self.NUM_CHANNELS
        for ch in range(self.NUM_CHANNELS):
            if self.ChEnabled[ch]==1:
                dataV[ch]=self.rawToV(ch, data[ch])
            else: 
                dataV[ch]=[]
        #print(type(dataV),dataV)
        # Ch a on: <type 'list'> [array([[-0.00015139, -0.00054206],
                #[-0.00015139, -0.00054206]]), 0, 0, array([[ 1.98461726,  1.98461726],
                #[ 1.98461726,  1.98461726]])]
        # Ch c off: <type 'list'> [0, array([[ 1.60153827,  1.60153827],
                #[ 1.60153827,  1.60153827]]), array([[ 0.19846173,  0.19846173],
                #[ 0.19846173,  0.19846173]]), array([[ 1.98461726,  1.98461726],
                #[ 1.98461726,  1.98461726]])]

        return np.array(dataV, dtype=object)
        
    def setSigGenBuiltInSimple(self, offsetVoltage=0, pkToPk=2, waveType="Sine", frequency=1E6,
                               shots=1, triggerType="Rising", triggerSource="None"):

        if triggerSource is None:
            triggerSource = "None"
        if not isinstance(waveType, int):
            waveType = self.WAVE_TYPES[waveType]
        if not isinstance(triggerType, int):
            triggerType = self.SIGGEN_TRIGGER_TYPES[triggerType]
        if not isinstance(triggerSource, int):
            triggerSource = self.SIGGEN_TRIGGER_SOURCES[triggerSource]

        m = self.lib.ps3000aSetSigGenBuiltIn(
            c_int16(self.handle),
            c_int32(int(offsetVoltage * 1000000)),
            c_int32(int(pkToPk        * 1000000)),
            c_int16(waveType),
            c_float(frequency), c_float(frequency),
            c_float(0), c_float(0), c_enum(0), c_enum(0),
            c_uint32(shots), c_uint32(0),
            c_enum(triggerType), c_enum(triggerSource),
            c_int16(0))
        self.checkResult(m)
        
    class ps3000a_TRIGGER_INFO(Structure):
            _fields_ = [("status", c_uint32),
                        ("segmentIndex", c_uint32),
                        ("triggerIndex", c_uint32),
                        ("triggerTime", c_int64),
                        ("timeUnits", c_int16 ),
                        ("reserved0", c_int16 ),
                        ("timeStampCounter", c_uint64 ),
                        ]
        
    def GetTriggerInfoBulk(self, fromSegment=0, toSegment=None):
        
        if toSegment is None:
            toSegment = self.noSegments - 1
            
        numSegmentsToCopy = toSegment - fromSegment + 1
        
        tinfo=[]
        for i in range(numSegmentsToCopy):
            tinfo.append(self.ps3000a_TRIGGER_INFO)
        tinfo = np.ascontiguousarray(
            tinfo
            )
        print("Before")
        tinfoPtr=tinfo.ctypes.data_as(POINTER(self.ps3000a_TRIGGER_INFO))  
                
        if platform.system() == 'Linux' or platform.system()=="Darwin":
            # gives segmentation fault
            pass
        else:
            try:
                m=self.lib.ps3000aGetTriggerInfoBulk(c_int16(self.handle),
                                                    tinfoPtr,
                                                    c_uint32(fromSegment), 
                                                    c_uint32(toSegment),
                                                    )
                print("Result",m)
                self.checkResult(m)
            except Exception as e:
                print(e)
            print("after")
            print (type(tinfo), tinfo)
                    
                    
            for ti in triggerinfo:
                print ("ti", type(ti), ti, end=" ")
                print (ti.status,end=" ")
                print (ti.segmentIndex,end=" ")
                print (ti.triggerIndex,end=" ")
                print (ti.triggerTime,end=" ")
                print (ti.timeUnits,end=" ")
                print (ti.reserved0,end=" ")
                print (ti.timeStampCounter,end=" ")
                break

        return tinfo
##########################################################################################

if __name__ == "__main__":

    mps=picoscope()

    mps.open()

    # if true use rapid block mode
    # if false use normal block mode
    rapid=True    
    getTriggerInfo=True
    mso=False
    
    print("Set Channels")
    VRange=mps.setChannel(channel="A",coupling="DC",VRange=0.050,VOffset= 0.040,enabled=1,)
    VRange=mps.setChannel(channel="B",coupling="DC",VRange=0.500,VOffset=0.000,enabled=0,)
    VRange=mps.setChannel(channel="C",coupling="DC",VRange=0.050,VOffset= 0.000,enabled=0,)
    VRange=mps.setChannel(channel="D",coupling="DC",VRange=0.050,VOffset= 0.000,enabled=0,)

    if mso: 
        print("Set Digital Ports")
        LogicLevel=mps.setDigitalPort(0, # 0 or 1
                                      logiclevel_V=0, # -5v to 5v
                                      enabled=True)

    print("Set Trigger")
    ret=mps.setSimpleTrigger("A",threshold_V=0.0,direction="Falling",delay=0,
                                timeout_ms=1000,enabled=1)

    print("Set Freq")
    res = mps.setSamplingFrequency(1e9, 4) # freq nosamples
    print ("Interval: %.2f"%(1./res[0]*1e9))

    if rapid:
        captures=3 # number of segments
        mps.memorySegments(captures)
        mps.setNoOfCaptures(captures)
    else: 
        mps.memorySegments(1)

    for i in range(2):

        print("\nRun", i)        
        timeIndisposedMs= mps.runBlock()
        
        print("Wait for trigger")

        while(mps.isReady() == False): 
            time.sleep(0.01)
        print("Trigger fired")

        print("timeIndisposedMs", timeIndisposedMs)

        #for channel in ["A", "B"]:# "C", "D"]:
        dataV = None

        #---------------------------------------------------------------------------------
        if not rapid:
            print("Get Data in Slow Mode ")
        
            dataV = mps.getDataV() 

            '''
            File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 511, in getDataV
    self.checkResult(m) # 0 if all ok(m)
  File "/Users/obertacke/sciebo/Lumi/Skripts/3_Picoscope/picogui/code/picoscope.py", line 261, in checkResult
    raise IOError('Error calling %s: %s (%s)' % (str(inspect.stack()[1][3]), ecName, ecDesc))
OSError: Error calling getDataV: PICO_RATIO_MODE_NOT_SUPPORTED (The selected downsampling mode (used for data reduction) is not allowed.)

            '''
            print("The data:")   
            print(dataV)
                                       
        #---------------------------------------------------------------------------------
        else:
            print("Get data in Rapid Mode")
            dataV=mps.getDataVBulk()
            
            if getTriggerInfo:
                    triggerinfo=mps.GetTriggerInfoBulk()
            

            print("The data:")          
            j=0
            for ch in ["A", "B", "C", "D"]:

                print(ch, dataV[i])
                j+=1
  
                                                                
        #---------------------------------------------------------------------------------
        #dataV = mps.rawToV(channel, dataRaw)
        
                    
            


    ##############################
    print("\nEnd")
    mps.close()

