import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # LOOK Added For convenience, a set of ALL cells, no matter what the state
        self.total = {(x, y) for x in range(self.height) for y in range(self.width)}

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        #    based on the value of `cell` and `count`
        cells = set()

        # find neighbors for the current cell
        for row in range(cell[0] - 1, cell[0] + 2):
            for col in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (row, col) == cell:
                    continue
                # If cell is a known mine then decrease mines count and continue
                if (row, col) in self.mines:
                    count -= 1
                    continue
                # If we know that the cell is already safe then continue loop
                if (row, col) in self.safes:
                    continue

                # Update safes if cell in bounds
                if 0 <= row < self.height and 0 <= col < self.width:
                    cells.add((row, col))

        #cells = cells - self.safes
        #cells = cells - self.mines
        sentence = Sentence(cells, count)
        self.knowledge.append(sentence)
        #self.print_debug(cell, count)

        # 4) mark any additional cells as safe or as mines
        #    if it can be concluded based on the AI's knowledge base

        # Now update self.safes, self.mines with any new knowledge.
        self.update_safes_n_mines()

        # Remove depricated empty sentence objects 
        empty_sentence = Sentence(set(), 0)
        self.knowledge = [sentence for sentence in self.knowledge if sentence != empty_sentence]

        # 5) add any new sentences to the AI's knowledge base
        #    if they can be inferred from existing knowledge

        # Normalize the knowledge base (KB) by consolidating knowledge 
        # into fewer sentences (aka Elimination)
        for sentence1 in self.knowledge:
            # Looping through sentences - looking for possible subset
            for sentence2 in self.knowledge:
                # Ignore your EXACT self
                if sentence1 is sentence2:
                    continue

                #  Eliminate duplicates (differect sentences, same content)
                if sentence1 == sentence2:
                    self.knowledge.remove(sentence2)

                # If found subset, inference by resolution
                #if sentence1.cells.issubset(sentence2.cells):
                if sentence1.cells <= sentence2.cells:
                    # Remove the same cells from superset
                    result_set = sentence2.cells - sentence1.cells
                    # Subtract amount of mines
                    result_count = sentence2.count - sentence1.count
                    # Create new sentence
                    new_knowledge = Sentence(result_set, result_count)
                    # And add to the knowledge list only when it is new knowledge
                    if new_knowledge not in self.knowledge:
                        self.knowledge.append(new_knowledge)

        # Now update (again) self.safes, self.mines with any new knowledge.
        self.update_safes_n_mines()
        #self.print_debug(cell, count)


    def update_safes_n_mines(self):
        """ Update the top level safes and mines sets 
            using the latest knowledge
        """
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            for c in mines.copy():
                self.mark_mine(c)

            safes = sentence.known_safes()
            for c in safes.copy():
                self.mark_safe(c)


    def print_debug(self, cell, count):

        print("Knowledge:")
        for alpha in self.knowledge:
            print("Count: %d, " % alpha.count, end = " ")
            print(alpha.cells)
        print("Cell %d,%d count %d" % (cell[0],cell[1],count))
        print("Safes: ", self.safes - self.moves_made - self.mines)
        print("Mines: ", self.mines)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_cells = self.safes - self.moves_made - self.mines
        if len(safe_cells) > 0:
            return safe_cells.pop()
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_cells = self.total - self.moves_made - self.mines
        if len(random_cells) > 0:
            return random.choice(tuple(random_cells))
        else:
            return None
