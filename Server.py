import Pyro4
import constants.Constants as constants
from topology.NetworkMap import NetworkMap
from topology.PhysicalMap import PhysicalMap
from pigs.Pig import Pig


daemon = Pyro4.Daemon()

###### This section is CONFIGURABLE ###########
mode = constants.RuntimeConstants.MODE_TESTING
serverHost = "localhost"
serverPort = 9090
################################################

nameServer = Pyro4.locateNS(serverHost, serverPort)

# The network map will be constant for all iterations
networkMap = NetworkMap(daemon, nameServer)

# Pigs are placed
physicalMap = PhysicalMap(daemon, nameServer, mode)

#Make pigs
for pig in range(0, constants.MapConstants.NUM_PIGS):
    Pig(pig, daemon, nameServer)

print "all pigs registered"

daemon.requestLoop()


