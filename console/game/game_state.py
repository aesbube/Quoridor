import numpy as np
from utils.stuff import Stuff
from utils.stuff import BoardPieceStat
from copy import copy
from searching import astar


class GameState:
    def __init__(self, initialization=True):
        self.rows = 17  # 9 rows for movement of pawn + 8 rows for wall placement
        self.cols = 17  # 9 columns for movement of pawn + 8 columns for wall placement
        self.player_one_walls = 10
        self.player_two_walls = 10
        self.turn = True

        if initialization:
            self.player_one_pos = (16, 8)
            self.player_two_pos = (0, 8)
            self.board = np.zeros((289,), dtype=int)
            self.setup_board()

        self.moves = {
            'up': (2, 0),
            'down': (-2, 0),
            'left': (0, -2),
            'right': (0, 2),
        }

        self.wall_places = {
            'up': (1, 0),
            'down': (-1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

    def setup_board(self):

        # Initializing the pawn and wall cells

        for row in range(self.rows):
            for col in range(self.cols):
                if row % 2 == 0 and col % 2 == 0:
                    self.board[row * self.rows +
                               col] = BoardPieceStat.FREE_PAWN
                else:
                    self.board[row * self.rows +
                               col] = BoardPieceStat.FREE_WALL

        # Initializing starting positions for each player's pawn

        self.board[self.player_one_pos[0] * self.rows +
                   self.player_one_pos[1]] = BoardPieceStat.OCCUPIED_BY_PLAYER_ONE
        self.board[self.player_two_pos[0] * self.rows +
                   self.player_two_pos[1]] = BoardPieceStat.OCCUPIED_BY_PLAYER_TWO

    def test_state(self):
        state = copy(self)
        state.player_one_pos = copy(self.player_one_pos)
        state.player_two_pos = copy(self.player_two_pos)
        state.board = copy(self.board)
        return state

    def get_id(self, x, y):
        return x * self.cols + y

    def player_stats(self):
        print(f'Player 1 remaining walls: {
              self.player_one_walls}   {Stuff.PLAYER_ONE}')
        print(f'Player 2 remaining walls: {
              self.player_two_walls}   {Stuff.PLAYER_TWO}')

    def print_board(self):
        player_positions = "|"
        wall_positions = "\u2500" * 5 + "o"
        ascii_capital = 65
        ascii_lower = 98

        # Printing the letters for the rows

        print("  ", end="")

        for row in range(self.rows):
            if row % 2 == 0:
                print(f'  {chr(ascii_capital)}  ', end="")
                ascii_capital += 2
            else:
                print(Stuff.WALL_COLOR + chr(ascii_lower) +
                      Stuff.COLOR_RESET, end="")
                ascii_lower += 2

        ascii_capital = 65
        ascii_lower = 98

        # Printing the letters for the columns and the grid\

        for col in range(self.cols):
            if col % 2 == 0:
                print(f'\n{chr(ascii_capital)} ', end="")
                ascii_capital = ascii_capital + 2
                for place in range(self.cols):
                    id = self.get_id(col, place)
                    if self.board[id] == BoardPieceStat.FREE_PAWN:
                        print(f'     ', end="")
                    elif self.board[id] == BoardPieceStat.FREE_WALL:
                        print(f'{player_positions}', end="")
                    elif self.board[id] == BoardPieceStat.OCCUPIED_BY_PLAYER_ONE:
                        print(f'  {Stuff.PLAYER_ONE} ', end="")
                    elif self.board[id] == BoardPieceStat.OCCUPIED_BY_PLAYER_TWO:
                        print(f'  {Stuff.PLAYER_TWO} ', end="")
                    else:
                        print(Stuff.WALL_COLOR + player_positions +
                              Stuff.COLOR_RESET, end="")

            else:
                print("\n" + Stuff.WALL_COLOR + chr(ascii_lower) +
                      " " + Stuff.COLOR_RESET, end="")
                ascii_lower = ascii_lower + 2
                for place in range(self.cols):
                    id = self.get_id(col, place)
                    if place % 2 == 0 and place < 16:
                        if self.board[id] == BoardPieceStat.OCCUPIED_WALL:
                            print(Stuff.WALL_COLOR + wall_positions[:5] +
                                  Stuff.COLOR_RESET + wall_positions[5], end="")
                        else:
                            print(f'{wall_positions}', end="")
                    elif place == 16:
                        if self.board[id] == BoardPieceStat.OCCUPIED_WALL:
                            print(Stuff.WALL_COLOR + wall_positions[:5] +
                                  Stuff.COLOR_RESET, end="")
                        else:
                            print(f'{wall_positions[:5]}', end="")
                    else:
                        self.board[id] == None

        print()

    def is_place_free(self, place):
        if place is not None:
            x, y = place
            id = self.get_id(x, y)
            if id > 288:
                return False
            return self.board[id] == BoardPieceStat.FREE_PAWN or self.board[id] == BoardPieceStat.FREE_WALL

    def is_diagonal_or_jump(self):
        check_for_wall = None
        for place in self.moves.values():
            opponent = (self.player_one_pos[0] + place[0],
                        self.player_one_pos[1] + place[1])
            if opponent == self.player_one_pos or opponent == self.player_two_pos:
                if self.player_one_pos[0] == opponent[0]:
                    if opponent[1] > self.player_one_pos[1]:
                        check_for_wall = (opponent[0], opponent[1] - 1)
                    else:
                        check_for_wall = (opponent[0], opponent[1] + 1)
                elif self.player_one_pos[1] == opponent[1]:
                    if opponent[0] > self.player_one_pos[0]:
                        check_for_wall = (opponent[0] - 1, opponent[1])
                    else:
                        check_for_wall = (opponent[0] + 1, opponent[1])

        return self.is_place_free(check_for_wall)

    def is_goal(self):
        return self.player_one_pos[0] == 0 or self.player_two_pos[0] == 16

    def move_pawn(self, move):
        x, y = move
        id = self.get_id(x, y)
        if move in self.possible_moves_pawn():
            if self.turn:
                old_x, old_y = self.player_one_pos
                self.player_one_pos = (x, y)
                self.board[id] = BoardPieceStat.OCCUPIED_BY_PLAYER_ONE
                self.turn = False
            else:
                old_x, old_y = self.player_two_pos
                self.player_two_pos = (x, y)
                self.board[id] = BoardPieceStat.OCCUPIED_BY_PLAYER_TWO
                self.turn = True
            self.board[self.get_id(old_x, old_y)] = BoardPieceStat.FREE_PAWN
            return True
        else:
            print(f'The move {
                  move} is not valid check out the list of possible moves!')
            return False

    def occupy_by_wall(self, place):
        if place[0] % 2 == 0:
            if place[0] < 15:
                self.board[self.get_id(place[0], place[1])] = self.board[self.get_id(
                    place[0] + 2, place[1])] = BoardPieceStat.OCCUPIED_WALL
            else:
                self.board[self.get_id(place[0], place[1])] = self.board[self.get_id(
                    place[0] - 2, place[1])] = BoardPieceStat.OCCUPIED_WALL

        # Placement of horizontal walls

        else:
            if place[1] < 15:
                self.board[self.get_id(place[0], place[1])] = self.board[self.get_id(
                    place[0], place[1] + 2)] = BoardPieceStat.OCCUPIED_WALL
            else:
                self.board[self.get_id(place[0], place[1])] = self.board[self.get_id(
                    place[0], place[1] - 2)] = BoardPieceStat.OCCUPIED_WALL

    def place_wall(self, place):
        if self.check_valid_wall(place):
            self.occupy_by_wall(place)
            if self.turn:
                self.player_one_walls -= 1
                self.turn = False
            else:
                self.player_two_walls -= 1
                self.turn = True
            return True
        else:
            wall = ""
            if self.get_wall_coords(place) is not None:
                wall = self.get_wall_coords(place)
            print(f'The wall {wall} is not valid!')
            return False

    def possible_moves_wall(self, include_state=False):
        if (self.turn and self.player_one_walls == 0) or (not self.turn and self.player_two_walls == 0):
            return []

        moves = []
        
        for row in range(0, 16, 2):
            for col in range(1, 16, 2):
                if self.check_valid_wall((row, col)):
                    state = self.test_state()
                    state.occupy_by_wall((row, col))
                    moves.append((row, col)) if not include_state else moves.append(
                        ((row, col), state))

        for row in range(1, 16, 2):
            for col in range(0, 16, 2):
                if self.check_valid_wall((row, col)):
                    state = self.test_state()
                    state.occupy_by_wall((row, col))
                    moves.append((row, col)) if not include_state else moves.append(
                        ((row, col), state))
        return moves

    def occupy_by_player(self, place):
        x, y = place
        id = self.get_id(x, y)
        if self.turn:
            curr_location = self.get_id(self.player_one_pos[0], self.player_one_pos[1])
            self.board[curr_location] = BoardPieceStat.FREE_PAWN
            self.board[id] = BoardPieceStat.OCCUPIED_BY_PLAYER_ONE
        else:
            curr_location = self.get_id(self.player_two_pos[0], self.player_two_pos[1])
            self.board[curr_location] = BoardPieceStat.FREE_PAWN
            self.board[id] = BoardPieceStat.OCCUPIED_BY_PLAYER_TWO
    
    def possible_moves_pawn(self, include_state=False):
        old_place = self.player_one_pos if self.turn else self.player_two_pos

        moves = []
        for wall, pawn in zip(self.wall_places.values(), self.moves.values()):
            wall_place = (old_place[0] + wall[0], old_place[1] + wall[1])
            pawn_place = (old_place[0] + pawn[0], old_place[1] + pawn[1])
            if self.check_valid_pawn(pawn_place) and self.is_place_free(wall_place):
                state = self.test_state()
                state.occupy_by_player(pawn_place)
                moves.append(pawn_place) if not include_state else moves.append(
                    (pawn_place, state))
        if self.is_diagonal_or_jump():
            opp=self.get_opp_location()
            if self.can_go_straight(opp):
                if old_place[0] == opp[0]:
                    if opp[1] > old_place[1]:
                        state=self.test_state()
                        state.occupy_by_player((opp[0], opp[1] + 2))
                        moves.append((opp[0], opp[1] + 2)) if not include_state else moves.append(
                            ((opp[0], opp[1] + 2), state)
                        )
                    else:
                        state=self.test_state()
                        state.occupy_by_player((opp[0], opp[1] - 2))
                        moves.append((opp[0], opp[1] - 2)) if not include_state else moves.append(
                            ((opp[0], opp[1] - 2), state))
                elif old_place[1] == opp[1]:
                    if opp[0] > old_place[0]:
                        state=self.test_state()
                        state.occupy_by_player((opp[0] + 2, opp[1]))
                        moves.append((opp[0] + 2, opp[1])) if not include_state else moves.append(
                            ((opp[0] + 2, opp[1]), state)
                        )
                    else:
                        state=self.test_state()
                        state.occupy_by_player((opp[0] - 2, opp[1]))
                        moves.append((opp[0] - 2, opp[1])) if not include_state else moves.append(
                            ((opp[0] - 2, opp[1]), state)
                        )
            else:
                for wall, pawn in zip(self.wall_places.values(), self.moves.values()):
                    wall_place=(opp[0] + wall[0], opp[1] + wall[1])
                    pawn_place=(opp[0] + pawn[0], opp[1] + pawn[1])
                    if self.check_valid_pawn(pawn_place) and self.is_place_free(wall_place):
                        state=self.test_state()
                        state.occupy_by_player(pawn_place)
                        moves.append((pawn_place)) if not include_state else moves.append(
                            (pawn_place, state)
                        )
        return moves

    def all_possible_moves(self, include_state=False):
        return self.possible_moves_pawn(include_state) + self.possible_moves_wall(include_state)

    def can_go_straight(self, place):
        player=self.player_one_pos if self.turn else self.player_two_pos
        if player[0] == place[0]:
            if place[1] > player[1]:
                check_for_wall=(place[0], place[1] + 1)
            else:
                check_for_wall=(place[0], place[1] - 1)
        elif player[1] == place[1]:
            if place[0] > player[0]:
                check_for_wall=(place[0] + 1, place[1])
            else:
                check_for_wall=(place[0] - 1, place[1])
        return self.is_place_free(check_for_wall)

    def get_opp_location(self):
        if self.turn:
            return self.player_two_pos
        return self.player_one_pos

    def check_valid_pawn(self, place):
        x, y=place[0], place[1]
        id=self.get_id(x, y)
        if x % 2 == 1 or y % 2 == 1 or x < 0 or x > 16 or y < 0 or y > 16 or self.board[id] != BoardPieceStat.FREE_PAWN:
            return False
        return True

    def get_wall_coords(self, place):
        if place[0] % 2 == 0 and place[1] % 2 == 1:
            if place[0] < 15:
                return ((place[0], place[1]), (place[0] + 2, place[1]))
            else:
                return ((place[0], place[1]), (place[0] - 2, place[1]))
        elif place[0] % 2 == 1 and place[1] % 2 == 0:
            if place[1] < 15:
                return ((place[0], place[1]), (place[0], place[1] + 2))
            else:
                return ((place[0], place[1]), (place[0], place[1] - 2))

    def check_valid_wall(self, place):
        if self.turn and self.player_one_walls == 0:
            return False
        elif not self.turn and self.player_two_walls == 0:
            return False

        x, y=place[0], place[1]

        # Vertical wall check
        if x % 2 == 0 and y % 2 == 1:
            if x < 15:
                # Check the wall placement itself
                if not self.is_place_free((x, y)) or not self.is_place_free((x + 2, y)):
                    return False
                # Check for intersecting horizontal wall
                if not self.is_place_free((x + 1, y + 1)) and not self.is_place_free((x + 1, y - 1)):
                    return False
            else:
                # Check the wall placement itself
                if not self.is_place_free((x, y)) or not self.is_place_free((x - 2, y)):
                    return False
                # Check for intersecting horizontal wall
                if not self.is_place_free((x - 1, y - 1)) and not self.is_place_free((x - 1, y + 1)):
                    return False

        # Horizontal wall check
        elif x % 2 == 1 and y % 2 == 0:
            if y < 15:
                # Check the wall placement itself
                if not self.is_place_free((x, y)) or not self.is_place_free((x, y + 2)):
                    return False
                # Check for intersecting vertical wall
                if not self.is_place_free((x + 1, y + 1)) and not self.is_place_free((x - 1, y + 1)):
                    return False
            else:
                # Check the wall placement itself
                if not self.is_place_free((x, y)) or not self.is_place_free((x, y - 2)):
                    return False
                # Check for intersecting vertical wall
                if not self.is_place_free((x - 1, y - 1)) and not self.is_place_free((x + 1, y - 1)):
                    return False
        else:
            return False
        test_state=self.test_state()
        test_state.occupy_by_wall(place)
        player_one_can_reach=astar.path_exists(
            test_state, test_state.player_one_pos, True)
        player_two_can_reach=astar.path_exists(
            test_state, test_state.player_two_pos, False)
        return player_one_can_reach and player_two_can_reach

    def get_winner(self):
        if self.player_one_pos[0] == 0:
            return "Player 1"
        elif self.player_two_pos[0] == 16:
            return "Player 2"
        else:
            return False
