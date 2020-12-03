import pyodrx
from copy import copy
import numpy as np
import math

import extensions

from junctions.StandardCurveTypes import StandardCurveTypes

class ExtendedRoad(pyodrx.Road):



    def __init__(self,road_id,planview,lanes, road_type = -1,name=None, rule=None):
        super().__init__(road_id, planview, lanes, road_type, name, rule)

        self.curveType = StandardCurveTypes.Line
        self.headingTangentMagnitude = 10 # 10 meters.
        self.isConnection = False
        self.elementType = pyodrx.ElementType.road

        if road_type == 1:
            self.isConnection = True
            self.elementType = pyodrx.ElementType.junction

        pass


    def reset(self, clearRoadLinks = False):
        """[summary]

        Args:
            clearRoadLinks (bool, optional): IF false, keeps successor and predecessor. Defaults to False.
        """
        
        self.planview.reset()

        if clearRoadLinks:
            self.clearAllLinks()
        else:
            self.clearLaneLinks()

        self.setAdjustmentsToFalse()

        pass


    def setAdjustmentsToFalse(self):
        self.adjusted = False
        pass

    
    def planViewAdjusted(self):
        return self.planview.adjusted

    
    def planViewNotAdjusted(self):
        if self.planViewAdjusted():
            return False
        return True


    def clearAllLinks(self):
        self.clearRoadLinks()
        self.clearLaneLinks()
        pass


    def clearRoadLinks(self):
        self.links = pyodrx.links._Links()
        self.predecessor = None
        self.successor = None
        pass


    def clearLaneLinks(self):
        for laneSecion in self.lanes.lanesections:
            for lane in laneSecion.leftlanes:
                lane.links = pyodrx.links._Links()
            for lane in laneSecion.rightlanes:
                lane.links = pyodrx.links._Links()


    def length(self):
        if self.planViewNotAdjusted():
            raise Exception(f"Planview for road {self.id} not adjusted. Cannot get length")

        return self.planview.get_total_length()

    
    def updatePredecessor(self, element_type,element_id,contact_point=None):
        """ updatePredecessor adds a predecessor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the predecessor on the predecessor

        """
        self.predecessor = None
        element_id = int(element_id)
        self.add_predecessor(element_type, element_id, contact_point)
        pass


    def updateSuccessor(self, element_type,element_id,contact_point=None):
        """ updateSuccessor adds a successor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the Successor on the Successor

        """
        self.successor = None
        element_id = int(element_id)
        self.add_successor(element_type, element_id, contact_point)
        pass


    def hasPredecessor(self):
        if self.predecessor is not None:
            return True
        return False

    def hasSuccessor(self):
        if self.successor is not None:
            return True
        return False

    def isPredecessorOf(self, road):
        return ( road.hasPredecessor() and road.predecessor.element_id == self.id )

    def isSuccessorOf(self, road):
        return ( road.hasSuccessor() and road.successor.element_id == self.id )


    def isJunction(self):
        return self.isConnection
        

    def shallowCopy(self):
        copiedRoad = copy(self)
        copiedRoad.reset()
        return copiedRoad
    



    def getArcAngle(self):
        """Assumes the road has an spiral, arc, spiral
            returns the angle between our endpoints in clockwise manner.
        """

        if self.curveType is None:
            raise Exception("curveType is None")

        if self.curveType == StandardCurveTypes.Line:
            raise Exception("curveType is Line")

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
        # geoms = self.planview._raw_geometries
        # for g in geoms:
        #     startX, startY, startH, _ = g.get_end_data(startX, startY, startH)
        
        # return startX, startY, startH


    def getAdjustedStartPosition(self):
        """[summary]

        Args:
            startX ([type]): [description]
            startY ([type]): [description]
            startH ([type]): [description]

        Returns:
            [type]: [description]
        """
        if self.planview.adjusted is False:
            raise Exception(f"getAdjustedStartPosition cannot work without road planview adjustments.")
        
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
        if self.planview.adjusted is False:
            raise Exception(f"getAdjustedEndPosition cannot work without road planview adjustments.")

        geoms = self.planview._adjusted_geometries
        for g in geoms:
            startX, startY, startH, _ = g.get_end_data()
        
        return startX, startY, startH


    def getPosition(self, contactPoint = pyodrx.ContactPoint.start ):

        if self.planview.adjusted is False:
            raise Exception(f"getPosition cannot work without road planview adjustments.")

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



    def getIncomingTangent(self, contactPoint = pyodrx.ContactPoint.start, tangentMagnitude = None):

        _, _, h = self.getPosition(contactPoint)

        # heading of start point goes into the road. no change in heading.
        # head of end point goes out of the road, so, we need to reverse the heading.

        if contactPoint == pyodrx.ContactPoint.end:
            # need to change the heading
            h = ( h + np.pi ) % (np.pi * 2)

        return extensions.headingToTangent(h, tangentMagnitude)


    def getOutgoingTangent(self, contactPoint = pyodrx.ContactPoint.start, tangentMagnitude = None):

        _, _, h = self.getPosition(contactPoint)

        # heading of start point goes into the road.  we need to reverse the heading
        # head of end point goes out of the road, so,no change

        # if contactPoint == pyodrx.ContactPoint.start:
        #     # need to change the heading
        #     # h = ( h + np.pi ) % (np.pi * 2)
        #     h = h 

        return extensions.headingToTangent(h, tangentMagnitude)



    def getLaneSections(self):
        return self.lanes.lanesections

        
    def getEndLaneSection(self):
        return self.lanes.lanesections[-1]


    def getFirstLaneSection(self):
        return self.lanes.lanesections[0]