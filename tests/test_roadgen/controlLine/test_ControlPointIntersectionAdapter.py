from pyodrx.enumerations import ContactPoint
import pyodrx
import unittest, math
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
import extensions, os
import logging
logging.basicConfig(level=logging.INFO)


class test_ControlPointIntersectionAdapter(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
        self.adapter = ControlPointIntersectionAdapter()
        self.builder = JunctionBuilderFromPointsAndHeading(country=CountryCodes.US,
                                                            laneWidth=3)

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

    

    def test_createIntersection(self):
        cx = 0
        cy = 0
        point = ControlPoint(position=(cx, cy))
        point.addAdjacents(points=[
            ControlPoint(position=(cx+100, cy+100)),
            # ControlPoint(position=(cx, cy+100)),
            # ControlPoint(position=(cx-100, cy+100)),
            # ControlPoint(position=(cx-100, cy-100)),
            # ControlPoint(position=(cx-100, cy)),
            ControlPoint(position=(cx+100, cy-100))
        ])

        intersection = ControlPointIntersectionAdapter.createIntersection(0, self.builder, point, firstIncidentId=0)
        odr = intersection.odr
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

        cx = 0
        cy = 0
        point = ControlPoint(position=(cx, cy))
        point.addAdjacents(points=[
            ControlPoint(position=(cx+100, cy+100)),
            ControlPoint(position=(cx-50, cy-100)),
            # ControlPoint(position=(cx, cy+100)),
            # ControlPoint(position=(cx-100, cy+100)),
            # ControlPoint(position=(cx-100, cy-100)),
            # ControlPoint(position=(cx-100, cy)),
            ControlPoint(position=(cx+100, cy-100))
        ])

        intersection = ControlPointIntersectionAdapter.createIntersection(0, self.builder, point, firstIncidentId=0)
        odr = intersection.odr
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 


    def test_another(self):

        # roadDefs = [{'x': 14.993254552835499, 'y': 100.44979763658513, 'heading': 0.029991004856882365, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end}, 
        #     {'x': 9.18485099360515e-16, 'y': 115.0, 'heading': 1.5707963267948966, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end}, 
        #     {'x': 9.18485099360515e-16, 'y': 115.0, 'heading': 4.71238898038469, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None}
        # ]
        
        cx = 0
        cy = 100
        point = ControlPoint(position=(cx, cy))
        point.addAdjacents(points=[
            ControlPoint(position=(cx, cy+100)),
            ControlPoint(position=(cx, cy-100)),
            # ControlPoint(position=(cx, cy+100)),
            # ControlPoint(position=(cx-100, cy+100)),
            # ControlPoint(position=(cx-100, cy-100)),
            # ControlPoint(position=(cx-100, cy)),
            ControlPoint(position=(cx+100, cy))
        ])

        intersection = ControlPointIntersectionAdapter.createIntersection(0, self.builder, point, firstIncidentId=0)
        odr = intersection.odr
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 