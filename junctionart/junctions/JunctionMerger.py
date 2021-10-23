import numpy as np
import os
import pyodrx 
import math
import dill
from junctionart.junctions.moreExceptions import *
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
import junctionart.extensions as extensions
from copy import copy
import logging
from junctionart.library.Configuration import Configuration

class JunctionMerger:

    

    def __init__(self, outputDir, outputPrefix='R3_', lastId=0, 
                esminiPath = None, 
                saveImage = True):
        """

        Args:
            outputDir ([type]): [description]
            outputPrefix ([type]): [description]
            lastId (int, optional): [description]. Defaults to 0.
        """

        self.destinationPrefix = os.path.join(outputDir, outputPrefix)
        self.lastId = lastId

        self.roadBuilder = RoadBuilder()

        self.configuration = Configuration()

        if esminiPath is None:
            self.esminiPath = self.configuration.get("esminipath")
        else:
            self.esminiPath = esminiPath

        self.saveImage = saveImage

        if os.path.isdir(self.esminiPath) is False:
            logging.warn(f"Esmini path not found {self.esminiPath}. Will break if you try to save images using merger.")

        pass


    def getOutputPath(self, fname):
        return self.destinationPrefix + fname + '.xodr'


    def canMerge(self, connectionRoadFirst, connectionRoadSecond):

        #1. if both straight, cannot merge
        if connectionRoadFirst.curveType is None and connectionRoadSecond.curveType is None:
            return False

        #1. if one straight, can merge
        if connectionRoadFirst.curveType is None or connectionRoadSecond.curveType is None:
            return True

        #1. if angles are same but curvatures are opposite. cannot merge because they overlap

        firstAngle = connectionRoadFirst.getArcAngle()
        # difference = abs(firstAngle - connectionRoadSecond.getArcAngle()) * 100 / firstAngle
        difference = abs(firstAngle - connectionRoadSecond.getArcAngle())

        dotSign = connectionRoadFirst.getFirstGeomCurvature() * connectionRoadSecond.getFirstGeomCurvature()

        if difference < (np.pi / 10) and dotSign < 0:
            return False
        return True


    def merge2R2L(self, odrs, save=True):
        
        # 1 find connectionRoad in the first, it's predecessor is first road, successor is the second road.

        connectionRoadsFirst = extensions.getConnectionRoads(odrs[0].roads, odrs[0].junctions[0])
        connectionRoadFirst = connectionRoadsFirst[0].shallowCopy()
        connectionRoadsSecond = extensions.getConnectionRoads(odrs[1].roads, odrs[1].junctions[0])
        connectionRoadSecond = connectionRoadsSecond[0].shallowCopy()

        if self.canMerge(connectionRoadFirst, connectionRoadSecond) is False:
            raise IncompatibleRoadsException("incompatible junctions to merge.")

        roadFirstPred = extensions.getRoadFromRoadDic(odrs[0].roads, connectionRoadFirst.predecessor.element_id).shallowCopy()
        roadFirstSuc = extensions.getRoadFromRoadDic(odrs[0].roads, connectionRoadFirst.successor.element_id).shallowCopy()

        roadSecondPred = extensions.getRoadFromRoadDic(odrs[1].roads, connectionRoadSecond.predecessor.element_id).shallowCopy()
        roadSecondSuc = extensions.getRoadFromRoadDic(odrs[1].roads, connectionRoadSecond.successor.element_id).shallowCopy()

        # case 1: remove roadSecondPred & rebuild links for roads in the first odr

        roadFirstPred.updateSuccessor(pyodrx.ElementType.junction, connectionRoadFirst.id)

        connectionRoadFirst.updatePredecessor(pyodrx.ElementType.road, roadFirstPred.id, pyodrx.ContactPoint.end) # interestingly, this becomes the start point after merging.
        connectionRoadFirst.updateSuccessor(pyodrx.ElementType.road, roadFirstSuc.id, pyodrx.ContactPoint.start) 

        roadFirstSuc.updatePredecessor(pyodrx.ElementType.junction, connectionRoadFirst.id)

        roadSecondSuc.updatePredecessor(pyodrx.ElementType.junction, connectionRoadFirst.id)


        roads = []
        roads.append(roadFirstPred)
        roads.append(connectionRoadFirst)
        roads.append(roadFirstSuc)
        roads.append(connectionRoadSecond)
        roads.append(roadSecondSuc)
        
        # fix links for roadFirstSuc, connectionRoadSecond, roadSecondSuc

        self.regenAndMergeWithConnectionRoad(roadFirstSuc, connectionRoadSecond, roadSecondSuc)

        # create new junction

        junction = self.createJunctionFor2Connections(roadFirstPred, connectionRoadFirst, roadFirstSuc, connectionRoadSecond)

        # newOdr = self.mergeByRoad(self, commonRoads, ords)

        self.lastId += 1


        # create the opendrive
        odr = pyodrx.OpenDrive("3R_2L_" + str(self.lastId))
        for r in roads:
            odr.add_road(r)
            
        odr.add_junction(junction)
        print(f"starting adjustment. May freeze!!!!!!!!!!!!!")
        odr.adjust_roads_and_lanes()

        xmlPath = self.getOutputPath(odr.name)
        if save:
            odr.write_xml(xmlPath)

        if self.saveImage:
            extensions.saveRoadImageFromFile(xmlPath, self.esminiPath)

        return odr


    def regenAndMergeWithConnectionRoad(self, lastRoad_odr_1, connectionRoad_odr_2, lastRoad_odr_2):
        """Clears all road and lane links for all roads except lastRoad_odr_1.
            

        Args:
            lastRoad_odr_1 ([type]): reassigns successor 
            connectionRoad_odr_2 ([type]): re-ids and reassigns successor and predecessors
            lastRoad_odr_2 ([type]): [description] re-ids and reassigns predecessor
        """
        
        # regenerate ids for connectionRoadSecond and roadSecondSuc
        connectionRoad_odr_2.id = lastRoad_odr_1.id + 100
        lastRoad_odr_2.id = connectionRoad_odr_2.id + 1

        # fix links for roadFirstSuc, connectionRoadSecond, roadSecondSuc
        lastRoad_odr_1.updateSuccessor(pyodrx.ElementType.junction, connectionRoad_odr_2.id)

        connectionRoad_odr_2.updatePredecessor(pyodrx.ElementType.road, lastRoad_odr_1.id, pyodrx.ContactPoint.start) # interestingly, this becomes the start point after merging.

        connectionRoad_odr_2.updateSuccessor(pyodrx.ElementType.road, lastRoad_odr_2.id, pyodrx.ContactPoint.start) # interestingly, this becomes the start point after merging.

        lastRoad_odr_2.updatePredecessor(pyodrx.ElementType.junction, connectionRoad_odr_2.id)

        pass


    def createJunctionFor2Connections(self, roadFirstPred, connectionRoadFirst, roadFirstSuc, connectionRoadSecond):

        
        # TODO experiment with connecting more lanes for a single connection road.

        con1 = pyodrx.Connection(roadFirstPred.id, connectionRoadFirst.id, pyodrx.ContactPoint.start)
        con1.add_lanelink(-1,-1)
        
        con2 = pyodrx.Connection(roadFirstSuc.id, connectionRoadSecond.id, pyodrx.ContactPoint.start)
        con2.add_lanelink(-1,-1)

        junction = pyodrx.Junction('junc',1)

        junction.add_connection(con1)
        junction.add_connection(con2)

        return junction
    