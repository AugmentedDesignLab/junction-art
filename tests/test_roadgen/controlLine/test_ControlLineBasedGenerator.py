import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator
import extensions, os


class test_ControlLineBasedGenerator(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
    

    def test_generateWithHorizontalControlines(self):

        generator = ControlLineBasedGenerator((500, 500), debug=True)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlines", 5)
        generator.grid.plot()
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 