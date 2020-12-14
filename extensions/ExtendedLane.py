import pyodrx
from junctions.TurnTypes import TurnTypes

class ExtendedLane(pyodrx.Lane):

    def __init__(self,lane_type=pyodrx.LaneType.driving,a=0,b=0,c=0,d=0,soffset=0, turnType=TurnTypes.ALL):
        """ initalizes the Lane

        Parameters
        ----------
            
            lane_type (LaneType): type of lane
                Default: LaneType.driving

            a (float): a coefficient
                Default: 0

            b (float): b coefficient
                Default: 0

            c (float): c coefficient
                Default: 0

            d (float): d coefficient
                Default: 0

            soffset (float): soffset of lane
                Default: 0
        """
        super().__init__(lane_type=lane_type, a=a, b=b, c=c, d=d, soffset=soffset)
        self.turnType = turnType
        



    def isProbableTurnLane(self):
        if self.a == 0 and (self.b != 0 or self.c!=0 or self.d !=0):
            return True


