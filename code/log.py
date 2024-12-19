from code.helpers import red, green, yellow, lila, pink, blue, nc
import time

class log:
    def __init__(self, save=False, level="debug", directory="./data/", end="log"):
        self.save=save
        self.directory=directory
        self.level=level # ["debug", "log", "error"]

        if self.save:
            t=time.time()
            self.filename=self.directory+"/"+self.formatTimeforLog(t)+"."+end            
            print (yellow+"Log messages will be saved to "+nc, self.filename)

        self.outfile=None

    def formatTimeforLog(self, t): # input given by time.time()
        s=time.localtime(float(t))
        return "%4d_%02d_%02d_%02d_%02d_%02d" % (s.tm_year,s.tm_mon,s.tm_mday,s.tm_hour,s.tm_min,s.tm_sec)

    def debug(self, message):
        if self.level in ["debug"]:
            self.__print__("DEBUG: "+message, "")

    def info(self, message):
        if self.level in ["debug", "log", "info"]:
            self.__print__("INFO: "+message, "")

    def warning(self, message):
            self.__print__("WARN: "+message, yellow)

    def error(self, message):
        self.__print__("ERROR: "+message, red)

    def __print__(self, message, color):
        if self.save:
            t=time.time()
            self.logfile=open(self.filename, "a")
            self.logfile.write("%20s: %s\n" % (self.formatTimeforLog(t),message))
            self.logfile.close()
        print (color+message+nc)

    def msg(self, message):
        self.__print__("MSG: "+message, "")

    def endLogging(self,):
        self.debug("End logging.")
            
