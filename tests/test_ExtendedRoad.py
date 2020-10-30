import unittest

import extensions, junctions
import numpy as np

class test_ExtendedRoad(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = junctions.RoadBuilder()

    def test_getArcAngle(self):

        for i in range(1, 10):
            inputAngle = (np.pi * i) / 10
            road = self.roadBuilder.createRandomCurve(0, inputAngle)
            outputAngle = road.getArcAngle()
            deviation = abs(inputAngle - outputAngle) * 100 / inputAngle

            print( f"inputAngle: {inputAngle} outputAngle: {outputAngle} deviation: {deviation}")
            assert deviation < 1.0

