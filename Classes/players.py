import random
from Setup.init_board_reprs import *

class NoMovesLeftError(Exception):
    pass

class Player:
    def __init__(self, name, color, game):
        self.name = name
        self.color = color
        self.game = game

    def get_heuristic(self, board):
        h = self.get_board_heuristic(board)
        h = h + self.get_space_heuristic(board, self.color)
        return h

    def get_board_heuristic(self, board):
        h = 0
        for piece in board.get_pieces():
            if piece.color == self.color:
                h += piece.value
            else:
                h -= piece.value
        return h

    def get_space_heuristic(self, board, color):
        h = 0
        for piece in board.get_pieces():
            if piece.color == color:
                h += (len(piece.get_possible_moves(board)))*0.1
            else:
                h -= (len(piece.get_possible_moves(board)))*0.1
        return h

    def get_king_pos_heuristic(self, board, color):
        king_pos = board.get_king_pos(color)
        

    def minimax(self, board, depth, color, alpha, beta):
        #return the best action and the best score
        if depth == 0 or self.game.game_over():
            return None, self.get_heuristic(board)
        
        next_color = "white" if color == "black" else "black"

        bestAction = None
        if color == self.color:
            maxEval = float('-inf')
            for action in board.action_space(color):
                new_board = board.copy()
                new_board.move_piece(action[0], action[1], color)
                newEval = self.minimax(new_board, depth - 1, next_color, alpha, beta)[1]
                maxEval = max(maxEval, newEval)
                if newEval >= maxEval:
                    bestAction = action
                alpha = max(alpha, newEval)
                if alpha >= beta:
                    break
            return bestAction, maxEval
        else:
            minEval = float('inf')
            bestAction= None
            for action in board.action_space(color):
                new_board = board.copy()
                new_board.move_piece(action[0], action[1], color)
                newEval = self.minimax(new_board, depth - 1, next_color, alpha, beta)[1]
                minEval = min(minEval, newEval)
                if newEval <= minEval:
                    bestAction = action
                beta = min(beta, newEval)
                if alpha >= beta:
                    break
            return bestAction, minEval

    def get_move(self):
        raise NotImplementedError("get_move() not implemented")
    
    def _user_play(self):
        return input()
    
    def _auto_play(self):
        action = self.minimax(self.game.board, 3, self.color, float('-inf'), float('inf'))[0]
        str_action = self.game.convert_coords_to_str(action[0]), self.game.convert_coords_to_str(action[1])
        return " ".join(str_action)
        
class AIPlayer(Player):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)
    
    def get_move(self):
        return self._auto_play()
        # return self._user_play()

class HumanPlayer(Player):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)

    def get_move(self):
        # return self._auto_play()
        return self._user_play()

    