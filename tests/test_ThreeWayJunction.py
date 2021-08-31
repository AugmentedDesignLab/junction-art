import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from junctions.threeWayJunction import ThreeWayJunctionBuilder
import junctionart.extensions as extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)

class test_ThreeWayJunction(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.seed = 2
        self.builder = ThreeWayJunctionBuilder(
                                                minAngle=np.pi/9, 
                                                maxAngle=np.pi * .25,
                                                straightRoadLen=20
                                                )

        self.randomState =self.configuration.get("random_state")

        pass

    def test_ThreeWayJunctionWithAngle(self):
        angleBetweenRoads = np.pi/4
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        # extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)

    def test_ThreeWayJunctionWithRandomAngle(self):

        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    firstRoadId=100,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)


        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        # extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)

        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        # extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)

        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        # extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)

        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        odr = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        # extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)

    def test_ThreeWayJunctionRandomAngleIntersection(self):
        angleBetweenRoads = ((7/18) * np.random.random() + (1/9)) * np.pi
        intersection = self.builder.ThreeWayJunctionWithAngle(id=1,
                                                    angleBetweenRoads=angleBetweenRoads,
                                                    firstRoadId=100,
                                                    maxLanePerSide=4,
                                                    minLanePerSide=2,
                                                    cp1=pyodrx.ContactPoint.end,
                                                    getAsOdr=False)
        
        odr = intersection.odr
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)