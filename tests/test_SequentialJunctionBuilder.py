import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration

class test_SequentialJunctionBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.builder = SequentialJunctionBuilder()
        pass


    def test_drawLikeAPainter2L(self):
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=3)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L.xodr"
        odr.write_xml(xmlPath)


    def test_drawLikeAPainter2LWihtoutInternalConnections(self):
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=5, internalConnections=False)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_drawLikeAPainter2LWihtoutInternalConnections.xodr"
        odr.write_xml(xmlPath)

