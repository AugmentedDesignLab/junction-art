import pyodrx
import junctions
import extensions


class LaneBuilder:

    def addLeftTurnLane(self, road, countryCode=extensions.CountryCodes.US):

        if countryCode == extensions.CountryCodes.US:
            return self.addLeftTurnLaneForUS(road)

        raise NotImplementedError("Only us turns are implemented")

    
    def addLeftTurnLaneForUS(self, road):

        raise NotImplementedError("addLeftTurnLaneForUS not implemented")


    def addRightTurnLaneUS(self, road, laneWidth, laneLength = 10):

        # 1. define lane equation params

        soffset = road.length() - laneLength

        a = 0
        b = (laneWidth / laneLength)

        lane = pyodrx.Lane(soffset=soffset, a=a, b=b)


        # 2. add lane
        laneSection = road.getEndLaneSection()
        laneSection.add_right_lane(lane)

        pass


    def addRightLaneUS(self, road, laneWidth = 3, soffset=0):

        laneSections = road.getLaneSections()

        for laneSection in laneSections:
            lane = pyodrx.Lane(soffset=soffset, a=laneWidth)
            laneSection.add_right_lane(lane)

        pass

