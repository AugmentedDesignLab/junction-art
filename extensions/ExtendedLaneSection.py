import pyodrx

class ExtendedLaneSection(pyodrx.LaneSection):

    def addLeftLaneToRightLanes(self, leftLane):
        

        # right lanes have negative numberings and starts from -1

        leftLane._set_lane_id(-1)
        self._right_id -= 1


        # decrement all the existing lane ids
        for existingLane in self.rightlanes:
            existingLane._set_lane_id(existingLane.lane_id - 1)


        self.rightlanes.append(leftLane)


    def addRightLaneToLeftLanes(self, rightLane):
        

        # left lanes have positive numberings and starts from 1

        rightLane._set_lane_id(1)
        self._left_id += 1


        # decrement all the existing lane ids
        for existingLane in self.leftlanes:
            existingLane._set_lane_id(existingLane.lane_id + 1)


        self.leftlanes.append(rightLane)

