import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)

class test_SequentialJunctionBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.builder = SequentialJunctionBuilder(straightRoadLen=20)
        
        self.randomState =self.configuration.get("random_state")

        pass


    def test_drawLikeAPainter2L(self):
        maxNumberOfRoadsPerJunction = 3
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)


    def test_drawLikeAPainter2LWihtoutInternalConnections(self):
        maxNumberOfRoadsPerJunction = 5
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, internalConnections=False)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_drawLikeAPainter2LWihtoutInternalConnections.xodr"
        odr.write_xml(xmlPath)


    def test_createWithRandomLaneConfigurations(self):

        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=1, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_FIRST)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-first.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=1, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_LAST)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-last.xodr"
        odr.write_xml(xmlPath)


        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=1, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any.xodr"
        odr.write_xml(xmlPath)

