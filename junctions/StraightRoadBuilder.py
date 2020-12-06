import numpy as np
import os
import pyodrx, extensions
import math

from junctions.LaneSides import LaneSides
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline

from junctions.RoadSeries import RoadSeries
from junctions.Direction import CircularDirection
from junctions.Geometry import Geometry
from junctions.LaneBuilder import LaneBuilder
from extensions.CountryCodes import CountryCodes


class StraightRoadBuilder:

    def __init__(self, country = CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        pass

    
    def createStraightRoad(self, roadId, length=100,junction = -1, 
                            n_lanes=1, lane_offset=3, 
                            laneSides=LaneSides.BOTH,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False):

        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)

        
        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road

    def createStraightRoadWithRightTurnLanesOnLeft(self, roadId, length=100,junction = -1, 
                                                    n_lanes=1, lane_offset=3, 
                                                    laneSides=LaneSides.BOTH,
                                                    isLeftTurnLane=False,
                                                    isRightTurnLane=False,
                                                    isLeftMergeLane=False,
                                                    isRightMergeLane=False,
                                                    numberOfRightTurnLanesOnLeft=1,
                                                    mergeLaneOnTheOppositeSideForInternalTurn=True
                                                    ):

        
        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)

        
        laneSections = self.laneBuilder.getStandardLanesWithInternalTurns(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane,
                                                            numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                                                            mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road
    
    


    def createStraightRoadWithLeftTurnLanesOnRight(self, roadId, length=100,junction = -1, 
                                                    n_lanes=1, lane_offset=3, 
                                                    laneSides=LaneSides.BOTH,
                                                    isLeftTurnLane=False,
                                                    isRightTurnLane=False,
                                                    isLeftMergeLane=False,
                                                    isRightMergeLane=False,
                                                    numberOfLeftTurnLanesOnRight=1,
                                                    mergeLaneOnTheOppositeSideForInternalTurn=True
                                                    ):
        """Will create numberOfLeftTurnLanesOnRight left turn lanes on the right side of the center line. Equal number of mergelanes will be created on the left side of the center lane, too.

        Args:
            roadId ([type]): [description]
            length (int, optional): [description]. Defaults to 100.
            junction (int, optional): [description]. Defaults to -1.
            n_lanes (int, optional): [description]. Defaults to 1.
            lane_offset (int, optional): [description]. Defaults to 3.
            laneSides ([type], optional): [description]. Defaults to LaneSides.BOTH.
            isLeftTurnLane (bool, optional): [description]. Defaults to False.
            isRightTurnLane (bool, optional): [description]. Defaults to False.
            isLeftMergeLane (bool, optional): [description]. Defaults to False.
            isRightMergeLane (bool, optional): [description]. Defaults to False.
            numberOfLeftTurnLanesOnRight (int, optional): [description]. Defaults to 1.

        Returns:
            [type]: [description]
        """

        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)

        
        laneSections = self.laneBuilder.getStandardLanesWithInternalTurns(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane,
                                                            numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                                                            mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road

    
    def createStraightRoadWithDifferentLanes(self, roadId, length=100,junction = -1, 
                            n_lanes_left=1, n_lanes_right=1,
                            lane_offset=3):

        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)

        
        laneSections = self.laneBuilder.getStandardLanesWithDifferentLeftAndRight(n_lanes_left, n_lanes_right, lane_offset)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road

    
    def createWithSingleSide(self, roadId, length=100,junction = -1, 
                            n_lanes=1, lane_offset=3, 
                            laneSide=LaneSides.RIGHT,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False):
        
    
        if laneSide == LaneSides.BOTH:
            raise Exception(f"Lanes side can be left or right only.")


        return self.createStraightRoad(roadId, length, junction,
                                        n_lanes, lane_offset, laneSides=laneSide,
                                        isLeftTurnLane=isLeftTurnLane,
                                        isRightTurnLane=isRightTurnLane,
                                        isLeftMergeLane=isLeftMergeLane,
                                        isRightMergeLane=isRightMergeLane
                                        )