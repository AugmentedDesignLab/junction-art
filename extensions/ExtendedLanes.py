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

    
