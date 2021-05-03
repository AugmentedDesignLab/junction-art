from roadgen.layout.Cell import Cell

class Grid:

    def __init__(self, size=(1000, 1000), cellSize=(100, 100)):
        self.size = size
        self.cellSize = cellSize
        self.nRows = self.size[0] / self.cellSize[0]
        self.nCols = self.size[1] / self.cellSize[1]
        self.cells = []
        self.createCells()
    

    def createCells(self):

        for i in range(self.nRows):
            self.cells.append([])
            for j in range(self.nCols):
                cell = Cell(self.cellSize, position=(i, j))
                self.cells[i].append(cell)
        pass


    def getCellsWithLowestEntropy(self):
        """For each blank cell around a cell, an entropy of 1 is given. A cell which has 0 entropy has no blank cells around.
        """

        """ TODO worst algo. Do a DIP to make it faster """
        for i in range(self.nRows):
            for j in range(self.nCols):
                cell = self.cells[i][j]
                self.updateEntropyFor(i, j)

    

    def updateEntropyFor(self, i, j):
        cell = self.cells[i][j]
        