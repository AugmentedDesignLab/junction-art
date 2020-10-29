import numpy as np
import os
import pyodrx 
import math
import dill
from junctions.RoadBuilder import RoadBuilder
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
import extensions
from copy import copy

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


    def getOutputPath(self, fname):
        return self.destinationPrefix + fname + '.xodr'
    

    def merge2R2L(self, odrs, save=True):

        # how do we merge 2 road junctions?
        
        # 1 find connectionRoad in the first, it's predecessor is first road, successor is the second road.

        connectionRoadsFirst = extensions.getConnectionRoads(odrs[0].roads, odrs[0].junctions[0])
        connectionRoadFirst = copy(connectionRoadsFirst[0])
        connectionRoadsSecond = extensions.getConnectionRoads(odrs[1].roads, odrs[1].junctions[0])
        connectionRoadSecond = copy(connectionRoadsSecond[0])

        roadFirstPred = copy(extensions.getRoadFromRoadDic(odrs[0].roads, connectionRoadFirst.predecessor.element_id))
        roadFirstSuc = copy(extensions.getRoadFromRoadDic(odrs[0].roads, connectionRoadFirst.successor.element_id))
        roadSecondPred = copy(extensions.getRoadFromRoadDic(odrs[1].roads, connectionRoadSecond.predecessor.element_id))
        roadSecondSuc = copy(extensions.getRoadFromRoadDic(odrs[1].roads, connectionRoadSecond.successor.element_id))


        roads = []
        roads.append(roadFirstPred)
        roads.append(connectionRoadFirst)
        roads.append(roadFirstSuc)
        roads.append(connectionRoadSecond)
        roads.append(roadSecondSuc)
        
        # regenerate ids for connectionRoadSecond and roadSecondSuc
        connectionRoadSecond.id = roadFirstSuc.id + 100
        roadSecondSuc.id = connectionRoadSecond.id + 1

        # fix links for roadFirstSuc, connectionRoadSecond, roadSecondSuc

        self.regenAndMerge(roadFirstSuc, connectionRoadSecond, roadSecondSuc)

        # create new junction

        junction = self.createJunction(roadFirstPred, connectionRoadFirst, roadFirstSuc, connectionRoadSecond)

        # newOdr = self.mergeByRoad(self, commonRoads, ords)

        self.lastId += 1


        # create the opendrive
        odr = pyodrx.OpenDrive("3R_2L_" + str(self.lastId))
        for r in roads:
            odr.add_road(r)
            
        odr.add_junction(junction)
        print(f"starting adjustment. May freeze!!!!!!!!!!!!!")
        # odr.adjust_roads_and_lanes()

        print(f"total number of roads added {len(roads)}")

        print(f"total number of roads in odr {len(odr.roads)}")

        if save:
            odr.write_xml(self.getOutputPath(odr.name))

        return odr


    def regenAndMerge(self, roadFirstSuc, connectionRoadSecond, roadSecondSuc):
        
        # regenerate ids for connectionRoadSecond and roadSecondSuc
        connectionRoadSecond.id = roadFirstSuc.id + 100
        roadSecondSuc.id = connectionRoadSecond.id + 1

        # fix links for roadFirstSuc, connectionRoadSecond, roadSecondSuc

        roadFirstSuc.successor = None
        roadFirstSuc.add_successor(pyodrx.ElementType.junction, connectionRoadSecond.id)

        connectionRoadSecond.predecessor = None
        connectionRoadSecond.add_predecessor(pyodrx.ElementType.road, roadFirstSuc.id, pyodrx.ContactPoint.start) # interestingly, this becomes the start point after merging.

        connectionRoadSecond.successor = None
        connectionRoadSecond.add_successor(pyodrx.ElementType.road, roadSecondSuc.id, pyodrx.ContactPoint.start) # interestingly, this becomes the start point after merging.

        roadSecondSuc.predecessor = None
        roadSecondSuc.add_predecessor(pyodrx.ElementType.junction, connectionRoadSecond.id)

        pass


    def createJunction(self, roadFirstPred, connectionRoadFirst, roadFirstSuc, connectionRoadSecond):

        
        # TODO experiment with connecting more lanes for a single connection road.

        con1 = pyodrx.Connection(roadFirstPred.id, connectionRoadFirst.id, pyodrx.ContactPoint.start)
        con1.add_lanelink(-1,-1)
        
        con2 = pyodrx.Connection(roadFirstSuc.id, connectionRoadSecond.id, pyodrx.ContactPoint.start)
        con2.add_lanelink(-1,-1)

        junction = pyodrx.Junction('junc',1)

        junction.add_connection(con1)
        junction.add_connection(con1)

        return junction
    