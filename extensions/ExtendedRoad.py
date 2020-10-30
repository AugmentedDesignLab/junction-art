import pyodrx
from copy import copy

class ExtendedRoad(pyodrx.Road):

    curveType = None

    pass

    def clearAllLinks(self):
        self.clearRoadLinks()
        self.clearLaneLinks()
        pass


    def clearRoadLinks(self):
        self.links = pyodrx.links._Links()
        pass


    def clearLaneLinks(self):
        for laneSecion in self.lanes.lanesections:
            for lane in laneSecion.leftlanes:
                lane.links = pyodrx.links._Links()
            for lane in laneSecion.rightlanes:
                lane.links = pyodrx.links._Links()

    
    def updatePredecessor(self, element_type,element_id,contact_point=None):
        self.predecessor = None
        self.add_predecessor(element_type, element_id, contact_point)
        pass


    def updateSuccessor(self, element_type,element_id,contact_point=None):
        self.successor = None
        self.add_successor(element_type, element_id, contact_point)
        pass
    

    def shallowCopy(self):
        copiedRoad = copy(self)
        copiedRoad.setAdjustmentsToFalse()
        return copiedRoad
    

    def setAdjustmentsToFalse(self):
        self.adjusted = False
        self.planview.adjusted = False
        pass