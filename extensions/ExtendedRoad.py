import pyodrx
from copy import copy
import numpy as np
import math

class ExtendedRoad(pyodrx.Road):

    curveType = None

    pass


    def reset(self, clearRoadLinks = False):

        
        self.planview.reset()

        if clearRoadLinks:
            self.clearAllLinks()
        else:
            self.clearLaneLinks()

        self.setAdjustmentsToFalse()

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
        copiedRoad.reset()
        return copiedRoad
    

    def setAdjustmentsToFalse(self):
        self.adjusted = False
        pass


    def getArcAngle(self):
        """Assumes the road has an spiral, arc, spiral
            returns the angle between our endpoints in clockwise manner.
        """

        if self.curveType is None:
            raise Exception("curveType is None")

        geoms = self.planview._raw_geometries
        spiral1 = geoms[0]

        if isinstance(spiral1, pyodrx.Spiral) is False:
            raise Exception("Not an arc")

        totalAngle = 0
        for g in geoms:
            # print(math.degrees(g.angle))
            totalAngle += g.angle

        return np.pi - totalAngle


    def getFirstGeomCurvature(self):

        if self.curveType is None:
            raise Exception("curveType is None")

        geoms = self.planview._raw_geometries
        spiral1 = geoms[0]
        if isinstance(spiral1, pyodrx.Spiral) is False:
            raise Exception("Not an arc")

        return spiral1.curvend



    def getEndPosition(self, startX, startY, startH):
        """[summary]

        Args:
            startX ([type]): [description]
            startY ([type]): [description]
            startH ([type]): [description]

        Returns:
            [type]: [description]
        """

        raise Exception("Why this method gives wrong measurements? They adjust curves in different ways")
        geoms = self.planview._raw_geometries
        for g in geoms:
            startX, startY, startH, _ = g.get_end_data(startX, startY, startH)
        
        return startX, startY, startH


    def getAdjustedStartPosition(self):
        """[summary]

        Args:
            startX ([type]): [description]
            startY ([type]): [description]
            startH ([type]): [description]

        Returns:
            [type]: [description]
        """
        # raise Exception("Never call this method because it changes the position.")
        geoms = self.planview._adjusted_geometries
        for g in geoms:
            # startX, startY, startH, _ = g.get_start_data() # this function changes the start position. Never call it
            startX, startY, startH = g.x, g.y, g.heading
        
        return startX, startY, startH

    def getAdjustedEndPosition(self):
        """[summary]

        Args:
            startX ([type]): [description]
            startY ([type]): [description]
            startH ([type]): [description]

        Returns:
            [type]: [description]
        """
        geoms = self.planview._adjusted_geometries
        for g in geoms:
            startX, startY, startH, _ = g.get_end_data()
        
        return startX, startY, startH


    def getPosition(self, contactPoint = pyodrx.ContactPoint.start ):

        if contactPoint == pyodrx.ContactPoint.end:
            return self.getAdjustedEndPosition() 
        else:
            return self.getAdjustedStartPosition() 

    
    def getHeading(self, contactPoint = pyodrx.ContactPoint.start):

        heading = None
        if contactPoint == pyodrx.ContactPoint.end:
            _, _, heading = self.getAdjustedEndPosition() 
        else:
            _, _, heading = self.getAdjustedStartPosition() 

        return heading


    def getClockWiseAngleWith(self, road2, cp1 = pyodrx.ContactPoint.end, cp2 = pyodrx.ContactPoint.start):
        """contact points must be the same as the connectionRoad contact points on the roads of the related junction.

        Args:
            road1 ([type]): [description]
            road2 ([type]): [description]
            cp1 ([type], optional): Contact point of the first road. Defaults to pyodrx.ContactPoint.end.
            cp2 ([type], optional): Contact point of the second road. Defaults to pyodrx.ContactPoint.start.

        Raises:
            Exception: [description]
        """
        if self.planview.adjusted is False or road2.planview.adjusted is False:
            raise Exception("road planviews are not adjusted yet. Cannot measure angles between them")
        
        # get the end headings because 
        heading1 = self.getHeading(cp1)
        heading2 = road2.getHeading(cp2)

        print(f"heading1 {heading1} heading2 {heading2}")

        return (heading2 - heading1) % np.pi

