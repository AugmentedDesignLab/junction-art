import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
# )
import junctionart.extensions as extensions, os
import math
from junctionart.roundabout.ClassicGenerator import ClassicGenerator



class test_ClassicGenerator(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()

        self.builder = ClassicGenerator(country=CountryCodes.US, laneWidth=3)
        pass

    def test_createRoundAboutFromIncidentPoints(self):

        threePoints = [
            {"x": 80, "y": 20, "heading": math.radians(30)},
            {"x": 180, "y": 20, "heading": math.radians(135)},
            {"x": 100, "y": 100, "heading": math.radians(270)},
        ]
        odr = self.builder.generateWithIncidentPointConfiguration(
            ipConfig=threePoints
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )
