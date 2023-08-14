def _get_piece_moves(self, player_turn, piece: Piece, start_position, last_direction, skipped_list,
                possible_directions, current_row, current_col):
    """
    Récupère l'ensemble des déplacements possibles d'une pièce.
    La valeur de retour est une liste d'objets de la classe 'Move.'
    """
    # Liste qui va contenir l'ensembles des déplacements de types 'Move'
    piece_moves = []
    for current_direction in possible_directions:
        # On vérifie que l'on ne revient pas "en arrière" ce qui pourrait provoquer des cas de récursion infinie.
        if current_direction == (-1 * last_direction[0], -1 * last_direction[1]):
            continue

        dx, dy = current_direction
        target_row, target_col = current_row + dx, current_col + dy

        # Vérification pour un potentiel déplacement libre
        if last_direction == (0, 0) and self.is_in_range_and_empty(target_row, target_col):
            is_free_move_available, piece_moves, target_row, target_col = self._check_free_moves(
                player_turn, piece, dx, dy, piece_moves, target_row, target_col
            )
            if is_free_move_available:
                continue

        # On vérifie si l'on passe dans le cas d'arrêt ou dans le cas récursif
        can_continue_recurion, updated_coords = self._check_recursion_stop_condition(
            current_direction, piece, target_row, target_col
        )

        if not can_continue_recurion:
            continue
        else:
            target_row, target_col = updated_coords
            new_target_row, new_target_col = target_row + dx, target_col + dy
            
            if self.is_in_range_and_empty(new_target_row, new_target_col) and (new_target_row, new_target_col) != start_position:
                # On met à jour la dernière direction parcourue et la liste des pièces capturées.
                new_last_dir = current_direction
                skipped = skipped_list + [(target_row, target_col)]
                # On ajoute le nouveau déplacement et on appelle la fonction récursivement
                piece_moves.append(Move(player_turn, piece, (piece.row, piece.col), (new_target_row, new_target_col), skipped))
                if piece.is_queen():
                    while self.is_in_range_and_empty(new_target_row, new_target_col) and (new_target_row, new_target_col) != start_position:
                        piece_moves.extend(self._get_piece_moves(player_turn, piece, start_position, new_last_dir, skipped,
                                                    possible_directions, new_target_row, new_target_col))
                        new_target_row += dx
                        new_target_col += dy
                else:
                    piece_moves.extend(self._get_piece_moves(player_turn, piece, start_position, new_last_dir, skipped,
                                                    possible_directions, new_target_row, new_target_col))
    return piece_moves
