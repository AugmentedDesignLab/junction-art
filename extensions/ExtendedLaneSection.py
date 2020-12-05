import pyodrx

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

