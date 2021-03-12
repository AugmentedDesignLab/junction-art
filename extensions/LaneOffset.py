import xml.etree.ElementTree as ET

class LaneOffset:
    
    """ 

        the inputs are on the following format:
            f(s) = a + b*s + c*s^2 + d*s^3

        Parameters
        ----------
            
            a (float): a coefficient
                Default: 0

            b (float): b coefficient
                Default: 0

            c (float): c coefficient
                Default: 0

            d (float): d coefficient
                Default: 0

            s (float): s of lane
                Default: 0


        Attributes
        ----------
            
            lane_type (LaneType): type of lane

            a (float): a coefficient

            b (float): b coefficient

            c (float): c coefficient

            d (float): d coefficient

            s (float): s of lane


        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of class

            add_roadmark(roadmark)
                adds a new roadmark to the lane

    """
    def __init__(self,a=0,b=0,c=0,d=0,s=0):
        """ initalizes the Lane

        Parameters
        ----------

            a (float): a coefficient
                Default: 0

            b (float): b coefficient
                Default: 0

            c (float): c coefficient
                Default: 0

            d (float): d coefficient
                Default: 0

            s (float): s of lane
                Default: 0

        """ 
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.s = s


    def get_attributes(self):
        dic = {}
        dic['s'] = str(self.s)
        dic['a'] = str(self.a)
        dic['b'] = str(self.b)
        dic['c'] = str(self.c)
        dic['d'] = str(self.d)
        return dic

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('laneOffset',attrib=self.get_attributes())
        return element

    def copy(self):
        laneOffset = LaneOffset(
                            a=self.a,
                            b=self.b,
                            c=self.c,
                            d=self.d,
                            s=self.s)
        return laneOffset
    
    @staticmethod
    def createLinear(s, maxWidth, laneLength):

        if laneLength is None:
            raise Exception("Lane length cannot be None for turn lanes")

        if maxWidth is None:
            raise Exception("maxWidth cannot be None for turn lanes")

        a = 0
        b = (maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        return LaneOffset(s=s, a=a, b=b)

    
    @staticmethod
    def createParallel(s, a):
        return LaneOffset(s=s, a=a)


