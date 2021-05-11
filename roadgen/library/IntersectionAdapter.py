class IntersectionAdapter:

    def odrTo4DirectionIntersection(self, odr):

        #1. TODO if not adjusted, adjust

        #2. find the minimum bounding box
        bbox = self.getBBox(odr)

        #3. find the center of the bounding box

        #4. assign direction based on the position of the incident points

        #5. adjust direction based on the heading.


    def getBBox(self, odr):
        """[summary]

        Args:
            odr ([type]): [description]
        """

        pass


    def getWH(self, odr, mode='incident-point'):
        """returns width and height. Assumes incidents road has almost 0 length for simplicity

        Args:
            odr ([type]): [description]
        """

        if mode == 'incident-point'

