# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# Copyright **`(c)`** 2021 Giovanni Squillero `<squillero@polito.it>`
# [`https://github.com/squillero/computational-intelligence`](https://github.com/squillero/computational-intelligence)
# Free for personal or classroom use; see 'LICENCE.md' for details.
# %% [markdown]
# # Connect 4

# %%
from collections import Counter
import numpy as np
import math
import time


# %%
NUM_COLUMNS = 7
COLUMN_HEIGHT = 6
FOUR = 4

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = -1
EMPTY = 0

MINMAX_DEEP = 2
MC_SAMPLES = 30

# Board can be initiatilized with `board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)`
# Notez Bien: Connect 4 "columns" are actually NumPy "rows"

# ## Basic Functions


def valid_moves(board):
    """Returns columns where a disc may be played"""
    return [n for n in range(NUM_COLUMNS) if board[n, COLUMN_HEIGHT - 1] == 0]


def play(board, column, player):
    """Updates `board` as `player` drops a disc in `column`"""
    (index,) = next((i for i, v in np.ndenumerate(board[column]) if v == 0))
    board[column, index] = player


def take_back(board, column):
    """Updates `board` removing top disc from `column`"""
    (index,) = [i for i, v in np.ndenumerate(board[column]) if v != 0][-1]
    board[column, index] = 0


def four_in_a_row(board, player):
    """Checks if `player` has a 4-piece line"""
    return (
        any(
            all(board[c, r] == player)
            for c in range(NUM_COLUMNS)
            for r in (list(range(n, n + FOUR)) for n in range(COLUMN_HEIGHT - FOUR + 1))
        )
        or any(
            all(board[c, r] == player)
            for r in range(COLUMN_HEIGHT)
            for c in (list(range(n, n + FOUR)) for n in range(NUM_COLUMNS - FOUR + 1))
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co, co + FOUR))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
    )


def printBoard(board):
    board2 = np.rot90(board, 1)
    for i in range(NUM_COLUMNS):
        print(i+1, end="  ")
    print()
    for i in range(0, COLUMN_HEIGHT):
        for j in range(0, NUM_COLUMNS):
            if board2[i][j] == 0:
                print('-', end="  ")
            if board2[i][j] == 1:
                print('X', end="  ")
            if board2[i][j] == -1:
                print('O', end="  ")
        print()
    print()



def _mc(board, player):
    p = -player
    while valid_moves(board):
        p = -p
        c = np.random.choice(valid_moves(board))
        play(board, c, p)
        if four_in_a_row(board, p):
            return p
    return 0


def montecarlo(board, player):

    cnt = Counter(_mc(np.copy(board), player)
                  for _ in range(MC_SAMPLES))
    return (cnt[1] - cnt[-1]) / MC_SAMPLES


def eval_board(board, player):
    if four_in_a_row(board, 1):
        # Alice won
        return 1
    elif four_in_a_row(board, -1):
        # Bob won
        return -1
    else:
        # Not terminal, let's simulate...
        return montecarlo(board, player)


## Minmax

def is_terminal_node(board):
    return four_in_a_row(board, PLAYER_PIECE) or four_in_a_row(board, AI_PIECE) or len(valid_moves(board)) == 0


# Minmax with alpha-beta pruning (https://it.wikipedia.org/wiki/Potatura_alfa-beta#Pseudocodice)
def minmax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = valid_moves(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if four_in_a_row(board, AI_PIECE):
                return (None, 1)
            elif four_in_a_row(board, PLAYER_PIECE):
                return (None, -1)
            else:
                return (None, 0)
        else:  # Depth is zero
            return (None, eval_board(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            play(board, col, AI_PIECE)
            new_score = minmax(board, depth-1, alpha, beta, False)[1]
            take_back(board, col)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = +math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:

            play(board, col, PLAYER_PIECE)
            new_score = minmax(board, depth-1, alpha, beta, True)[1]
            take_back(board, col)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


#Game

game_over = False
move = -1

turn = np.random.randint(2)  # To choose randomly who will start the game
board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
printBoard(board)

while not game_over:

    if turn == PLAYER:  # PLAYER TURN
        player_moves = new_list = [x+1 for x in valid_moves(board)]
        while(move not in player_moves):
            print(f"Inserire numero colonna tra {player_moves}: ", end=" ")
            move = input()
            if move.isdigit():
                move = int(move)

        # HERE SHOULD HAVE THE MOVE CHOOSEN BY THE PLAYER
        print("Player chooses " + str(move) + " column!", end="\n\n")
        play(board, move-1, PLAYER_PIECE)
        printBoard(board)

        if four_in_a_row(board, PLAYER_PIECE):
            print("PLAYER 1 WINS!!!")
            game_over = True

        move = -1

    else:  # AI TURN
        print("AI: I'm thinking a good move...")
        start = time.time()

        best_move, minimax_score = minmax(board, 2, -math.inf, math.inf, True)
        end = time.time()

        print(
            f"AI chooses {best_move+1} column! (took {round(end-start,3)}s)", end="\n\n")
        play(board, best_move, AI_PIECE)
        printBoard(board)
        if four_in_a_row(board, AI_PIECE):
            print("AI WINS!!!")
            game_over = True

    turn += 1
    turn %= 2


