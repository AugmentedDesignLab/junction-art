from junctions.Intersection import Intersection
import pyodrx
from enum import Enum
from extensions.CountryCodes import CountryCodes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedLaneSection import ExtendedLaneSection
from library.Combinator import Combinator
from typing import List


class LaneMarks(Enum):
    WHITE_SOLID = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing, color=pyodrx.RoadMarkColor.white)
    WHITE_BROKEN = pyodrx.RoadMark(pyodrx.RoadMarkType.broken, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.white)
    WHITE_BOTT_DOTS = pyodrx.RoadMark(pyodrx.RoadMarkType.botts_dots, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.white)

    YELLOW_SOLID = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing, color=pyodrx.RoadMarkColor.yellow)
    YELLOW_BROKEN = pyodrx.RoadMark(pyodrx.RoadMarkType.broken, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.yellow)
    YELLOW_BOTT_DOTS = pyodrx.RoadMark(pyodrx.RoadMarkType.botts_dots, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.yellow)

    NONE = pyodrx.RoadMark(pyodrx.RoadMarkType.none, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.standard)

class LaneMarkGenerator:

    def __init__(self, countryCode) -> None:
        self.countryCode = countryCode
        pass


    def addBrokenWhite(self, lanes):
        for lane in lanes:
            lane.add_roadmark(LaneMarks.WHITE_BROKEN.value)
        pass

    def addBottsDotWhite(self, lanes):
        for lane in lanes:
            lane.add_roadmark(LaneMarks.WHITE_BOTT_DOTS.value)
        pass


    def removeLaneMarkFromRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.removeLaneMarkFrom(road)


    def removeLaneMarkFrom(self, road: ExtendedRoad):

        self.removeCenterLineFromRoad(road)

        for ls in road.lanes.lanesections:
            if len(ls.leftlanes) > 0:
                self.removeMarkFromLanes(ls.leftlanes)
            if len(ls.rightlanes) > 0:
                self.removeMarkFromLanes(ls.rightlanes)
        pass


    def removeMarkFromLanes(self, lanes):
        for lane in lanes:
            lane.add_roadmark(LaneMarks.NONE.value)
        pass

    #region inside lanes
    def addBrokenWhiteToInsideLanesOfRoads(self, roads: List[ExtendedRoad]):
        
        for road in roads:
            self.addBrokenWhiteToInsideLanesOfARoad(road)
            
        pass

    def addBrokenWhiteToInsideLanesOfARoad(self, road: ExtendedRoad):
        
        for ls in road.lanes.lanesections:
            self.addBrokenWhiteToInsideLanesOfLaneSection(ls)
            
        pass


    def addBrokenWhiteToInsideLanesOfLaneSection(self, laneSection: ExtendedLaneSection):
        if len(laneSection.leftlanes) > 1:
            self.addBrokenWhite(laneSection.leftlanes[0:-1])
        if len(laneSection.rightlanes) > 1:
            self.addBrokenWhite(laneSection.rightlanes[0:-1])
        pass
    #endregion

    #region all lanes except centerlane
    
    # Broken white
    def addBrokenWhiteToSideLanesOfRoads(self, roads: List[ExtendedRoad]):
        
        for road in roads:
            self.addBrokenWhiteToSideLanesOfARoad(road)
            
        pass

    def addBrokenWhiteToSideLanesOfARoad(self, road: ExtendedRoad):
        
        for ls in road.lanes.lanesections:
            self.addBrokenWhiteToSideLanesOfLaneSection(ls)
            
        pass
    
    def addBrokenWhiteToSideLanesOfLaneSection(self, laneSection: ExtendedLaneSection):
        
        self.addBrokenWhite(laneSection.leftlanes)
        self.addBrokenWhite(laneSection.rightlanes)
        pass
    
    # bott dots

    def addBottsDotsToSideLanesOfRoads(self, roads: List[ExtendedRoad]):
        
        for road in roads:
            self.addBottsDotsToSideLanesOfARoad(road)
            
        pass

    def addBottsDotsToSideLanesOfARoad(self, road: ExtendedRoad):
        
        for ls in road.lanes.lanesections:
            self.addBottsDotsToSideLanesOfLaneSection(ls)
            
        pass
    
    def addBottsDotsToSideLanesOfLaneSection(self, laneSection: ExtendedLaneSection):
        
        self.addBottsDotWhite(laneSection.leftlanes)
        self.addBottsDotWhite(laneSection.rightlanes)
        pass
    #region center lines

    def removeCenterLineFromRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.removeCenterLineFromRoad(road)

    def removeCenterLineFromRoad(self, road:ExtendedRoad):
        self.addCenterLineOnRoad(road, LaneMarks.NONE)
    
    def addCenterLineOnRoad(self, road: ExtendedRoad, markType: LaneMarks):
        for ls in road.lanes.lanesections:
            ls.centerlane.add_roadmark(markType.value)


    def addSolidYellowCenterLineOnRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.addSolidYellowCenterLineOnARoad(road)


    def addSolidYellowCenterLineOnARoad(self, road: ExtendedRoad):
        self.addCenterLineOnRoad(road, LaneMarks.YELLOW_SOLID)

    def addBrokenYellowCenterLineOnRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.addBrokenYellowCenterLineOnARoad(road)

    def addBrokenYellowCenterLineOnARoad(self, road: ExtendedRoad):
        self.addCenterLineOnRoad(road, LaneMarks.YELLOW_BROKEN)

    def addBrokenWhiteCenterLineOnRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.addBrokenWhiteCenterLineOnARoad(road)

    def addBrokenWhiteCenterLineOnARoad(self, road: ExtendedRoad):
        self.addCenterLineOnRoad(road, LaneMarks.WHITE_BROKEN)

    

    #endregion

    #region connection roads

    def addBrokenLinesForAdjacentConnectionRoads(self, connectionRoads: List[ExtendedRoad]):
        self.addBrokenWhiteToSideLanesOfRoads(connectionRoads)
        self.removeCenterLineFromRoads(connectionRoads)
        # for inside connection roads, add broken white to their center
        for i in range(1, len(connectionRoads)-1):
            self.addBrokenWhiteCenterLineOnRoads(connectionRoads[i])


    #region restricted lanes

    def addMarkForRestrictedLanesOnRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.addMarkForRestrictedLanesOnARoad(road)
            
    
    def addMarkForRestrictedLanesOnARoad(self, road):
        
        for ls in road.lanes.lanesections:
            self.addMarkForRestrictedLanes(ls.leftlanes)
            self.addMarkForRestrictedLanes(ls.rightlanes)

    
    def addMarkForRestrictedLanes(self, lanes):
        for lane in lanes:
            if lane.lane_type == pyodrx.LaneType.restricted:
                lane.add_roadmark(LaneMarks.YELLOW_SOLID.value)


    #region intersections

    def adjustMarksForIntersection(self, intersection: Intersection, markOptions=None):
        
            self.adjustMarksForIncidentRoads(intersection=intersection, markOptions=markOptions)
            self.adjustMarksForConnectionRoads(intersection=intersection, markOptions=markOptions)
            pass


    def adjustMarksForIncidentRoads(self, intersection: Intersection, markOptions=None):
            self.addSolidYellowCenterLineOnRoads(intersection.incidentRoads)
            self.addMarkForRestrictedLanesOnRoads(intersection.incidentRoads)
            pass


    def adjustMarksForConnectionRoads(self, intersection: Intersection, markOptions=None):
            # for each pair of intersection incident roads, call getOrderedConnectionRoadsBetween
            # then call addBrokenLinesForAdjacentConnectionRoads

            markType = LaneMarks.WHITE_BROKEN
            if (markOptions is not None) and ("connectionType"  in markOptions):
                markType = markOptions["connectionType"]

            # for each linkconfig for an incoming road
            incidentPairs = Combinator.nP2(intersection.incidentRoads)
            for (fromRoad, toRoad) in incidentPairs:
                adjacentConnectionRoads = intersection.getOrderedConnectionRoadsBetween(fromRoad, toRoad)
                if len(adjacentConnectionRoads) == 0:
                    continue
                
                self.removeLaneMarkFromRoads(adjacentConnectionRoads)

                # we need lane marks only when incoming lane changes 
                # corner case is median lane.
                lastIncomingLane = adjacentConnectionRoads[0].predecessorOffset
                for connectionRoad in adjacentConnectionRoads:
                    if connectionRoad.predecessorOffset > lastIncomingLane:
                        lastIncomingLane = connectionRoad.predecessorOffset
                        self.addCenterLineOnRoad(connectionRoad, markType)
                        

            # U-turns
            connectionRoads = intersection.internalConnectionRoads
            for connectionRoad in connectionRoads:
                if connectionRoad.isUturn():
                    self.removeLaneMarkFrom(connectionRoad)


    #endregion