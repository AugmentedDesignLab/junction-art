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

    def __init__(self, size=(1000, 1000), controlLinePairs = None, continuationPairs=None, debug=True):
        self.size = size
        self.controlLinePairs = controlLinePairs
        self.continuationPairs = continuationPairs
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

        snapDistance = 60 # in meters
        minSeperation = 100
        maxSeparation = 150

        # change seperation per pair
        changeInSeperation = np.random.uniform(0.0, 1.1)
        minSeperation += minSeperation * changeInSeperation
        maxSeparation += maxSeparation * changeInSeperation


        mdp = {
            'orthogonal': {
                'parallel': 0.4,
                'random': 0.3,
                'commonEnd': 0.3
            },
            'parallel': {
                'orthogonal': 0.4,
                'parallel': 0.3,
                'random': 0.2,
                'commonEnd': 0.1
            },
            'random': {
                'orthogonal': 0.1,
                'parallel': 0.5,
                'random': 0.3,
                'commonEnd': 0.1
            },
            'commonEnd': {
                'orthogonal': 0.5,
                'parallel': 0.1,
                'random': 0.4,
                'commonEnd': 0
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
        
        nextType = 'random'
        # Create the first connection
        projectionOn1 = line1Copy.getProjection(line2.start)
        if projectionOn1 is not None:
            # line 2 starts inside line 1
            point1 = line1Copy.createControlPoint(projectionOn1)
            point2 = line2Copy.createControlPoint(line2.start)
        else:
            projectionOn2 = line2Copy.getProjection(line1.start)
            if projectionOn2 is None:
                # floating point error
                point1 = line1Copy.createControlPoint(line1.start)
                point2 = line2Copy.createControlPoint(line2.start)
            else:
                point1 = line1Copy.createControlPoint(line1.start)
                point2 = line2Copy.createControlPoint(projectionOn2)

        # point1 = line1Copy.createControlPoint(line1.start)
        # point2 = line2Copy.createControlPoint(line2.start)
        # now we have the first pair (point1, point2)

        pointOnLine1 = line1.createControlPoint(point1.position)
        pointOnLine2 = line2.createControlPoint(point2.position)
        pointOnLine1 = line1.mergeWithNearestSiblingIfClose(pointOnLine1, minSeparation=snapDistance)
        pointOnLine2 = line2.mergeWithNearestSiblingIfClose(pointOnLine2, minSeparation=snapDistance)
        self.createConnection(line1, line2, pointOnLine1, pointOnLine2)

        commonEndToggler = 2 # toggles between 1 and 2


        # we are gonna try until we reach the end

        while(True):
            prevType = nextType
            try:
                separation1 = np.random.uniform(minSeperation, maxSeparation)
                separation2 = np.random.uniform(minSeperation, maxSeparation)
                # candidate1 = line1Copy.createNextControlPoint(separation1)

                nextType = np.random.choice(list(mdp[prevType].keys()), p=list(mdp[prevType].values()))
                if self.debug:
                    logging.info(f"{self.name}: Lines ({line1.id}, {line2.id}): connectControlLinesWithRectsAndTriangles: nextType: {nextType}")

                if nextType == 'orthogonal':
                    try:
                        point1, point2 = self.createOrthogonalPoints(line1=line1Copy, line2=line2Copy, separation1=separation1, separation2=separation2)
                    except:
                        continue

                elif nextType == 'parallel':
                    point1 = line1Copy.createNextControlPoint(separation1)
                    point2 = line2Copy.createNextControlPoint(separation1)
                    pass
                elif nextType == 'random':
                    point1 = line1Copy.createNextControlPoint(separation1)
                    point2 = line2Copy.createNextControlPoint(separation2)
                    pass
                elif nextType == 'commonEnd':

                    # randomly choose and end
                    if commonEndToggler ==  2:
                        point1 = line1Copy.createNextControlPoint(separation1)
                        point2 = line2Copy.getLastPoint()
                        commonEndToggler = 1
                    else:
                        point1 = line1Copy.getLastPoint()
                        point2 = line2Copy.createNextControlPoint(separation2)
                        commonEndToggler = 2

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
                    logging.info(f"{self.name}: Lines ({line1.id}, {line2.id}): connectControlLinesWithRectsAndTriangles: ends due to {e}")
                break

    
    def createOrthogonalPoints(self, line1, line2, separation1, separation2):
        candidate1 = line1.createNextControlPoint(separation1)
        # try projection on 2
        projectionOn2failed = False
        projectionOn2 = line2.getProjection(candidate1.position)
        if projectionOn2 is None:
            projectionOn2failed = True
            # we could not get a projection. just break for now. 
            if self.debug:
                logging.info(f"{self.name}: createOrthogonalPoints: Lines ({line1.id}, {line2.id}): Projection out of boundary for candidate 1 at {candidate1.position}")
        
        elif line2.isProjectionInsideControlPoints(projectionOn2):
            projectionOn2failed = True
            if self.debug:
                logging.info(f"{self.name}: createOrthogonalPoints: Lines ({line1.id}, {line2.id}): Projection {projectionOn2} is inside existing control points")
            # continue
        
        # try projection on 1
        if projectionOn2failed:
            line1.deleteControlPoint(candidate1)

            candidate2 = line2.createNextControlPoint(separation2)
            projectionOn1 = line1.getProjection(candidate2.position)
            if projectionOn1 is None:
                line2.deleteControlPoint(candidate2)
                if self.debug:
                    logging.info(f"{self.name}: createOrthogonalPoints: Lines ({line1.id}, {line2.id}): Projection out of boundary for candidate 2 at {candidate2.position}")
                raise Exception(f"{self.name}: createOrthogonalPoints")
            elif line1.isProjectionInsideControlPoints(projectionOn1):
                line2.deleteControlPoint(candidate2)
                if self.debug:
                    logging.info(f"{self.name}: createOrthogonalPoints: Lines ({line1.id}, {line2.id}): Projection {projectionOn1} is inside existing control points")
                raise Exception(f"{self.name}: createOrthogonalPoints")

            point1 = line1.createControlPoint(projectionOn1)
            point2 = candidate2

        else: # projection on 2 is valid
            point1 = candidate1
            point2 = line2.createControlPoint(projectionOn2)

        return point1, point2

    def connectContinuationPairs(self):
        for pair in self.continuationPairs:
            self.connectContinuationPair(pair)
    

    def connectContinuationPair(self, pair: Tuple[ControlLine]):
        """ connections the control lines as if they were sequentially connected"""
        
        if self.debug:
            logging.info(f"{self.name}: connectContinuationPair: Connecting continuation pairs")

        snapDistance = 60 # in meters

        line1 = pair[0]
        line2 = pair[1]
        line1Copy = ControlLine(id=pair[0].id, start=pair[0].start, end=pair[0].end)
        line2Copy = ControlLine(id=pair[1].id, start=pair[1].start, end=pair[1].end)

        # TODO ideally we should create new control points at the end of line1 and at the start of line2 if not existing to avoid overlaps. But for now, we will live with existing

        pointOnLine1 = line1.getLastPoint()
        pointOnLine2 = line2.getFirstPoint()

        if pointOnLine1 is None or pointOnLine2 is None:
            if self.debug:
                logging.info(f"{self.name}: connectContinuationPair. Cannot create continuation connection between line {line1.id} and line {line2.id}")
        
            return
        
        self.createConnection(line1, line2, pointOnLine1, pointOnLine2)




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
            plt.plot([line.start[0], line.end[0]], [line.start[1], line.end[1]], '-', linewidth=1.5)
        
        for (line1, line2, point1, point2) in self.connections:
            if line1 == line2:
                continue
            plt.plot([point1.position[0], point2.position[0]], [point1.position[1], point2.position[1]], ':', color='gray', linewidth=1.5)
            plt.plot(point1.position[0], point1.position[1], 'o', color='#555555')
            plt.plot(point2.position[0], point2.position[1], 'o', color='#555555')
        plt.grid(color = '#f0f0f0', linestyle = '--', linewidth = 0.3)
        plt.show()


    def plotControlLines(self):
        for line in self.lines:
            plt.plot([line.start[0], line.end[0]], [line.start[1], line.end[1]], '-', linewidth=1.5)
        plt.show()

        
    def plotConnections(self):
       
        for (line1, line2, point1, point2) in self.connections:
            plt.plot([point1.position[0], point2.position[0]], [point1.position[1], point2.position[1]], ':', color='gray', linewidth=1.5)
            plt.plot(point1.position[0], point1.position[1], 'o', color='#555555')
            plt.plot(point2.position[0], point2.position[1], 'o', color='#555555')
        plt.grid(color = '#f0f0f0', linestyle = '--', linewidth = 0.3)
        plt.show()
