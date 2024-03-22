"""
Tic Tac Toe Player
"""

import math
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player (X or O) who has the next turn on a board.
    """
    xcount = 0
    ocount = 0
    for row in range(len(board)):
      for col in range(len(board[row])):
        if board[row][col] == X:
          xcount += 1
        elif board[row][col] == O:
          ocount += 1

    if xcount > ocount:
      return O
    else:
      return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    options = set()
    for row in range(len(board)):
      for col in range(len(board[row])):
        if board[row][col] == EMPTY:
            options.add((row, col))
    return options


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    playr = player(board)
    res = initial_state()

    if terminal(board):
        raise ValueError("Game over.")
    elif action not in actions(board):
        raise ValueError("Invalid action.")

    # Overlay the previous boars state
    for row in range(len(board)):
      for col in range(len(board[row])):
        res[row][col] = board[row][col]

    # Make the move, return the result
    if board[action[0]][action[1]] == EMPTY:
      res[action[0]][action[1]] = playr
      return res
    else:
      raise NameError("Invalid (%d, %d) move for player %s as the cell is already occupied!" \
              % (int(action[0]), int(action[1]), playr))


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    ## First the rows
    for row in range(len(board)):
      if all(i == board[row][0] for i in board[row]) and board[row][0]:
        return board[row][0]

    ## Next, the colums
    for col in range(len(board[0])):
      list = []
      for row in range(len(board)):
        list.append(board[row][col])
      if all(i == list[0] for i in list) and list[0]:
        return list[0]

    ## Next, the diagonals:
    ## top,left -> bottom,right 
    list = []
    col = 0
    for row in range(len(board)):
      list.append(board[row][col])
      col += 1
    if all(i == list[0] for i in list) and list[0]:
      return list[0]

    ## bottom,left -> top,right
    list = []
    col = len(board[0])-1
    for row in range(len(board)):
      list.append(board[row][col])
      col -= 1
    if all(i == list[0] for i in list) and list[0]:
      return list[0]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    val = winner(board)
    if val:
      return True   ## We have a winner
    else:
      for row in range(len(board)):
        if any(i == EMPTY for i in board[row]):
          return False    ## Found at least one empty cell

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    val = winner(board)
    if val:
      if val == X:
        return 1
      if val == O:
        return -1
      
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
      return None

    # If empty board is provided as input, return a random first move.
    if board == initial_state():
      return (random.randint(0,2),random.randint(0,2))

    playr = player(board)

    if playr == X:
      bestmove = None
      bestscore = -math.inf
      for action in actions(board):
        val = minvalue(result(board, action))

        if val > bestscore:
          bestscore = val
          bestmove = action
    elif playr == O:
      bestmove = None
      bestscore = math.inf
      for action in actions(board):
        val = maxvalue(result(board, action))

        if val < bestscore:
          bestscore = val
          bestmove = action

    return bestmove


def maxvalue(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
      return utility(board)

    val = -math.inf
    for action in actions(board):
      val = max(val, minvalue(result(board, action)))

    return val
      
       
def minvalue(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
      return utility(board)

    val = math.inf
    for action in actions(board):
      val = min(val, maxvalue(result(board, action)))

    return val

