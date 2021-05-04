import unittest
from roadgen.layout.Grid import Grid

class test_Grid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid(size=(1000, 1000), cellSize=(100, 100))

    
    def test_InitialEntropy(self):
        grid = self.grid
        for i in range(grid.nRows):
            for j in range(grid.nCols):
                cell = grid.cells[i][j]
                print(cell.cell_position, " entropy: ", cell.getEntropy())
                if i == 0 or i == 9:
                    if (j == 0 or j ==9):
                        assert cell.getEntropy() == 3
                    else:
                        assert cell.getEntropy() == 5

                if j == 0 or j == 9:
                    if i == 0 or i == 9:
                        assert cell.getEntropy() == 3
                    else:
                        assert cell.getEntropy() == 5

    
    def test_Entropy(self):
        grid = self.grid
        # case 0, 0
        cell = grid.cells[0][0]
        grid.setCellElement(cell, "hi")

        assert grid.cells[0][0].getEntropy() == 10

        assert grid.cells[0][1].getEntropy() == 4
        assert grid.cells[1][1].getEntropy() == 7
        assert grid.cells[1][0].getEntropy() == 4

        
        assert grid.cells[0][2].getEntropy() == 5



        # case 0, 9
        cell = grid.cells[0][9]
        grid.setCellElement(cell, "hi")

        assert grid.cells[0][8].getEntropy() == 4
        assert grid.cells[1][8].getEntropy() == 7
        assert grid.cells[1][9].getEntropy() == 4

        # case 9, 0
        cell = grid.cells[9][0]
        grid.setCellElement(cell, "hi")

        assert grid.cells[9][1].getEntropy() == 4
        assert grid.cells[8][1].getEntropy() == 7
        assert grid.cells[8][0].getEntropy() == 4

        # case 9, 9
        cell = grid.cells[9][9]
        grid.setCellElement(cell, "hi")

        assert grid.cells[9][8].getEntropy() == 4
        assert grid.cells[8][8].getEntropy() == 7
        assert grid.cells[8][9].getEntropy() == 4

        # case 5, 5
        cell = grid.cells[5][5]
        grid.setCellElement(cell, "hi")
        assert grid.cells[4][6].getEntropy() == 7
        assert grid.cells[4][5].getEntropy() == 7
        assert grid.cells[4][4].getEntropy() == 7

        assert grid.cells[6][6].getEntropy() == 7
        assert grid.cells[6][5].getEntropy() == 7
        assert grid.cells[6][4].getEntropy() == 7

        assert grid.cells[5][6].getEntropy() == 7
        assert grid.cells[5][4].getEntropy() == 7

        # case 4, 4
        
        cell = grid.cells[4][4]
        grid.setCellElement(cell, "hi")
        assert grid.cells[3][5].getEntropy() == 7
        assert grid.cells[3][4].getEntropy() == 7
        assert grid.cells[3][3].getEntropy() == 7

        assert grid.cells[5][5].getEntropy() == 10
        assert grid.cells[5][4].getEntropy() == 6
        assert grid.cells[5][3].getEntropy() == 7

        assert grid.cells[4][5].getEntropy() == 6
        assert grid.cells[4][3].getEntropy() == 7