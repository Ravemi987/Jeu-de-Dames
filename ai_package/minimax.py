from src.game import Game
from .ai import AI


def evaluate(game: Game, color='black'):
    opposite_color = game.get_opposite_color(color)
    return game.board.get_pawns_count(color) - game.board.get_pawns_count(opposite_color) \
        + game.board.get_queens_count(color) * 3 - game.board.get_queens_count(opposite_color) * 3

def MiniMax_Max(game: Game, depth):
    if depth < 1 or game.is_finished:
        return evaluate(game), game

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game), game

    best_score = float('-inf')
    best_move = None

    for move in valid_moves:
        new_game = AI.simulate_move(move, game)
        score, _ = MiniMax_Min(new_game, depth - 1)
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_score, best_move

def MiniMax_Min(game: Game, depth):
    if depth < 1 or game.is_finished:
        return evaluate(game), game

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game), game
        
    best_score = float('inf')
    best_move = None

    for move in valid_moves:
        new_game = AI.simulate_move(move, game)
        score, _ = MiniMax_Max(new_game, depth - 1)
        if score < best_score:
            best_score = score
            best_move = move
    
    return best_score, best_move
