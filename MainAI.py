from random import randint
import math
import copy
from BoardClasses import Move
from BoardClasses import Board

from collections import defaultdict
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
# Testing command: python3 AI_Runner.py 7 7 2 l ../src/checkers-python/main.py Sample_AIs/Average_AI/main.py

# def step_iteration(x: int):
#     return int(100 + (650 / (1 + math.exp(-2 * (x - 15)))) - (500 / (1 + math.exp(-0.5 * (x - 30)))))

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        # self.MCTS_root = MCTSNode(board, None, color, None)
        self.iteration = 500

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        
        MCTS = MonteCarloTreeSearch(self.board, self.color, self.iteration)
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1:
            if len(moves[0]) == 1:
                self.board.make_move(moves[0][0], self.color)
                # self.iteration = step_iteration(self.iteration)
                return moves[0][0]
        move = MCTS.do_all_iteration()
        self.board.make_move(move, self.color)
        # self.iteration = step_iteration(self.iteration)
        return move

def do_custom_moves(moves):
    index = randint(0,len(moves)-1)
    inner_index = randint(0,len(moves[index])-1)
    move = moves[index][inner_index]
    return move

class MCTSNode():
    def __init__(self, board: Board, color, move=None, parent=None):
        self.board = board # tracks the board after this move is made
        self.color = color # the color of our AI
        self.move = move # tracks the move that was made
        self.parent = parent
        self.children = []
        self.next_child_to_expand = 0 # will keep track of which child in self.children is next to be expanded
        self.wins = 0.0
        self.total = 0.0

    def compute_uct(self, c=10) -> float:
        if self.total > 0:
            wins_prob = self.wins / self.total
            explore_factor = c * math.sqrt(math.log(self.parent.total) / self.total)
            uct_result = wins_prob + explore_factor
            return uct_result
        else:
            return 0

    def backpropagate(self, isWin: bool):
        if isWin:
            self.wins += 1
        
        self.total += 1
        if self.parent is not None:
            self.parent.backpropagate(not isWin)
    
    def expand(self):
        moves = self.board.get_all_possible_moves(self.color)
        for move in moves:
            for m in move:
                board_cpy = copy.deepcopy(self.board)
                board_cpy.make_move(m, self.color)
                self.children.append(MCTSNode(board_cpy, self.color, m, self))


    def simulate(self):
        try:
            # Test children existence.
            node = self.children[-1]
        except IndexError:
            return
        rand_child = self.children[randint(0,len(self.children)-1)]
        temp_board = copy.deepcopy(rand_child.board)
        temp_color = 3 - self.color
        while temp_board.is_win(temp_color) == 0:
            moves = temp_board.get_all_possible_moves(temp_color)
            if len(moves) == 0 :
                break

            move = do_custom_moves(moves)
            temp_board.make_move(move, temp_color)
            temp_color = 3 - temp_color
        
        rand_child.backpropagate(temp_board.is_win(3 - temp_color) == self.color or temp_board.is_win(3 - temp_color) == -1)

class MonteCarloTreeSearch():
    def __init__(self, board: Board, color, iteration: int):
        self.board = copy.deepcopy(board)
        self.iteration = iteration
        self.all_moves = None
        self.counter = 0
        self.moves_counter = 0
        self.color = color
        self.root = MCTSNode(self.board, self.color)

    def do_all_iteration(self):
        self.root.expand()
        for _ in range(self.iteration):
            self.root.simulate()
        
        child_uct = [c.compute_uct() for c in self.root.children]
        max_uct = max(child_uct)
        max_index = child_uct.index(max_uct)
        return self.root.children[max_index].move

    def selection(self):
        # Get all child node and compute their uct. Whoever gets the max score will traverse to that child node.
        # Repeat until it's a leaf node.
        while True:
            if len(self.root.children) > 0:
                child_uct = [c.compute_uct() for c in self.root.children]
                max_uct = max(child_uct)
                max_index = child_uct.index(max_uct)
                self.root = self.root.children[max_index]
            else:
                break

    def iterate(self):
        # Selection
        self.selection()
        self.root.simulate()