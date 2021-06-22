import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint


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

        
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [11,1])))
        assert angle == 45
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [10,1])))
        assert angle == 90
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [9,1])))
        assert angle == 135
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [9,0])))
        assert angle == 180
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [9,-1])))
        assert angle == 225
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [10,-1])))
        assert angle == 270
        angle = round(math.degrees(ControlPointIntersectionAdapter.getHeading([10,0], [11,-1])))
        assert angle == 315

    

    def test_orderAjacentCW(self):

        cx = 0
        cy = 0
        point = ControlPoint(position=(cx, cy))
        point.addAdjacents(points=[
            ControlPoint(position=(cx+1, cy+1)),
            ControlPoint(position=(cx, cy-1)),
            ControlPoint(position=(cx, cy+1)),
            ControlPoint(position=(cx-1, cy+1)),
            ControlPoint(position=(cx-1, cy-1)),
            ControlPoint(position=(cx-1, cy)),
            ControlPoint(position=(cx+1, cy-1))
        ])

        ControlPointIntersectionAdapter.orderAjacentCW(point)
        print(point.printAdjacentPointsCW())