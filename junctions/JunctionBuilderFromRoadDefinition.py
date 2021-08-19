import copy
from junctions import Intersection
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.RoadLinker import RoadLinker
import pyodrx
from junctions.ODRHelper import ODRHelper
import extensions
from extensions.CountryCodes import CountryCodes
from junctions.Intersection import Intersection
import numpy as np
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder

class JunctionBuilderFromRoadDefinition(SequentialJunctionBuilder):
    
    def __init__(self, 
                 roadBuilder=None, 
                 straightRoadLen=10, 
                 minAngle=np.pi/6, 
                 maxAngle=np.pi, 
                 country=CountryCodes.US, 
                 random_seed=2, 
                 minConnectionLength=10, 
                 maxConnectionLength=30, 
                 probMinAngle=0.5, 
                 probLongConnection=0.5, 
                 probRestrictedLane=0.2):

        super().__init__(roadBuilder=roadBuilder, 
                         straightRoadLen=straightRoadLen, 
                         minAngle=minAngle, 
                         maxAngle=maxAngle, 
                         country=country, 
                         random_seed=random_seed, 
                         minConnectionLength=minConnectionLength, 
                         maxConnectionLength=maxConnectionLength, 
                         probMinAngle=probMinAngle, 
                         probLongConnection=probLongConnection, 
                         probRestrictedLane=probRestrictedLane)

        self.name = 'JunctionBuilderFromRoadDefinition'
        
        

    def assertNoNegativeHeadings(self, roadDefinition):
        for roadDef in roadDefinition:
            if roadDef['heading'] < 0:
                raise Exception(f"heading cannot be negative")

    def assertClockwiseOrder(self, roadDefinition):
        
        if len(roadDefinition) == 2:
            return
        
        print(roadDefinition)

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
        self.assertClockwiseOrder(roadDefinitionCopy)



    def createIntersectionFromPointsWithRoadDefinition(self,
                                                       odrID,
                                                       roadDefinition,
                                                       firstRoadID,
                                                       straightRoadLength=20,
                                                       getAsOdr = False):

        self.validateRoadDefinition(roadDefinition)
        # variable declaration
        outsideRoads = []
        outsideRoadsShallowCopy = []
        geoConnectionRoads = []
        roads = []

        nextRoadID = firstRoadID

        # creating straight roads
        outsideRoads, nextRoadID = self.createStraightRoadsFromRoadDefinition(nextRoadID=nextRoadID,
                                                                              roadDefinition=roadDefinition,
                                                                              straightRoadLength=straightRoadLength)
        
        # creating geometric connection roads
        geoConnectionRoads, nextRoadID = self.createGeoConnectionRoads(nextRoadId=nextRoadID,
                                                                       outsideRoads=outsideRoads)

        for outsideRoad in outsideRoads:
            outsideRoadsShallowCopy.append(outsideRoad.shallowCopy())
        
        roads = self.createSuccPredAndAppendRoadsInOrder(outSideRoadsShallowCopy=outsideRoadsShallowCopy,
                                                         geoConnectionRoads=geoConnectionRoads)
        
        
        odrName = "odr_from_points" + str(odrID)
        odr = extensions.createOdrByPredecessor(odrName, roads, [])

        for geoConnectionRoad in geoConnectionRoads:
            geoConnectionRoad.clearLanes()
        
        # internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(nextRoadId=nextRoadID,
        #                                                                             outsideRoads=outsideRoadsShallowCopy,
        #                                                                             cp1=pyodrx.ContactPoint.start,
        #                                                                             strategy=LaneConfigurationStrategies.SPLIT_ANY)
        # roads += internalConnections
        # odr.updateRoads(roads)
        # odr.resetAndReadjust(byPredecessor=True)
        finalTransformedODR = ODRHelper.transform(odr=odr,
                                                  startX=roadDefinition[0]['x'],
                                                  startY=roadDefinition[0]['y'],
                                                  heading=roadDefinition[0]['heading'])

        incidentContactPoints = []

        for _ in outsideRoadsShallowCopy:
            incidentContactPoints.append(pyodrx.ContactPoint.start)

        if getAsOdr:
            return odr

        intersection = Intersection(odrID, 
                                    outsideRoadsShallowCopy, 
                                    incidentContactPoints, 
                                    geoConnectionRoads=geoConnectionRoads, 
                                    odr=finalTransformedODR)
        return intersection


    def createStraightRoadsFromRoadDefinition(self,
                                              nextRoadID,
                                              roadDefinition,
                                              straightRoadLength):

        roadID = nextRoadID
        straightRoadList = []
        for road in roadDefinition:
            if road['medianType'] != None:
                straightRoad = self.straightRoadBuilder.createWithMedianRestrictedLane(roadId=roadID,
                                                                                       n_lanes_left=road['leftLane'],
                                                                                       n_lanes_right=road['rightLane'],
                                                                                       length=straightRoadLength,
                                                                                       medianType=road['medianType'],
                                                                                       medianWidth=3,
                                                                                       skipEndpoint=road['skipEndpoint'])
            else:
                straightRoad = self.straightRoadBuilder.create(roadId=roadID,
                                                               n_lanes_right=road['rightLane'],
                                                               n_lanes_left=road['leftLane'],
                                                               length=straightRoadLength,
                                                               )

            odrName = "tempODR_StraightRoad" + str(roadID)
            odrStraightRoad = extensions.createOdrByPredecessor(odrName, [straightRoad], [])
            newStartX, newStartY, newHeading = road['x'], road['y'], road['heading']
            odrAfterTransform = ODRHelper.transform(odrStraightRoad, newStartX, newStartY, newHeading)
            extensions.printRoadPositions(odrAfterTransform)
            straightRoadList.append(straightRoad)
            roadID += 1

        return straightRoadList, roadID      


    def createGeoConnectionRoads(self,nextRoadId,  outsideRoads):
        roadID = nextRoadId
        paramPolyRoadList = []
        numberOfStraightRoad = len(outsideRoads)
        for i in range(0, numberOfStraightRoad):
            road1 = outsideRoads[i]
            # road2 = outsideRoads[i+1]
            if i == numberOfStraightRoad-1:
                road2 = outsideRoads[0]
            else:
                road2 = outsideRoads[i+1]
            
            paramPolyRoad = self.createConnectionFor2Roads(nextRoadId=roadID,
                                                           road1=road1,
                                                           road2=road2,
                                                           junction=None,
                                                           cp1=pyodrx.ContactPoint.start,
                                                           cp2=pyodrx.ContactPoint.start)
            paramPolyRoadList.append(paramPolyRoad)
            roadID += 1
        return paramPolyRoadList, roadID



    def createSuccPredAndAppendRoadsInOrder(self, outSideRoadsShallowCopy, geoConnectionRoads):
        numberOfShallowRoads = len(outSideRoadsShallowCopy)
        orderedRoadsList = []
        for i in range(0, numberOfShallowRoads):
            RoadLinker.createExtendedPredSuc(predRoad=outSideRoadsShallowCopy[i], 
                                             predCp=pyodrx.ContactPoint.start,
                                             sucRoad=geoConnectionRoads[i],
                                             sucCP=pyodrx.ContactPoint.start)
            if i != numberOfShallowRoads - 1:
                RoadLinker.createExtendedPredSuc(predRoad=geoConnectionRoads[i],
                                                 predCp=pyodrx.ContactPoint.end,
                                                 sucRoad=outSideRoadsShallowCopy[i+1],
                                                 sucCP=pyodrx.ContactPoint.start)
            orderedRoadsList.append(outSideRoadsShallowCopy[i])
            orderedRoadsList.append(geoConnectionRoads[i])
        return orderedRoadsList
