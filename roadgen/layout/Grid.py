from roadgen.layout.Cell import Cell
from roadgen.layout.BoundaryException import BoundaryException

class Grid:

    def __init__(self, size=(1000, 1000), cellSize=(100, 100)):
        self.size = size
        self.cellSize = cellSize
        self.nRows = int(self.size[0] / self.cellSize[0])
        self.nCols = int(self.size[1] / self.cellSize[1])
        self.cells = []
        self.entropyDicEmptyCells = {}
        self.createCells()
    

    def createCells(self):

        for i in range(self.nRows):
            self.cells.append([])
            for j in range(self.nCols):
                cell = Cell(self.cellSize, cell_position=(i, j))
                self.cells[i].append(cell)
        
        self.updateAllEntropy()
        pass

    #region ################ Entropy methods ##################

    def getEmptyCellsWithLowestEntropy(self):
        """For each blank cell around a cell, an entropy of 1 is given. A cell which has 0 entropy has no blank cells around.
        """

        """ TODO worst algo. Do a DIP to make it faster """
        # for i in range(self.nRows):
        #     for j in range(self.nCols):
        #         cell = self.cells[i][j]
        #         self.updateEntropyFor(cell)

        for entropy in self.entropyDicEmptyCells:
            return self.entropyDicEmptyCells[entropy] # the first element


    def setCellElement(self, cell, element):
        cell.setElement(element)
        self.updateAllEntropy() # TODO write a better algo. Do not need to update the whole grid.


    def updateAllEntropy(self):

        self.entropyDicEmptyCells = {} # reset

        for i in range(self.nRows):
            for j in range(self.nCols):
                cell = self.cells[i][j]
                entropy = self.updateEntropyFor(cell)

                if entropy < 10: # no full cell.
                    if entropy not in self.entropyDicEmptyCells:
                        self.entropyDicEmptyCells[entropy] = []
                    self.entropyDicEmptyCells[entropy].append(cell)

        self.entropyDicEmptyCells = dict(sorted((self.entropyDicEmptyCells.items())))

    def updateEntropyFor(self, cell):
        (i, j) = cell.cell_position
        cell = self.cells[i][j]
        entropy = 0
        try:
            if self.emptyLeft(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyRight(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyTop(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyBot(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyLeftTop(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyLeftBot(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyRightTop(cell):
                entropy += 1
        except BoundaryException:
            pass

        try:
            if self.emptyRightBot(cell):
                entropy += 1
        except BoundaryException:
            pass
        
        cell.updateEntropy(entropy)
        
        return entropy

    #endregion 
    
    #region ######## relative cell stats ###########

    def isLeftBoundary(self, cell):
        (i, j) = cell.cell_position
        if i == 0:
            return True
        return False

    def isRightBoundary(self, cell):
        (i, j) = cell.cell_position
        if i == self.nCols - 1:
            return True
        return False

    def isTopBoundary(self, cell):
        (i, j) = cell.cell_position
        if j == self.nRows - 1:
            return True
        return False

    def isBotBoundary(self, cell):
        (i, j) = cell.cell_position
        if j == 0:
            return True
        return False

    
    def isEmpty(self, i, j):
        cell = self.cells[i][j]
        return cell.isEmpty()

    def emptyLeft(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")

        (i, j) = cell.cell_position
        return self.isEmpty(i-1, j)

    def emptyRight(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")

        (i, j) = cell.cell_position
        return self.isEmpty(i+1, j)

    def emptyTop(self, cell):
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.isEmpty(i, j+1)

    def emptyBot(self, cell):
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.isEmpty(i, j-1)
        
    def emptyLeftTop(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.isEmpty(i-1, j+1)

    def emptyLeftBot(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.isEmpty(i-1, j-1)
        
        
    def emptyRightTop(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.isEmpty(i+1, j+1)

    def emptyRightBot(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.isEmpty(i+1, j-1)

    #endregion #### END relative cell stats ###########

    #region elements

    
    def left(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")

        (i, j) = cell.cell_position
        return self.cells[i-1][j]
    
    def right(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")

        (i, j) = cell.cell_position
        return self.cells[i+1][j]
    
    def top(self, cell):
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.cells[i+1][j+1]
    
    def bot(self, cell):
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.cells[i-1][j-1]


    def leftElement(self, cell):
        neighbourCell = self.left(cell)
        return neighbourCell.element

    def rightElement(self, cell):
        neighbourCell = self.right(cell)
        return neighbourCell.element

    def topElement(self, cell):
        neighbourCell = self.top(cell)
        return neighbourCell.element
        
    def botElement(self, cell):
        neighbourCell = self.bot(cell)
        return neighbourCell.element
    
    #endregion
