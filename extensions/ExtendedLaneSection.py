import pyodrx
from junctions.Geometry import Geometry


class ExtendedLaneSection(pyodrx.LaneSection):
    
    def __init__(self,s,centerlane, singleSide=False):
        """ initalize the LaneSection

            Parameters
            ----------
                s (float): start of lanesection

                centerlane (Lane): the centerline of the road
        """
        super().__init__(s, centerlane)

        self.singleSide = singleSide

        
    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = super().get_attributes()
        if self.singleSide:
            retdict['singleSide'] = "true"

        return retdict

    def clearLanes(self):
        self._left_id = 1
        self._right_id = -1
        self.leftlanes = []
        self.rightlanes = []
        pass
    

    def prependLaneToRightLanes(self, leftLane):
        

        # right lanes have negative numberings and starts from -1

        leftLane._set_lane_id(-1)
        self._right_id -= 1


        # decrement all the existing lane ids
        for existingLane in self.rightlanes:
            existingLane._set_lane_id(existingLane.lane_id - 1)


        self.rightlanes.append(leftLane)


    def prependLaneToLeftLanes(self, rightLane):
        

        # left lanes have positive numberings and starts from 1

        rightLane._set_lane_id(1)
        self._left_id += 1


        # decrement all the existing lane ids
        for existingLane in self.leftlanes:
            existingLane._set_lane_id(existingLane.lane_id + 1)


        self.leftlanes.append(rightLane)


    def laneWidths(self, lane, laneLength):
        """returns the width of the lane at ds=0 and ds=laneLength as a list of values

        Args:
            lane ([type]): [description]
            laneLength ([type]): [description]

        Returns:
            startWidth
            endWidth
        """

        coeffs = [lane.a, lane.b, lane.c, lane.d]
        pRange = [0, laneLength]
        return Geometry.evalPoly(coeffs, pRange)


    def length(self, roadLength, laneOffset = None, laneOffsetNext = None):
        """The width of the lane section depends on its laneOffset and next section's offset

        Args:
            roadLength ([type]): [description]
            laneOffset ([type], optional): [description]. Defaults to None.
            laneOffsetNext ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        s = 0
        if laneOffset is not None:
            s = laneOffset.s

        if laneOffsetNext is not None:
            return laneOffsetNext.s - s

        laneLength = roadLength - s
        return laneLength


    def widths(self, roadLength, laneOffset = None, laneOffsetNext = None):
        """ returns the width of the section at the start and end of the secion.

        Args:
            roadLength ([type]): [description]
            laneOffset ([type]): The corresponding laneOffset. None if only one laneOffset in the road.
            laneOffsetNext ([type]): The corresponding next laneOffset. None if only one laneOffset in the road.
            
        Returns:
            (tuple) : (startWidth, endWidth)
        """

        sectionLength = self.length(roadLength, laneOffset, laneOffsetNext)

        startWidth = 0
        endWidth = 0

        allLanes = self.leftlanes + self.rightlanes

        for lane in allLanes:
            laneWidths = self.laneWidths(lane, sectionLength)
            startWidth += laneWidths[0]
            endWidth += laneWidths[1]


        return (startWidth, endWidth)

