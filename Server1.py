import Pyro4
import constants.Constants as constants
from topology.NetworkMap import NetworkMap
from topology.PhysicalMap import PhysicalMap
from pigs.Pig import Pig
import config



###### This section is CONFIGURABLE ###########
mode = config.mode
serverHost = config.serverHost1
serverPort = config.serverPort1
################################################

daemon1 = Pyro4.Daemon("localhost")

nameServer = Pyro4.locateNS(serverHost, serverPort)
print "Server 1: "
print nameServer

# The network map will be constant for all iterations
networkMap = NetworkMap(daemon1, nameServer)

# Pigs are placed
physicalMap = PhysicalMap(daemon1, nameServer, mode)

#Make pigs
for pig in range(0, constants.MapConstants.NUM_PIGS):
    if (pig %2 == 0):
        Pig(pig, daemon1, nameServer)

print "all pigs registered"

daemon1.requestLoop()


