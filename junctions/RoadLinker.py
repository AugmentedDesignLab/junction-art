import pyodrx
import logging
from extensions.ExtendedRoad import ExtendedRoad

class RoadLinker:

    @staticmethod
    
    def getContactPoints(road1: ExtendedRoad, road2: ExtendedRoad):

        # if road1 is a pred, then road1's cp and start
        road1IsPred = road2.getExtendedPredecessorByRoadId(road1.id)

        if road1IsPred is not None:
            return road1IsPred.cp, pyodrx.ContactPoint.start # road1's cp is connected to road2's start

        # if road2 is a pred, then road2's cp and start
        road2IsPred = road1.getExtendedPredecessorByRoadId(road2.id)

        if road2IsPred is not None:
            return pyodrx.ContactPoint.start, road2IsPred.cp # road1's start is connected to road2's cp

        
        road2IsSuc = road1.getExtendedSuccessorByRoadId(road2.id)
        if road2IsSuc is not None:
            return pyodrx.ContactPoint.end, road2IsSuc.cp # road1's end is connected to road2's cp
        
        road1IsSuc = road2.getExtendedSuccessorByRoadId(road1.id)
        if road1IsSuc is not None:
            return road1IsSuc.cp, pyodrx.ContactPoint.end # road1's cp is connected to road2's start
        
        raise Exception(f"contact points not available for {road1.id} and {road2.id}")

    


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

