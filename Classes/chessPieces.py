class Piece:
    def __init__(self, color, position, name, symbol, value):
        self.color = color
        self.position = position
        self.name = name
        self.symbol = symbol
        self.stretch = False
        self.value = value

    def get_name(self):
        return self.name
    
    def get_color(self):
        return self.color
    
    def get_position(self):
        return self.position
    
    def __str__(self):
        return self.symbol
    
    def get_possible_moves(self, board) -> list[(tuple, tuple)]:
        moves = []
        for delta in self.deltas:
            curr = (self.position[0] + delta[0], self.position[1] + delta[1])
            while board.coords_valid(curr) and self.move_valid(self.position, curr, board):
                if (self.position, curr) not in moves:
                    moves.append((self.position, curr))
                curr = (curr[0] + delta[0], curr[1] + delta[1])
        return moves

    def get_delta(self, start, end):   
        return (end[0] - start[0], end[1] - start[1])
    
    def check_scaling(self, delta):
        #is the general direction that im moving in allowed
        if self.stretch:
            #if not perfect horizontal/vertical/diagonal, return False
            if delta[0] != 0 and delta[1] != 0:
                if abs(delta[0]) != abs(delta[1]):
                    return False, delta
            if delta[0] != 0:
                delta = int(delta[0]/abs(delta[0])), delta[1]
            if delta[1] != 0:
                delta = delta[0], int(delta[1]/abs(delta[1]))
        return delta in self.deltas, delta
#start: 8,8, end 1,8, delta: (-7, 0), (-1, 0)

    def is_friendly(self, piece):
        if piece is None:
            return False
        if self.color == piece.color:
            return True
        return False
        
class Pawn(Piece):
    def __init__(self, color, position):
        symbol = "wP" if color == "white" else "bP"
        super().__init__(color, position, "Pawn", symbol, 100)
        if color == "black":
            self.deltas = [(1, 0), (2, 0), (1, 1), (1, -1)]
        else:
            self.deltas = [(-1, 0), (-2, 0), (-1, 1), (-1, -1)]
        self.first_move = True

    def move_valid(self, start, end, board):
        #move is within possible deltas
        # print(f"start: {start}, end {end}, delta: {self.get_delta(start, end)}")
        delta = self.get_delta(start, end)
        delta_valid, _ = self.check_scaling(delta)
        if not delta_valid:
            return False
        #check if there is a piece in the way
        f_delta = self.forward_deltas()
        if delta[1] == 0:
            if delta[0] == -1 or delta[0] == 1:
                piece = board.get_piece((start[0] + delta[0], start[1]))
                if piece is not None:
                    return False
            for d in range(1, abs(delta[0])):
                piece = board.get_piece((start[0] + d*delta[0], start[1]))
                if piece is not None:
                    return False
        #check if there is a piece to capture
        else:
            piece = board.get_piece((start[0] + delta[0], start[1] + delta[1]))
            if piece is None:
                return False
            #check if piece is friendly
            if self.is_friendly(piece):
                return False

        return True

    def forward_deltas(self):
        return self.deltas[:2] if len(self.deltas) == 4 else self.deltas[:1]
#start: 4, 4; end: 6, 4, delta: (2, 0)

class Rook(Piece):
    def __init__(self, color, position):
        symbol = "wR" if color == "white" else "bR"
        super().__init__(color, position, "Rook", symbol, 500)
        self.deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        self.first_move = True
        self.stretch = True
    
    def move_valid(self, start, end, board):
        #move is within possible deltas
        delta = self.get_delta(start, end)
        delta_valid, delta = self.check_scaling(delta)

        if not delta_valid:
            return False
        
        #check if there is a piece in the way to destination
        current = (start[0] + delta[0], start[1] + delta[1])
        while current != end:
            piece = board.get_piece(current)
            if piece is not None:
                return False
            current = (current[0] + delta[0], current[1] + delta[1])

        #check if destination piece is friendly
        if self.is_friendly(board.get_piece(end)):
            return False

        return True
   
class Knight(Piece):
    def __init__(self, color, position):
        symbol = "wN" if color == "white" else "bN"
        super().__init__(color, position, "Knight", symbol, 320)
        self.deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    
    def move_valid(self, start, end, board):
        #move is within possible deltas
        delta = self.get_delta(start, end)
        if delta not in self.deltas:
            return False

        #check if destination piece is friendly
        if self.is_friendly(board.get_piece(end)): 
            return False
        
        return True

class Bishop(Piece):
    def __init__(self, color, position):
        symbol = "wB" if color == "white" else "bB"
        super().__init__(color, position, "Bishop", symbol, 330)
        self.deltas = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        self.stretch = True
    
    def move_valid(self, start, end, board):
        #move is within possible deltas
        delta = self.get_delta(start, end)
        delta_valid, delta = self.check_scaling(delta)
        if not delta_valid:
            return False
    
        #check if there is a piece in the way to destination
        current = (start[0] + delta[0], start[1] + delta[1])
        while current != end:
            piece = board.get_piece(current)
            if piece is not None:
                return False
            current = (current[0] + delta[0], current[1] + delta[1])

        #check if destination piece is friendly
        if self.is_friendly(board.get_piece(end)):
            return False
        return True 

class Queen(Piece):
    def __init__(self, color, position):
        symbol = "wQ" if color == "white" else "bQ"
        super().__init__(color, position, "Queen", symbol, 900)
        self.deltas = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        self.stretch = True
    
    def move_valid(self, start, end, board):
        #move is within possible deltas
        delta = self.get_delta(start, end)
        delta_valid, delta = self.check_scaling(delta)
        if not delta_valid:
            return False
    

        #check if there is a piece in the way to destination
        current = (start[0] + delta[0], start[1] + delta[1])
        while current != end:
            piece = board.get_piece(current)
            if piece is not None:
                return False
            current = (current[0] + delta[0], current[1] + delta[1])
        
        #check if destination piece is friendly
        if self.is_friendly(board.get_piece(end)):
            return False
        
        return True

class King(Piece):
    def __init__(self, color, position):
        symbol = "wK" if color == "white" else "bK"
        super().__init__(color, position, "King", symbol, 10000)
        self.deltas = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2), (0, -2)]
        self.castle_deltas = [(0, 2), (0, -2)]
        self.first_move = True
        self.in_check = False
    
    def move_valid(self, start, end, board):
        delta = self.get_delta(start, end)
        #check for castle
        if self.first_move:
            if delta in self.castle_deltas:
                current = start
                while current != end:
                    current = (current[0], current[1] + delta[1])
                    piece = board.get_piece(current)
                    if piece is not None:
                        return False
                #nothing in the way at this point
                if delta[1] == 2:
                    current = (current[0], current[1] + 1)
                else:
                    current = (current[0], current[1] - 2)
                piece = board.get_piece(current)
                if piece is None:
                    return False
                if piece.name != "Rook":
                    return False
                if piece.color != self.color:
                    return False
                if not piece.first_move:
                    return False
                self.first_move = False
                return True
        #move is within possible deltas
        if delta not in self.deltas:
            return False
        
        #check if destination piece is friendly
        if self.is_friendly(board.get_piece(end)):
            return False

        self.first_move = False

        return True