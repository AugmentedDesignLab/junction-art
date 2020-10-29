import numpy as np
import os
import pyodrx 
import math
import dill
from junctions.RoadBuilder import RoadBuilder
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
import extensions


class JunctionMerger:

    

    def __init__(self, outputDir, outputPrefix='R3_', lastId=0, minAngle = np.pi / 10, maxAngle = np.pi - .0001):
        """The angle between two connected roads are >= self.minAngle <= self.maxAngle

        Args:
            outputDir ([type]): [description]
            outputPrefix ([type]): [description]
            lastId (int, optional): [description]. Defaults to 0.
            minAngle ([type], optional): [description]. Defaults to np.pi/10.
            maxAngle ([type], optional): [description]. Defaults to np.pi.
        """

        self.destinationPrefix = os.path.join(outputDir, outputPrefix)
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.lastId = lastId

        self.roadBuilder = RoadBuilder()

        pass


    def merge2R2L(self, odrs):

        # how do we merge 2 road junctions?
        
        # 1 find connectionRoad in the first, it's predecessor is first road, successor is the second road.

        connectionRoadsFirst = extensions.getConnectionRoads(odrs[0].roads, odrs[0].junction)
        connectionRoadFirst = connectionRoadsFirst[0]
        connectionRoadsSecond = extensions.getConnectionRoads(odrs[1].roads, odrs[1].junction)
        connectionRoadSecond = connectionRoadsFirst[0]

        roadFirstPred = odrs[0].roads[connectionRoadFirst.predecessor.element_id]
        roadFirstSuc = odrs[0].roads[connectionRoadFirst.successor.element_id]
        roadSecondPred = odrs[1].roads[connectionRoadSecond.predecessor.element_id]
        roadSecondSuc = odrs[1].roads[connectionRoadSecond.successor.element_id]

        print(roadFirstPred)
        print(roadFirstSuc)
        print(roadSecondPred)
        print(roadSecondSuc)

        roads = []
        roads.append(roadFirstPred)
        roads.append(connectionRoadFirst)
        roads.append(roadFirstSuc)
        roads.append(connectionRoadSecond)
        roads.append(roadSecondSuc)

        # fix links for roadFirstSuc, connectionRoadSecond

        roadFirstSuc.successor = None
        roadFirstSuc.add_successor(pyodrx.ElementType.junction, connectionRoadSecond.id)

        connectionRoadSecond.predecessor = None
        connectionRoadSecond.add_predecessor(pyodrx.ElementType.road, roadFirstSuc.id, pyodrx.ContactPoint.start) # interestingly, this becomes the start point after merging.


        # create new junction

        # experiment with connecting more lanes for a single connection road.
        con1 = pyodrx.Connection(roadFirstPred.id, connectionRoadFirst.id, pyodrx.ContactPoint.start)
        con1.add_lanelink(-1,-1)
        
        con2 = pyodrx.Connection(roadFirstSuc.id, connectionRoadSecond.id, pyodrx.ContactPoint.start)
        con2.add_lanelink(-1,-1)

        junction = pyodrx.Junction('junc',1)

        junction.add_connection(con1)
        junction.add_connection(con1)

        # newOdr = self.mergeByRoad(self, commonRoads, ords)

        newOrd = pyodrx.OpenDrive("new road")

        # create the opendrive
        odr = pyodrx.OpenDrive('myroad')
        for r in roads:
            odr.add_road(r)
            
        # odr.create_junction()

        odr.add_junction(junction)
        odr.adjust_roads_and_lanes()

        pyodrx.prettyprint(odr.get_element())

        extensions.view_road(odr,os.path.join('..','F:\\myProjects\\av\\esmini'))

        return odr
    
    
