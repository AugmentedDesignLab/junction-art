import pyodrx
import xml.etree.ElementTree as ET
import extensions


class ExtendedLanes(pyodrx.Lanes):

    def __init__(self):
        super().__init__()
        self.laneOffsets=[extensions.LaneOffset.createParallel(0, 0)]
    pass

    def addLaneOffset(self, laneOffset):
        self.laneOffsets.append(laneOffset)
    

    def get_element(self):
        """ returns the elementTree of Lanes

        """
        element = super().get_element()

        for lo in self.laneOffsets:
            element.append(lo.get_element())
        
        return element

    def copy(self):
        newLaneSections = []
        newLaneOffsets = []

        for ls in self.lanesections:
            newLaneSections.append(ls.copy())
        
        for laneOffset in self.laneOffsets:
            newLaneOffsets.append(laneOffset.copy())
        
        lanes = ExtendedLanes()
        lanes.laneOffsets = newLaneOffsets
        lanes.lanesections = newLaneSections

        return lanes

    def hasLanes(self):
        for ls in self.lanesections:
            if len(ls.leftlanes) > 0 or len(ls.rightlanes) > 0:
                return True
        return False

    
    def clearLanes(self):
        for ls in self.lanesections:
            ls.clearLanes()

    
    def getLaneOffsetAt(self, index, default=None):

        if index < 0:
            raise Exception("getLaneOffsetAt does not work with negative indices")

        if index < len(self.laneOffsets):
            return self.laneOffsets[index]

        return default
    
    def getEndPointWidths(self, roadLength):
        """[summary]

        Args:
            roadLength ([type]): [description]

        Returns:
            (tuple) : (startWidth, endWidth)
        """

        firstSection = self.lanesections[0]

        firstOffset = self.getLaneOffsetAt(0)
        secondOffset = self.getLaneOffsetAt(1)

        firstWidths = firstSection.widths(roadLength, firstOffset, secondOffset)

        if len(self.lanesections) == 1:
            return firstWidths
        
        lastSection = self.lanesections[-1]
        lastOffset = self.getLaneOffsetAt(len(self.lanesections) - 1)
        lastWidths = lastSection.widths(roadLength, lastOffset)

        return (firstWidths[0], lastWidths[0])

        