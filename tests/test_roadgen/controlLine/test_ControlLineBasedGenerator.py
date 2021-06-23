import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator
import extensions, os, logging
logfile = 'ControlLineBasedGenerator.log'
logging.basicConfig(level=logging.INFO, filename=logfile)


class test_ControlLineBasedGenerator(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
        with open(logfile, 'w') as f:
            f.truncate()
        pass
    

    def test_generateWithHorizontalControlines(self):

        generator = ControlLineBasedGenerator((1500, 1500), debug=True)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlines", 7)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 