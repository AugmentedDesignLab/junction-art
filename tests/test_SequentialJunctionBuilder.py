import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration
import pyodrx

class test_SequentialJunctionBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.builder = SequentialJunctionBuilder()
        
        self.randomState =self.configuration.get("random_state")

        pass


    def test_drawLikeAPainter2L(self):
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=5)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L.xodr"
        odr.write_xml(xmlPath)


    def test_drawLikeAPainter2LWihtoutInternalConnections(self):
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=3, internalConnections=False)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_drawLikeAPainter2LWihtoutInternalConnections.xodr"
        odr.write_xml(xmlPath)


    def test_createWithRandomLaneConfigurations(self):

        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 0, maxNumberOfRoadsPerJunction=3, maxLanePerSide=2, minLanePerSide=1, internalConnections=False, cp1=pyodrx.ContactPoint.end)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations.xodr"
        odr.write_xml(xmlPath)

