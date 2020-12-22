import pyodrx
import logging
from extensions.ExtendedRoad import ExtendedRoad
import math
import numpy as np

class RoadLinker:

    @staticmethod
    def createExtendedPredSuc(predRoad, predCp, sucRoad, sucCP):
        predRoad.addExtendedSuccessor(sucRoad, 0, sucCP)
        sucRoad.addExtendedPredecessor(predRoad, 0, predCp)
        pass
     

    @staticmethod
    def getContactPoints(road1: ExtendedRoad, road2: ExtendedRoad):

        # TODO we are assuming start points
        road1Cp = None
        road2Cp = None
        # if road1 is a pred, then road1's cp and start
        road1IsPred = road2.getExtendedPredecessorByRoadId(road1.id)

        if road1IsPred is not None:
            road1Cp = road1IsPred.cp

        # if road2 is a pred, then road2's cp and start
        road2IsPred = road1.getExtendedPredecessorByRoadId(road2.id)

        if road2IsPred is not None:
            road2Cp = road2IsPred.cp # road1's start is connected to road2's cp

        
        road2IsSuc = road1.getExtendedSuccessorByRoadId(road2.id)
        if road2IsSuc is not None:
            road2Cp = road2IsSuc.cp # road1's end is connected to road2's cp
        
        road1IsSuc = road2.getExtendedSuccessorByRoadId(road1.id)
        if road1IsSuc is not None:
            road1Cp =  road1IsSuc.cp # road1's cp is connected to road2's start

        
        
        # if road1IsPred is not None:
        #     return road1IsPred.cp, pyodrx.ContactPoint.start # road1's cp is connected to road2's start

        # # if road2 is a pred, then road2's cp and start
        # road2IsPred = road1.getExtendedPredecessorByRoadId(road2.id)

        # if road2IsPred is not None:
        #     return pyodrx.ContactPoint.start, road2IsPred.cp # road1's start is connected to road2's cp

        
        # road2IsSuc = road1.getExtendedSuccessorByRoadId(road2.id)
        # if road2IsSuc is not None:
        #     return pyodrx.ContactPoint.end, road2IsSuc.cp # road1's end is connected to road2's cp
        
        # road1IsSuc = road2.getExtendedSuccessorByRoadId(road1.id)
        # if road1IsSuc is not None:
        #     return road1IsSuc.cp, pyodrx.ContactPoint.end # road1's cp is connected to road2's start

        if road1Cp is None or road2Cp is None:
            raise Exception(f"contact points not available for {road1.id} and {road2.id}")

        return road1Cp, road2Cp



    @staticmethod
    def getAngleBetweenStraightRoads(road1: ExtendedRoad, road2: ExtendedRoad):
        """roads must be already adjusted

        Args:
            road1 (ExtendedRoad): [description]
            road2 (ExtendedRoad): [description]
        """

        x1Start, y1Start, _ = road1.getAdjustedStartPosition()
        x1End, y1End, _ = road1.getAdjustedEndPosition()

        x2Start, y2Start, _ = road2.getAdjustedStartPosition()
        x2End, y2End, _ = road2.getAdjustedEndPosition()

        angle1 = math.atan((y1End - y1Start) / (x1End - x1Start))
        angle2 = math.atan((y2End - y2Start) / (x2End - x2Start))

        if angle1 < 0:
            angle1 = angle1 + np.pi
        if angle2 < 0:
            angle2 = angle2 + np.pi

        print(f"angle1 {math.degrees(angle1)}")
        print(f"angle2 {math.degrees(angle2)} start { x2Start, y2Start } end {x2End, y2End}")

        return angle2 - angle1


    


    def linkConsecutiveRoadsWithNoBranches(self, roads, linkLastToFirst=False, cp1 = pyodrx.ContactPoint.end, cpRest=pyodrx.ContactPoint.start):
        """establishes sucessor, predecessor relationships in a sequantial manner given a list of roads..

        Args:
            roads ([type]): [description]
            linkLastToFirst (bool, optional): [description]. Defaults to False.
            cp1 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.end.
            cpRest ([type], optional): [description]. Defaults to pyodrx.ContactPoint.start.
        """

        previousRoad = None
        previousFirst = True
        for road in roads:
            if previousRoad is not None:
                previousRoad.updateSuccessor(road.elementType, road.id, pyodrx.ContactPoint.start)

                if previousFirst:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, cp1)
                elif previousRoad.isConnection:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, pyodrx.ContactPoint.end)
                else:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, cpRest)
                    previousFirst = False
            previousRoad = road
        
        if linkLastToFirst:
            roads[-1].updateSuccessor(roads[0].elementType, roads[0].id, cp1)


    def adjustLaneOffsetsForOdr(self, odr):
        """Given and ExtendedOpenDrive object, it adjusts the laneOffset of the starting lane section of the successor.

        Args:
            odr ([type]): [description]
        
        Danger:
            if a road has more than one lane section, it will not adjust the laneoffsets of each.
        """
        

        for road in odr.roads.values():
            if road.hasLaneOffsets() is False:
                logging.error(F"The road object do not have extended lanes properties. Please, update your code.")
                return

            pred = odr.getPredecessorRoad(road)
            if pred is not None:
                self.adjustLaneOffsets(pred, road)


    def adjustLaneOffsets(self, pred, suc):
        """adjusts the laneOffset of the starting lane section of the successor depending on the laneOffset of the last lane section of pred

        Args:
            pred ([type]): [description]
            suc ([type]): [description]
        """
        suc.setFirstLaneOffset(pred.getLastLaneOffset())

