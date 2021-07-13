import pyodrx
from copy import copy
import numpy as np
import math
import extensions
from pyodrx.signals import Signals
from junctions.StandardCurveTypes import StandardCurveTypes
from junctions.Geometry import Geometry
from extensions.ExtendedPredecessor import ExtendedPredecessor
from extensions.ExtendedSuccessor import ExtendedSuccessor

class ExtendedRoad(pyodrx.Road):



    def __init__(self,road_id,planview,lanes, road_type = -1,name=None, rule=None, curveType = StandardCurveTypes.Line, predecessorOffset = 0): 
        """[summary]

        Args:
            road_id ([type]): [description]
            planview ([type]): [description]
            lanes ([type]): [description]
            road_type (int, optional): [description]. Defaults to -1.
            name ([type], optional): [description]. Defaults to None.
            rule ([type], optional): [description]. Defaults to None.
            curveType ([type], optional): [description]. Defaults to StandardCurveTypes.Line.
            predecessorOffset (int, optional): lane number of predecessor. refernce line of this road can be shifted with this setting wrt the predecessor. -1 means reference line will start from the border of -1 lane of predecessor
        """
        super().__init__(road_id, planview, lanes, road_type, name, rule)
        self.signals = Signals()

        self.curveType = curveType
        self.headingTangentMagnitude = 10 # 10 meters.
        self.isConnection = False
        self.isSingleLaneConnection = False
        self.elementType = pyodrx.ElementType.road

        if road_type == 1:
            self.isConnection = True
            self.elementType = pyodrx.ElementType.junction
        
        if self.isConnection is False and predecessorOffset != 0:
            raise Exception("Cannot set predecessorOffset for non-connection road to non-zero")

        self.predecessorOffset = predecessorOffset
        self.extendedPredecessors = {}
        self.extendedSuccessors = {}
        self.startHeading = None

        self.junctionId = None # populated by junctionDef
        self.junctionRelation = None # successor if the junction is the successor, predecessor is otherwise.
        self.junctionCP = None # populated by junction builder or connection builder.
        self.linkConfig = None # populated by connection builder

        self.predefinedLaneLinks = []

        pass

    def isUturn(self):
        """When successor and predecessor are the same road and have the same cp"""
        if len(self.extendedPredecessors) != 1 or len(self.extendedSuccessors) !=1:
            return False

        eSuccessor = list(self.extendedSuccessors.values())[0]
        ePredecessor = list(self.extendedPredecessors.values())[0]

        if (eSuccessor.road == ePredecessor.road) and (eSuccessor.cp == ePredecessor.cp):
            return True
        return False


    
    def get_attributes(self):
        """ returns the attributes as a dict of the Road

        """
        retdict = {}
        if self.name:
            retdict['name'] = self.name
        if self.rule:
            retdict['rule'] = self.rule
        retdict['id'] = str(self.id)
        if self.isConnection:
            retdict['junction'] = str(self.junctionId)
        else:
            retdict['junction'] = '-1'
        retdict['length'] = str(self.planview.get_total_length())
        return retdict

    def get_element(self):

        """Changes successor or predecessor links to junction if available

        Returns:
            [type]: [description]
        """

        if self.hasLanes() == False:
            return None

        if self.junctionId is not None and self.isConnection == False:
            if self.junctionRelation == 'successor':
                self.updateSuccessor(pyodrx.ElementType.junction, self.junctionId, self.junctionCP)
                self._removePredecessor()
            else:
                self.updatePredecessor(pyodrx.ElementType.junction, self.junctionId, self.junctionCP)
                self._removeSuccessor()

        element = super().get_element()
        element.append(self.signals.get_element())
        return element

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
        return self.planview.getTotalLength()

    

    #region successor, predecessor
    def updatePredecessor(self, element_type,element_id,contact_point=None):
        """ updatePredecessor adds a predecessor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the predecessor on the predecessor

        """
        self._removePredecessor()
        element_id = int(element_id)
        self.add_predecessor(element_type, element_id, contact_point)
        pass


    def _removePredecessor(self):
        self.predecessor = None
        for link in self.links.links:
            if link.link_type == 'predecessor':
                self.links.links.remove(link)
                break


    def updateSuccessor(self, element_type,element_id,contact_point=None):
        """ updateSuccessor adds a successor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the Successor on the Successor

        """
        self._removeSuccessor()
                
        element_id = int(element_id)
        self.add_successor(element_type, element_id, contact_point)
        pass


    def _removeSuccessor(self):
        self.successor = None
        for link in self.links.links:
            if link.link_type == 'successor':
                self.links.links.remove(link)
                break


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

    def getElementType(self):
        # if self.isConnection:
        #     return pyodrx.ElementType.junction
        return pyodrx.ElementType.road


    def addExtendedPredecessor(self, road, angleWithRoad, cp, xodr=False):
        self.extendedPredecessors[road.id] = ExtendedPredecessor(road, angleWithRoad, cp)
        if xodr or self.predecessor is None:
            self.updatePredecessor(road.getElementType(), road.id, contact_point=cp)
        pass


    def getExtendedPredecessorByRoadId(self, roadId):

        if roadId in self.extendedPredecessors:
            return self.extendedPredecessors[roadId]
        
        return None
    

    def isExtendedPredecessorOf(self, road):
        if road.getExtendedPredecessorByRoadId(self.id) is not None:
            return True
        return False


    def addExtendedSuccessor(self, road, angleWithRoad, cp, xodr=False):
        self.extendedSuccessors[road.id] = ExtendedSuccessor(road, angleWithRoad, cp)
        if xodr or self.successor is None:
            self.updateSuccessor(road.getElementType(), road.id, contact_point=cp)
        pass


    def getExtendedSuccessorByRoadId(self, roadId):

        if roadId in self.extendedSuccessors:
            return self.extendedSuccessors[roadId]
        
        return None


    def isExtendedSuccessorOf(self, road):
        if road.getExtendedSuccessorByRoadId(self.id) is not None:
            return True
        return False

    #endregion
    
    def isConnectionFor(self, road1, road2):

        # to be a connection, one of the roads needs to be an extended predecessor and another and extended successor.

        if (road1.isExtendedPredecessorOf(self) and road2.isExtendedSuccessorOf(self)) or (road2.isExtendedPredecessorOf(self) and road1.isExtendedSuccessorOf(self)):
            return True
        return False

    
    def updatePredecessorOffset(self, predecessorOffset):
        if self.isConnection is False:
            raise Exception("Cannot set predecessorOffset for non-connection road")

        self.predecessorOffset = predecessorOffset




    def isJunction(self):
        return self.isConnection
        

    def shallowCopy(self):
        copiedRoad = copy(self)
        copiedRoad.reset(clearRoadLinks=True)
        self.reinitializePropertiesForCopy(copiedRoad)
        self.copyLanesForCopy(copiedRoad)
        self.copyPVforCopy(copiedRoad)
        return copiedRoad
        

    def reinitializePropertiesForCopy(self, copiedRoad):
        copiedRoad.extendedPredecessors = {}
        copiedRoad.extendedSuccessors = {}
        copiedRoad.startHeading = None
    

    def copyLanesForCopy(self, copiedRoad):
        copiedRoad.lanes = self.lanes.copy()


    def copyPVforCopy(self, copiedRoad):
        copiedRoad.planview = self.planview.copy()
        

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
        startX, startY, startH = geoms[0].x, geoms[0].y, geoms[0].heading
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
        g = geoms[-1]
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


    #region Lane Section related functions

    def hasLanes(self):
        return self.lanes.hasLanes()


    def clearLanes(self):
        self.lanes.clearLanes()
        self.clearLaneLinks()

    def getLaneSections(self):
        return self.lanes.lanesections

        
    def getLastLaneSection(self):
        return self.lanes.lanesections[-1]


    def getFirstLaneSection(self):
        return self.lanes.lanesections[0]

    
    def getLaneSectionByCP(self, cp):

        if cp == pyodrx.ContactPoint.start:
            return self.getFirstLaneSection()
        return self.getLastLaneSection()

    def getLaneOffsetByCP(self, cp):
        if cp == pyodrx.ContactPoint.start:
            return self.getFirstLaneOffset()
        return self.getLastLaneOffset()

    
    def getLaneSectionAndLaneOffsetByCP(self, cp):
        return self.getLaneSectionByCP(cp), self.getLaneOffsetByCP(cp)
    
    
    def hasLaneOffsets(self):
        if hasattr(self.lanes, 'laneOffsets'):
            return True
        return False

    def getFirstLaneOffset(self):

        if len(self.lanes.laneOffsets) == 0:
            return extensions.LaneOffset.createParallel(0, 0)
        return self.lanes.laneOffsets[0]
        

    def getLastLaneOffset(self):
        if len(self.lanes.laneOffsets) == 0:
            return extensions.LaneOffset.createParallel(0, 0)
        return self.lanes.laneOffsets[-1]


    def setFirstLaneOffset(self, laneOffset):
        if len(self.lanes.laneOffsets) == 0:
            self.lanes.laneOffsets.append(laneOffset)
        else:
            self.lanes.laneOffsets[0] = laneOffset

    def setLastLaneOffset(self, laneOffset):
        if len(self.lanes.laneOffsets) == 0:
            self.lanes.laneOffsets.append(laneOffset)
        else:
            self.lanes.laneOffsets[-1] = laneOffset

    
    def getEndPointWidths(self):
        """[summary]
        Returns:
            (tuple) : (startWidth, endWidth)
        """

        return self.lanes.getEndPointWidths(self.length())
    
    
    
    def getBorderDistanceLeft(self, cp):
        ls = self.getLaneSectionByCP(cp)
        lastLaneNo = len(ls.leftlanes)
        return self.getBorderDistanceOfLane(lastLaneNo, cp)


    def getBorderDistanceRight(self, cp):
        ls = self.getLaneSectionByCP(cp)
        lastLaneNo = -len(ls.rightlanes)
        return self.getBorderDistanceOfLane(lastLaneNo, cp)



    def getBorderDistanceOfLane(self, laneNo, cp):
        """returns distance of outer border to the center lane.

        Args:
            laneNo ([type]): [description] 
            cp ([type]):  cp = pyodrx.ContactPoint.end/start. border distance  reference point.

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """

        if laneNo == 0:
            return 0

        # 1. Assuming cp is start point
        laneSection = self.lanes.lanesections[0]
        laneOffset = self.lanes.getLaneOffsetAt(0)
        nextLaneOffset = self.lanes.getLaneOffsetAt(1)
        sectionLength = None # not needed for start point as ds is 0

        # 2. Chaning if cp is end.

        if cp ==  pyodrx.ContactPoint.end:
            if self.length is None:
                raise Exception("Lane border distance cannot be calcualted at the end point without road length")

            laneSection = self.lanes.lanesections[-1]
            laneOffset = self.lanes.getLaneOffsetAt(len(self.lanes.lanesections) - 1)
            nextLaneOffset = None
            sectionLength = laneSection.length(self.length(), laneOffset, nextLaneOffset)

        # 3. Now the calculations

        lanes = laneSection.leftlanes
        if laneNo < 0:
            lanes = laneSection.rightlanes
        
        laneLimit = abs(laneNo)

        width = 0

        for i in range(laneLimit):
            lane = lanes[i]

            if cp == pyodrx.ContactPoint.start and lane.soffset == 0: # if offset is not 0, this lane does not contribute to the width.
                width += lane.a
            elif cp == pyodrx.ContactPoint.end:
                
                sectionLength = self.length() - lane.soffset

                coeffs = [lane.a, lane.b, lane.c, lane.d]
                pRange=[sectionLength]
                laneWidths = Geometry.evalPoly(coeffs, pRange)
                width += laneWidths[0]
        
        return width


    def getLanePosition(self, laneNo, cp):
        """returns the intertial position of lane boundary. road must be 

        Args:
            laneNo ([type]): [description]
            cp ([type]): [description]
        """

        # 1. get reference line position

        x, y, h = self.getPosition(cp)

        if laneNo == 0:
            return x, y, h

        # 2. shift reference line position
        
        # in local coordinate the reference line moves along v

        localShiftAmount = self.getBorderDistanceOfLane(laneNo, cp)

        if laneNo > 0: 
            x += localShiftAmount * math.cos(h + np.pi/2)
            y += localShiftAmount * math.sin(h + np.pi/2)
        else:
            x += localShiftAmount * math.cos(h - np.pi/2)
            y += localShiftAmount * math.sin(h - np.pi/2) 

        return x, y, h


    #endregion


    #region junction