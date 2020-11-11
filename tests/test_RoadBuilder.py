import unittest, os
from junctions.RoadBuilder import RoadBuilder
from scipy.interpolate import CubicHermiteSpline
import numpy as np
import pyodrx, extensions

class test_RoadBuilder(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = RoadBuilder()



    def test_ParamPoly(self):
        tangentX = np.array([
            3.09016992482654, -10.0
        ])

        t = np.array([0, 1])
        x = np.array([44.30602949438151, 40.0])
        y = np.array([-5.223206854241455, 0.0])
        hermiteX = CubicHermiteSpline(t, x, tangentX)

        tangentY = np.array([
        9.51056516909997, 1.2246467991473533e-15
        ])
        hermiteY = CubicHermiteSpline(t, y, tangentY)
        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()

        # scipy coefficient and open drive coefficents have opposite order.
        myRoad = self.roadBuilder.createParamPoly3(
                                                0, 
                                                isJunction=False,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0]

                                            )

        odr = pyodrx.OpenDrive("test")
        odr.add_road(myRoad)
        odr.adjust_roads_and_lanes()

        extensions.printRoadPositions(odr)

        extensions.view_road(odr, os.path.join('..','F:\\myProjects\\av\\esmini'))


    def test_getConnectionRoadBetween(self):
        # test scenario for connection road
        pass