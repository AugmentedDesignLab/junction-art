import pyodrx
from enum import Enum
from extensions.CountryCodes import CountryCodes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedLaneSection import ExtendedLaneSection
from typing import List


class LaneMarks(Enum):
    WHITE_SOLID = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing, color=pyodrx.RoadMarkColor.white)
    WHITE_BROKEN = pyodrx.RoadMark(pyodrx.RoadMarkType.broken, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.white)
    YELLOW_SOLID = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing, color=pyodrx.RoadMarkColor.yellow)
    YELLOW_BROKEN = pyodrx.RoadMark(pyodrx.RoadMarkType.broken, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.yellow)
    NONE = pyodrx.RoadMark(pyodrx.RoadMarkType.none, 0.2, rule=pyodrx.MarkRule.none, color=pyodrx.RoadMarkColor.standard)

class LaneMarkGenerator:

    def __init__(self, countryCode) -> None:
        self.countryCode = countryCode
        pass


    def addBrokenWhite(self, lanes):
        for lane in lanes:
            lane.add_roadmark(LaneMarks.WHITE_BROKEN.value)
        pass


    def removeLaneMarkFromRoads(self, roads: List[ExtendedRoad]):
        for road in roads:
            self.removeLaneMarkFrom(road)


    def removeLaneMarkFrom(self, road: ExtendedRoad):
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

    