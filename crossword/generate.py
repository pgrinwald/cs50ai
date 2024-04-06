import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for domain in self.domains:
            self.domains[domain] = {word for word in self.domains[domain] if len(word) == domain.length }

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # Check if two variables overlap
        if self.crossword.overlaps[x, y]:
            i, j = self.crossword.overlaps[x, y]
            # Check if there is possible value for y
            for wordx in self.domains[x].copy():
                counter = 0
                for wordy in self.domains[y]:
                    if wordx[i] == wordy[j]:
                        break
                    counter += 1
                # If there is no possible value for y
                if counter == len(self.domains[y]):
                    self.domains[x].remove(wordx)
                    revised= True
            return revised
        else:
            return False


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            # Queue all arcs in the CSP
            arcs = []
            for vars, cell in self.crossword.overlaps.items():
                if cell != None:
                    arcs.append(vars)

        while len(arcs) != 0:
            # De-queue an arc
            X, Y = arcs.pop()
            if self.revise(X, Y):           # if domain of X arc-consistent w.r.t. to Y
                if len(self.domains[X]) == 0:
                    return False            # problem cannot be solved

                # for each neighbor z to X, excluding Y, add (z,X) to queue
                neighbors = self.crossword.neighbors(X)
                for neighbor in neighbors:
                    if neighbor != Y:
                        arcs.append((neighbor, X))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.crossword.variables) == len(assignment.keys()):
            for value in self.crossword.variables:
                # Check if variable is assigned a value
                if assignment[value] is None:
                    return False
            return True
        return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var1 in assignment:
            # All values (words) are the correct length
            if len(assignment[var1]) != var1.length:
                return False
            # all values are distinct
            for var2 in assignment:
                if var1 == var2:
                    continue
                if assignment[var1] == assignment[var2]:
                    return False
            # No conflicts between neighbors
            for neighbor in self.crossword.neighbors(var1):
                cell = self.crossword.overlaps[var1, neighbor]
                if neighbor not in assignment:
                    continue
                if assignment[var1][cell[0]] != assignment[neighbor][cell[1]]:
                    return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Get a list of all var's neighbors
        neighbors = self.crossword.neighbors(var)
        domain_values = []

        # If there are neightbors
        if neighbors:
            for word in self.domains[var]:
                score = 0
                for neighbor in neighbors:
                    # If neighbor is not alreaady assigned
                    if neighbor not in list(assignment.keys()):
                        i, j = self.crossword.overlaps[var, neighbor]
                        # for each neighbor, calculate a higher score the more
                        # non-overlapping words in the doamin
                        for neighbor_word in self.domains[neighbor]:
                            if word[i] != neighbor_word[j]:
                                score += 1
                domain_values.append((word, score))
        else:
            for word in self.domains[var]:
                domain_values.append((word, 0))

        # Sort the list by n
        domain_values.sort(key=lambda var: var[1])

        domain = []
        # Get a list of words only
        for word in domain_values.copy():
            domain.append(word[0])

        return domain


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        scores = []

        # load up a list with tuples (variable, num_remaining_words, num_neigbors
        for var in self.crossword.variables:
            if var not in list(assignment.keys()):
                if self.crossword.neighbors(var):
                    scores.append((var, len(self.domains[var]), len(self.crossword.neighbors(var))))
                else:
                    scores.append((var, len(self.domains[var]), 0))

        # Sort by num_remaining_words, num_neighbors, return 
        # the variable
        scores = sorted(scores, key=lambda vars: vars[2], reverse=True)
        scores = sorted(scores, key=lambda vars: vars[1])
        var = scores.pop(0)
        return var[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        # If not complete
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            # Add value to assignment
            assignment[var] = value
            # If new assignment is consistent
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            # If new assignment is not consistent
            assignment.pop(var)


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
