import constants.Constants as constants
import utils.Utils as utils

class Bird:

    def __init__(self, mode):
        if (mode == constants.RuntimeConstants.MODE_RANDOM):
            self._makeBird()
        else:
            self._testing_makeBird()

    def _makeBird(self):
        """
        Makes a random bird
        :return:
        """
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.duration = utils.getInRange(constants.BirdConstants.MIN_DURATION, constants.BirdConstants.MAX_DURATION)
        self.destination = utils.getInRange(constants.MapConstants.MAP_BEGINS,
                                            constants.MapConstants.MAP_SIZE - 1)


    def getFlightDetails(self):
        flightDetails = (self.duration, self.destination)
        return flightDetails


    def _testing_makeBird1(self):
        """
        Allows to make a custom bird object
        :return:
        """
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 6
        self.duration = 10

    def _testing_makeBird2(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 2
        self.duration = 9  # duration in seconds

    def _testing_makeBird3(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 2
        self.duration = 10  # duration in seconds

    def _testing_makeBird4(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 1
        self.duration = 10  # duration in secondds

    def _testing_makeBird5(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 2
        self.duration = 10  # duration in seconds

    def _testing_makeBird6(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 4
        self.duration = 20 # duration in seconds





