from Classes.board import Board, InvalidCoordError
from Classes.chessPieces import *
from Classes.players import HumanPlayer, AIPlayer
import pprint
from Setup.init_board_reprs import *
from time import sleep

class CoordCoversionError(Exception):
    pass

def prnt(s):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(s)

class Game:
    def __init__(self, white_player=None, black_player=None, init_board_repr=None):
        self.board = Board(init_board_repr)
        self.turn_color = "white"
        self.white_player = white_player
        self.black_player = black_player

    def play(self):
        while True:
            self.display_board()
            if self.game_over():
                break
            move = self.prompt()
            try:
                start, end = self.convert_coords(move[:2]), self.convert_coords(move[3:5])
                if self.board.move_piece(start, end, self.turn_color, verbose=True):
                    self.next_turn()
            except InvalidCoordError as e:
                print(e)
            except CoordCoversionError as e:
                print(e)

    def display_board(self):
        print(self.board)

    def game_over(self):
        if not self.check_king_alive(self.turn_color):
            winner = self.get_next_player()
            print(f"KING DEAD! {winner.name} ({winner.color}) WINS!")
            return True
        
        if self.check_for_mate(self.turn_color):
            winner = self.get_next_player()
            print(f"CHECKMATE! {winner.name} ({winner.color}) WINS!")
            return True
        
        if self.check_for_stalemate(self.turn_color):
            print("STALEMATE!")
            return True

        return False
    
    def check_king_alive(self, color):
        king_pos = self.board.get_king_pos(color)
        return king_pos != None

    def check_for_stalemate(self, color):
        if self.board.in_check(color):
            return False
        state_space = self.board.state_space(color)
        for state in state_space:
            if not state.in_check(color):
                return False
        return True

    def get_curr_player(self):
        return self.white_player if self.turn_color == "white" else self.black_player

    def get_next_player(self):
        return self.black_player if self.turn_color == "white" else self.white_player

    def next_turn(self):
        self.turn_color = "white" if self.turn_color == "black" else "black"
    
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

    def prompt(self):
        prompt = f"{self.turn_color.title()}'s ({self.get_curr_player().name}) turn: "
        print(prompt, end=" ")
        move = self.get_move()
        print(move)
        return move

    def get_move(self):
        return self.get_curr_player().get_move()

    def check_for_mate(self, color):
        if self.board.in_check(color):
            state_space = self.board.state_space(color)
            for state in state_space:
                if not state.in_check(color):
                    return False
            return True
        return False
                           
def main():
    players = input("Enter number of players (1 or 2): ")
    game = Game(init_board_repr=starting_board)

    if players == "1":
        color = input("Enter color (white or black): ")
        if color == "white":
            game.white_player = HumanPlayer("Human", "white", game)
            game.black_player = AIPlayer("AI-Bartholomew", "black", game)
        elif color == "black":
            game.white_player = AIPlayer("AI-Bartholomew", "white", game)
            game.black_player = HumanPlayer("Human", "black", game)
        else:
            print("Invalid color")
            return
    elif players == "2":
        game.white_player = HumanPlayer("Human 1", "white", game)
        game.black_player = HumanPlayer("Human 2", "black", game)
    else:
        print("Invalid number of players")
        return
    game.play()

if __name__ == "__main__":
    main()