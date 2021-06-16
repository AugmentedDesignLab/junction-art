import unittest, math

from roadgen.controlLine.ControlLine import ControlLine
from roadgen.controlLine.ControlLineGrid import ControlLineGrid

class test_ControlLineGrid(unittest.TestCase):


    def test_nearest(self):

        
        line1 = ControlLine(1, (0,0), (1000, 0))
        line1.createControlPoints(20, 50, 70, p=[0.8, 0.1, 0.1])

        line2 = ControlLine(1, (0,50), (1000, 30))
        line2.createControlPoints(20, 50, 60, p=[0.5, 0.1, 0.4])

        line3 = ControlLine(1, (0,100), (1000, 120))
        line3.createControlPoints(20, 50, 70, p=[0.8, 0.1, 0.1])

        line4 = ControlLine(1, (0,150), (1000, 220))
        line4.createControlPoints(20, 50, 60, p=[0.6, 0.1, 0.3])

        pairs = [(line1, line2), (line2, line3), (line3, line4)]
        grid = ControlLineGrid(controlLinePairs=pairs)

        # grid.nearestDisconnectedPoints(line1, line2)

        # grid.connect(pairs[0])
        grid.connectControlLinesWithExistingControlPoints(pairs[0])
        grid.connectControlLinesWithExistingControlPoints(pairs[1])
        grid.connectControlLinesWithExistingControlPoints(pairs[2])
        # grid.printConnectionBetween(line1, line2)
        # grid.printConnectionBetween(line2, line3)
        # print(line1)
        # print(line2)
        # print(line3)

        grid.plot()