import pyodrx, math
from junctions.RoadBuilder import RoadBuilder
import numpy as np
import extensions
from junctions.LaneSides import LaneSides
from junctions.Direction import CircularDirection
from junctions.JunctionAreaTypes import JunctionAreaTypes
from junctions.StraightRoadBuilder import StraightRoadBuilder
from extensions.ExtendedRoad import ExtendedRoad
from junctions.RoadLinker import RoadLinker
from junctions.JunctionBuilder import JunctionBuilder
from junctions.StandardCurveTypes import StandardCurveTypes
from junctions.AngleCurvatureMap import AngleCurvatureMap

class SequentialJunctionBuilder(JunctionBuilder):
    

    def drawLikeAPainter2L(self, odrId, maxNumberOfRoadsPerJunction, save=True, internalConnections=True, cp1=pyodrx.ContactPoint.start):
        if maxNumberOfRoadsPerJunction < 3:
            raise Exception("drawLikeAPainter is not for the weak. Please add more than 3 roads")

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length=self.straightRoadLen * 4)) # first road

        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / (maxNumberOfRoadsPerJunction - 1)
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            print(f"availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = self.straightRoadBuilder.create(newRoadId, length=self.straightRoadLen)

            # 2. create a new connection road
            newConnection, availableAngle = self.createNewConnectionForDrawing(action, newConnectionId, availableAngle, maxAnglePerConnection)
            
            # 5 add new roads and increase road id
            roads.append(newConnection)
            roads.append(newRoad)

            # roads[previousRoadId].add_successor(pyodrx.ElementType.junction, newConnection.id)
            roads[previousRoadId].addExtendedSuccessor(newConnection, 0, pyodrx.ContactPoint.start)

            if newConnection.id == 1:
                # TODO this is a hack. It will not eventually work because outgoing roads' ends will come to join other junctions.
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , cp1)
            else:
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , pyodrx.ContactPoint.start)
            
            RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=newRoad, sucCP=pyodrx.ContactPoint.start)


            # 6 get next action
            action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
            pass
        
        # 3. create connections and junction

        junction = self.createJunctionForASeriesOfRoads(roads)

        # print(f"number of roads created {len(roads)}")
        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction, cp1=cp1)
        odr.add_road(lastConnection)

        print(f"roads before internal connections {len(roads)}")

        if internalConnections:
            self.createInternalConnectionsForOddIndices(roads, junction, cp1=cp1)
            odr.updateRoads(roads)

        print(f"roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        
        return odr


    def createNewConnectionForDrawing(self, action, newConnectionId, availableAngle, maxAnglePerConnection):

        newConnection = None
        newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        return newConnection, availableAngle
        # if action is 'straightLine':
        #     newConnection = pyodrx.create_straight_road(newConnectionId, self.straightRoadLen, junction=1)
        #     availableAngle -= np.pi
        # elif action is 'curve':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        # elif action is 'spiral':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle,maxAnglePerConnection,  newConnectionId, curveType= StandardCurveTypes.Simple)
        # elif action is 's':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.S)

        # return newConnection, availableAngle


    def createCurveForDrawing(self, availableAngle, maxAnglePerConnection, newConnectionId, curveType):
        angleBetweenEndpoints = self.getSomeAngle(availableAngle, maxAnglePerConnection)
        availableAngle -= angleBetweenEndpoints
        # curvature = StandardCurvature.getRandomValue()
        curvature = AngleCurvatureMap.getCurvatureForJunction(angleBetweenEndpoints)

        print(f"Curvature for angle {math.degrees(angleBetweenEndpoints)} is {curvature}")
        # if curvature < StandardCurvature.Medium.value:
        #     curvature = StandardCurvature.Medium.value

        newConnection = self.roadBuilder.createCurve(newConnectionId, angleBetweenEndpoints, isJunction=True, curvature=curvature, curveType=curveType)
        return newConnection, availableAngle



    def getSomeAngle(self, availableAngle, maxAnglePerConnection):

        angle = (availableAngle * np.random.choice(10)) / 9

        
        if angle < self.minAngle:
            angle = self.minAngle

        if angle > maxAnglePerConnection:
            angle = maxAnglePerConnection
        return angle

    
    def actionAfterDrawingOne(self, currentRoads, availableAngle, maxNumberOfRoads):


        actions = ['straightLine', "curve", "spiral", "s"]
        
        if availableAngle < self.minAngle:
            return "end"
        
        if len(currentRoads) >= (maxNumberOfRoads * 2 - 1): # dont count connection roads
            return "end"
        
        return actions[np.random.choice(len(actions))]


