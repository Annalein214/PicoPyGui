from __future__ import print_function
from __future__ import absolute_import

import inspect
import numpy as np



class Settings:

    '''
    Reads from daq: int, float, str, bool, dicts
    Doesn't save: lists, objects
    '''

    def __init__(self, log, #daq
        ):
        # while appliation starts load old settings from file
        # save settings into daq
        self.log=log
        self.filename="code/settings.cfg"
        self.attr={}
        self.loadSettings() # they are saved into self.attr for now
        self.log.msg("Loaded settings from file %s"%self.filename)
        #print(self.attr)
        
    def saveSetting(self, var, val):
        # first save in our local repo
        if "." in var: # dictionaries
            d,e=var.split(".")
            if d not in self.attr:
                self.attr[d]={}
            self.attr[d][e]=val
        else:
            self.attr[var]=val

        # now save into the file, sadly full file needs to be re-written
        self.setfile=open(self.filename, "w")
        items=self.attr.items() # python3
        for attr, value in items:
            tipe=type(value)
            #print(attr, value, tipe)
            if tipe!=dict and tipe!=list and tipe!=np.ndarray:
                self.setfile.write("%s %s\n" % (attr, value))
            elif tipe==dict:
                keys=value.items()
                for entry, v in keys:
                    self.setfile.write("%s.%s %s\n" % (attr, entry, v))
        self.setfile.close()

    def saveSettings(self, daq):
        
        # write to file
        self.setfile=open(self.filename, "w")
        #help(self.attributes)
        items=self.attributes.items() # python3
        for attr, (tipe, value) in items:
            #if attr=="voltagerange":
            #    print ("save",attr, (tipe, value))
            if tipe!=dict and tipe !=list and tipe!=np.array:
                if tipe==str or tipe==int or tipe==float or tipe==bool:
                    self.setfile.write("%s %s\n" % (attr,getattr(daq, attr)))
                else:
                    #print("Error saving:", attr,getattr(self.daq, attr))
                    pass
            elif tipe==dict:
                # if dict
                try:
                    keys=value.keys() # python3
                except:
                    keys=value.iterkeys() # python2
                for entry in keys: # iterkeys
                    #if entry not in ["LowestPriority", "InheritPriority"]:
                        #print ("\n",attr, entry)   
                        self.setfile.write("%s.%s %s\n" % (attr, entry,getattr(daq, attr)[entry]))
            elif tipe==list:
                # these are data arrays which shouldn't be saved here
                pass
            else:
                print("Not know how to save:", attr,getattr(daq, attr))
        self.setfile.close()
        
    def convertType(self, value, tipe, verbose=False):
        if tipe==str:
            return str(value)
        elif tipe==int:
            return int(float(value))
        elif tipe==float:
            return float(value)
        elif tipe==bool:
            if type(value)==str:
                if value=="False":
                    return False
                else:
                    return True
            elif type(value)==int:
                if value==0:
                    return False
                else:
                    return True
            else:
                return bool(value)
        else:
            return value
            
    def guessType(self, value):
        if value=="True" or value=="False":
            return bool
        try:
            integer=int(value)
            return int
        except:
            pass
        try:
            integer=float(value)
            return float
        except:
            pass

        return str

    def loadSettings(self):
        self.setfile=open(self.filename, "r")
        for line in self.setfile:
            #print (line)
            n,v=line.replace("\n", "").split(" ")
            #print(n,v, type(v))
            tipe=self.guessType(v)
            
            if "." in n: # dictionaries
                d,e=n.split(".")
                if d not in self.attr:
                    self.attr[d]={}
                self.attr[d][e]=self.convertType(v, tipe)
            else:
                
                self.attr[n]=self.convertType(v, tipe)
        self.setfile.close()
##########################################################################################
'''
if __name__ == "__main__":

    # dummy daq
    names=["triggerenabled", 
            "measurementrunning",
            "measurementenabled",
            "threadIsStopped",
            "loopduration",
            "triggerchannel",
            "triggervoltage",
            "triggermode"
          ]
        # directories with entries A B C D
    dirs=["channelEnabled",
              "coupling",
              "voltagerange",
              "offset",
              "channelEnabled",
    
             ]
    entries=["A", "B", "C", "D"]
    
    class DAQ:
        blub=False            
        
    daq=DAQ()
    
    for name in names:
        setattr(daq, name, "1")
        
    for dyr in dirs:
        d={}
        for entry in entries:
            d[entry]="2"
        setattr(daq, dyr, d)
        
        
    s=Settings(daq)
    s.saveSettings()
    s.loadSettings()
    s.saveSettings()

'''