from matplotlib.pyplot import disconnect
from roadgen.controlLine.ControlLine import ControlLine
from roadgen.controlLine.ControlPoint import ControlPoint
from typing import List, Tuple, Dict
from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np
import logging
import traceback

class ConnectionStrategy(Enum):
    NO_ORPHANS_BOTH = auto()
    NO_ORPHANS_FIRST = auto()
    NO_ORPHANS_SECOND = auto()
    MIN = auto()
    pass

class ControlLineGrid:

    def __init__(self, size=(1000, 1000), controlLinePairs = None, debug=True):
        self.size = size
        self.controlLinePairs = controlLinePairs
        self.lines = set([])
        for pair in controlLinePairs:
            self.lines.add(pair[0])
            self.lines.add(pair[1])

        self.connections = [] # just for cache
        self.debug = debug
        self.name = "ControlLineGrid"

    
    def createConnection(self, line1: ControlLine, line2:ControlLine, point1: ControlPoint, point2: ControlPoint):
        line1.createConnection(line2, point1, point2)
        line2.createConnection(line1, point2, point1)
        self.connections.append((line1, line2, point1, point2))


    def connect(self, pair: Tuple[ControlLine], strategy: ConnectionStrategy=ConnectionStrategy.MIN):

        # 1. connect closes points first


        if strategy == ConnectionStrategy.MIN:
            self.connectMIN(pair)



        # 2. connect orphane points.

    def connectMIN(self, pair: Tuple[ControlLine]):
        line1 = pair[0]
        line2 = pair[1]

        nearestDisconnectedPoints = self.nearestDisconnectedPoints(line1, line2)
        while nearestDisconnectedPoints is not None:
            self.createConnection(line1, line2, nearestDisconnectedPoints[0], nearestDisconnectedPoints[1])
            nearestDisconnectedPoints = self.nearestDisconnectedPoints(line1, line2)


    def connectControlPointsOnALine(self, line: ControlLine):

        prevPoint = None
        for point in line.getOrderedControlPoints():
            if prevPoint is not None:
                self.createConnection(line, line, prevPoint, point)
            prevPoint = point
            
    
    def connectControlLinesWithRectsAndTriangles(self, pair: Tuple[ControlLine]):

        # copy lines without control points
        # merge lines after done.


        
        if self.debug:
            logging.info(f"{self.name}: connectControlLinesWithRectsAndTriangles: Connecting new pairs")

        snapDistance = 50 # in meters
        minSeperation = 300
        maxSeparation = 400

        mdp = {
            'orthogonal': {
                'parallel': 0.4,
                'random': 0.4,
                'commonEnd': 0.2
            },
            'parallel': {
                'orthogonal': 0.3,
                'parallel': 0.4,
                'random': 0.2,
                'commonEnd': 0.1
            },
            'random': {
                'orthogonal': 0.2,
                'parallel': 0.4,
                'random': 0.3,
                'commonEnd': 0.1
            },
            'commonEnd': {
                'orthogonal': 0.3,
                'parallel': 0.4,
                'random': 0.2,
                'commonEnd': 0.1
            },
            'none': {
                'orthogonal': 0.3,
                'random': 0.7
            },
        }

        line1 = pair[0]
        line2 = pair[1]
        line1Copy = ControlLine(id=pair[0].id, start=pair[0].start, end=pair[0].end)
        line2Copy = ControlLine(id=pair[1].id, start=pair[1].start, end=pair[1].end)

        prevType = 'none'
        # nextType = np.random.choice(list(mdp[prevType].keys()), p=list(mdp[prevType].values()))

        # if nextType == 'orthogonal':
        #     projectionOn1 = line1.getProjection(line2.start)
        #     projectionOn2 = line2.getProjection(line1.start)
        #     if projectionOn2 is None and projectionOn1 is None:
        #         raise Exception(f"{self.name}: connectControlLinesWithRectsAndTriangles cannot create the first line as orthogonal")
            
        #     if projectionOn1 is None:
        #         point1 = line1.createControlPoint(line1.start)
        #         point2 = line2.createControlPoint(projectionOn2)
        #     else:
        #         point1 = line1.createControlPoint(projectionOn1)
        #         point2 = line2.createControlPoint(line2.start)
        
        # elif nextType == 'random':
        #     separation1 = np.random.uniform(minSeperation, maxSeparation)
        #     separation2 = np.random.uniform(minSeperation, maxSeparation)
        #     point1 = line1.createNextControlPoint(separation1)
        #     point2 = line2.createNextControlPoint(separation2)

        nextType = 'random'
        point1 = line1Copy.createControlPoint(line1.start)
        point2 = line2Copy.createControlPoint(line2.start)
        # now we have the first pair (point1, point2)

        pointOnLine1 = line1.createControlPoint(line1.start)
        pointOnLine2 = line2.createControlPoint(line2.start)
        pointOnLine1 = line1.mergeWithNearestSiblingIfClose(pointOnLine1, minSeparation=snapDistance)
        pointOnLine2 = line2.mergeWithNearestSiblingIfClose(pointOnLine2, minSeparation=snapDistance)
        self.createConnection(line1, line2, pointOnLine1, pointOnLine2)



        # we are gonna try until we reach the end

        while(True):
            prevType = nextType
            try:
                separation1 = np.random.uniform(minSeperation, maxSeparation)
                separation2 = np.random.uniform(minSeperation, maxSeparation)
                candidate1 = line1Copy.createNextControlPoint(separation1)

                nextType = np.random.choice(list(mdp[prevType].keys()), p=list(mdp[prevType].values()))
                if self.debug:
                    logging.info(f"{self.name}: connectControlLinesWithRectsAndTriangles: nextType: {nextType}")

                if nextType == 'orthogonal':

                    projectionOn2 = line2Copy.getProjection(candidate1.position)
                    if projectionOn2 is None:
                        line1Copy.deleteControlPoint(candidate1)
                        # we could not get a projection. just break for now. 
                        raise Exception(f"Projection out of boundary for candidate 1 at {candidate1.position}")
                    
                    if line2Copy.isProjectionInsideControlPoints(projectionOn2):
                        line1Copy.deleteControlPoint(candidate1)
                        if self.debug:
                            logging.info(f"Projection {projectionOn2} is inside existing control points")
                        continue
                    
                    # candidate2 = line2Copy.createNextControlPoint(separation2)
                    point1 = candidate1
                    point2 = line2Copy.createControlPoint(projectionOn2)
                    # line2Copy.deleteControlPoint(candidate2)

                elif nextType == 'parallel':
                    point1 = candidate1
                    point2 = line2Copy.createNextControlPoint(separation1)
                    pass
                elif nextType == 'random':
                    point1 = candidate1
                    point2 = line2Copy.createNextControlPoint(separation2)
                    pass
                elif nextType == 'commonEnd':

                    # randomly choose and end
                    if np.random.choice([True, False], p=[0.5, 0.5]):
                        point1 = candidate1
                        point2 = line2Copy.getLastPoint()
                    else:
                        line1Copy.deleteControlPoint(candidate1)
                        point1 = line1Copy.getLastPoint()
                        point2 = line2Copy.createNextControlPoint(separation2)

                    pass
                
                # we need to snap before creating connection
                pointOnLine1 = line1.createControlPoint(point1.position)
                pointOnLine2 = line2.createControlPoint(point2.position)

                pointOnLine1 = line1.mergeWithNearestSiblingIfClose(pointOnLine1, minSeparation=snapDistance)
                pointOnLine2 = line2.mergeWithNearestSiblingIfClose(pointOnLine2, minSeparation=snapDistance)

                # TODO validate distance from previous connection
                

                self.createConnection(line1, line2, pointOnLine1, pointOnLine2)

            except Exception as e:
                if self.debug:
                    logging.info(f"{self.name}: connectControlLinesWithRectsAndTriangles: ends due to {e}")
                    traceback.print_exc()
                break

    
    def connectControlLinesWithExistingControlPoints(self, pair: Tuple[ControlLine], maxPerPoint=2, ConnectionStrategy=ConnectionStrategy.MIN, connectionDensity=0.9):
        line1 = pair[0]
        line2 = pair[1]

        # 1 choose a set of points from each of the lines that must be connected. The points must be ordered.
        points1 = []
        points2 = []
        if (ConnectionStrategy == ConnectionStrategy.NO_ORPHANS_FIRST) or  (ConnectionStrategy == ConnectionStrategy.NO_ORPHANS_BOTH):
            points1 = self.getPointsWithStrategy(line1, connectionDensity=connectionDensity, noOrphans=True)
        else:
            points1 = self.getPointsWithStrategy(line1, connectionDensity=connectionDensity, noOrphans=False)
            
        if (ConnectionStrategy == ConnectionStrategy.NO_ORPHANS_SECOND) or  (ConnectionStrategy == ConnectionStrategy.NO_ORPHANS_BOTH):
            points2 = self.getPointsWithStrategy(line2, connectionDensity=connectionDensity, noOrphans=True)
        else:
            points2 = self.getPointsWithStrategy(line2, connectionDensity=connectionDensity, noOrphans=False)


        allPoints = points1 + points2
        connectionCountPerPoint = {}
        for point in allPoints:
            connectionCountPerPoint[point] = 0
        

        # 2 how do we connect this two sets of points.
        
        minimalSet = None
        maximalSet = None
        minimalLine = None
        maximalLine = None

        if len(points1) > len(points2):
            minimalSet = points2
            maximalSet = points1
            minimalLine = line2
            maximalLine = line1
        else:
            minimalSet = points1
            maximalSet = points2
            minimalLine = line1
            maximalLine = line2
        
        pairs = []
        for point1 in minimalSet:
            # nToConnect = np.random.choice(range(maxPerPoint)) + 1
            nToConnect = np.random.choice([1, 2], p=[0.8, 0.2])
            # nToConnect = 1
            for _ in range(nToConnect):
                if len(maximalSet) > 0:
                    point2 = maximalSet.pop(0)
                    pairs.append((point1, point2))
                    connectionCountPerPoint[point1] += 1
                    connectionCountPerPoint[point2] += 1
                # else:
                #     raise Exception("ran out of options")
            if nToConnect > 1:
                maximalSet.insert(0, point2) # push back the last point 

        
        if len(maximalSet) > 0:
            # for point2 in maximalSet:
            #     pairs.append((point1, point2))
            point2 = maximalSet[-1]
            pairs.append((point1, point2))
            connectionCountPerPoint[point1] += 1
            connectionCountPerPoint[point2] += 1
        

        # 3 now we have the pair
        for point1, point2 in pairs:
            keep = np.random.choice([True, False], p=[0.65, 0.35])
            # keep = True
            if keep:
                print(f"{self.name}: connectRandom: created pair {(point1.position, point2.position)}")
                self.createConnection(minimalLine, maximalLine, point1, point2)

        print(connectionCountPerPoint)


    def getPointsWithStrategy(self, line, connectionDensity=0.8, noOrphans=True):
        points = []
        if noOrphans:
            for point in line.getOrderedControlPoints():
                if point.isOrphan():
                    points.append(point)
                else:
                    if np.random.choice([False, True], p=[1 - connectionDensity, connectionDensity]):
                        points.append(point)
        else:
            for point in line.getOrderedControlPoints():
                if np.random.choice([False, True], p=[1 - connectionDensity, connectionDensity]):
                    points.append(point)
        
        if len(points) == 0:
            points.append(line.getOrderedControlPoints()[0])

        return points

    
    def nearestDisconnectedPoints(self, line1: ControlLine, line2:ControlLine):

        disconnectedPoints1 = line1.pointsNotConnectedTo(line2)
        disconnectedPoints2 = line2.pointsNotConnectedTo(line1)

        # print(disconnectedPoints1)
        # print(disconnectedPoints2)

        nearestPair = None
        globalMinDistance = 99999999999
        for point1 in disconnectedPoints1:
            minDistance = 99999999999
            pair = None
            for point2 in disconnectedPoints2:
                distance = point1.distanceFrom(point2)
                if self.debug:
                    print(f"{self.name}: nearestDisconnectedPoints: distance = {distance}, points = {(point1.position, point2.position)}")

                # if this distance is bigger than minDistance, we stop as our control lines are linearly increasing or decreasing
                if distance > minDistance:
                    break

                minDistance = distance
                pair = (point1, point2)
            
            if pair is not None:
                if self.debug:
                    print(f"{self.name}: nearestDisconnectedPoints: minDistance = {minDistance}, points = {pair[0].position, pair[1].position}")
                if minDistance < globalMinDistance:
                    globalMinDistance = minDistance
                    nearestPair = pair
                    if self.debug:
                        print(f"{self.name}: nearestDisconnectedPoints: globalMinDistance = {minDistance}, points = {pair[0].position, pair[1].position}")
             
        return nearestPair

    # region plots and prints

    def printConnectionBetween(self, line1: ControlLine, line2:ControlLine):
        for point1 in line1.pointsConnectedTo(line2):
            for point2 in point1.adjacentPoints:
                if line2.hasPoint(point2):
                    print(f"{self.name}: printConnectionBetween: {(point1.position, point2.position)}")

    # end region

    def plot(self):


        for line in self.lines:
            plt.plot([line.start[0], line.end[0]], [line.start[1], line.end[1]])
        
        for connection in self.connections:
            point1 = connection[2]
            point2 = connection[3]
            plt.plot([point1.position[0], point2.position[0]], [point1.position[1], point2.position[1]])
        plt.show()
