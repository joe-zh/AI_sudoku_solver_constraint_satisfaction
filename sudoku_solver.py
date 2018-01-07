import time
import cProfile
import re
import copy

# helper method that returns a list of coordinates from (0,0) to (8,8)
def sudoku_cells():
    return [(i, j) for i in xrange(9) for j in xrange(9)]

# helper method that returns a list of constraint arcs following the constraint
# satisfaction paradigm
def sudoku_arcs():
    cells = sudoku_cells()
    return [(pair1, pair2) for pair1 in cells for pair2 in cells \
            if pair1 != pair2 and (is_same_row(pair1, pair2) or \
            is_same_col(pair1, pair2) or is_same_square(pair1, pair2))]

def not_same_spot(pair1, pair2):
    return not (pair1[0] == pair2[0] and pair1[1] == pair2[1])

def is_same_row(pair1, pair2):
    row1 = pair1[0]
    row2 = pair2[0]
    return row1 == row2

def is_same_col(pair1, pair2):
    col1 = pair1[1]
    col2 = pair2[1]
    return col1 == col2

def is_same_square(pair1, pair2):
    rowDomain1 = pair1[0] / 3 * 3
    rowDomain2 = pair2[0] / 3 * 3
    if rowDomain1 != rowDomain2:
        return False
    colDomain1 = pair1[1] / 3 * 3
    colDomain2 = pair2[1] / 3 * 3
    return colDomain1 == colDomain2
    
# stores a board imported as txt file as a dictionary of integers
# each space corresponds to a coordinate in the board, and maps to a set of
# possible values that coordinate may contain, without breaking sudoku invariant
def read_board(path):
    dict = {}
    file = open(path, "r")
    row = 0
    for line in file:
        for val in xrange(9):
            digit = line[val]
            if digit != "*":
                dict[(row, val)] = set([int(digit)])
            else:
                dict[(row, val)] = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
        row += 1
    file.close()
    return dict

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    # removes all inconsistent/illegal values by cross examining two cell coordinates
    def remove_inconsistent_values(self, cell1, cell2):
        set2 = self.get_values(cell2)
        if len(set2) != 1:
            return False
        if cell1 == cell2 or (not is_same_row(cell1, cell2) and \
            not is_same_col(cell1, cell2) and not is_same_square(cell1, cell2)):
            return False
        x = min(set2) # get the only value in set 2
        if x in self.get_values(cell1):
            self.board[cell1].remove(x)
            return True
        return False

    # naive inference method that simply solves the game by removing inconsistent values
    # at first glance
    def infer_ac3(self):
        q = list(self.ARCS)
        while len(q) != 0:
            pair = q.pop(0)
            if self.remove_inconsistent_values(pair[0], pair[1]):
                added = []
                x_i = pair[0]
                otherPair = pair[1]
                # add all arcs same row to q
                row = x_i[0]
                for col in xrange(9):
                    if (row, col) != otherPair and (row, col) not in added:
                        q.append(((row, col), x_i))
                        added.append((row, col))
                # add all arcs same col to q
                col = x_i[1]
                for r in xrange(9):
                    if (r, col) != otherPair and (r, col) not in added:
                        q.append(((r, col), x_i))
                        added.append((r, col))
                # add all arcs same square to q
                squareStartR = row / 3 * 3
                squareStartC = col / 3 * 3
                for r in xrange(3):
                    for c in xrange(3):
                        if (r + squareStartR, c + squareStartC) != otherPair and \
                            (r + squareStartR, c + squareStartC) not in added:
                            q.append(((r + squareStartR, c + squareStartC), x_i))   
                            added.append((r + squareStartR, c + squareStartC))             

    # calls deduction helper and uses deduction with legal values in the same row/col/square
    # able to solve more problems than infer_arcs()
    def infer_improved(self):
        while True:
            self.infer_ac3()
            if self.deductionHelper():
                self.ARCS = sudoku_arcs() # replenish arcs
            else:
                break
    # finds more spots based on possibilities of same row/col/square
    # update dictionary accordingly
    def deductionHelper(self):
        hasDeduct = False
        for cell in self.CELLS:
            if len(self.get_values(cell)) > 1:
                for poss in self.get_values(cell):
                    if self.isOnlyValue(cell, poss):
                        hasDeduct = True
                        break
        return hasDeduct

    def isOnlyValue(self, coord, value):
        # is it the only possible that row?
        row = coord[0]
        hasAnother = False
        for c in xrange(9):
            if c != coord[1] and value in self.get_values((row, c)):
                hasAnother = True
                break
        if not hasAnother:
            self.board[coord] = set([value])
            return True                            
        # is it the only possible that col?
        col = coord[1]
        hasAnother = False
        for r in xrange(9):
            if r != coord[0] and value in self.get_values((r, col)):
                hasAnother = True
                break
        if not hasAnother:          
            self.board[coord] = set([value])
            return True
        # is it the only possible that square?
        squareStartR = coord[0] / 3 * 3
        squareStartC = coord[1] / 3 * 3   
        for r in xrange(3):
            for c in xrange(3):
                if (r + squareStartR, c + squareStartC) != coord and \
                        value in self.get_values((r + squareStartR, c + squareStartC)):
                    return False
        self.board[coord] = set([value])
        return True      

    # uses infer_improved() to solve harder sudoku problems by incorporating guessing 
    # when there are multiple values possible, and regular inference is insufficient
    def infer_with_guessing(self):
        self.infer_improved()
        self.board = self.backtracking()[1]
        
    def backtracking(self):
        # check if state is complete
        isComplete = True
        for cell in self.CELLS:
            if len(self.get_values(cell)) > 1:
                isComplete = False
                var = cell # an unassigned value
                break
        if isComplete:
            return (True, self.board)
        for poss in self.get_values(var): # for each possibility
            if self.isConsistent(var, poss):
                boardState = copy.deepcopy(self.board)
                self.board[var] = set([poss]) # make guess
                self.infer_improved()
                if not self.is_failure():  
                    result = self.backtracking()    
                    self.board = result[1]
                    if result[0]:
                        return (True, self.board)
                self.board = boardState
        return (False, self.board)

    def isConsistent(self, coord, value):
        # consistent in row?
        row = coord[0]
        for c in xrange(9):
            if c != coord[1] and len(self.get_values((row, c))) == 1 and \
                value in self.get_values((row, c)):
                return False                    
        # consistent that col?
        col = coord[1]
        for r in xrange(9):
            if r != coord[0] and len(self.get_values((r, col))) == 1 and \
                value in self.get_values((r, col)):
                return False
        # consistent that square
        squareStartR = coord[0] / 3 * 3
        squareStartC = coord[1] / 3 * 3   
        for r in xrange(3):
            for c in xrange(3):
                if (r + squareStartR, c + squareStartC) != coord and \
                    len(self.get_values((r + squareStartR, c + squareStartC))) == 1 and \
                    value in self.get_values((r + squareStartR, c + squareStartC)):
                    return False
        return True 
   
    def is_failure(self):
        for cell in self.CELLS:
            if len(self.get_values(cell)) == 0:
                return True
        return False
