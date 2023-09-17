from src.game import Game
from .ai import AI
import time


MAX_TIME = 5 # arrêt en largeur
nodes = 0


def evaluate(game: Game, color):
    opposite_color = game.get_opposite_color(color)
    return game.board.get_number_of_pawns(color) - game.board.get_number_of_pawns(opposite_color) \
        + game.board.get_number_of_queens(color) * 3 - game.board.get_number_of_queens(opposite_color) * 3


def AlphaBeta(game: Game, color, depth, alpha, beta, is_max):
    global nodes
    nodes += 1
    start_time = time.time()
    
    if depth < 1 or game.is_finished:
        return evaluate(game, color), game, depth, nodes

    valid_moves = game.valid_moves
    if len(valid_moves) == 0:
        return evaluate(game, color), game, depth, nodes

    if is_max:
        best_score = float('-inf')
        best_move = None
        depth -= 1

        for move in valid_moves:
            new_game = AI.simulate_move(move, game)
            score, *_ = AlphaBeta(new_game, color, depth, alpha, beta, False)
            if score > best_score:
                best_score = score
                best_move = move
                if best_score > alpha:
                    alpha = best_score
                    # élagage beta
                    if alpha >= beta:
                        break
            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_TIME:
                return best_score, best_move, depth, nodes
    else:
        best_score = float('inf')
        best_move = None
        depth -= 1

        for move in valid_moves:
            new_game = AI.simulate_move(move, game)
            score, *_ = AlphaBeta(new_game, color, depth, alpha, beta, True)
            if score < best_score:
                best_score = score
                best_move = move
                if best_score < beta:
                    beta = best_score
                    # élagage alpha
                    if alpha >= beta:
                        break
            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_TIME:
                return best_score, best_move, depth, nodes
    
    return best_score, best_move, depth, nodes


MAIN_FUNC = AlphaBeta
