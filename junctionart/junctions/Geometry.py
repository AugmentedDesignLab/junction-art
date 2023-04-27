from abc import ABC, abstractmethod
from threading import stack_size
import numpy as np
import math
import pyodrx
from scipy.interpolate import CubicHermiteSpline
from perlin_noise import PerlinNoise


class Geometry(ABC):
    @staticmethod
    def headingsTooClose(h1, h2, threshold=0.1):
        h1 = h1 % (np.pi * 2)
        h2 = h2 % (np.pi * 2)
        if abs(h1 - h2) % np.pi <= threshold:
            return True
        return False

    @staticmethod
    def getLengthOfGeoms(geoms):
        """[summary]

        Args:
            geoms ([type]): List of Geometries of type Arc, Spiral, Line, ParamPoly3

        Returns:
            [type]: [description]
        """
        totalLength = 0
        for geom in geoms:
            _, _, _, length = geom.get_end_data(0, 0, 0)
            totalLength += length

        return totalLength

    @staticmethod
    def evalPoly(coeffs, pRange):
        vals = []
        for p in pRange:
            val = coeffs[0]  # first one is the intercept
            for i in range(1, len(coeffs)):
                val += coeffs[i] * p
                p = p * p  # smelly but faster than powers

            vals.append(val)

        return vals

    @staticmethod
    def evalSpiral(spiral):
        raise NotImplementedError()
        # curveRange = np.arange(spiral.curvestart + 0.001, spiral.curveEnd, 0.001)

        # fromCurv = spiral.curvstart

        # points = []

        # for nextCurve in curveRange:

        #     eulerSp = EulerSpiral.createFromLengthAndCurvature(self.length, fromCurv, nextCurve)
        #     (deltax, deltay, t) = eulerSp.calc(self.length, x, y, self.curvstart, h)
        #     points.append((deltax, deltay))

    @staticmethod
    def inertialToLocal(localCenter, localRotation, intertialPoint):

        uBeforeRotation = intertialPoint[0] - localCenter[0]
        vBeforeRotation = intertialPoint[1] - localCenter[1]

        u = uBeforeRotation * math.cos(localRotation) + vBeforeRotation * math.sin(
            localRotation
        )
        v = -uBeforeRotation * math.sin(localRotation) + vBeforeRotation * math.cos(
            localRotation
        )

        return u, v

    @staticmethod
    def positiveNormalizeHeading(h):
        h = h % (np.pi * 2)
        if h < 0.0:
            h = (np.pi * 2) + h
        return h

    @staticmethod
    def getRelativeHeading(rootHeading, anotherHeading):
        return (anotherHeading + (np.pi * 2) - rootHeading) % (np.pi * 2)

    @staticmethod
    def headingToTangent(h, tangentMagnitude):

        xComponent = math.cos(h) * tangentMagnitude
        yComponent = math.sin(h) * tangentMagnitude

        return (xComponent, yComponent)

    @staticmethod
    def getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, cp1, cp2, vShiftForSamePoint=0):
        """ Assumes traffice goes from point1 to point2. By default if the contact point is start, traffic is going into the road, and end, traffic is going out. """

        if cp1 == pyodrx.ContactPoint.start:
            h1 = h1 + np.pi

        if cp2 == pyodrx.ContactPoint.end:
            h2 = h2 + np.pi

        h1 = h1 % (np.pi * 2)
        h2 = h2 % (np.pi * 2)

        # TODO we need to solve the problem with param poly, not a straight road, as there can still be some angles near threshold for which it can fail.

        # if Geometry.headingsTooClose(h1, h2):
        #     # return a straight road. This is flawed because heading is assumed to be 0 for straight roads in pyodrx
        #     return self.getStraightRoadBetween(newRoadId, road1, road2, incomingCp, ioutgoingCp,
        #                             isJunction=isJunction,
        #                             n_lanes=n_lanes,
        #                             lane_offset=lane_offset,
        #                             laneSides=laneSides)
        # TODO return a curve because points can have the same heading, but big translation which creates problem.

        tangentMagnitude = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        if tangentMagnitude < 3:  # it too short, for U-turns
            tangentMagnitude = 3

        localRotation = h1  # rotation of local frame wrt inertial frame.

        u1 = 0
        v1 = 0

        u2, v2 = Geometry.inertialToLocal((x1, y1), localRotation, (x2, y2))

        if u1 == u2 and v1 == v2:
            v1 -= vShiftForSamePoint
            v2 += vShiftForSamePoint

        localStartTangent = Geometry.headingToTangent(0, tangentMagnitude)
        localEndHeading = Geometry.getRelativeHeading(h1, h2)
        localEndTangent = Geometry.headingToTangent(localEndHeading, tangentMagnitude)

        X = [u1, u2]
        Y = [v1, v2]

        tangentX = [localStartTangent[0], localEndTangent[0]]
        tangentY = [localStartTangent[1], localEndTangent[1]]

        # print(f"connecting road #{road1.id} and # {road2.id}: {x1, y1, x2, y2}")
        # print(f"connecting road #{road1.id} and # {road2.id}: X, Y, tangentX, tangentY")
        # print(X)
        # print(Y)
        # print(tangentX)
        # print(tangentY)

        p = [0, 1]

        hermiteX = CubicHermiteSpline(p, X, tangentX)
        hermiteY = CubicHermiteSpline(p, Y, tangentY)

        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()
        return xCoeffs, yCoeffs

    @staticmethod
    def forward_elimination(A, b, is_partial_pivot_enabled, showall, round_digit):
        nCol = A.shape[0]
        for i in range(nCol - 1):
            if is_partial_pivot_enabled == True:
                max_col_index = i + np.abs(A[i:, i]).argmax()
                A[[i, max_col_index]] = A[[max_col_index, i]]
                b[[i, max_col_index]] = b[[max_col_index, i]]
            for j in range(i + 1, nCol):
                multiply_factor = A[j][i] / A[i][i]
                A[j] = A[j] - A[i] * multiply_factor.round(round_digit)
                b[j] = b[j] - b[i] * multiply_factor.round(round_digit)
                if showall == True:
                    print("A :", A, "B :", b)

        return A, b

    @staticmethod
    def back_substitution(A, b):
        X = np.zeros(A.shape[0])
        nCol = A.shape[0]
        for i in range(nCol - 1, -1, -1):
            X[i] = (b[i] - (A[i][i + 1 : nCol] * X[i + 1 : nCol]).sum()) / A[i][i]

        return X

    @staticmethod
    def guassian_elimination(
        A, b, is_partial_pivot_enabled=True, showall=True, round_digit=3
    ):
        A, b = Geometry.forward_elimination(
            A, b, is_partial_pivot_enabled, showall, round_digit
        )
        X = Geometry.back_substitution(A, b)
        return X.round(round_digit)

    @staticmethod
    def cubic_eqn_finder(points):
        a = []
        b = []
        for point in points:
            x, y = point
            a.append([x ** 3, x ** 2, x, 1])
            b.append(y)

        a = np.array(a).astype(float)
        b = np.array(b).astype(float)
        x = Geometry.guassian_elimination(a, b, round_digit=7, showall=False)
        return x

    @staticmethod
    def cubic_equation_finder_start_end(start, end):
        x1, y1 = start
        x4, y4 = end
        x2, y2 = x1 + (x4 - x1) * 0.5, y1 + (y4 - y1) * 0.2
        x3, y3 = x1 + (x4 - x1) * 0.9, y1 + (y4 - y1) * 0.8
        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        return Geometry.cubic_eqn_finder(points)

    @staticmethod
    def get_points(startx, start_width, endx, end_width):
        return (
            [(startx, start_width / 2), (startx, -start_width / 2)],
            [(endx, +end_width / 2), (endx, -end_width / 2)],
        )

    @staticmethod
    def cubicEquationSolver(startX, startWidth, endX, endWidth):
        starts, ends = Geometry.get_points(startX, startWidth, endX, endWidth)
        a, b, c, d = Geometry.cubic_equation_finder_start_end(starts[0], ends[0])
        a1, b1, c1, d1 = Geometry.cubic_equation_finder_start_end(starts[1], ends[1])
        return [a, b, c, d], [a1, b1, c1, d1]

    @staticmethod
    def cubic_equation_find(w, l, factor):
        p1 = (0, w)
        p4 = (l, w)
        p2 = (l * 0.33, factor * w)
        p3 = (l * 0.66, factor * w)
        points = [p1, p2, p3, p4]
        a, b, c, d = Geometry.cubic_eqn_finder(points)
        return a, b, c, d

    @staticmethod
    def cubic_equation_with_width(w1, w2, l):
        p1 = (0, w1)
        p4 = (l, w2)
        p2 = (l * 0.5, w1 + (w2 - w1) * 0.33)
        p3 = (l * 0.75, w1 + (w2 - w1) * 0.66)
        points = [p1, p2, p3, p4]
        a, b, c, d = Geometry.cubic_eqn_finder(points)
        return a, b, c, d

    @staticmethod
    def cubic_equation_with_three_width(w1, m, w2, l):
        p1 = (0, w1)
        p4 = (l, w2)
        p2 = (l * 0.65, m)
        p3 = (l * 0.85, m + (w2 - m) * 0.66)
        points = [p1, p2, p3, p4]
        a, b, c, d = Geometry.cubic_eqn_finder(points)
        return a, b, c, d

    @staticmethod
    def getRepulsionForces(points):
        nNodes = points.shape[0]
        forceConstant = 1000
        repulsionForce = np.zeros((2 * nNodes)).reshape((nNodes, -1))

        for i in range(nNodes):
            for j in range(i + 1, nNodes):
                direction = points[i] - points[j]
                if np.dot(direction, direction) != 0:
                    force = direction / np.dot(direction, direction)
                force *= forceConstant
                repulsionForce[i] += force
                repulsionForce[j] -= force

        return repulsionForce

    @staticmethod
    def getSpringForces(points, connections):
        nNodes = points.shape[0]
        springForces = np.zeros((2 * nNodes)).reshape((nNodes, -1))
        for i in range(connections.shape[0]):
            u = int(connections[i][0])
            v = int(connections[i][1])
            maxDis = connections[i][2]

            direction = points[u] - points[v]
            pointDistance = np.sqrt(np.dot(direction, direction))
            difference = pointDistance - maxDis

            if pointDistance != 0:
                direction = direction / pointDistance

            springForces[u] -= direction * difference
            springForces[v] += direction * difference

        return springForces

    @staticmethod
    def getGravitationalForces(points):
        nNodes = points.shape[0]
        graviationalConstant = 1.1
        gravitationalForces = np.zeros((2 * nNodes)).reshape((nNodes, -1))
        for i in range(points.shape[0]):
            gravitationalForces[i] += points[i] * -1 * graviationalConstant

        return gravitationalForces

    @staticmethod
    def updatePoints(points, connections):
        totalForces = Geometry.getSpringForces(
            points, connections
        )  # + getRepulsionForces(points) + getGravitationalForces(points)
        #     print(getRepulsionForces(points), "sptring", getSpringForces(points, connections) , getGravitationalForces(points))

        points += totalForces / 20

    @staticmethod
    def randomizePoints(points, connections, radius):
        length = points.shape[0]
        randomIndices = np.zeros(length)
        noise = PerlinNoise(octaves=3)
        for i in range(length):
            randomIndices[i] = 100 * noise(i / 100)

        # print(randomIndices)

        # points[:, 1] += randomIndices * radius / 400
        points[:, 0] += randomIndices * radius / 100

        # for i in range(int(10 * radius / 100)):
        #     Geometry.updatePoints(points, connections)

