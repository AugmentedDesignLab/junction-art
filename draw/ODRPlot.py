from extensions.moreHelpers import laneWidths
import math
import matplotlib.pyplot as plt
import pyodrx
from extensions.ExtendedOpenDrive import ExtendedOpenDrive
from junctions.StandardCurveTypes import StandardCurveTypes
import numpy as np
from sympy import Point, Line

class ODRPlot():
    def __init__(self, odr):
        self.odr = odr
        self.roads = odr.roads
        self.xVal = []
        self.yVal = []


    def draw_odr(self):
        for key in self.odr.roads:
            road = self.odr.roads.get(key)
            if road.curveType == StandardCurveTypes.Line:
                self.draw_straight_road(road)
                # print()
            # elif road.curveType == StandardCurveTypes.Poly:
            #     if road.id < 6:
            #         # self.draw_poly_road(road)
            #         print(road.id)


        for i in range(len(self.xVal)):
            plt.plot(self.xVal[i], self.yVal[i])
            
        # plt.plot(self.xVal, self.yVal)
        plt.show()
        pass

    def draw_straight_road(self, StraightRoad):
        pv = StraightRoad.planview
        start_x, start_y, _ = pv.get_start_point()
        end_x, end_y, _ = pv.get_end_point()
        x_val = [start_x, end_x]
        y_val = [start_y, end_y]
        self.xVal.append(x_val)
        self.yVal.append(y_val)

        lane_width = 15

        start_point = Point(start_x, start_y)
        end_point = Point(end_x, end_y)

        ab = Line(start_point, end_point) # ab
        cd, ef = self.calculate_parallel_line_at_distance(ab, lane_width)

        # print('parallel_line1 ', parallel_line1, ' parallel_line2 ', parallel_line2)
        

        print('ab ', ab)
        print('cd ', cd)
        print('ef ', ef)

        ce, df = ab.perpendicular_line(end_point), ab.perpendicular_line(start_point) 

        c = ce.intersection(cd)[0]
        d = df.intersection(cd)[0]
        e = ce.intersection(ef)[0]
        f = df.intersection(ef)[0]

        print(c)
        print(d)
        print(e)
        print(f)

        # x_val = [c.x, d.x]
        # y_val = [c.y, d.y]
        # self.xVal.append(x_val)
        # self.yVal.append(y_val)

        # x_val = [e.x, f.x]
        # y_val = [e.y, f.y]
        # self.xVal.append(x_val)
        # self.yVal.append(y_val)

        # print('center line ', center_line)
        # perpendicular_line = center_line.perpendicular_line(start_point)
        # parallel_line = center_line.
        # print('perpendicular line ', perpendicular_line.coefficients)

        pass

    def calculate_parallel_line_at_distance(self, line, distance):
        a, b, c = line.coefficients # ax + by + c = 0
        m, c = -(a/b), -(c/b) # y = mx + c
        # slope = line.slope
        # print('slope ', slope, ' m ', m)
        abs_diff = distance*math.sqrt(m**2 + 1)
        c1, c2 = abs_diff - c, abs_diff + c
        line1 = Line(Point(-m/c1, 0), Point(0, 1/c1))
        line2 = Line(Point(-m/c2, 0), Point(0, 1/c2))
        return line1, line2


    def draw_poly_road(self, ParamPolyRoad):
        pv = ParamPolyRoad.planview
        adjusted_geoms = pv._adjusted_geometries
        x_start, y_start, h_start = pv.get_start_point()
        x_end, y_end, h_end = pv.get_end_point()

        # print('start ', x_start, y_start, h_start)
        # print('end ', x_end, y_end, h_end)

        for geom in adjusted_geoms:
            _attr = geom.geom_type.get_attributes()

            aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
            aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])

            # print('U ',aU, bU, cU, dU)
            # print('V ',aV, bV, cV, dV)

            x_val = []
            y_val = []
            
            # h_start = h_start - h_end
             
            for i in np.arange(0, 1.1, 0.1):
                # getting the value from the actual equation from (0, 0) origin
                x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
                y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)

                # transforming the points from the end of incident roads
                # TODO: transform wrt contact point 
                x_trans = x_abs*math.cos(h_start) - y_abs*math.sin(h_start) + x_start
                y_trans = x_abs*math.sin(h_start) + y_abs*math.cos(h_start) + y_start

                # x_trans = x_abs
                # y_trans = y_abs

                x_val.append(x_trans)
                y_val.append(y_trans)
                # print(i, x_abs, y_abs)

            self.xVal.append(x_val)
            self.yVal.append(y_val)
        pass

    



