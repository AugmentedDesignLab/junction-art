import unittest, os
from junctions.RoadBuilder import RoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration



class test_ExtendedOpenDrive(unittest.TestCase):

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
    
 
    def test_AdjustStartPointsForAnyRoadCombinations(self):
        # test scenario for connection road
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createSimpleCurve(1, np.pi/4, False, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(2, 10))
        roads.append(self.roadBuilder.createSimpleCurve(3, np.pi/3, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(4, 10))
        roads.append(self.roadBuilder.createSimpleCurve(5, np.pi/2, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(6, 10))

        roads[0].add_successor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.start)

        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)
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
        odr.add_road(lastConnection)

        # randConnection = self.harvester.junctionBuilder.createConnectionFor2Roads(8, roads[0], roads[4], junction, cp1=pyodrx.ContactPoint.start)
        # roads.append(randConnection)
        # odr.add_road(randConnection)

        # randConnection2 = self.harvester.junctionBuilder.createConnectionFor2Roads(9, roads[2], roads[6], junction, cp1=pyodrx.ContactPoint.start)
        # roads.append(randConnection2)
        # odr.add_road(randConnection2)


        odr.resetAndReadjust()
        
        extensions.printRoadPositions(odr)

        extensions.view_road(odr,os.path.join('..', self.configuration.get("esminipath")))
        pass



    def test_3ConsecutiveConnectionRoads(self):
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createSimpleCurve(1, np.pi/4, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(2, 10, junction=1))
        roads.append(self.roadBuilder.createSimpleCurve(3, np.pi/3, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(4, 10))
        roads.append(self.roadBuilder.createSimpleCurve(5, np.pi/2, True, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(6, 10))

        roads[0].add_successor(pyodrx.ElementType.junction,1)

        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1, pyodrx.ContactPoint.end)
        roads[2].add_successor(pyodrx.ElementType.junction,3, pyodrx.ContactPoint.start)

        roads[3].add_predecessor(pyodrx.ElementType.junction,2,pyodrx.ContactPoint.start)
        # roads[3].add_predecessor(pyodrx.ElementType.junction,2)
        roads[3].add_successor(pyodrx.ElementType.road,4,pyodrx.ContactPoint.start)

        roads[4].add_predecessor(pyodrx.ElementType.junction,3, pyodrx.ContactPoint.end)
        roads[4].add_successor(pyodrx.ElementType.junction,5)

        roads[5].add_predecessor(pyodrx.ElementType.road,4,pyodrx.ContactPoint.start)
        roads[5].add_successor(pyodrx.ElementType.road,6,pyodrx.ContactPoint.start)

        roads[6].add_predecessor(pyodrx.ElementType.junction,5, pyodrx.ContactPoint.end)

        junction = self.junctionBuilder.createJunctionForASeriesOfRoads(roads)
        
        odrName = "test_connectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        lastConnection = self.harvester.junctionBuilder.createLastConnectionForLastAndFirstRoad(7, roads, junction, cp1=pyodrx.ContactPoint.start)
        odr.add_road(lastConnection)

        randConnection = self.harvester.junctionBuilder.createConnectionFor2Roads(8, roads[0], roads[4], junction, cp1=pyodrx.ContactPoint.start)
        roads.append(randConnection)
        odr.add_road(randConnection)

        randConnection2 = self.harvester.junctionBuilder.createConnectionFor2Roads(9, roads[2], roads[6], junction, cp1=pyodrx.ContactPoint.start)
        roads.append(randConnection2)
        odr.add_road(randConnection2)

        odr.reset()
        odr.add_road(lastConnection)
        odr.adjust_roads_and_lanesByPredecessor()

        # odr.resetAndReadjust()
        
        

        # pyodrx.prettyprint(odr.get_element())

        extensions.printRoadPositions(odr)

        extensions.view_road(odr,os.path.join('..', self.configuration.get("esminipath")))
        pass