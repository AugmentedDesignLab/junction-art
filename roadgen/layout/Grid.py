from roadgen.layout.Cell import Cell
from roadgen.definitions.EmptySpace import EmptySpace
from roadgen.layout.PerlinNoise import PerlinNoiseFactory
from roadgen.layout.BoundaryException import BoundaryException
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib

class Grid:

    def __init__(self, size=(1000, 1000), cellSize=(100, 100)):
        self.size = size
        self.cellSize = cellSize
        self.nRows = int(self.size[0] / self.cellSize[0])
        self.nCols = int(self.size[1] / self.cellSize[1])
        self.cellXScale = self.size[1] / self.nCols
        self.cellYScale = self.size[0] / self.nRows
        self.cells = []
        self.entropyDicEmptyCells = {}
        self.cellNoises = {}
        self.noiseFactory = PerlinNoiseFactory(2)
        self.createCells()
        self.cellPlacementOrder = []

        
    

    def createCells(self):

        for i in range(self.nRows):
            self.cells.append([])
            for j in range(self.nCols):
                cell = Cell(self.cellSize, cell_position=(i, j))
                self.cells[i].append(cell)
                # self.cellNoises[cell] = self.noiseFactory(i/self.nRows, j/self.nCols)
                self.cellNoises[cell] = abs(self.noiseFactory(i/self.nRows, j/self.nCols)) *  cell.size[0]
        
        self.updateAllEntropy()

        # print(self.cellNoises)
        pass

    def cellGenerator(self):
        for i in range(self.nRows):
            for j in range(self.nCols):
                yield self.cells[i][j]

    
    def getAbsCellPosition(self, cell):
        (i, j) = cell.cell_position
        return (self.cellXScale * j, self.cellYScale * i)


    def nCells(self):
        return self.nRows * self.nCols

    
    def nEmptyCells(self):
        return len(self.entropyDicEmptyCells.values())


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


    def updateAllEntropy(self):

        self.entropyDicEmptyCells = {} # reset

        for i in range(self.nRows):
            for j in range(self.nCols):
                cell = self.cells[i][j]
                self.updateEntropyFor(cell)

                if cell.isEmpty():
                    entropy = cell.getEntropy()
                    if entropy not in self.entropyDicEmptyCells:
                        self.entropyDicEmptyCells[entropy] = []
                    self.entropyDicEmptyCells[entropy].append(cell)

        self.entropyDicEmptyCells = dict(sorted((self.entropyDicEmptyCells.items())))

    def updateEntropyFor(self, cell: Cell):
        (i, j) = cell.cell_position
        cell = self.cells[i][j]
        entropy = 0
        try:
            if self.emptyLeft(cell) or self.hasEmptySpaceOnLeft(cell):
                entropy += 1
            
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyRight(cell) or self.hasEmptySpaceOnRight(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyTop(cell) or self.hasEmptySpaceOnTop(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyBot(cell) or self.hasEmptySpaceOnBot(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyLeftTop(cell) or self.hasEmptySpaceOnLeftTop(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyLeftBot(cell) or self.hasEmptySpaceOnLeftBot(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyRightTop(cell) or self.hasEmptySpaceOnRightTop(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass

        try:
            if self.emptyRightBot(cell) or self.hasEmptySpaceOnRightBot(cell):
                entropy += 1
        except BoundaryException:
            entropy += 1
            pass
        
        cell.updateEntropy(entropy)
        

    #endregion 
    
    #region ######## relative cell stats ###########

    def isLeftBoundary(self, cell):
        (i, j) = cell.cell_position
        if j == 0:
            return True
        return False

    def isRightBoundary(self, cell):
        (i, j) = cell.cell_position
        if j == self.nCols - 1:
            return True
        return False

    def isTopBoundary(self, cell):
        (i, j) = cell.cell_position
        if i == self.nRows - 1:
            return True
        return False

    def isBotBoundary(self, cell):
        (i, j) = cell.cell_position
        if i == 0:
            return True
        return False

    
    def isEmpty(self, i, j):
        cell = self.cells[i][j]
        return cell.isEmpty()

    def emptyLeft(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")

        (i, j) = cell.cell_position
        return self.isEmpty(i, j-1)

    def emptyRight(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")

        (i, j) = cell.cell_position
        return self.isEmpty(i, j+1)

    def emptyTop(self, cell):
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.isEmpty(i+1, j)

    def emptyBot(self, cell):
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.isEmpty(i-1, j)
        
    def emptyLeftTop(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.isEmpty(i+1, j-1)

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
        return self.isEmpty(i-1, j+1)

    
    def hasEmptySpaceOnLeft(self, cell):
        if isinstance(self.leftElement(cell), EmptySpace):
            return True
        return False
    
    def hasEmptySpaceOnRight(self, cell):
        if isinstance(self.rightElement(cell), EmptySpace):
            return True
        return False
    
    def hasEmptySpaceOnTop(self, cell):
        if isinstance(self.topElement(cell), EmptySpace):
            return True
        return False
    
    def hasEmptySpaceOnBot(self, cell):
        if isinstance(self.botElement(cell), EmptySpace):
            return True
        return False

    def hasEmptySpaceOnLeftTop(self, cell):
        if isinstance(self.leftTopElement(cell), EmptySpace):
            return True
        return False
    
    def hasEmptySpaceOnLeftBot(self, cell):
        if isinstance(self.leftBotElement(cell), EmptySpace):
            return True
        return False
    
    def hasEmptySpaceOnRightTop(self, cell):
        if isinstance(self.rightTopElement(cell), EmptySpace):
            return True
        return False

    def hasEmptySpaceOnRightBot(self, cell):
        if isinstance(self.rightBotElement(cell), EmptySpace):
            return True
        return False

    #endregion #### END relative cell stats ###########

    #region elements

    
    def setCellElement(self, cell, element):
        self.cellPlacementOrder.append(cell)
        cell.setElement(element)
        self.updateAllEntropy() # TODO write a better algo. Do not need to update the whole grid.


    def left(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")

        (i, j) = cell.cell_position
        return self.cells[i][j-1]
    
    def right(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")

        (i, j) = cell.cell_position
        return self.cells[i][j+1]
    
    def top(self, cell):
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.cells[i+1][j]
    
    def bot(self, cell):
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.cells[i-1][j]

    def leftTop(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.cells[i+1][j-1]

    def leftBot(self, cell):
        if self.isLeftBoundary(cell):
            raise BoundaryException("Left")
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.cells[i-1][j-1]

    def rightTop(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")
        if self.isTopBoundary(cell):
            raise BoundaryException("Top")

        (i, j) = cell.cell_position
        return self.cells[i+1][j+1]

    def rightBot(self, cell):
        if self.isRightBoundary(cell):
            raise BoundaryException("Right")
        if self.isBotBoundary(cell):
            raise BoundaryException("Bot")

        (i, j) = cell.cell_position
        return self.cells[i-1][j+1]


    def leftElement(self, cell):
        try:
            neighbourCell = self.left(cell)
            return neighbourCell.element
        except BoundaryException:
            return None

    def rightElement(self, cell):
        try:
            neighbourCell = self.right(cell)
            return neighbourCell.element
        except BoundaryException:
            return None

    def topElement(self, cell):
        try:
            neighbourCell = self.top(cell)
            return neighbourCell.element
        except BoundaryException:
            return None
        
    def botElement(self, cell):
        try:
            neighbourCell = self.bot(cell)
            return neighbourCell.element
        except BoundaryException:
            return None

    def leftTopElement(self, cell):
        try:
            neighbourCell = self.leftTop(cell)
            return neighbourCell.element
        except BoundaryException:
            return None

    def leftBotElement(self, cell):
        try:
            neighbourCell = self.leftBot(cell)
            return neighbourCell.element
        except BoundaryException:
            return None
    
    def rightTopElement(self, cell):
        try:
            neighbourCell = self.rightTop(cell)
            return neighbourCell.element
        except BoundaryException:
            return None

    
    def rightBotElement(self, cell):
        try:
            neighbourCell = self.rightBot(cell)
            return neighbourCell.element
        except BoundaryException:
            return None


    #endregion

    #region prints

    def printCellElements(self):
        for cell in self.cellGenerator():
            print(f"Cell ({cell.cell_position})")
            print(f"{cell.element}")

    
    def plot(self):

        fig,ax=plt.subplots()

        ax.set_xlim(0, self.size[0])
        ax.set_ylim(0, self.size[1])

        xLocator = MultipleLocator(self.cellSize[0])
        yLocator = MultipleLocator(self.cellSize[1])

        ax.xaxis.set_major_locator(xLocator)
        ax.yaxis.set_major_locator(yLocator)
        ax.grid(which='major', axis='both', linestyle='--')
        cellIdArgs = dict(ha='left', va='bottom', fontsize=7, color='C1')
        for cell in self.cellGenerator():
            (x, y) = self.getAbsCellPosition(cell)
            placementOrder = self.cellPlacementOrder.index(cell)
            # plt.text(x, y, f"{cell.cell_position}", cellIdArgs)

            contentX = x + 3
            contentY = y + self.cellSize[0] - 3
            clipBox = matplotlib.transforms.Bbox.from_bounds(x, y, 50, 50)
            bbox = dict(x=x, y=y)
            cellContentArgs = dict(ha='left', va='top', fontsize=8, color='C1', 
                # bbox=bbox, 
                clip_on=True,
                clip_box=clipBox, 
                wrap=True)
            plt.text(contentX, contentY, f"{cell.cell_position}: order: {placementOrder}\n{cell.element}", **cellContentArgs)

        ax.set_title("Cell placements")
        ax.set_xlabel("x in meters")
        ax.set_ylabel("y in meters")
        plt.show()

    #endregion
