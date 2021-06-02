import unittest, math

from roadgen.controlLine.ControlLine import ControlLine
from roadgen.controlLine.ControlLineGrid import ControlLineGrid

class test_ControlLineGrid(unittest.TestCase):


    def test_nearest(self):

        
        line1 = ControlLine(1, (0,0), (500, 0))
        line1.createControlPoints(10, 50, 100)

        line2 = ControlLine(1, (0,50), (500, 30))
        line2.createControlPoints(10, 50, 100)

        pairs = [(line1, line2)]
        grid = ControlLineGrid(controlLinePairs=pairs)

        grid.nearestDisconnectedPoints(line1, line2)

        grid.connect(pairs[0])
        grid.printConnectionBetween(line1, line2)

        grid.plot()