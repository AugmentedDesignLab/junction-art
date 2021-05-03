class Cell:

    def __init__(self, size, position, element=None):
        self.size = size
        self.left = None
        self.leftTop = None
        self.leftBot = None
        self.right = None
        self.rightTop = None
        self.rightBot = None
        self.top = None
        self.bot = None
        self.position = position
        self.element = element
        self.entropy = None
        


    def setElement(self, element):
        """ element is either a road segment or an obstacle """
        self.element = element