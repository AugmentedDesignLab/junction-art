import unittest, os
from junctions.RoadBuilder import RoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration
import junctions

from junctions.Direction import CircularDirection

class test_RoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.roadBuilder = RoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.harvester = JunctionHarvester(outputDir=outputDir, 
                                        outputPrefix='test_', 
                                        lastId=lastId,
                                        minAngle = np.pi / 30, 
                                        maxAngle = np.pi)



    def test_ParamPoly(self):
        tangentX = np.array([9.389829642616592, -7.596531772501544])
        tangentY = np.array([0.0, 5.5192033616035365])

        t = np.array([0, 1])
        x = np.array([0, 17.8605173461395])
        y = np.array([0, -5.803233839653106])
        hermiteX = CubicHermiteSpline(t, x, tangentX)

        hermiteY = CubicHermiteSpline(t, y, tangentY)
        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()

        # scipy coefficient and open drive coefficents have opposite order.
        myRoad = self.roadBuilder.curveBuilder.createParamPoly3(
                                                0, 
                                                isJunction=False,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0]

                                            )

        odr = pyodrx.OpenDrive("test")
        odr.add_road(myRoad)
        odr.adjust_roads_and_lanes()

        extensions.printRoadPositions(odr)

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


    def test_getConnectionRoadBetween(self):
        # test scenario for connection road
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.curveBuilder.createSimple(1, np.pi/4, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(2, 10))
        roads.append(self.roadBuilder.curveBuilder.createSimple(3, np.pi/3, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(4, 10))
        roads.append(self.roadBuilder.curveBuilder.createSimple(5, np.pi/2, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(6, 10))

        roads[0].add_successor(pyodrx.ElementType.junction,1)

        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)
        roads[2].add_successor(pyodrx.ElementType.junction,3)

        roads[3].add_predecessor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)
        roads[3].add_successor(pyodrx.ElementType.road,4,pyodrx.ContactPoint.start)

        roads[4].add_predecessor(pyodrx.ElementType.junction,3)
        roads[4].add_successor(pyodrx.ElementType.junction,5)

        roads[5].add_predecessor(pyodrx.ElementType.road,4,pyodrx.ContactPoint.start)
        roads[5].add_successor(pyodrx.ElementType.road,6,pyodrx.ContactPoint.start)

        roads[6].add_predecessor(pyodrx.ElementType.junction,5)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)
        
        odrName = "test_connectionRoad"
        odr = extensions.createOdr(odrName, roads, [junction])

        lastConnection = self.harvester.junctionBuilder.createLastConnectionForLastAndFirstRoad(7, roads, junction, cp1=pyodrx.ContactPoint.start)
        roads.append(lastConnection)
        odr.add_road(lastConnection)

        # randConnection = self.harvester.junctionBuilder.createConnectionFor2Roads(8, roads[0], roads[4], junction, cp1=pyodrx.ContactPoint.start)
        # roads.append(randConnection)
        # odr.add_road(randConnection)

        # randConnection2 = self.harvester.junctionBuilder.createConnectionFor2Roads(9, roads[2], roads[6], junction, cp1=pyodrx.ContactPoint.start)
        # roads.append(randConnection2)
        # odr.add_road(randConnection2)

        # odr.reset()
        # odr.add_road(lastConnection)
        # odr.adjust_roads_and_lanes()

        odr.resetAndReadjust()
        
        

        # pyodrx.prettyprint(odr.get_element())
        
        odr.write_xml(f"output/test_connectionRoad.xodr")

        # extensions.printRoadPositions(odr)

        extensions.view_road(odr,os.path.join('..', self.configuration.get("esminipath")))
        pass

    

    def test_createMShape(self):

        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createMShape(1, 1, np.pi / 1.5, 10))
        roads.append(pyodrx.create_straight_road(2, 10))


        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)

        odrName = "test_connectionRoad"
        odr = extensions.createOdr(odrName, roads, [junction])

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

    
    
    def test_createMShapeLeftLanes(self):

        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createMShape(1, 1, np.pi / 1.5, 10, laneSides=junctions.LaneSides.LEFT))
        roads.append(pyodrx.create_straight_road(2, 10))


        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)

        odrName = "test_connectionRoad"
        odr = extensions.createOdr(odrName, roads, [junction])

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))
    
    
    def test_createMShapeRightLanes(self):

        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createMShape(1, 1, -np.pi / 1.5, 10, laneSides=junctions.LaneSides.RIGHT, direction=CircularDirection.COUNTERCLOCK_WISE))
        roads.append(pyodrx.create_straight_road(2, 10))


        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)

        odrName = "test_connectionRoad"
        odr = extensions.createOdr(odrName, roads, [junction])

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))