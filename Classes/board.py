from .chessPieces import *
from copy import deepcopy

class InvalidCoordError(Exception):
    pass

class ParsePieceError(Exception):
    pass

class CoordCoversionError(Exception):
    pass

class Board:
    def __init__(self, init_board_repr:list[list[str]]):
        self.board = self.parse_board(init_board_repr)

    @property
    def size(self):
        return (len(self.board), len(self.board[0]))
    
    @property
    def n_rows(self):
        return self.size[0]
    
    @property
    def n_cols(self):
        return self.size[1]

    def copy(self):
        return deepcopy(self)

    def action_space(self, color):
        actions = []
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                piece = self.get_piece((i, j))
                if piece is not None and piece.color == color:
                    for move in piece.get_possible_moves(self):
                        actions.append(move)
        return actions

    def state_space(self, turn_color):
        action_space = self.action_space(turn_color)
        state_space = []
        for action in action_space:
            board_copy = self.copy()
            board_copy.move_piece(action[0], action[1], turn_color)
            state_space.append(board_copy)
        return state_space

    def parse_board(self, board_repr:list[list[str]]):
        board = [[self.parse_piece(board_repr, (row, col)) for col in range(len(board_repr[0]))] for row in range(len(board_repr))]
        return board
    
    def parse_piece(self, board_repr, position):
        piece = board_repr[position[0]][position[1]]
        if piece == "__":
            return None
        color = "white" if piece[0] == "w" else "black"
        name = piece[1]
        if name == "P":
            return Pawn(color, position)
        elif name == "R":
            return Rook(color, position)
        elif name == "N":
            return Knight(color, position)
        elif name == "B":
            return Bishop(color, position)
        elif name == "Q":
            return Queen(color, position)
        elif name == "K":
            return King(color, position)
        else:
            raise ParsePieceError(f"Invalid piece name: {name}")
    
    def move_piece(self, start, end, turn_color, verbose=False):
        def _print(msg):
            if verbose:
                print(msg)

        if self.move_valid(start, end, turn_color, verbose=verbose):
            piece = self.get_piece(start)
            if piece.name in ["Pawn", "King", "Rook"]:
                if piece.first_move:
                    piece.first_move = False
                    if piece.name == "Pawn":
                        del piece.deltas[1]
            self.set_piece(end, piece)
            self.remove_piece(start)
            if piece.name == "Pawn":
                self.attempt_promotion(end)
            if piece.name == "King":
                self.attempt_castle(piece, start, end)    
            return True
        _print("Invalid move")
        return False

    def get_pieces(self):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece is not None:
                    pieces.append(piece)
        return pieces

    def move_valid(self, start, end, turn_color, verbose=False):
        def _print(msg):
            if verbose:
                print(msg)
                
        if not self.coords_valid(start) or not self.coords_valid(end):
            raise InvalidCoordError("Invalid coordinates")
        if start == end:
            _print(f"piece cannot stay in the same position {start}")
            return False
        piece = self.get_piece(start)
        if piece is None:
            _print(f"No piece at start position {start}")
            return False
        if turn_color != piece.color:
            _print(f"Cannot move opponent's piece {piece} at {start}")
            return False
        if not piece.move_valid(start, end, self):
            _print(f"piece cannot move to end position {end}")
            return False
        return True
    
    def in_check(self, color):
        king_pos = self.get_king_pos(color)
        #when king is found, check if any enemy piece can move to that position
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.board[i][j] is not None and self.board[i][j].color != color:
                    if self.board[i][j].move_valid((i, j), king_pos, self):
                        return True
        return False
    
    def get_king_pos(self, color):
        #go through board to find position of king
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.board[i][j] is not None and self.board[i][j].name == "King" and self.board[i][j].color == color:
                    return (i, j)
        return None

    def attempt_promotion(self, position):
        piece = self.get_piece(position)
        if position[0] == 0 or position[0] == 7:
            self.remove_piece(position)
            self.set_piece(position, Queen(piece.color, position))
        
    def attempt_castle(self, piece, start, end):
        delta = (end[0] - start[0], end[1] - start[1])
        if delta in piece.castle_deltas:
            self.castle(piece, delta)
            piece.deltas = piece.deltas[:-2]
            
    def castle(self, piece, delta):
        if piece.color == "white":
            rook = self.get_piece((7, 7)) if delta[1] > 0 else self.get_piece((7,0))
            if delta[1] == -2:
                self.remove_piece((7, 0))
                self.set_piece((7, 3), rook)
            else:
                self.remove_piece((7, 7))
                self.set_piece((7, 5), rook)
        else:
            rook = self.get_piece((0, 7)) if delta[1] > 0 else self.get_piece((0,0))
            if delta[1] == -2:
                self.remove_piece((0, 0))
                self.set_piece((0, 3), rook)
            else:
                self.remove_piece((0, 7))
                self.set_piece((0, 5), rook)
                
    def get_piece(self, position):
        return self.board[position[0]][position[1]]
    
    def set_piece(self, position, piece):
        self.board[position[0]][position[1]] = piece
        if piece is not None:
            piece.position = position
    
    def remove_piece(self, position):
        self.board[position[0]][position[1]] = None
    
    def coords_valid(self, position):
        return 0 <= position[0] < self.n_rows and 0 <= position[1] < self.n_cols

    def convert_coords(self, coords):
        if not isinstance(coords, str):
            raise CoordCoversionError("Coordinates must be a string")
        if len(coords) != 2:
            raise CoordCoversionError("Coordinates must be 2 characters")
        try:
            x = int(coords[1]) - 1
            y = ord(coords[0].upper()) - ord("A")
        except CoordCoversionError:
            raise CoordCoversionError("Coordinates must be in the format A1")
        return (x, y)

    def convert_coords_to_str(self, coords):
        if not isinstance(coords, tuple):
            raise CoordCoversionError("Coordinates must be a tuple")
        if len(coords) != 2:
            raise CoordCoversionError("Coordinates must be a tuple of length 2")
        try:
            x = coords[0] + 1
            y = chr(coords[1] + ord("A"))
        except CoordCoversionError:
            raise CoordCoversionError("Coordinates must be in the format (0, 0)")
        return f"{y}{x}"
    
    def get_board_repr(self):
        repr = ""
        for row in self.board:
            for piece in row:
                if piece is None:
                    repr += "__"
                else:
                    repr += str(piece)
        return repr

    def __str__(self):
        repr = ""
        f_col, i = True, 1
        for row in self.board:
            f_col = True
            for piece in row:
                if f_col:
                    repr += str(i) + "  "
                    i += 1
                    f_col = False
                if piece is None:
                    repr += " .  "
                else:
                    repr += str(piece) + "  "
            repr += "\n"
        repr += "    A   B   C   D   E   F   G   H\n"
        return repr
