import math
from shapely.geometry import LineString
import numpy as np
from sympy import symbols, Eq, solve, expand
import torch 

class RewardUtil():
    @staticmethod
    def score(roundabout):
        if RewardUtil.is_intersect(roundabout):
            return 0
    
        return RewardUtil.getTotalOffset(roundabout).mean()
    
    @staticmethod
    def is_intersect(roundabout, nPoints = 10):
        coeffs, _ = RewardUtil.getCoeffs(roundabout)
        for i in range(len(coeffs)):
            for j in range(i + 1, len(coeffs)):
                if RewardUtil.find_intersection_point_by_coeffs(coeffs[i], coeffs[j], nPoints):
                    return True
                
        return False
    
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
    def encodeState(laneToCircularIDs, nCircularID):
        encode = torch.zeros(len(laneToCircularIDs) * nCircularID)
        for i, laneToCircularID in enumerate(laneToCircularIDs):
            if laneToCircularID == -1:
                continue
            encode[i * nCircularID + laneToCircularID] = 1
            
        return encode
    
    @staticmethod
    def getAllowedActionsFilter(encoding, nSlots):
        filter = torch.zeros(len(encoding))
        for i in range(0, len(encoding), nSlots):
        # encoding[i : i + nSlots] = 1 - encoding[i : i + nSlots].count(1)
            _ = encoding[i : i + nSlots]
            filter[i : i + nSlots] = 1 - len(_[_ == 1]) != 0
        return filter