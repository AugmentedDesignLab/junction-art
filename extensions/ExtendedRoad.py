import pyodrx
from copy import copy
import numpy as np

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


    def getArcAngle(self):
        """Assumes the road has an spiral, arc, spiral
            returns the angle between our endpoints in clockwise manner.
        """

        geoms = self.planview._raw_geometries
        spiral1 = geoms[0]

        if isinstance(spiral1, pyodrx.Spiral) is False:
            raise Exception("Not an arc")

        totalAngle = 0
        for g in geoms:
            totalAngle += g.angle

        return np.pi - totalAngle