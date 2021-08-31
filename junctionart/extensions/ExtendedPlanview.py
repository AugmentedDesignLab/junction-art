import pyodrx
from junctionart.junctions.Geometry import Geometry
class ExtendedPlanview(pyodrx.PlanView):

    def reset(self):
        """resets the derived values and positions. Useful for recomputing the network geometires.
        """
        
        self.present_x = 0
        self.present_y = 0
        self.present_h = 0
        self.present_s = 0

        self.x_start = None
        self.y_start = None
        self.h_start = None 

        self.x_end = None
        self.y_end = None
        self.h_end = None

        self._adjusted_geometries = []

        self.adjusted = False
        # add more derived data created in the process of adjustment and link building.

        pass

    def copy(self):
        newPV = ExtendedPlanview(x_start=self.x_start, y_start=self.y_start, h_start=self.h_start)
        for geom in self._raw_geometries:
            newPV.add_geometry(geom)
        
        return newPV

    def getTotalLength(self):
        if self.adjusted:
            return self.get_total_length()
        else:
            return Geometry.getLengthOfGeoms(self._raw_geometries)