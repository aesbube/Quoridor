from game_state import GameState
from searching import astar

def evaluate_position(game_state: GameState, is_maximizing, is_expectimax=False):
    player_one_distance = game_state.player_one_pos[0] // 2
    player_two_distance = (16 - game_state.player_two_pos[0]) // 2
    result = 0

    if is_maximizing:
        opponent_path_len, player_path_len = player_two_distance, player_one_distance
        if game_state.player_one_walls != 10 and game_state.player_two_walls != 10:
            previous = game_state.player_one
            game_state.player_one = True
            player_path_len = astar.path_exists(
                game_state, game_state.player_one_pos, True)[1]
            game_state.player_one = previous

        result += opponent_path_len
        result -= player_one_distance
        num = 100
        if player_path_len != 0:
            num = player_path_len
        result += round(100 / num, 2)

        num_1 = 50
        if player_two_distance != 0:
            num_1 = player_two_distance
        result -= round(50 / num_1, 2)

        result += (game_state.player_one_walls -
                   game_state.player_two_walls) 
        if game_state.player_one_pos[0] == 0:
            result += 100
        if player_path_len == 0 and game_state.player_one_pos[0] != 0:
            result -= 500
        return result

    else:
        opponent_path_len, player_path_len = player_one_distance, player_two_distance
        if game_state.player_one_walls != 10 and game_state.player_two_walls != 10:
            previous = game_state.player_one
            game_state.player_one = False
            player_path_len = astar.path_exists(
                game_state, game_state.player_two_pos, False)[1]
            game_state.player_one = previous

        if not is_expectimax:
            result += opponent_path_len
        else:
            result += 17 * opponent_path_len
        result -= player_two_distance
        num = 100
        if player_path_len != 0:
            num = player_path_len
        result += round(100 / num, 2)

        num_1 = 50
        if player_one_distance != 0:
            num_1 = player_one_distance
        result -= round(50 / num_1, 2)

        result += (game_state.player_two_walls -
                   game_state.player_one_walls)
        if game_state.player_two_pos[0] == 16:
            result += 100
        if player_path_len == 0 and game_state.player_two_pos[0] != 16:
            result -= 500
        return result
