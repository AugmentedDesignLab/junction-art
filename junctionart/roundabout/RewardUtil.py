import math
from shapely.geometry import LineString, LinearRing, Point
import numpy as np
from sympy import symbols, Eq, solve, expand
import torch
import matplotlib.pyplot as plt
from frechetdist import frdist

class RewardUtil():
    @staticmethod
    def score(roundabout):
        # if RewardUtil.is_intersect(roundabout):
        #     return 0
        
        if RewardUtil.isIntersectV2(roundabout):
            return 0
        
    
        return RewardUtil.getTotalOffset(roundabout).mean()
    
    @staticmethod
    def score2(roundabout):
        reward = 0
        circle = RewardUtil.getCircleFromRoundabout(roundabout)
        centerLanes, rightLanes = RewardUtil.getCenterAndRightLanesFromRoundabout(roundabout)
        for rightLane in rightLanes:
            if not rightLane.intersects(circle):
               reward += .5 
        for i in range(len(rightLanes)):
            for j in range(i+1, len(rightLanes)):
                if not rightLanes[i].intersects(rightLanes[j]):
                    reward += .5
                
        for i in range(len(centerLanes)):
            for j in range(i+1, len(centerLanes)):
                if not centerLanes[i].intersects(centerLanes[j]):
                    reward += .5
        return reward
        
    @staticmethod
    def is_intersect(roundabout, nPoints = 10):
        coeffs, isIncoming = RewardUtil.getCoeffs(roundabout)
        for i in range(len(coeffs)):
            if RewardUtil.isIntersectWithCircle(roundabout, coeffs[i], isIncoming[i], nPoints):
                return True
        for i in range(len(coeffs)):
            for j in range(i + 1, len(coeffs)):
                if RewardUtil.find_intersection_point_by_coeffs(coeffs[i], coeffs[j], nPoints):
                    return True
                
        return False
    
    @staticmethod
    def isIntersectWithCircle(roundabout, coeffs1, isIncoming, nPoints=10):
        u_coeffs1, v_coeffs1 = coeffs1
        x1, y1 = RewardUtil.get_coordinate_wrt_origin(u_coeffs1, v_coeffs1, nPoints)
        points1 = [(x1[i], y1[i]) for i in range(len(x1))]
        line1 = LineString(points1[4:len(points1) -1]) if isIncoming else LineString(points1[1:len(points1) -4])
        circle = LineString([(point.x, point.y) for point in roundabout.circularRoadStartPoints])

        return line1.intersects(circle)
    @staticmethod
    def getTotalOffset(roundabout, nPoints = 10):
        coeffs, isIncoming = RewardUtil.getCoeffs(roundabout)
        offsets = []
        center = roundabout.center
        for i, coeff in enumerate(coeffs):
            flip = isIncoming[i]
            points = RewardUtil.getPointsFromCoeff(coeff, nPoints)
            pointA = points[-1] if flip else points[0] 
            pointB = points[0] if flip else points[-1]

            angle = np.rad2deg(np.arctan2(pointB[1] - pointA[1], pointB[0] - pointA[0]))
            angle2 = np.rad2deg(np.arctan2(center.y - pointA[1], center.x - pointA[0]))
            offset = np.abs(angle - angle2)
            offset = offset if offset < 180 else 360 - offset
            offsets.append(offset)
            
        return np.array(offsets)
    
    @staticmethod
    def getCoeffs(roundabout):
        coeffs = []
        isIncoming = []
        for i in range(len(roundabout.incomingConnectionRoads)):
            connectionRoad = roundabout.incomingConnectionRoads[i]
            u_coeffs, v_coeffs = RewardUtil.getTransformedParampoly(connectionRoad)
            coeffs.append((u_coeffs, v_coeffs))
            isIncoming.append(True)
            
        for i in range(len(roundabout.outgoingConnectionRoads)):
            connectionRoad = roundabout.outgoingConnectionRoads[i]
            ppoly = connectionRoad.planview._raw_geometries[0]
            u_coeffs, v_coeffs = RewardUtil.getTransformedParampoly(connectionRoad)
            coeffs.append((u_coeffs, v_coeffs))
            isIncoming.append(False)
        return coeffs, isIncoming
    
    @staticmethod
    def getPointsFromCoeff(coeffs, nPoints):
        u_coeffs, v_coeffs = coeffs
        x, y = RewardUtil.get_coordinate_wrt_origin(u_coeffs, v_coeffs, nPoints)
        points = [(x[i], y[i]) for i in range(len(x))]
        return points
    
    @staticmethod
    def find_intersection_point_by_coeffs(coeffs1, coeffs2, nPoints=10):
        u_coeffs1, v_coeffs1 = coeffs1
        u_coeffs2, v_coeffs2 = coeffs2
        x1, y1 = RewardUtil.get_coordinate_wrt_origin(u_coeffs1, v_coeffs1, nPoints)
        x2, y2 = RewardUtil.get_coordinate_wrt_origin(u_coeffs2, v_coeffs2, nPoints)
        points1 = [(x1[i], y1[i]) for i in range(len(x1))]
        points2 = [(x2[i], y2[i]) for i in range(len(x2))]
        line1 = LineString(points1[1:len(points1) -1])
        line2 = LineString(points2[1:len(points2) - 1])
        # if line1.intersects(line2):
        #     plt.plot(x1, y1)
        #     plt.plot(x2, y2)
        #     plt.show()
        return line1.intersects(line2)
    
    @staticmethod
    def getTransformedParampoly(polyRoad):
        # Get start Point
        x_start, y_start, h_start = polyRoad.planview.get_start_point()
    
        # Get four points
        ppoly = polyRoad.planview._raw_geometries[0]
        x, y = RewardUtil.get_coordinate_wrt_origin([ppoly.au, ppoly.bu, ppoly.cu, ppoly.du], [ppoly.av, ppoly.bv, ppoly.cv, ppoly.dv], step = 4)

        # Transform these four points
        x, y = RewardUtil.transform_to_geometric_start_point(x_start, y_start, h_start, x, y)
        
        points = []
        for i in range(len(x)):
            points.append((x[i], y[i]))
        u_coeffs, v_coeffs = RewardUtil.calculate_parametric_cubic_equation(points)
        
        # x, y = get_coordinate_wrt_origin(u_coeffs, v_coeffs, step = 100)
        return u_coeffs, v_coeffs
    
    @staticmethod
    def getTransformedPoints(polyRoad):
        # Get start Point
        x_start, y_start, h_start = polyRoad.planview.get_start_point()
    
        # Get four points
        ppoly = polyRoad.planview._raw_geometries[0]
        x, y = RewardUtil.get_coordinate_wrt_origin([ppoly.au, ppoly.bu, ppoly.cu, ppoly.du], [ppoly.av, ppoly.bv, ppoly.cv, ppoly.dv], step = 4)

        # Transform these four points
        x, y = RewardUtil.transform_to_geometric_start_point(x_start, y_start, h_start, x, y)
        

        return x, y
    
    @staticmethod
    def get_coordinate_wrt_origin(u_coeffs, v_coeffs, step):
    
        array_size = np.int64((1/step)+1)
        
        coff1 = np.array([u_coeffs])
        coff2 = np.array([v_coeffs])

        mat_i = np.linspace(0.0, 1.0, step, dtype=np.float64)
        new_mat = np.zeros((4, step))
        
        for i in range(4):
            new_mat[i] = mat_i**i
    
        xVal = coff1.dot(new_mat)
        yVal = coff2.dot(new_mat)

        return xVal[0], yVal[0]
    
    @staticmethod
    def calculate_parametric_cubic_equation(points):
        t = symbols('t')
        
        # Extract the x and y coordinates of the given points
        x0, y0 = points[0]
        x1, y1 = points[1]
        x2, y2 = points[2]
        x3, y3 = points[3]
        
        # Calculate the coefficients for the parametric cubic equation
        uA = x0
        uB = 3*(x1 - x0)
        uC = 3*(x2 - 2*x1 + x0)
        uD = x3 - 3*x2 + 3*x1 - x0
        
        vA = y0
        vB = 3*(y1 - y0)
        vC = 3*(y2 - 2*y1 + y0)
        vD = y3 - 3*y2 + 3*y1 - y0
        
        # Construct the parametric cubic equation
        x_t = uA + uB*t + uC*t**2 + uD*t**3
        y_t = vA + vB*t + vC*t**2 + vD*t**3
        
        # Expand the equation for better readability
        # x_t = expand(x_t)
        # y_t = expand(y_t)
        
        # Return the equations for x(t) and y(t)
        return [uA, uB, uC, uD], [vA, vB, vC, vD]
    
    @staticmethod
    def transform_to_geometric_start_point(x, y, h, x_wrt_origin, y_wrt_origin):
        x_trans = x_wrt_origin*math.cos(h) - y_wrt_origin*math.sin(h) + x
        y_trans = x_wrt_origin*math.sin(h) + y_wrt_origin*math.cos(h) + y
        return x_trans,y_trans
    
    @staticmethod
    def encodeState(laneToSlotConfig, nSlots):
        encode = torch.zeros(len(laneToSlotConfig) * nSlots)
        for i, laneToCircularID in enumerate(laneToSlotConfig):
            if laneToCircularID == -1:
                continue
            encode[i * nSlots + laneToCircularID] = 1
            
        return encode
    
    @staticmethod
    def getAllowedActionsFilter(encoding, nSlots):
        filter = torch.zeros(len(encoding))
        for i in range(0, len(encoding), nSlots):
        # encoding[i : i + nSlots] = 1 - encoding[i : i + nSlots].count(1)
            _ = encoding[i : i + nSlots]
            filter[i : i + nSlots] = 1 - len(_[_ == 1]) != 0
        return filter
    
    @staticmethod
    def getLanePointsFromPolyRoads(ParamPolyRoad, lanewidth=3, step=0.1):
        x_start, y_start, h_start = ParamPolyRoad.planview.get_start_point()
        start_point = Point(x_start, y_start)
        for geom in ParamPolyRoad.planview._adjusted_geometries:

            aU, bU, cU, dU, aV, bV, cV, dV = RewardUtil.get_parampoly_coefficiants(geom)
            xVal_centerline, yVal_centerline = [], []
            xVal_leftlane, yVal_leftlane = [], []
            xVal_rightlane, yVal_rightlane = [], []

            for i in np.arange(0, 1+step, step):
                # getting the value from the actual equation from (0, 0) origin
                x_abs, y_abs = RewardUtil.get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i)

                # getting the differentiated value
                x_diff_val, y_diff_val = RewardUtil.get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i)
                
                # transforming the points from the end of incident roads
                # TODO: transform wrt contact point
                centerline_point = Point(x_abs, y_abs)
                x_trans, y_trans = RewardUtil.transform_by_start_point(h_start, start_point, centerline_point)
                xVal_centerline.append(x_trans)
                yVal_centerline.append(y_trans)

                # if len(ParamPolyRoad.lanes.lanesections[0].leftlanes) != 0:
                #     x_trans_left, y_trans_left = RewardUtil.calc_coordinate_wrt_geometric_start(h_start, start_point, -lanewidth, x_diff_val, y_diff_val, centerline_point)
                #     xVal_leftlane.append(x_trans_left)
                #     yVal_leftlane.append(y_trans_left)

                if len(ParamPolyRoad.lanes.lanesections[0].rightlanes) != 0:
                    x_trans_right, y_trans_right = RewardUtil.calc_coordinate_wrt_geometric_start(h_start, start_point, +lanewidth, x_diff_val, y_diff_val, centerline_point)
                    xVal_rightlane.append(x_trans_right)
                    yVal_rightlane.append(y_trans_right)

            
            return xVal_centerline, yVal_centerline, xVal_leftlane, yVal_leftlane, xVal_rightlane, yVal_rightlane

    @staticmethod
    def get_parampoly_coefficiants(geom):
        _attr = geom.geom_type.get_attributes()
        aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
        aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])
        return aU,bU,cU,dU,aV,bV,cV,dV
    
    @staticmethod
    def transform_by_start_point(h_start, geometric_start_point, point_wrt_origin):
        x_trans = point_wrt_origin.x*math.cos(h_start) - point_wrt_origin.y*math.sin(h_start) + geometric_start_point.x
        y_trans = point_wrt_origin.x*math.sin(h_start) + point_wrt_origin.y*math.cos(h_start) + geometric_start_point.y
        return x_trans,y_trans
    
    @staticmethod
    def calc_coordinate_wrt_geometric_start(h_start, start_point, lanewidth, x_diff_val, y_diff_val, centerline_point):
        x_leftlane, y_leftlane = RewardUtil.calc_coordinate_for_lane(lanewidth, centerline_point, x_diff_val, y_diff_val)
        point_wrt_origin = Point(x_leftlane, y_leftlane)
        x_trans_left, y_trans_left = RewardUtil.transform_by_start_point(h_start, start_point, point_wrt_origin)
        return x_trans_left,y_trans_left
    
    @staticmethod
    def calc_coordinate_for_lane(lanewidth, point_wrt_origin, x_diff_val, y_diff_val): 
        temp = lanewidth/math.sqrt(x_diff_val**2 + y_diff_val**2)
        x_leftlane = point_wrt_origin.x + temp*y_diff_val
        y_leftlane = point_wrt_origin.y - temp*x_diff_val
        return x_leftlane,y_leftlane
    
    @staticmethod
    def get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i):
        x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
        y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)
        return x_abs,y_abs
    

    @staticmethod
    def get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i):
        x_diff_val = bU + 2*cU*i + 3*dU*(i**2)
        y_diff_val = bV + 2*cV*i + 3*dV*(i**2)
        return x_diff_val,y_diff_val
    
    @staticmethod
    def getCenterAndRightLane(road, isIncoming):
        centerLanes, rightLanes = RewardUtil.getCenterAndRightLanePoints(road, step=0.05)
        return LineString(centerLanes[:-4] if isIncoming else centerLanes[4:]), LineString(rightLanes)
    
    @staticmethod
    def getCenterAndRightLanePoints(road, step):
        xVal_centerline, yVal_centerline, xVal_leftlane, yVal_leftlane, xVal_rightlane, yVal_rightlane = RewardUtil.getLanePointsFromPolyRoads(road, step=step)
        rightLanes = [(xVal_rightlane[i], yVal_rightlane[i]) for i in range(len(xVal_rightlane))]
        centerLanes = [(xVal_centerline[i], yVal_centerline[i]) for i in range(len(xVal_centerline))]
        return centerLanes, rightLanes
    @staticmethod
    def getCenterAndRightLanesFromRoundabout(roundabout):
        centerLanes = []
        rightLanes = []
        for road in roundabout.incomingConnectionRoads:
            centerLane, rightLane = RewardUtil.getCenterAndRightLane(road, True)
            centerLanes.append(centerLane)
            rightLanes.append(rightLane)
  
        for road in roundabout.outgoingConnectionRoads:
            centerLane, rightLane = RewardUtil.getCenterAndRightLane(road, False)
            centerLanes.append(centerLane)
            rightLanes.append(rightLane)

        return centerLanes, rightLanes
    
    @staticmethod
    def getCircleFromRoundabout(roundabout):
        circle = LinearRing([(point.x, point.y) for point in roundabout.circularRoadStartPoints])
        return circle
    
    @staticmethod
    def isIntersectV2(roundabout):
        circle = RewardUtil.getCircleFromRoundabout(roundabout)
        centerLanes, rightLanes = RewardUtil.getCenterAndRightLanesFromRoundabout(roundabout)
        for rightLane in rightLanes:
            if rightLane.intersects(circle):
                return True
        for i in range(len(rightLanes)):
            for j in range(i+1, len(rightLanes)):
                if rightLanes[i].intersects(rightLanes[j]):
                    return True
                
        for i in range(len(centerLanes)):
            for j in range(i+1, len(centerLanes)):
                if centerLanes[i].intersects(centerLanes[j]):
                    return True
        return False
    
    @staticmethod
    def showRewardView(roundabout):
        circle = RewardUtil.getCircleFromRoundabout(roundabout)
        centerLanes, rightLanes = RewardUtil.getCenterAndRightLanesFromRoundabout(roundabout)
        for rightLane in rightLanes:
            plt.plot(*rightLane.xy)
        for centerLane in centerLanes:
            plt.plot(*centerLane.xy)
        plt.plot(*circle.xy)
        plt.show()
    
    @staticmethod
    def getLeftAndRightLanePoints(roundabout, nPoints):
        leftLanes = []
        rightLanes = []
        for road in roundabout.incomingConnectionRoads:
            centerLane, rightLane = RewardUtil.getCenterAndRightLanePoints(road, 1/nPoints)
            rightLanes.append(rightLane)
  
        for road in roundabout.outgoingConnectionRoads:
            centerLane, rightLane = RewardUtil.getCenterAndRightLanePoints(road, 1/nPoints)
            leftLanes.append(rightLane)

        return np.array(leftLanes), np.array(rightLanes)
    
    @staticmethod
    def getDistance(roundabout1, roundabout2, nPoints = 10):
        leftPoints, rightPoints = roundabout1.getConnectionPoints(nPoints)
        p = RewardUtil.getAllPoints(leftPoints, rightPoints)
        leftPoints, rightPoints = roundabout2.getConnectionPoints(nPoints)
        q = RewardUtil.getAllPoints(leftPoints, rightPoints)
        score = 0
        for i in range(len(p)):
            score += frdist(p[i], q[i])
      
        score = score / len(p)
        return score
    
    @staticmethod
    def getAllPoints(leftPoints, rightPoints):
        return np.concatenate((leftPoints, rightPoints), axis = 0)