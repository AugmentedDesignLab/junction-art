import unittest, os
import numpy as np
import pyodrx, extensions
from library.Configuration import Configuration

from junctions.threeWayJunction import ThreeWayJunctionBuilder
from extensions.OpenDriveHelper import OpenDriveHelper


class test_OpenDriveHelper(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.threeWayJunctionBuilder = ThreeWayJunctionBuilder(minAngle=np.pi/9, 
                                                               maxAngle=np.pi * .25,
                                                               straightRoadLen=20)

    
    def test_RotateOpenDrive(self):
        angleBetweenRoads = np.pi/4
        odr = self.threeWayJunctionBuilder.ThreeWayJunctionWithAngle(odrId=1,
                                                                    angleBetweenRoads=angleBetweenRoads,
                                                                    maxLanePerSide=4,
                                                                    minLanePerSide=2,
                                                                    cp1=pyodrx.ContactPoint.end
                                                                    )
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))
        # extensions.printRoadPositions(odr)
        openDriveHelper = OpenDriveHelper(odr=odr)
        RotatedODR = openDriveHelper.rotateOpenDrive(startX=0.0, startY=0.0, heading=np.pi)

        # RotatedODR = extensions.rotateOpenDrive(odr=odr, startX=0.0, startY=0.0, heading=np.pi)
        extensions.printRoadPositions(RotatedODR)
        extensions.view_road(RotatedODR, os.path.join('..', self.configuration.get("esminipath")))


    def test_getMinMaxRoadIDFromODR(self):
        angleBetweenRoads = np.pi/4
        odr = self.threeWayJunctionBuilder.ThreeWayJunctionWithAngle(odrId=1,
                                                                    angleBetweenRoads=angleBetweenRoads,
                                                                    maxLanePerSide=2,
                                                                    minLanePerSide=2,
                                                                    cp1=pyodrx.ContactPoint.end
                                                                    )
        openDriveHelper = OpenDriveHelper(odr=odr)
        minID, maxID = openDriveHelper.getMinMaxRoadIDFromODR()
        print(minID, maxID)

    
    def test_updateOpenDriveRoadIDStartFrom(self):
        angleBetweenRoads = np.pi/4
        odr = self.threeWayJunctionBuilder.ThreeWayJunctionWithAngle(odrId=1,
                                                                    angleBetweenRoads=angleBetweenRoads,
                                                                    maxLanePerSide=1,
                                                                    minLanePerSide=1,
                                                                    cp1=pyodrx.ContactPoint.end
                                                                    )
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))
        openDriveHelper = OpenDriveHelper(odr=odr)
        new_odr = openDriveHelper.updateOpenDriveRoadIDStartFrom(startRoadID=100)
        extensions.printRoadPositions(new_odr)
        extensions.view_road(new_odr, os.path.join('..', self.configuration.get("esminipath")))

