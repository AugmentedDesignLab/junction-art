
import unittest, os
import numpy as np

from library.Configuration import Configuration
from junctions.threeWayJunction import ThreeWayJunctionBuilder
import pyodrx
import junctionart.extensions as extensions
from junctions.ODRHelper import ODRHelper

class test_ODRHelper(unittest.TestCase):

    def setUp(self):

        self.configuration = Configuration()
        self.threeWayJunctionBuilder = ThreeWayJunctionBuilder(minAngle=np.pi/9, 
                                                               maxAngle=np.pi * .25,
                                                               straightRoadLen=20)


    def test_updateRoadIDStartFrom(self):
        angleBetweenRoads = np.pi/4
        odr = self.threeWayJunctionBuilder.ThreeWayJunctionWithAngle(odrId=1,
                                                                    angleBetweenRoads=angleBetweenRoads,
                                                                    maxLanePerSide=2,
                                                                    minLanePerSide=2,
                                                                    cp1=pyodrx.ContactPoint.end
                                                                    )

        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))
        ODRHelper.updateRoadIDStartFrom(odr=odr, startRoadID=5)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


