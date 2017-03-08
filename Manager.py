import Pyro4
import constants.Constants as constants
from bird.Bird import Bird
import time

mode = constants.RuntimeConstants.MODE_RANDOM
physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
physicalMap = Pyro4.Proxy(physicalMapURI)

networkURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_NETWORK_MAP
networkMap = Pyro4.Proxy(networkURI)

nearestPigIP = physicalMap.getNearestPigIP()
print nearestPigIP

# get flight details from bird
(duration, destination) = Bird(mode).getFlightDetails()
print "Bird destination: {}".format(destination)

nearestPigURI = constants.UriConstants.URI_PYRONAME + str(nearestPigIP)
nearestPig = Pyro4.Proxy(nearestPigURI)  # use name server object lookup uri shortcut

# message is a tuple
currentTime = time.time()
message = [constants.MessageConstants.MSGTYPE_BIRD_APPROACHING, constants.MessageConstants.DEFAULT_MESSAGE_ID, constants.MessageConstants.ID_MANAGER, destination, currentTime + duration]
print nearestPig.pushMessage(message)

# start timer
time.sleep(10)
# query status
for pig in range(0, constants.MapConstants.NUM_PIGS):
    pigURI = constants.UriConstants.URI_PYRONAME + str(pig)
    pigProxy = Pyro4.Proxy(pigURI)
    print "Status of pig {} :  {}".format(pig, pigProxy.checkStatus())




