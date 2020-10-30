import unittest

import extensions, junctions
import numpy as np
import math

from junctions.StandardCurveTypes import StandardCurveTypes

class test_ExtendedRoad(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = junctions.RoadBuilder()

    def test_getArcAngle(self):

        for _ in range(1, 10):
            for i in range(1, 10):
                inputAngle = (np.pi * i) / 10
                road = self.roadBuilder.createRandomCurve(0, inputAngle)

                if road.curveType == StandardCurveTypes.S:
                    continue

                outputAngle = road.getArcAngle()
                deviation = abs(inputAngle - outputAngle) * 100 / inputAngle

                print( f"curveType: {road.curveType} inputAngle: {math.degrees(inputAngle)} outputAngle: {math.degrees(outputAngle)} deviation: {deviation}")
                assert deviation < 50.0

