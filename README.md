# ai_sudoku_solver_constraint_satisfaction

This project simulates an automatic sudoku solver using paradigms of constraint satisfaction.

Each row represents a row in the sudoku game, and digits(1-9) indicate pre-filled values of the puzzle, and * indicates empty space.

Check out the principles of CSP here: https://en.wikipedia.org/wiki/Constraint_satisfaction_problem

# There are 3 layers to this sudoku solver:

In each version, the board is solved by manipulating values within the dictionary (self.board), and a correct board will be returned with all coordinates mapping to a single integer value, if the input is solvable.

1. Simple deduction with infer_ac3() that eliminates values based on same row/col/square. Solves a limited number of sudoku games by obvious process of elimination (files initialized as 'easy')

2. A build-up from layer-1 with infer_improved(). Solves by repetitively calling infer_ac3() and in between calls eliminates other possible values by comparing all values within a single square/row/col. (files initialized as 'medium')
  For example:
    If the given row is of possible values (1, 3), (2), (6), (7, 8), (5), (9, 8), (4, 3), (7, 9), (1, 2). We know that by rules of Sudoku, column 1, (1, 3), can only be 3 as no other columns in the row can contain the value 3. This goes beyond layer 1 and can help fill in values in between calls of infer_ac3().
    
3. A build-up from layer-2 with infer_with_guessing(). Solves by repetitively calling infer_improved, and in between calls eliminates other values by recursively guess values from a list of possible values, and backtracking if a failure state is encountered.
  For example:
    If the given row is of values (1, 3), (2), (6), (7, 8, 6), (5), (9, 8, 6), (4, 3, 9), (7, 9), (3, 2, 4). We will pick the easiest coordinate to guess from (column 1 with (1, 3)), and recursively guess using either 1 or 3 to solve the puzzle, and backtrack if the answer is incorrect (resulting in a conflicting board).
    
It is important to note that since the possibility of an unsolvable may exist, this feature is not strictly implemented, thus an incorrect board input would result in the algorithm returning a conflicting/partially filled board.

# Running the program:
Preparing puzzle files in the same directory

Call from terminal: Python sudoku_solver.py
