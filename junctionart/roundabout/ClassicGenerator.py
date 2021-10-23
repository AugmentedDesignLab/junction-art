from typing_extensions import Literal
from roundabout.Generator import Generator
from junctions.IncidentPoint import IncidentPoint
from extensions.ExtendedRoad import ExtendedRoad
from typing import List, Dict
import random
import math


class ClassicGenerator(Generator):



    def generateWithIncidentPointConfiguration(self, ipConfig: List[Dict]):

        # 0 construct incident points

        incidentPoints = self.parseIncidentPoints(ipConfig)

        # 1. get a circle
        center, radius = self.getCircle(ipConfig)

        # 2. make the circular road with segments

        nLanes = 2
        circularRoads = self.getCircularRoads(center, radius, nLanes)

        # 3. create 3-way intersections

    
        intersections = self.createIntersections(incidentPoints, circularRoads)

        # 4. create the  roundabout object

        pass
    
    
    def parseIncidentPoints(self, ipConfig: List[Dict]):
        return []

    def getCircularRoads(self, center, radius, nLanes = 2, nSegments=10):

        # TODO, diya.

        return []


    def getCircle(self, ipConfig: List[Dict]):
        points = [Point(point["x"], point["y"]) for point in ipConfig]
        optimalCenter, radius = self.getOptimalCircle(points)
        quality, center, radius = self.circleRandomizer(points, optimalCenter, radius)

        return center, radius

    def createIntersections(self, incidentPoints: List[IncidentPoint], circularRoads: List[ExtendedRoad]):
        return []


    def getOptimalCircle(self, points):
        sum_x = (
            sum_y
        ) = sum_xx = sum_yy = sum_xy = sum_xxy = sum_xyy = sum_xxx = sum_yyy = 0.0
        A = B = C = D = E = 0.0
        x2 = y2 = xy = xDiff = yDiff = 0.0
        for point in points:
            sum_x += point.x
            sum_y += point.y
            x2 = point.x * point.x
            y2 = point.y * point.y
            xy = point.x * point.y
            sum_xx += x2
            sum_yy += y2
            sum_xy += xy
            sum_xxy += x2 * point.y
            sum_xyy += y2 * point.x
            sum_xxx += x2 * point.x
            sum_yyy += y2 * point.y

        n = len(points)
        A = n * sum_xx - sum_x * sum_x
        B = n * sum_xy - sum_x * sum_y
        C = n * sum_yy - sum_y * sum_y
        D = 0.5 * (n * (sum_xyy + sum_xxx) - sum_x * sum_yy - sum_x * sum_xx)
        E = 0.5 * (n * (sum_xxy + sum_yyy) - sum_y * sum_xx - sum_y * sum_yy)

        F = A * C - B * B
        centerX = (D * C - B * E) / F
        centerY = (A * E - B * D) / F
        center = Point(centerX, centerY)

        radius = 10000000
        for i in range(n):
            xDiff = points[i].x - centerX
            yDiff = points[i].y - centerY
            radius = min(radius, (xDiff * xDiff + yDiff * yDiff) ** 0.5)

        return center, radius * 0.9
        # returns optimal circle (x, y, r) for the given list of points.

    def getRandomizedCircle(self, points, optimalCenter, radius):
        a = random.uniform(0, 2)
        b = random.uniform(0, 2)
        newX = optimalCenter.x * a
        newY = optimalCenter.y * b
        newCenter = Point(newX, newY)

        radius = 1000000
        resultQuality = 0
        for i in range(len(points)):
            resultQuality += math.sqrt(
                (points[i].x - newX) ** 2 + (points[i].y - newY) ** 2
            )
            xDiff = points[i].x - newX
            yDiff = points[i].y - newY
            radius = min(radius, (xDiff * xDiff + yDiff * yDiff) ** 0.5)

        radius *= 0.9
        resultQuality -= len(points) * (radius)
        resultQuality /= len(points)
        return (resultQuality), newCenter, radius


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def plotNode(self):
        plt.scatter(self.x, self.y, s=50, c=[[0, 0, 0]])
