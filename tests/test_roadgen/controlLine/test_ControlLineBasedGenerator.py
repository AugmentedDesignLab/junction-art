import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator
import extensions, os, logging
import numpy as np
logfile = 'ControlLineBasedGenerator.log'
logging.basicConfig(level=logging.INFO, filename=logfile)


class test_ControlLineBasedGenerator(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
        with open(logfile, 'w') as f:
            f.truncate()
        pass
    

    def test_generateWithHorizontalControlines(self):

        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=2, randomizeDistance=False)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlines", 5)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlines.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

    def test_generateWithHorizontalControlinesCurvy(self):

        generator = ControlLineBasedGenerator((800, 800), debug=True, seed=2, randomizeDistance=True, randomizeHeading=True)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesCurvy", 5)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlinesCurvy.xodr"
        odr.write_xml(xmlPath)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

    def test_generateWithHorizontalControlinesBig(self):
        generator = ControlLineBasedGenerator((2000, 2000), debug=True, seed=1)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesBig", 10)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlinesBig.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 