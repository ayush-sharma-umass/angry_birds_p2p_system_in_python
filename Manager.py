import Pyro4
import constants.Constants as constants
from bird.Bird import Bird
import config

import time


mode = constants.RuntimeConstants.MODE_TESTING


serverHost1 = config.serverHost1
serverPort1 = config.serverPort1
ns1 = Pyro4.locateNS(serverHost1, serverPort1)

print "Manager", ns1
serverHost2 = config.serverHost2
serverPort2 = config.serverPort2
ns2 = Pyro4.locateNS(serverHost2, serverPort2)
print "manager", ns2

physicalMapProxy = constants.UriConstants.URI_PHYSICAL_MAP
physicalMapUri = ns1.lookup(physicalMapProxy)
physicalMap = Pyro4.Proxy(physicalMapUri)


networkMapProxy = constants.UriConstants.URI_NETWORK_MAP
networkMapUri = ns1.lookup(networkMapProxy)
networkMap = Pyro4.Proxy(networkMapUri)


nearestPigIP = physicalMap.getNearestPigIP()
print "nearest pig IP: {}".format(nearestPigIP)

# get flight details from bird
(duration, destination) = Bird(mode).getFlightDetails()
print "Bird destination: {}".format(destination)

# We need to provide each pig with list of all possible lookup servers
for pigIP in range(0, constants.MapConstants.NUM_PIGS):
    pigProxy = str(pigIP)
    pigUri = ""
    if (pigIP %2 == 0):
        pigUri = ns1.lookup(pigProxy)
    else:
        pigUri = ns2.lookup(pigProxy)
    print pigUri
    pig = Pyro4.Proxy(pigUri)
    pig.loadNamerServer([ns1, ns2])


nearestPigProxy = str(nearestPigIP)
nearestPigUri = ""
if (nearestPigIP %2 == 0):
    nearestPigUri = ns1.lookup(nearestPigProxy)
else:
    nearestPigUri = ns2.lookup(nearestPigProxy)

nearestPig = Pyro4.Proxy(nearestPigUri)  # use name server object lookup uri shortcut


# message is a tuple
currentTime = time.time()
message = [constants.MessageConstants.MSGTYPE_BIRD_APPROACHING, constants.MessageConstants.DEFAULT_MESSAGE_ID, constants.MessageConstants.ID_MANAGER, destination, currentTime + duration]
nearestPig.pushMessage(message)

# start timer: waits for sometime before checking the result
time.sleep(10)
# query status
for pigIP in range(0, constants.MapConstants.NUM_PIGS):
    pigProxy = str(pigIP)
    pigUri = ""
    if (pigIP %2 == 0):
        pigUri = ns1.lookup(pigProxy)
    else:
        pigUri = ns2.lookup(pigProxy)
    pig = Pyro4.Proxy(pigUri)
    print "Status of pig {} :  {}".format(pig, pig.checkStatus())




