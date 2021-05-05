from roadgen.layout.NotEmptyException import NotEmptyException
class Cell:

    def __init__(self, size, cell_position, abs_position=None, element=None):
        self.size = size
        self.left = None
        self.leftTop = None
        self.leftBot = None
        self.right = None
        self.rightTop = None
        self.rightBot = None
        self.top = None
        self.bot = None
        self.cell_position = cell_position
        self.abs_position = abs_position
        self.element = element
        self._entropy = None
        
    

    def getEntropy(self):
        return self._entropy
        
    def updateEntropy(self, entropy):
        """ entropy is only updated if the cell is empty """
        if self.element is None:
            self._entropy = entropy

    def isEmpty(self):
        if self.element is None:
            return True
        return False


    def setElement(self, element):
        """ element is either a road segment or an obstacle. Don't call this method. """
        if self.element is not None:
            raise NotEmptyException(self.element)
        self.element = element
        self._entropy = 10

    def updateElement(self, element):
        """ element is either a road segment or an obstacle. Don't call this method. """
        self.element = element
        self._entropy = 10