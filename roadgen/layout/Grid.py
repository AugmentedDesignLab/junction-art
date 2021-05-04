from roadgen.layout.Cell import Cell
from roadgen.layout.BoundaryException import BoundaryException

class Grid:

    def __init__(self, size=(1000, 1000), cellSize=(100, 100)):
        self.size = size
        self.cellSize = cellSize
        self.nRows = int(self.size[0] / self.cellSize[0])
        self.nCols = int(self.size[1] / self.cellSize[1])
        self.cells = []
        self.createCells()
    

    def createCells(self):

        for i in range(self.nRows):
            self.cells.append([])
            for j in range(self.nCols):
                cell = Cell(self.cellSize, cell_position=(i, j))
                self.cells[i].append(cell)
        
        self.updateAllEntropy()
        pass


    def getCellsWithLowestEntropy(self):
        """For each blank cell around a cell, an entropy of 1 is given. A cell which has 0 entropy has no blank cells around.
        """

        """ TODO worst algo. Do a DIP to make it faster """
        # for i in range(self.nRows):
        #     for j in range(self.nCols):
        #         cell = self.cells[i][j]
        #         self.updateEntropyFor(cell)

    def setCellElement(self, cell, element):
        cell.setElement(element)
        self.updateAllEntropy() # TODO write a better algo. Do not need to update the whole grid.


    def updateAllEntropy(self):
        for i in range(self.nRows):
            for j in range(self.nCols):
                cell = self.cells[i][j]
                self.updateEntropyFor(cell)


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

    
    #### relative cell stats ###########
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

    #### END relative cell stats ###########