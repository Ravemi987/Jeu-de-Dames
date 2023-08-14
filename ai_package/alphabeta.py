from src.game import Game
from .ai import AI


def evaluate(game: Game, color='black'):
    opposite_color = game.get_opposite_color(color)
    #print(game.board.get_pawns_count(color), game.board.get_pawns_count(opposite_color))
    return game.board.get_pawns_count(color) - game.board.get_pawns_count(opposite_color) \
        + game.board.get_queens_count(color) * 3 - game.board.get_queens_count(opposite_color) * 3

def AlphaBeta(game: Game, depth, alpha, beta, is_max):
    if depth < 1 or game.is_finished:
        return evaluate(game), game

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game), game

    if is_max:
        best_score = float('-inf')
        best_move = None
        for move in valid_moves:
            new_game = AI.simulate_move(move, game)
            score, _ = AlphaBeta(new_game, depth - 1, alpha, beta, False)
            if score > best_score:
                best_score = score
                best_move = move
                if best_score > alpha:
                    alpha = best_score
                    # élagage beta
                    if alpha >= beta:
                        break
    else:
        best_score = float('inf')
        best_move = None
        for move in valid_moves:
            new_game = AI.simulate_move(move, game)
            score, _ = AlphaBeta(new_game, depth - 1, alpha, beta, True)
            if score < best_score:
                best_score = score
                best_move = move
                if best_score < beta:
                    beta = best_score
                    # élagage alpha
                    if alpha >= beta:
                        break
    return best_score, best_move
