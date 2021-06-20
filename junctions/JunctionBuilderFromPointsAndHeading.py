import pyodrx
import extensions
from junctions.StraightRoadBuilder import StraightRoadBuilder
from junctions.ODRHelper import ODRHelper
import math
from junctions.JunctionBuilder import JunctionBuilder
import copy
from junctions.RoadLinker import RoadLinker
from junctions.LaneBuilder import LaneBuilder
from junctions.LaneConfiguration import LaneConfiguration
from extensions.CountryCodes import CountryCodes
from junctions.ConnectionBuilder import ConnectionBuilder
from junctions.LaneConfiguration import LaneConfigurationStrategies


class JunctionBuilderFromPointsAndHeading():
    def __init__(self,
                 country=CountryCodes.US,
                 laneWidth=3):

        self.name = 'Junction Builder From Points And Heading'
        self.straightRoadBuilder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.connectionBuilder = ConnectionBuilder()
        self.countryCode = country
        self.laneWidth = laneWidth
        pass

    

    def createIntersectionFromPoints(self,
                                     odrID=0, 
                                     points=None, 
                                     straightRoadLen=10,
                                     firstRoadID=0,
                                     maxLanePerSide=2,
                                     minLanePerSide=0,
                                     skipEndpoint=None):

        if points is None or len(points) < 3:
            raise Exception("provide three or more points")

        outsideRoads = []
        outSideRoadsShallowCopy = []
        paramPolyRoads = []
        roads = []

        # create all the straight road with even numbered ID
        outsideRoads = self.createStraightRoads(points, straightRoadLen, firstRoadID, maxLanePerSide, minLanePerSide, skipEndpoint)
            
        
        # create all parampoly roads
        paramPolyRoads, roadID = self.createParamPolyRoads(firstRoadID, outsideRoads)

        for outsideRoad in outsideRoads:
            outSideRoadsShallowCopy.append(outsideRoad.shallowCopy())
        
        # joining roads by successor predecessor relationship
        self.createSuccPredStraightAndParamPloyRoads(outSideRoadsShallowCopy, paramPolyRoads, roads)


        self.fixNumOutgoingLanes(outSideRoadsShallowCopy, pyodrx.ContactPoint.start)
        odrName = "ODR_from_points " + str(odrID)
        odr = extensions.createOdrByPredecessor(odrName, roads, [])

        roadID = roadID+1
        internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(roadID, outSideRoadsShallowCopy, 
                                                                                    pyodrx.ContactPoint.start,
                                                                                    LaneConfigurationStrategies.SPLIT_ANY)
        roadID += len(internalConnections)
        roads += internalConnections
        odr.updateRoads(roads)

        odr.resetAndReadjust(byPredecessor=True)
        

        odr = ODRHelper.transform(odr=odr, 
                                  startX=points[0][0],
                                  startY=points[0][1],
                                  heading=points[0][2])
        # for road in roads:
        #     print(road.getAdjustedStartPosition())
        #     print(road.getAdjustedEndPosition())
        
        return odr

    def createSuccPredStraightAndParamPloyRoads(self, outSideRoadsShallowCopy, paramPolyRoads, roads):
        for i in range(0, len(outSideRoadsShallowCopy)-1):
            RoadLinker.createExtendedPredSuc(predRoad=outSideRoadsShallowCopy[i],  predCp=pyodrx.ContactPoint.start,
                                              sucRoad=paramPolyRoads[i],            sucCP=pyodrx.ContactPoint.start)
            RoadLinker.createExtendedPredSuc(predRoad=paramPolyRoads[i],           predCp=pyodrx.ContactPoint.end,
                                              sucRoad=outSideRoadsShallowCopy[i+1], sucCP=pyodrx.ContactPoint.start)

            roads.append(outSideRoadsShallowCopy[i])
            roads.append(paramPolyRoads[i])

        RoadLinker.createExtendedPredSuc(predRoad=outSideRoadsShallowCopy[-1], predCp=pyodrx.ContactPoint.start,
                                          sucRoad=paramPolyRoads[-1],           sucCP=pyodrx.ContactPoint.start)


        roads.append(outSideRoadsShallowCopy[-1])
        roads.append(paramPolyRoads[-1])

    def createParamPolyRoads(self, firstRoadID, outsideRoads):
        roadID = firstRoadID+1
        paramPolyRoadList = []
        for i in range(0, len(outsideRoads)-1):
            paramPolyRoad = self.junctionBuilder.createConnectionFor2Roads(nextRoadId=roadID,
                                                                           road1=outsideRoads[i],
                                                                           road2=outsideRoads[i+1],
                                                                           junction=None,
                                                                           cp1=pyodrx.ContactPoint.start,
                                                                           cp2=pyodrx.ContactPoint.start)
            paramPolyRoadList.append(paramPolyRoad)
            roadID += 2

        # connection between first and last road
        paramPolyRoad = self.junctionBuilder.createConnectionFor2Roads(nextRoadId=roadID,
                                                                       road1=outsideRoads[-1],
                                                                       road2=outsideRoads[0],
                                                                       junction=None,
                                                                       cp1=pyodrx.ContactPoint.start,
                                                                       cp2=pyodrx.ContactPoint.start)
        paramPolyRoadList.append(paramPolyRoad)
        return paramPolyRoadList, roadID

    def createStraightRoads(self, 
                            points, 
                            straightRoadLen, 
                            firstRoadID, 
                            maxLanePerSide, 
                            minLanePerSide, 
                            skipEndpoint):
        
        roadID = firstRoadID
        straightRoadList = []
        for point in points:
            straightRoad = self.straightRoadBuilder.createRandom(roadId=roadID, 
                                                                 length=straightRoadLen,
                                                                 maxLanePerSide=maxLanePerSide,
                                                                 minLanePerSide=minLanePerSide,
                                                                 skipEndpoint=skipEndpoint)
            odrName = "tempODR_StraightRoad" + str(roadID)
            odrStraightRoad = extensions.createOdrByPredecessor(odrName, [straightRoad], [])
            newStartX, newStartY, newHeading = point[0], point[1], point[2]
            odrAfterTransform = ODRHelper.transform(odrStraightRoad, newStartX, newStartY, newHeading)
            # outsideRoads.append(straightRoad.shallowCopy())
            straightRoadList.append(straightRoad)
            roadID += 2

        return straightRoadList
        


    def fixNumOutgoingLanes(self, roads, cp1): 
        """Assumes all roads except the first road have start point in the intersection.

        Args:
            roads ([type]): outside roads for an intersection
            cp1 ([type]): contact point of the first road
        """

        roadDic = {}
        for road in roads:
            roadDic[road.id] = road


        firstRoadId = roads[0].id
        incomingLanes = []
        outgoingLanes = []
        cp = None
        for road in roads:

            if road.id == firstRoadId:
                cp = cp1
            else:
                cp = pyodrx.ContactPoint.start
            
            incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(road, cp, self.countryCode)
            outgoingLaneIds = LaneConfiguration.getOutgoingLanesIdsFromARoad(road, roads, cp1, self.countryCode)


            diff = len(incomingLanes) - len(outgoingLaneIds) 
            if diff > 0:

                if len(outgoingLaneIds) == 0:
                    # special case when we have no outgoing lanes
                    if road.id != firstRoadId:
                        self.laneBuilder.addOutgoingLanes(roads[0], cp1, diff, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addOutgoingLanes(roads[-1], pyodrx.ContactPoint.start, diff, self.countryCode, laneWidth=self.laneWidth)
                else:
                    # add necessary outgoing lanes to the first road with existing outgoing lanes
                    firstOutgoinRoadId = int(outgoingLaneIds[0].split(':')[0])
                    if firstOutgoinRoadId == firstRoadId:
                        self.laneBuilder.addOutgoingLanes(roads[0], cp1, diff, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addOutgoingLanes(roadDic[firstOutgoinRoadId], pyodrx.ContactPoint.start, diff, self.countryCode, laneWidth=self.laneWidth)


            # now check if the road as lonely outgoing lanes, add one incoming lane to some other road if needed.
            outgoingLanes = LaneConfiguration.getOutgoingLanesOnARoad(road, cp, self.countryCode)
            incomingLaneIds = LaneConfiguration.getIncomingLanesIdsToARoad(road, roads, cp1, self.countryCode)

            if len(outgoingLanes) > 0 and len(incomingLaneIds) == 0:
                if len(incomingLaneIds) == 0:
                    # special case when we have no incoming lanes
                    if road.id != firstRoadId:
                        self.laneBuilder.addIncomingLanes(roads[0], cp1, 1, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addIncomingLanes(roads[-1], pyodrx.ContactPoint.start, 1, self.countryCode, laneWidth=self.laneWidth)
                else:
                    firstIncomingRoadId = int(incomingLaneIds[0].split(':')[0])
                    if firstIncomingRoadId == firstRoadId:
                        self.laneBuilder.addIncomingLanes(roads[0], cp1, 1, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addIncomingLanes(roadDic[firstIncomingRoadId], pyodrx.ContactPoint.start, 1, self.countryCode, laneWidth=self.laneWidth)



        pass