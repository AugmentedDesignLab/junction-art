import unittest
import extensions, os, junctions
import numpy as np
import pyodrx

class test_RandomNetworks(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = junctions.RoadBuilder()

    def test_curve(self):
        roads = []
        roads.append(pyodrx.create_straight_road(0))
        roads.append(self.roadBuilder.createS(1, -np.pi/20, True, curvature = 0.1))
        roads.append(pyodrx.create_straight_road(2))

        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)

        con1 = pyodrx.Connection(0,1,pyodrx.ContactPoint.start)
        con1.add_lanelink(-1,-1)

        junction = pyodrx.Junction('test',1)
        junction.add_connection(con1)

        odr = pyodrx.OpenDrive('test')
        for r in roads:
            odr.add_road(r)
        odr.add_junction(junction)
        odr.adjust_roads_and_lanes()

        extensions.view_road(odr,os.path.join('..','F:\\myProjects\\av\\esmini'))

    
    
    def test_cubicParams(self):
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createParamPoly3(1, isJunction=True))
        roads.append(pyodrx.create_straight_road(2, 1))

        roads[0].add_successor(pyodrx.ElementType.junction,1)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.junction,1)

        con1 = pyodrx.Connection(0,1,pyodrx.ContactPoint.start)
        con1.add_lanelink(-1,-1)

        junction = pyodrx.Junction('test',1)
        junction.add_connection(con1)

        odr = pyodrx.OpenDrive('test')
        for r in roads:
            odr.add_road(r)
        odr.add_junction(junction)
        odr.adjust_roads_and_lanes()

        extensions.view_road(odr,os.path.join('..','F:\\myProjects\\av\\esmini'))
