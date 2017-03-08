import topology.NetworkMap as networkMap
import constants.Constants as constants
import Pyro4
import time



@Pyro4.expose
class Pig:
    msgID = 1
    birdAttackTime = constants.PigConstants.PIG_DEFAULT_BIRD_ATTACKTIME
    def __init__(self, ip, daemon, nameServer):
        """
        self.ip = pig's ip
        self.messageCache = initial message chache
        self.status = The pig's initial status
        self.alertCaller = the IP that alerted you
        self.orginalSender = Flag if this pig was the original sender of TAKE_SHELTER
        :param ip: Integer
        :param daemon: daemon to register
        :param nameServer: nameserver to register
        """
        self.ip = ip
        self.messageCache = []
        self._registerOnServer(daemon, nameServer)
        self.status = constants.PigConstants.PIG_ALIVE
        self.alertCaller = -1
        self.orginalSender = False

    def pushMessage(self, message):
        """
        The public function which sends the message according to its type to various handlers
        :param message: message packet
        :return:
        """
        currentTime = time.time()
        if currentTime < Pig.birdAttackTime and message[1] not in self.messageCache:
            # checks if the bird has already landed
            self.messageCache.append(message[1])
            if (message[0] == constants.MessageConstants.MSGTYPE_BIRD_APPROACHING):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self._handleBirdApproachingMessage(message)
            elif (self.status == constants.PigConstants.PIG_ALIVE and message[0] == constants.MessageConstants.MSGTYPE_TAKE_SHELTER):
                # this is to ensure that if pig has been DEAD, it does not pass this
                # message on to other pigs
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self._handleTakeShelterMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_STATUS):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleStatusMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                print "Acknowledgement receiver: {}".format(message[4])
                self._handleAcknowledgement(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_I_AM_SAFE):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleIAmSafe(message)

    def handleIAmSafe(self, message):
        """
        This method handles the I_AM_SAFE message.
        I_AM_SAFE message is sent by an original alerting node to its physical neighbour to mark itself safe now.
        An I_AM_SAFE message has following params:
        0: Message Type,
        1: Message ID
        2: Message sender
        3: Receiver's physical address
        :param message: the message packet
        :return:
        """
        ownPhysicalAddress = self._getPhysicalAddress()
        if (message[3] == ownPhysicalAddress):
            # If you were the intended receiver
            self.status = constants.PigConstants.PIG_EVADED
        else:
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendIAmSafe(nbr, message)

    def sendIAmSafe(self, nbr, message):
        """
        This method sends the I_AM_SAFE message.
        I_AM_SAFE message is sent by an original alerting node to its physical neighbour to mark itself safe now.
        :param nbr: The IP neighbour
        :param message: message packet
        :return:
        """
        time.sleep(constants.MapConstants.DEFAULT_WAIT_TIME) # we add a delay in message propagation
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def _handleBirdApproachingMessage(self, message):
        """
        This function handles the BIRD_APPROACHING message.
        THE BIRD_APPROACHING message has following parameters:
        0: Message Type,
        1: Message ID
        2: Message sender
        3: Attack Target coordinate
        4: The bird attack time.
        :param message:
        :return:
        """
        targetHit = message[3]
        Pig.birdAttackTime = message[4]

        if (self._isGettingAffected(targetHit)):
            self._sendAlert()

        else:
            self.nbrs = self._getNetworkNeighbours()
            for nbr in self.nbrs:
                self._sendBirdApproachingMessage(nbr, message)

    def _sendBirdApproachingMessage(self, nbr, message):
        """
        This function relays the BIRD_APPROACHING message to it network neighbours.
        :param nbr: the neighbour's IP
        :param message: message packet
        :return:
        """
        time.sleep(constants.MapConstants.DEFAULT_WAIT_TIME)
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        message[2] = self.ip
        pigProxy.pushMessage(message)

    def _handleTakeShelterMessage(self, message):
        """
        This function handles the TAKE_SHELTER message.
        A TAKE_SHELTER message has following params:
        0: Message Type,
        1: Message ID
        2: Message sender
        3: Target Physical address
        4: Sender Type : {Original, Relay}
        :param message: message packet
        :return:
        """
        shelterAddress = message[3]
        ownPhysicalAddress = self._getPhysicalAddress()
        if (shelterAddress == ownPhysicalAddress):
            # If the message was intended for this pig
            if (self._canMove()):
                # If this can move to safety
                # send acknowledgement to its caller
                self.status = constants.PigConstants.PIG_ALIVE
                newmessage = [constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT,
                           Pig.msgID, self.ip,
                           constants.MessageConstants.ACK_TYPE_POSITIVE, message[2]]
                Pig.msgID += 1
                self._sendAcknowledgement(message[2], newmessage)

            else:
                # alert your immediate neighbours to move and set your status to be dead if you received from original sender
                if (message[4] == constants.PigConstants.PIG_SENDER_ORIGINAL):
                    self.status = constants.PigConstants.PIG_DEAD
                # This is the IP address of the caller. Save it so that you can pass Acknowledgement to him.
                self.alertCaller = message[2]
                message1 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER, Pig.msgID, self.ip, ownPhysicalAddress + 1,
                              constants.PigConstants.PIG_SENDER_RELAY]
                Pig.msgID += 1
                message2 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER, Pig.msgID, self.ip,
                              ownPhysicalAddress - 1,
                              constants.PigConstants.PIG_SENDER_RELAY]
                Pig.msgID += 1
                nbrs = self._getNetworkNeighbours()
                for nbr in nbrs:
                    self._sendTakeShelterMessage(nbr, message1)
                    self._sendTakeShelterMessage(nbr, message2)

        else:
            # The message was not for this pig
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self._sendTakeShelterMessage(nbr, message)

    def _sendTakeShelterMessage(self, nbr, message):
        """
        This functions sends the take shelter message to its neighbours.
        :param nbr: neighbour IP
        :param message: message packet
        :return:
        """
        time.sleep(constants.MapConstants.DEFAULT_WAIT_TIME)
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def checkStatus(self):
        """
        Returns status
        Status can be three types:
        1) ALIVE
        2) DEAD
        3) EVADED - basically it means alive but could have been affected
        :return:
        """
        return self.status

    def _handleAcknowledgement(self, message):
        """
        This function handles the acknowledgement message.
        An ACKNOWLEDGEMENT message contains the following parameters:
        0: Message Type,
        1: Message ID
        2: Message sender
        3: Acknowledgement type.
        4: Acknowledgement reciever's IP address
        :param message: message packet
        :return:
        """
        receiverIP = message[4]
        if (self.ip == receiverIP):
            # If this pig is the intended receiver
            if (self.orginalSender == True):
                # This pig started the original alert

                self.status = constants.PigConstants.PIG_EVADED
                ownPhysicalAddress = self._getPhysicalAddress()

                # This pig now needs to alert its physical neighbours that he is safe.
                message1 = [constants.MessageConstants.MSGTYPE_I_AM_SAFE,
                       Pig.msgID, self.ip, ownPhysicalAddress + 1]
                Pig.msgID += 1
                message2 = [constants.MessageConstants.MSGTYPE_I_AM_SAFE,
                            Pig.msgID, self.ip, ownPhysicalAddress - 1]
                Pig.msgID += 1
                nbrs = self._getNetworkNeighbours()
                for nbr in nbrs:
                    self.sendIAmSafe(nbr, message1)
                    self.sendIAmSafe(nbr, message2)

            else:
                #If this pig is not the original sender
                acknowedgementType = message[3]
                if acknowedgementType == constants.MessageConstants.ACK_TYPE_POSITIVE:
                    self.status = constants.PigConstants.PIG_EVADED
                    if self.alertCaller != -1:
                        message[4] = self.alertCaller
                        message[2] = self.ip
                    nbrs = self._getNetworkNeighbours()
                    for nbr in nbrs:
                        self._sendAcknowledgement(nbr, message)
        else:
            # The message is not intended for this pig. So he needs to relay it.
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self._sendAcknowledgement(nbr, message)

    def _sendAcknowledgement(self, nbr, message):
        """
        This function sends acknowledgement to its neighbours.
        :param nbr: neighbour IP
        :param message: message packet
        :return:
        """
        time.sleep(constants.MapConstants.DEFAULT_WAIT_TIME)
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def _sendAlert(self):
        """
        Pig is in threat. So, it sends a Take Shelter message to its immediate PHYSICAL neighbours.
        If the pig can move then it forwards it to no one.
        The message TAKE_SHELTER is forwarded only when the pig can't move.
        :return:
        """
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        ownPhysicalAddress = self._getPhysicalAddress()

        if physicalMap.isEmptySpace(ownPhysicalAddress + 1) or physicalMap.isEmptySpace(ownPhysicalAddress - 1):
            # Pig can move to safety. No need to relay threat.
            pass
        else:
            # Pig changes status until an acknowledgement comes
            self.status = constants.PigConstants.PIG_DEAD
            self.orginalSender = True
            # For physical address to immediate right
            message1 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                       Pig.msgID, self.ip, ownPhysicalAddress + 1, constants.PigConstants.PIG_SENDER_ORIGINAL]
            Pig.msgID += 1
            # For physical address to immediate left
            message2 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                       Pig.msgID, self.ip, ownPhysicalAddress - 1, constants.PigConstants.PIG_SENDER_ORIGINAL]
            Pig.msgID += 1
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self._sendTakeShelterMessage(nbr, message1)
                self._sendTakeShelterMessage(nbr, message2)

    def _isGettingAffected(self, targetHit):
        """
        This function checks if pig is getting affected.
        It sees if the bird is attacking him or if the bird is attacking a wall and he is beside the wall.
        :param targetHit: the coordinate where bird is falling
        :return: boolean
        """
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        physicalAddress = self._getPhysicalAddress()
        if (physicalAddress == targetHit) or (physicalAddress == targetHit + 1 and physicalMap.isStone(targetHit)) or (physicalAddress == targetHit - 1 and physicalMap.isStone(targetHit)):
            return True
        return False

    def _canMove(self):
        """
        This function checks to see, if there is an empty space to move.
        :return: boolean
        """
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        ownPhysicalAddress = physicalMap.getPhysicalAddress(self.ip)
        if (physicalMap.isEmptySpace(ownPhysicalAddress - 1) == True or physicalMap.isEmptySpace(ownPhysicalAddress + 1) == True):
            return True
        return False

    def _getPhysicalAddress(self):
        """
        This function returns the physical address of the pig.
        :return: physical address (integer)
        """
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        return physicalMap.getPhysicalAddress(self.ip)

    def _getNetworkNeighbours(self):
        """
        This function returns a list of neighbours of the pig
        :return: a list of neighbours
        """
        networkURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_NETWORK_MAP
        networkMap = Pyro4.Proxy(networkURI)
        nbrList = networkMap.getNetworkNeighbours(self.ip)
        return nbrList

    def _registerOnServer(self, daemon, nameServer):
        """
        This function registers the pig with the server
        :param daemon: daemon process
        :param nameServer: server name
        :return:
        """
        # register this pig with the name server
        uri = daemon.register(self)
        nameServer.register(str(self.ip), uri)
        print("Pig registered with ip: {}".format(self.ip))




# The Message received has following structure:
# 0) Message Type
# 1) Message ID
# 2) Message Caller


# Bird_Approaching params
# 3) Target Coordinate
# 4) Duration

# Take_Shelter params
# 3) Target Coordinate
# 4) Sender type  = {Original, Relay}

# Acknowldegment params
# 3) Acknowledgement type
# 4) Acknowledgement receiver ip

# CheckStatus params
#   return state

# IAmSafe params
# 3) receiver's physical Address