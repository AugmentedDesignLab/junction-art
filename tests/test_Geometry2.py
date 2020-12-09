import unittest
from junctions.Geometry import Geometry


class test_Geometry2(unittest.TestCase):

    def test_evalPoly(self):

        # test 1

        pRange = [1, 2, 3]
        coeffs = [10, 2, 1]

        vals = Geometry.evalPoly(coeffs, pRange)

        print(vals)

        assert vals[0] == 13
        assert vals[1] == 18
        assert vals[2] == 25

        # test 2

        pRange = [1, 2, 3]
        coeffs = [10]

        vals = Geometry.evalPoly(coeffs, pRange)

        print(vals)

        assert vals[0] == 10
        assert vals[1] == 10
        assert vals[2] == 10
        
