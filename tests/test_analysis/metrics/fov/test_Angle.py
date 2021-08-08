import unittest
import math

from analysis.metrics.fov.Angle import Angle

class test_Angle(unittest.TestCase):


    def test_first(self):
        p0 = [3.5, 6.7]
        p1 = [7.9, 8.4]
        p2 = [10.8, 4.8]

        angle = Angle.cornerAngle(p0, p1, p2)
        print(math.degrees(angle))
        print("hello")
        pass
    