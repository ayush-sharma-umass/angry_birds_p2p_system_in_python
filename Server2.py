import Pyro4
import constants.Constants as constants
from pigs.Pig import Pig
import config



###### This section is CONFIGURABLE ###########
mode = config.mode
serverHost = config.serverHost2
serverPort = config.serverPort2
################################################


daemon2 = Pyro4.Daemon(host = serverHost, port = serverPort)
#Pyro4.Daemon.serveSimple(daemon = custom_daemon)

print "Server 1: "
print serverHost, serverPort

nameServer = Pyro4.locateNS(serverHost, serverPort)

#Make pigs
for pig in range(0, constants.MapConstants.NUM_PIGS):
    if (pig %2 == 1):
        Pig(pig, daemon2, nameServer)


daemon2.requestLoop()


