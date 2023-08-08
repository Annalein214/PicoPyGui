import math

class dummyScope():
    def __init__(self):
        self.dummy=True

    NUM_CHANNELS = 4
    CHANNELS     = {"A": 0, "B": 1, "C": 2, "D": 3,
                    "External": 4, "MaxChannels": 4, "TriggerAux": 5}

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


    CHANNEL_COUPLINGS = {"DC": 1, "AC": 0}

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

    def maxOffset(self, coupling, voltagerange):

        if coupling=="DC50" or coupling=="DC":
            return self.MAXOFFSETDC[voltagerange]
        else:
            return self.MAXOFFSETAC[voltagerange]

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