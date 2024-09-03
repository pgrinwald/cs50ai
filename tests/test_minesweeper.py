#import sys

# Print the current search path
#print(sys.path)

# Add a custom directory to the search path
#sys.path.append('../minesweeper')

import pytest
from minesweeper import Minesweeper, Sentence, MinesweeperAI 

# Minesweeper Class Tests

def test_minesweeper_initialization():
    game = Minesweeper()
    assert game.height == 8
    assert game.width == 8
    assert len(game.mines) == 8
    assert all(not cell for row in game.board for cell in row)  # No mines initially
    assert game.mines_found == set()

def test_minesweeper_mine_placement():
    game = Minesweeper(height=5, width=5, mines=3)
    assert len(game.mines) == 3
    for mine in game.mines:
        assert 0 <= mine[0] < 5 and 0 <= mine[1] < 5  # Mines within bounds
        assert game.board[mine[0]][mine[1]]  # Mine cells are True

def test_minesweeper_is_mine():
    game = Minesweeper(height=3, width=3, mines=1)
    assert game.is_mine((0, 0)) == False  # Assuming (0, 0) doesn't have a mine
    assert any(game.is_mine(mine) for mine in game.mines)  # At least one mine is True

def test_minesweeper_nearby_mines():
    # Create a specific board configuration to test nearby_mines
    game = Minesweeper(height=4, width=4, mines=0)  # No mines initially
    game.board[1][1] = True  # Add a mine at (1, 1)
    game.board[2][2] = True  # Add another mine at (2, 2)

    assert game.nearby_mines((0, 0)) == 1  # Corner cell
    assert game.nearby_mines((1, 0)) == 1  # Edge cell
    assert game.nearby_mines((1, 2)) == 2  # Cell near both mines
    assert game.nearby_mines((3, 3)) == 1  # Another corner cell

def test_minesweeper_won():
    game = Minesweeper(height=3, width=3, mines=2)
    game.mines_found = {(0, 1), (2, 2)}  # Assume these are the actual mine locations
    assert game.won() == (game.mines == game.mines_found)

# Sentence Class Tests

def test_sentence_initialization():
    cells = {(0, 1), (1, 2), (2, 0)}
    count = 2
    sentence = Sentence(cells, count)
    assert sentence.cells == cells
    assert sentence.count == count

def test_sentence_equality():
    s1 = Sentence({(0, 0), (1, 1)}, 1)
    s2 = Sentence({(1, 1), (0, 0)}, 1)
    s3 = Sentence({(0, 0), (1, 1)}, 2)
    assert s1 == s2
    assert s1 != s3

def test_sentence_known_mines_and_safes():
    s1 = Sentence({(0, 0), (1, 1), (2, 2)}, 3)
    s2 = Sentence({(0, 0), (1, 1), (2, 2)}, 0)
    assert s1.known_mines() == {(0, 0), (1, 1), (2, 2)}
    assert s1.known_safes() == set()
    assert s2.known_mines() == set()
    assert s2.known_safes() == {(0, 0), (1, 1), (2, 2)}

def test_sentence_mark_mine_and_safe():
    s = Sentence({(0, 0), (1, 1), (2, 2)}, 2)
    s.mark_mine((1, 1))
    assert s.cells == {(0, 0), (2, 2)}
    assert s.count == 1
    s.mark_safe((0, 0))
    assert s.cells == {(2, 2)}
    assert s.count == 1

# MinesweeperAI Class Tests (These will be more involved due to the AI's logic)

def test_minesweeperai_initialization():
    ai = MinesweeperAI()
    assert ai.height == 8
    assert ai.width == 8
    assert ai.moves_made == set()
    assert ai.mines == set()
    assert ai.safes == set()
    assert ai.knowledge == []

# ... Add more tests for MinesweeperAI methods like add_knowledge, make_safe_move, make_random_move
# You'll likely need to create specific game scenarios and knowledge bases to test these thoroughly.

# Example test for add_knowledge (simplified)
def test_minesweeperai_add_knowledge_basic():
    ai = MinesweeperAI(height=3, width=3)
    ai.add_knowledge((1, 1), 0)  # Center cell with 0 nearby mines
    assert (1, 1) in ai.safes
    assert (1, 1) in ai.moves_made
    assert len(ai.knowledge) == 1
    assert ai.knowledge[0].cells == {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}
    assert ai.knowledge[0].count == 0

# ... More elaborate tests for add_knowledge, considering different cell positions, counts,
# and existing knowledge in the AI's knowledge base

if __name__ == "__main__":
    pytest.main()
