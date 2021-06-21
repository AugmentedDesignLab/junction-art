import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter


class test_ControlPointIntersectionAdapter(unittest.TestCase):

    def test_getHeading(self):
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [1,1])))
        assert angle == 45
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [0,1])))
        assert angle == 90
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [-1,1])))
        assert angle == 135
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [-1,0])))
        assert angle == 180
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [-1,-1])))
        assert angle == 225
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [0,-1])))
        assert angle == 270
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([0,0], [1,-1])))
        assert angle == 315