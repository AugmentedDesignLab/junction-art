import numpy as np
import os
import pyodrx
import math

import junctionart.extensions as extensions
from junctionart.junctions.LaneSides import LaneSides
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
from junctionart.extensions.ExtendedRoad import ExtendedRoad
from junctionart.extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline

from junctionart.junctions.RoadSeries import RoadSeries
from junctionart.junctions.Direction import CircularDirection
from junctionart.junctions.Geometry import Geometry
from junctionart.junctions.LaneBuilder import LaneBuilder
from junctionart.extensions.CountryCodes import CountryCodes

from junctionart.library.Configuration import Configuration


class StraightRoadBuilder:

    def __init__(self, country = CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        self.configuration = Configuration()
        self.name = 'StraightRoadBuilder'
        pass


    def createPVForLine(self, length):
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)
        return pv


    def createRandom(self, 
                    roadId, 
                    randomState=None,
                    length=20, 
                    junction=-1, 
                    lane_offset=None, 
                    maxLanePerSide=2, 
                    minLanePerSide=0, 
                    turns=False,
                    merges=False,
                    medianType=None,
                    medianWidth=3,
                    skipEndpoint=None,
                    force3Section=False):

        if randomState is not None:
            np.random.set_state(randomState)

        if lane_offset is None:
            lane_offset = self.configuration.get("default_lane_width")

        if maxLanePerSide < 1:
            raise Exception(f"{self.name}: createRandom: maxLanePerSide cannot be less than 1")
        
        laneRange = np.arange(minLanePerSide, maxLanePerSide + 1)
        n_lanes_left = np.random.choice(laneRange)
        n_lanes_right = np.random.choice(laneRange)

        if (n_lanes_left == 0) and (n_lanes_right == 0):
            return self.createRandom(
                                        roadId, 
                                        randomState=randomState,
                                        length=length, 
                                        junction=junction, 
                                        lane_offset=lane_offset, 
                                        maxLanePerSide=maxLanePerSide, 
                                        minLanePerSide=minLanePerSide, 
                                        turns=turns,
                                        merges=merges,
                                        medianType=medianType,
                                        medianWidth=3,
                                        skipEndpoint=skipEndpoint,
                                        force3Section=force3Section
                                        )

        numLeftTurnsOnLeft = 0
        numRightTurnsOnRight = 0
        numLeftMergeOnLeft = 0
        numRightMergeOnRight = 0
        numberOfLeftTurnLanesOnRight = 0
        numberOfRightTurnLanesOnLeft = 0
        mergeLaneOnTheOppositeSideForInternalTurn = np.random.choice([True, False])
        if turns:
            numLeftTurnsOnLeft = np.random.choice([0, 1])
            numRightTurnsOnRight = np.random.choice([0, 1])
            numberOfLeftTurnLanesOnRight = np.random.choice([0, 1])
            numberOfRightTurnLanesOnLeft = np.random.choice([0, 1])
        elif merges:
            numLeftMergeOnLeft = np.random.choice([0, 1])
            numRightMergeOnRight = np.random.choice([0, 1])
        
        if medianType is None:
            return self.create(
                        roadId, 
                        n_lanes_left=n_lanes_left, 
                        n_lanes_right=n_lanes_right, 
                        length=length,
                        junction = junction, 
                        lane_offset=lane_offset, 
                        laneSides=LaneSides.BOTH,
                        numLeftTurnsOnLeft=numLeftTurnsOnLeft,
                        numRightTurnsOnRight=numRightTurnsOnRight,
                        numLeftMergeOnLeft=numLeftMergeOnLeft,
                        numRightMergeOnRight=numRightMergeOnRight,
                        numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                        numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                        mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn,
                        force3Section=force3Section
                    )
        else:
            return self.createWithMedianRestrictedLane(
                        roadId, 
                        n_lanes_left=n_lanes_left, 
                        n_lanes_right=n_lanes_right, 
                        length=length,
                        junction = junction, 
                        lane_offset=lane_offset, 
                        laneSides=LaneSides.BOTH,
                        numLeftTurnsOnLeft=numLeftTurnsOnLeft,
                        numRightTurnsOnRight=numRightTurnsOnRight,
                        numLeftMergeOnLeft=numLeftMergeOnLeft,
                        numRightMergeOnRight=numRightMergeOnRight,
                        numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                        numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                        mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn,
                        medianType=medianType,
                        medianWidth=medianWidth,
                        skipEndpoint=skipEndpoint
                    )

        pass

    

    
    def create(self, 
                    roadId, 
                    n_lanes_left=1, 
                    n_lanes_right=1, 
                    length=20,
                    junction = -1, 
                    lane_offset=3, 
                    laneSides=LaneSides.BOTH,
                    numLeftTurnsOnLeft=0,
                    numRightTurnsOnRight=0,
                    numLeftMergeOnLeft=0,
                    numRightMergeOnRight=0,
                    numberOfLeftTurnLanesOnRight=0,
                    numberOfRightTurnLanesOnLeft=0,
                    mergeLaneOnTheOppositeSideForInternalTurn=True,
                    force3Section=False
                ):

        # create geometry
        pv = self.createPVForLine(length)

        
        # laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
        #                                                     roadLength=length, 
        #                                                     isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
        #                                                     isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)
        singleSide=False
        if laneSides != LaneSides.BOTH:
            singleSide=True
        laneSections = self.laneBuilder.getLanes( 
                                                    n_lanes_left, 
                                                    n_lanes_right, 
                                                    lane_offset = lane_offset, 
                                                    singleSide=singleSide,
                                                    roadLength=length,
                                                    numLeftTurnsOnLeft=numLeftTurnsOnLeft,
                                                    numRightTurnsOnRight=numRightTurnsOnRight,
                                                    numLeftMergeOnLeft=numLeftMergeOnLeft,
                                                    numRightMergeOnRight=numRightMergeOnRight,
                                                    numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                                                    numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                                                    mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn,
                                                    force3Section=force3Section
                                                )



        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road



    
    def createWithMedianRestrictedLane(self, 
                    roadId, 
                    n_lanes_left=1, 
                    n_lanes_right=1, 
                    length=20,
                    junction = -1, 
                    lane_offset=3, 
                    laneSides=LaneSides.BOTH,
                    numLeftTurnsOnLeft=0,
                    numRightTurnsOnRight=0,
                    numLeftMergeOnLeft=0,
                    numRightMergeOnRight=0,
                    numberOfLeftTurnLanesOnRight=0,
                    numberOfRightTurnLanesOnLeft=0,
                    mergeLaneOnTheOppositeSideForInternalTurn=True,
                    medianType='partial',
                    medianWidth=3,
                    skipEndpoint=None
                ):
        
        road = self.create(
                    roadId, 
                    n_lanes_left=n_lanes_left, 
                    n_lanes_right=n_lanes_right, 
                    length=length,
                    junction = junction, 
                    lane_offset=lane_offset, 
                    laneSides=laneSides,
                    numLeftTurnsOnLeft=numLeftTurnsOnLeft,
                    numRightTurnsOnRight=numRightTurnsOnRight,
                    numLeftMergeOnLeft=numLeftMergeOnLeft,
                    numRightMergeOnRight=numRightMergeOnRight,
                    numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                    numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                    mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn,
                    force3Section=True
                )
        if medianType=='partial':
            if skipEndpoint  is None:
                raise Exception(f"{self.name}: createWithMedianRestrictedLane skipEndpoint cannot be None for partial median lanes." )
            
            self.laneBuilder.addMedianIslandsTo2Of3Sections(road, roadLength=length, skipEndpoint=skipEndpoint, width=medianWidth)
        else:
            self.laneBuilder.addMedianIslandsToAllSections(road, width=medianWidth)
        
        return road


    def createWithRightTurnLanesOnLeft(self, roadId, length=100,junction = -1, 
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
        pv = self.createPVForLine(length)

        
        laneSections = self.laneBuilder.getStandardLanesWithInternalTurns(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane,
                                                            numberOfRightTurnLanesOnLeft=numberOfRightTurnLanesOnLeft,
                                                            mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road
    
    


    def createWithLeftTurnLanesOnRight(self, roadId, length=100,junction = -1, 
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
        pv = self.createPVForLine(length)

        
        laneSections = self.laneBuilder.getStandardLanesWithInternalTurns(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane,
                                                            numberOfLeftTurnLanesOnRight=numberOfLeftTurnLanesOnRight,
                                                            mergeLaneOnTheOppositeSideForInternalTurn=mergeLaneOnTheOppositeSideForInternalTurn)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road

    
    def createWithDifferentLanes(self, roadId, length=100,junction = -1, 
                            n_lanes_left=1, n_lanes_right=1,
                            lane_offset=3,
                            force3Section=False):

        return self.create(
                            roadId,                             
                            n_lanes_left=n_lanes_left,
                            n_lanes_right=n_lanes_right,
                            length=length, 
                            junction=junction,
                            lane_offset=lane_offset,
                            force3Section=force3Section
                            )

    
    # def createWithSingleSide(self, roadId, length=100,junction = -1, 
    #                         n_lanes=1, lane_offset=3, 
    #                         laneSide=LaneSides.RIGHT,
    #                         isLeftTurnLane=False,
    #                         isRightTurnLane=False,
    #                         isLeftMergeLane=False,
    #                         isRightMergeLane=False,
    #                         force3Section=False):
        
    
    #     if laneSide == LaneSides.BOTH:
    #         raise Exception(f"Lanes side can be left or right only.")

    #     n_lanes_left = 0
    #     n_lanes_right = 0
    #     if laneSide == LaneSides.RIGHT:
    #         n_lanes_right = n_lanes
    #     elif laneSide == LaneSides.LEFT:
    #         n_lanes_left = n_lanes
    #     else:
    #         raise Exception(f"{self.name}: createWithSingleSide: lane sides cannot be both")

    #     return self.create(
    #                         roadId,                      
    #                         n_lanes_left=n_lanes_left,
    #                         n_lanes_right=n_lanes_right,
    #                         length=length, 
    #                         junction=junction,
    #                         lane_offset=lane_offset,
    #                         laneSides=laneSide,
    #                         isLeftTurnLane=isLeftTurnLane,
    #                         isRightTurnLane=isRightTurnLane,
    #                         isLeftMergeLane=isLeftMergeLane,
    #                         isRightMergeLane=isRightMergeLane,
    #                         force3Section=force3Section
    #                         )