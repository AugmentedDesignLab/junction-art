import unittest, math

from roadgen.controlLine.ControlLine import ControlLine

class test_ControlLine(unittest.TestCase):

    def test_Theta(self):

        controlLine = ControlLine(1, (0,0), (500, 0))
        assert int(math.degrees(controlLine.theta)) == 0
        assert controlLine.slopeSign == 1
        controlLine = ControlLine(1, (0,0), (500, 500))
        assert int(math.degrees(controlLine.theta)) == 45
        assert controlLine.slopeSign == 1
        controlLine = ControlLine(1, (0,0), (0, 500))
        assert int(math.degrees(controlLine.theta)) == 90
        assert controlLine.slopeSign == 1

        controlLine = ControlLine(1, (0,500), (500, 0))
        assert int(math.degrees(controlLine.theta)) == 45
        assert controlLine.slopeSign == -1

        controlLine = ControlLine(1, (0,50), (500, 30))
        assert controlLine.slopeSign == -1

        controlLine.createControlPoints(10, 50, 100)
        print(controlLine)
        # # print("hello")

    
    