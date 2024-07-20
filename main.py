from random import randint
from time import time as timenow
from copy import deepcopy
from typing import List

# List of characters that sudoku can use
AVAILABLE_CHARS = list("123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz?&!")

# Exceptions
class RequestOutOfBounds(Exception):
    """
    This exception is raised when trying to get character in sudoku outside the sudoku's 
    range (say, sudoku is 9x9, and you're trying to get character from 10x9).
    """

    def __init__(self):
        super().__init__("Requested element is out of sudoku's range.")

class IncorrectCharacter(Exception):
    """
    This exception is raised when trying to insert character that is not inside of sudoku's 
    character pool. (say, sudoku is 4x4, and player tries to insert number 5).
    """

    def __init__(self, char: str):
        super().__init__(f"Character \"{char}\" is not part of sudoku's character pool.")

class IsNotCharacter(Exception):
    """
    This exception is raised when string that user provides is longer than 1 character.
    """

    def __init__(self, string: str):
        super().__init__(f"Must request character, got string ({string}) instead.")

class IncorrectSize(Exception):
    """
    This exception is raised when sudoku's size prompt outside of the possible range.
    """

    def __init__(self, size: int):
        super().__init__(f"Sudoku size is invalid. From 2 to 8 expected, got {size}.")

class IllegalMove(Exception):
    """
    This exception is raised when user tries to perform illegal move in sudoku (ex. 
    inserting character that is already in square, line or column).
    """

    def __init__(self) -> None:
        super().__init__("Attempted to perform illegal move.")


# Sudoku class
class Sudoku():
    """
    Main class for sudoku game, holding necessary info inside and all useful functions 
    to modify or interact with the game.

    ### Variables
    size: Size of sudoku.

    sudoku: Sudoku-like list, consisting of sudoku line, sudoku square and square's inner line. 
    Or to put simply, list containing `size` amount of characters inside of list containing `size` 
    amount of square's inner lines inside of list containing `size` amount of such squares inside 
    of list containing `size` amount of these lines of squares.
    
    chars: List of characters that sudoku uses.

    gen_duration: Duration of sudoku's generation. Not set if sudoku was copied from architecture.
    """

    def __init__(self, size: int = 3, silent: bool = True, architecture: list = list()):
        """
        ### Arguments
        size: Sudoku's square's size. By default is 3, and this value will generate classic 9x9 sudoku. Must be from 2 to 8. \n
        silent: Whether sudoku's generation should not output "Generating" and "Generated in N seconds" message. By default True. \n
        architecture: Other Sudoku class' `.sudoku` list (or just sudoku-like list). When provided, does not generate new sudoku.
        """

        if len(architecture) > 0:
            self.sudoku = architecture
            self.size = len(self.sudoku)
            self.chars = AVAILABLE_CHARS[:self.size**2]

            return

        if not silent:
            print(f"Generating {size}x{size} sudoku...")

        if size not in range(2, 8):
            raise IncorrectSize(size)

        self.size = size
        self.chars = AVAILABLE_CHARS[:self.size**2]

        self._gen_start_timestamp = timenow()

        # Generation sequence

        self.sudoku = [                                         # Sudoku body
            [                                                   # Line
                [                                               # Square
                    ["#"] * self.size for _ in range(self.size) # Cells
                ] for _w in range(self.size)
            ] for _h in range(self.size)
        ]

        treshold = [deepcopy(self.chars) for _ in range(self.size**4)]

        line = 1
        column = 1
        i = 0

        while line < (self.size ** 2) + 1:
            while column < (self.size ** 2) + 1 and column > 0:
                pick = None
                
                # Repeat if pick is not chosen, violating sudoku's rules and treshold is not drained
                while pick is None or (self.is_violating(pick, column, line) and len(treshold[i]) > 1):
                    if len(treshold[i]) < 1:
                        treshold[i] = deepcopy(self.chars)

                    pick = treshold[i][randint(0, len(treshold[i])-1)]
                    treshold[i].pop(treshold[i].index(pick))

                # If no valid character can be inserted, go back a step
                if self.is_violating(pick, column, line):
                    self.insert_into_cell("#", column, line, True)

                    treshold[i] = deepcopy(self.chars)

                    column -= 1
                    i -= 1
                else:
                    self.insert_into_cell(pick, column, line, True)

                    column += 1
                    i += 1

            if column > 0:
                line += 1
                column = 1
            else:
                line -= 1
                column = self.size**2

        self._gen_finish_timestamp = timenow()
        self.gen_duration = self._gen_finish_timestamp - self._gen_start_timestamp

        if not silent:
            print(f"Generated sudoku in {round(self.gen_duration, 5)} seconds!")

    def get_cell(self, column: int, line: int) -> str:
        """
        Returns character that the cell on `column`x`line` position holds.

        ### Arguments
        column: Column where cell is positioned.
        line: Line where cell is positioned.

        ### Returns
        `str` character.
        """

        column -= 1
        line -= 1

        if line not in range(self.size**2) or column not in range(self.size**2):
            raise RequestOutOfBounds

        sudoku_line = self.sudoku[line // self.size]
        sudoku_square = sudoku_line[column // self.size]
        square_line = sudoku_square[line % self.size]

        cell = square_line[column % self.size]

        return cell
    
    def get_line_elements(self, line: int) -> List[str]:
        """
        Returns all characters in `line` line of sudoku.

        ### Arguments
        line: Sudoku's line from where we will get all values.

        ### Returns
        List containing all characters inside of a line.
        """

        line -= 1

        if line not in range(self.size**2):
            raise RequestOutOfBounds
        
        result = list()
        
        sudoku_line = self.sudoku[line // self.size]

        for sudoku_square in sudoku_line:
            square_line = sudoku_square[line % self.size]

            result += square_line

        return result
    
    def get_column_elements(self, column: int) -> List[str]:
        """
        Returns all characters in `column` column of sudoku.

        ### Arguments
        column: Sudoku's column from where we will get all values.

        ### Returns
        List containing all characters inside of a column.
        """

        column -= 1

        if column not in range(self.size**2):
            raise RequestOutOfBounds
        
        result = list()

        for sudoku_line in self.sudoku:
            sudoku_square = sudoku_line[column // self.size]
            
            for square_line in sudoku_square:
                result.append(square_line[column % self.size])

        return result
    
    def get_square_elements(self, square_column_no: int, square_line_no: int) -> List[str]:
        """
        Returns all characters inside sudoku's square determined by `square_column_no` column 
        and `square_line_no` line. 

        Not to be confused with normal columns and lines! `square_column_no` and 
        `square_line_no` are searching by SQUARES' column and line, NOT CELLS'.

        ### Arguments
        square_column_no: Column from where we will be getting square.
        square_line_no: Line from where we will be getting square.

        ### Returns
        List containing all characters inside of a square.
        """

        square_column_no -= 1
        square_line_no -= 1

        if square_column_no not in range(self.size) or square_line_no not in range(self.size):
            raise RequestOutOfBounds
        
        result = list()

        for square_line in self.sudoku[square_line_no][square_column_no]:
            result += square_line

        return result
    
    def to_matrix_string(self) -> str:
        """
        This function takes class' `.sudoku` variable and turns it into readable string. 
        This string will resemble how sudoku should look on paper.

        ### Returns
        String which resembles sudoku.
        """

        matrix_string = ""

        for line in range(1, (self.size**2) + 1):
            for column in range(1, (self.size**2) + 1):
                matrix_string += self.get_cell(column, line)

                if column % self.size == 0:
                    matrix_string += " "

            matrix_string += "\n"

            if line % self.size == 0:
                matrix_string += "\n"

        return matrix_string
    
    def is_violating(self, char: str, column: int, line: int) -> bool:
        """
        Function that checks whether `char` character inside of `column` column and `line` line 
        violates sudoku's rules (if character is already inside of square, line and column).

        Please note that it will not check whether this column and line is already filled with 
        another character.

        ### Arguments
        char: Character that will be checked.
        column: Column from where that character will be checked.
        line: Line from where that character will be checked.

        ### Returns
        Boolean. `True` if it violates the sudoku's rules, and `False` if not.
        """

        if len(char) != 1:
            raise IsNotCharacter(char)
        
        if char not in self.chars:
            raise IncorrectCharacter(char)

        line_elements = self.get_line_elements(line)
        column_elements = self.get_column_elements(column)
        square_elements = self.get_square_elements(((column - 1) // self.size) + 1, ((line - 1) // self.size) + 1)

        return any([char in line_elements, char in column_elements, char in square_elements])
    
    def insert_into_cell(self, char: str, column: int, line: int, no_check: bool = False):
        """
        Inserts and overwrites cell inside of a sudoku with new character with violation check. 

        ### Arguments
        char: Character that will be inserted.
        column: Column that the character will be inserted inside of.
        line: Line that the character will be inserted inside of.
        no_check: Whether violation check should be performed on that character. By default `False`, which means violation check WILL be performed.
        """

        if not no_check and self.is_violating(char, column, line):
            raise IllegalMove
        
        self.sudoku[(line - 1) // self.size][(column - 1) // self.size][(line - 1) % self.size][(column - 1) % self.size] = char

    def poke(self, amount: int) -> object:
        """
        Pokes holes inside of a new `Sudoku` class with the `.sudoku` variable being not fully 
        filled.

        ### Arguments
        amount: Amount of pokes new Sudoku should have

        ### Returns
        New `Sudoku` object with poked `.sudoku` variable.
        """

        new_sudoku = Sudoku(architecture=deepcopy(self.sudoku))
        poked_sudoku = new_sudoku.sudoku

        for _ in range(amount):
            target = None

            while target is None:
                sudoku_line = poked_sudoku[randint(0, len(poked_sudoku)-1)]
                sudoku_square = sudoku_line[randint(0, len(sudoku_line)-1)]
                square_line = sudoku_square[randint(0, len(sudoku_square)-1)]

                target = randint(0, len(square_line)-1)

                if square_line[target] != "#":
                    square_line[target] = "#"
                else:
                    target = None

        return new_sudoku
    
# Run a game if launched as a main file
if __name__ == "__main__":
    size = int(input("Enter sudoku's size (Classic Sudoku = 3): "))
    pokes = int(input("Choose an amount of cells you want to poke: "))

    s = Sudoku(size, False)
    unsolved_s = s.poke(pokes)

    print(f"\n{unsolved_s.to_matrix_string()}")

    while unsolved_s.sudoku != s.sudoku:
        try:
            char, pos = map(str, input("Choose character and its position [ex. 1 1x1]: ").split(sep=" "))
            column, line = map(int, pos.split(sep="x"))

            try:
                if s.get_cell(column, line) != char:
                    raise IllegalMove

                unsolved_s.insert_into_cell(char, column, line)
            except IllegalMove:
                print("Illegal move! Try again!\n")
            else:
                print(f"\n{unsolved_s.to_matrix_string()}")
        except Exception:
            print("Something went wrong! Try again!\n")

    print("CONGRATULATIONS!\nYou've solved sudoku!")