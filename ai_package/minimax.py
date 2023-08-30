from src.game import Game
from .ai import AI
import time


MAX_TIME = 2000
nodes = 0


def evaluate(game: Game, color='black'):
    opposite_color = game.get_opposite_color(color)
    return game.board.get_number_of_pawns(color) - game.board.get_number_of_pawns(opposite_color) \
        + game.board.get_number_of_queens(color) * 3 - game.board.get_number_of_queens(opposite_color) * 3


def MiniMax_Max(game: Game, depth):
    global nodes
    nodes += 1
    start_time = time.time()

    if depth < 1 or game.is_finished:
        return evaluate(game), game, depth, nodes

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game), game, depth, nodes

    best_score = float('-inf')
    best_move = None
    depth -= 1

    for move in valid_moves:
        new_game = AI.simulate_move(move, game)
        score, *_ = MiniMax_Min(new_game, depth)
        if score > best_score:
            best_score = score
            best_move = move
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_TIME:
            return best_score, best_move, depth, nodes
        
    return best_score, best_move, depth, nodes


def MiniMax_Min(game: Game, depth):
    start_time = time.time()

    if depth < 1 or game.is_finished:
        return evaluate(game), game, depth, nodes

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game), game, depth, nodes
        
    best_score = float('inf')
    best_move = None
    depth -= 1

    for move in valid_moves:
        new_game = AI.simulate_move(move, game)
        score, *_ = MiniMax_Max(new_game, depth)
        if score < best_score:
            best_score = score
            best_move = move
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_TIME:
            return best_score, best_move, depth, nodes
    
    return best_score, best_move, depth, nodes


MAIN_FUNC = MiniMax_Max
