import copy
from dlgo.gotypes import Player

# a class that represents a move on a go board.
class Move():
    # intializes a move, with parameters for a point, a boolean for checking
    # if the move was passed, and a boolean for checking if the move was
    # to resign.
    def __init__(self, point=None, is_pass=False, is_resign=False):
        # if a move is a mix of a resign, pass, or valid move, throw an error
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # creates a new valid move based on a given point.
    @classmethod
    def play(cls, point):
        return Move(point=point)

    # creates a new pass move.
    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    # creates a new resign move
    @classmethod
    def resign(cls):
        return Move(is_resign=True)

# a class that represents a convienent data structure for describing a group of stones.
class GoString():
    # given a color, a set of stones, and a number of liberties, creates a new go string. Also
    # checks given stones in a string by points in a set, and liberties by given points in a set
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)
    
    # removes a point from this GoString if its in the liberties set.
    def remove_liberty(self, point):
        self.liberties.remove(point)
    
    # adds a point to this GoString's liberties set.
    def add_liberty(self, point):
        self.liberties.add(point)
    
    # merges a given goString with this goString.
    def merged_with(self, go_string):
        # make sure they are both of the same color
        assert go_string.color == self.color
        # combined_stones  = set | set is equilivant to combined_stones = union(set, et);
        # - with sets is difference of two sets 
        combined_stones = self.stones | go_string.stones
        return GoString(self.color, 
            combined_stones, 
            (self.liberties | go_string.liberties) - combined_stones)
    
    # return the number of liberties this goString has.
    @property
    def num_liberties(self):
        return len(self.liberties)

    # custom === for object
    def __eq__(self, other):
        return isinstance(other, GoString) and \
        self.color == other.color and \
        self.stones == other.stones and \
        self.liberties == other.liberties

# class the represents a go board given a number of rows and columns.
class Board():
    # creates an instance of a board given num_rows and num_cols
    # it also keeps a private Dictionary<Move, GoString> which bookkeps
    # what spots on the grid are occupied, and which GoStrings they are
    # associated with.
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
    
    # places a stone on the board, given the player and the point.
    def place_stone(self, player, point):
        # if not on grid throw an error
        assert self.is_on_grid(point)
        # if the point is occupied throw an error
        assert self._grid.get(point) is None
        adjacent_same_color =[ ]
        adjacent_opposite_color = [ ]
        liberties = [ ]
        # for each neighbor of the point...
        for neighbor in point.neighbors():
            # ignore any neighboor who is not on the grid
            if not self.is_on_grid(neighbor):
                continue    
            neighbor_string = self._grid.get(neighbor)
            # if the neighbooring point is empty, add it the list of liberties
            if neighbor_string is None:
                liberties.append(neighbor)
            # if the neighboring point is of the same color add it to list of adjacent_same_color if not there
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else: 
                # if the neighboring point is of the opposite color add it to list of adjacent_oppposite_color
                # if not there
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        # create a new string with the point and number of liberties we counted d
        new_string = GoString(player, [point], liberties)
        # merge the new GoString with neighbors of the same color
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        # make sure all the points in the new goString are registered together on the grid
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        # remove liberties of all adjacent opposite colors points
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_liberty(point)
        # destroy all opposite color goStrings with zero liberties
        for other_color_string in  adjacent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)
    
    # given a point, checks if that point is valid on this board.
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols
   
    # given a point, gets the color of it
    def get(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    # given a point, gets the goString associated with it.
    def get_go_string(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string 
    
    # given a goString removes all the points associated with it.
    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in  point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None

# this class represents the game state of a go game instance
class GameState():
    # takes in a Board, the next player to play, the previous player,
    # and the last move 
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move

    def apply_move(self, player, move):
        if player != self.next_player:
            raise ValueError(player)
        if move.is_play: 
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, player.other, self, move)
    
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string == 0

    @property
    def situation(self):
        return (self.next_player, self.board)

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board)
        past_state = self.previous_state
        while past_state is not None:
            if past_state.situation == next_situation:
                return True
            past_state = past_state.previous_state
        return False

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return(
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move))


