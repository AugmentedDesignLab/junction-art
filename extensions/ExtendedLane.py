import pyodrx
from junctions.TurnTypes import TurnTypes

class ExtendedLane(pyodrx.Lane):

    def __init__(self,lane_type=pyodrx.LaneType.driving,a=0,b=0,c=0,d=0,soffset=0, turnType=TurnTypes.UNDEFINED):
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
        self.rules = []
        

    def copy(self, copyLinks=False):
        lane = ExtendedLane(lane_type=self.lane_type,
                            a=self.a,
                            b=self.b,
                            c=self.c,
                            d=self.d,
                            soffset=self.soffset)
        lane.lane_id = self.lane_id
        lane.turnType = self.turnType
        lane.roadmark = self.roadmark
        # TODO copy the rules.
        for rule in self.rules:
            lane.rules.append(rule)
        
        if copyLinks:
            for link in self.links.links:
                lane.links.add_link(link) # TODO may be problematic if link is changed. it should be immutable.

        return lane


    def isProbableTurnLane(self):
        if self.a == 0 and (self.b != 0 or self.c!=0 or self.d !=0):
            return True


    def addRule(self, rule):
        """A rule is a tuple (soffset, serialized rule)

        Args:
            rule ([type]): [description]
        """

        self.rules.append(rule)

