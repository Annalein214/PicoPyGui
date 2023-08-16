# small stuff and classes

##########################################################################################
# small stuff

import platform, time

if platform.system() == 'Linux' or platform.system()=="Darwin": # linux and mac
    red='\033[31;1m' # for errors
    green='\033[32;1m' #
    yellow='\033[33;1m' #
    lila='\033[34m' #
    pink='\033[35;1m' #
    blue='\033[36;1m' #
    nc='\033[0m'
else:
    red='' # for errors
    green='' #
    yellow=''
    lila=''
    pink=''
    blue=''
    nc=''



##########################################################################################
def timestring_humanReadable(t): # input given by time.time()
    s=time.localtime(float(t))
    return "%4d_%02d_%02d_%02d_%02d_%02d" % (s.tm_year,s.tm_mon,s.tm_mday,s.tm_hour,s.tm_min,s.tm_sec)

def dateTime(t):
    s=time.localtime(float(t))
    return "%4d.%02d.%02d %02d:%02d:%02d" % (s.tm_year,s.tm_mon,s.tm_mday,s.tm_hour,s.tm_min,s.tm_sec)

def dateTime_plusHours(t, hours):
    '''
    get time string plus certain number of hours
    '''
    t=float(t)+60*60*int(hours)
    s=time.localtime(float(t))
    return "%4d.%02d.%02d %02d:%02d:%02d" % (s.tm_year,s.tm_mon,s.tm_mday,s.tm_hour,s.tm_min,s.tm_sec)


##########################################################################################
