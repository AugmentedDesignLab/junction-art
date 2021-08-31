import junctions
from junctions.LaneSides import LaneSides
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
from junctions.Intersection import Intersection
from junctions.JunctionDef import JunctionDef
from junctions.LaneMarkGenerator import LaneMarkGenerator


class JunctionBuilderFromPointsAndHeading():
    def __init__(self,
                 country=CountryCodes.US,
                 laneWidth=3):

        self.name = 'Junction Builder From Points And Heading'
        self.straightRoadBuilder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.connectionBuilder = ConnectionBuilder()
        self.laneMarkGenerator = LaneMarkGenerator(countryCode=country)
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
        odr = extensions.createOdrByPredecessor(odrName, roads, [], countryCode=self.countryCode)

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
            odrStraightRoad = extensions.createOdrByPredecessor(odrName, [straightRoad], [], countryCode=self.countryCode)
            newStartX, newStartY, newHeading = point[0], point[1], point[2]
            odrAfterTransform = ODRHelper.transform(odrStraightRoad, newStartX, newStartY, newHeading)
            # outsideRoads.append(straightRoad.shallowCopy())
            straightRoadList.append(straightRoad)
            roadID += 2

        return straightRoadList
        
    
    def assertNoNegativeHeadings(self, roadDefinition):
        for roadDef in roadDefinition:
            if roadDef['heading'] < 0:
                raise Exception(f"heading cannot be negative")

    
    def assertClockwiseOrder(self, roadDefinition):
        
        if len(roadDefinition) == 2:
            return
        
        # print(roadDefinition)

        # 3. start with the second road and stop at first.
        prevHeading = roadDefinition[1]['heading']
        n = len(roadDefinition)

        for i in range(2, n):
            if roadDefinition[i]['heading'] > prevHeading:
                raise Exception(f"Road definition is not in clockwise manner")
            prevHeading = roadDefinition[i]['heading']

        
        



    def validateRoadDefinition(self, roadDefinition):

        # for road in roadDefinition:
        #     print(road)
        
        if roadDefinition is None or len(roadDefinition) < 2:
            raise Exception("Provide definition for more then two roads")

        
        roadDefinitionCopy = copy.deepcopy(roadDefinition)
        
        # validate if the points are clockwise (headings need to be decreasing in clockwise manner assuming first roads heading is 0)
        # 1. subtract first road heading from all NO!!
        firstHeading = roadDefinitionCopy[0]['heading']
        for roadDef in roadDefinitionCopy:
            roadDef['heading'] -= firstHeading

        # for now, do not accept negative headings
        # self.assertNoNegativeHeadings(roadDefinition)
        # self.assertNoNegativeHeadings(roadDefinitionCopy)

        # # 2 special case, last road and first road. If the heading of the last road is positive, it will be greater than 0, else it will be less than 0.
        # if roadDefinitionCopy[-1]['heading']
        # 3. start with the second road and stop at first.
        print(roadDefinitionCopy)
        self.assertClockwiseOrder(roadDefinitionCopy)
            



    def createIntersectionFromPointsWithRoadDefinition(self,
                                                       odrID,
                                                       roadDefinition,
                                                       firstRoadId,
                                                       straightRoadLen=20,
                                                       getAsOdr=False):

        self.validateRoadDefinition(roadDefinition)

        outsideRoads = []
        outSideRoadsShallowCopy = []
        paramPolyRoads = []
        roads = []

        nextRoadId = firstRoadId

        # create straight road
        outsideRoads, nextRoadId = self.createStraightRoadsFromRoadDefinition(nextRoadId=nextRoadId, 
                                                                              roadDefinition=roadDefinition,
                                                                              straighRoadLength=straightRoadLen)

        
        # create parampoly connection road
        geoConnectionRoads, nextRoadId = self.createParamPolyConnectionRoads(nextRoadId=nextRoadId, outsideRoads=outsideRoads)

        for outsideRoad in outsideRoads:
            outSideRoadsShallowCopy.append(outsideRoad.shallowCopy())

        roads = self.createSuccPredAndAppendRoadsInOrder(outSideRoadsShallowCopy=outSideRoadsShallowCopy,
                                                         paramPolyRoads=geoConnectionRoads)

        # self.fixNumOutgoingLanes(outSideRoadsShallowCopy, pyodrx.ContactPoint.start)

        odrName = "odr_from_points" + str(odrID)
        odr = extensions.createOdrByPredecessor(odrName, roads, [], countryCode=self.countryCode)

        # We need link configurations only if the number of incident roads are greater than 2.
        # if len(roadDefinition) > 2:
        for geoRoad in geoConnectionRoads:
            geoRoad.clearLanes()
        internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(nextRoadId=nextRoadId,
                                                                                    outsideRoads=outSideRoadsShallowCopy,
                                                                                    cp1=pyodrx.ContactPoint.start,
                                                                                    strategy=LaneConfigurationStrategies.SPLIT_ANY)
        
        nextRoadId += len(internalConnections)
        roads += internalConnections
        odr.updateRoads(roads)
        connectionRoads = internalConnections
        
        # U-turns
        uTurnConnections = self.connectionBuilder.createUTurnConnectionRoads(nextRoadId, outSideRoadsShallowCopy, pyodrx.ContactPoint.start)
        nextRoadId += len(uTurnConnections)
        roads += uTurnConnections
        odr.updateRoads(roads)
        # self.addInternalConnectionsToJunction(junction, internalConnections)
        connectionRoads += uTurnConnections

        # U-turns ends

        # lane marks
        # self.laneMarkGenerator.removeLaneMarkFromRoads(uTurnConnections)
        # self.laneMarkGenerator.addBrokenWhiteToInsideLanesOfRoads(outSideRoadsShallowCopy)

        # junction creation
        junction = JunctionDef(nextRoadId).build(connectionRoads)
        
        odr.resetAndReadjust(byPredecessor=True)
        odr.add_junction(junction)
        finalTransformedODR = ODRHelper.transform(odr=odr,
                                                  startX=roadDefinition[0]['x'],
                                                  startY=roadDefinition[0]['y'],
                                                  heading=roadDefinition[0]['heading'])

        incidentContactPoints = []

        for _ in outSideRoadsShallowCopy:
            incidentContactPoints.append(pyodrx.ContactPoint.start)

        if getAsOdr:
            return odr

        intersection = Intersection(odrID, outSideRoadsShallowCopy, incidentContactPoints, geoConnectionRoads=paramPolyRoads, internalConnectionRoads=connectionRoads, odr=finalTransformedODR)
        return intersection

    
    def createSuccPredAndAppendRoadsInOrder(self, outSideRoadsShallowCopy, paramPolyRoads):
        numberOfShallowRoads = len(outSideRoadsShallowCopy)
        orderedRoadsList = []
        for i in range(0, numberOfShallowRoads):
            RoadLinker.createExtendedPredSuc(predRoad=outSideRoadsShallowCopy[i], predCp=pyodrx.ContactPoint.start,
                                              sucRoad=paramPolyRoads[i],           sucCP=pyodrx.ContactPoint.start)
            if i != numberOfShallowRoads - 1:
                RoadLinker.createExtendedPredSuc(predRoad=paramPolyRoads[i],           predCp=pyodrx.ContactPoint.end,
                                                  sucRoad=outSideRoadsShallowCopy[i+1], sucCP=pyodrx.ContactPoint.start)
            orderedRoadsList.append(outSideRoadsShallowCopy[i])
            orderedRoadsList.append(paramPolyRoads[i])
        return orderedRoadsList

    def createParamPolyConnectionRoads(self,nextRoadId,  outsideRoads):
        roadID = nextRoadId
        paramPolyRoadList = []
        numberOfStraightRoad = len(outsideRoads)
        for i in range(0, numberOfStraightRoad):
            road1 = outsideRoads[i]
            if i == numberOfStraightRoad-1:
                road2 = outsideRoads[0]
            else:
                road2 = outsideRoads[i+1]
            
            paramPolyRoad = self.junctionBuilder.createConnectionFor2Roads(nextRoadId=roadID,
                                                                            road1=road1,
                                                                            road2=road2,
                                                                            junction=None,
                                                                            cp1=pyodrx.ContactPoint.start,
                                                                            cp2=pyodrx.ContactPoint.start)
            paramPolyRoadList.append(paramPolyRoad)
            roadID += 1
        return paramPolyRoadList, roadID


    def createStraightRoadsFromRoadDefinition(self, nextRoadId, roadDefinition, straighRoadLength):
        roadID = nextRoadId
        straightRoadList = []
        for road in roadDefinition:
            if road['medianType'] != None:
                straightRoad = self.straightRoadBuilder.createWithMedianRestrictedLane(roadId=roadID,
                                                                                       n_lanes_left=road['leftLane'],
                                                                                       n_lanes_right=road['rightLane'],
                                                                                       length=straighRoadLength,
                                                                                       medianType=road['medianType'],
                                                                                       medianWidth=2,
                                                                                       skipEndpoint=road['skipEndpoint'])
            else:
                straightRoad = self.straightRoadBuilder.create(roadId=roadID,
                                                               n_lanes_right=road['rightLane'],
                                                               n_lanes_left=road['leftLane'],
                                                               length=straighRoadLength,
                                                               )
            
            
            straightRoad.junctionCP = pyodrx.ContactPoint.start
            straightRoad.junctionRelation = 'predecessor'

            odrName = "tempODR_StraightRoad" + str(roadID)
            odrStraightRoad = extensions.createOdrByPredecessor(odrName, [straightRoad], [], countryCode=self.countryCode)
            newStartX, newStartY, newHeading = road['x'], road['y'], road['heading']
            odrAfterTransform = ODRHelper.transform(odrStraightRoad, newStartX, newStartY, newHeading)
            # extensions.printRoadPositions(odrAfterTransform)
            straightRoadList.append(straightRoad)
            roadID += 1

        return straightRoadList, roadID
                


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