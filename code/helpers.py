# small stuff and classes

##########################################################################################
# small stuff

import platform

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


##########################################################################################
