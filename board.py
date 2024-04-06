from numpy import random
from copy import deepcopy
from sys import setrecursionlimit
from math import pow, log2

setrecursionlimit(10**9)
max_depth = 4
w, b = 0, 1
WHITE, BLACK = 0, 1
forced_put = -1
end_game = -2
can_move = -3
up, down = 0, 1
possible_moves = {}
for i in range(1, 7):
    for j in range(i, 7):
        possible_moves[(i, j)] = 1 + (i != j)

def rule(dice):
    if dice[0] == dice[1]:
        return [dice[0], dice[0], dice[0], dice[0]]
    return [dice[0], dice[1]]

class Board:
    # white = 0, black = 1
    # down = 1, up = 0

    def __init__(self):
        self.white = [[0 for i in range(13)] for j in range(2)]
        self.black = [[0 for i in range(13)] for j in range(2)]
        
        self.white[0][1] = 2
        self.white[0][12] = 5
        self.white[1][6] = 5
        self.white[1][8] = 3
        
        self.black[1][1] = 2
        self.black[1][12] = 5
        self.black[0][6] = 5
        self.black[0][8] = 3
        
        self.inactive_white = 0
        self.inactive_black = 0
        self.collect_white = 0
        self.collect_black = 0

        self.states = []
        self.turn_num = 0

    # this function is used to make a virtual move and know where the piece would be
    def make_virtual_move(self, color, dice, pos):
        pos = list(pos)
        if color == w:
            
            if pos[0] == 1:
                return (pos[0], pos[1] - dice)
            else:
                if pos[1] + dice > 12:
                    dice -= 12 - pos[1] + 1
                    pos[1] = 12
                    pos[0] = 1
                    return self.make_virtual_move(color, dice, pos)
                else:
                    return (pos[0], pos[1] + dice)
        else:
            if pos[0] == 0:
                return (pos[0], pos[1] - dice)
            else:
                if pos[1] + dice > 12:
                    dice -= 12 - pos[1] + 1
                    pos[1] = 12
                    pos[0] = 0
                    return self.make_virtual_move(color, dice, pos)
                else:
                    return (pos[0], pos[1] + dice)

    # this function is used to check if a move is possible
    def check_possible(self, color, dice, pos):
        if not (dice in range(1, 7) and pos[0] in range(0, 2) and pos[1] in range(1, 13)):
            return False
        if color == w:
            if self.white[pos[0]][pos[1]] == 0:
                return False
            x, y = self.make_virtual_move(color, dice, pos)
            if y < 1 or y > 12 or self.black[x][y] > 1:
                return False
            return True
        else:
            if self.black[pos[0]][pos[1]] == 0:
                return False
            x, y = self.make_virtual_move(color, dice, pos)
            if y < 1 or y > 12 or self.white[x][y] > 1:
                return False
            return True

    # this function is used to check if there is a captured piece
    def is_forced(self, color):
        if color == w:
            return self.inactive_white > 0
        else:
            return self.inactive_black > 0

    # this function is used to move a piece
    def move(self, color, pos, dice, save = 0):
        if save:
            self.states.append([deepcopy(self.white), deepcopy(self.black), self.inactive_white, self.inactive_black, self.collect_white, self.collect_black])
        
        if self.is_forced(color):
            if color == w:
                if self.black[0][dice] > 1:
                        return
                if self.black[0][dice] == 1:
                    self.black[0][dice] = 0
                    self.inactive_black += 1
                self.inactive_white -= 1
                self.white[0][dice] += 1
            else:
                if self.white[1][dice] > 1:
                    return
                if self.white[1][dice] == 1:
                    self.white[1][dice] = 0
                    self.inactive_white += 1
                self.inactive_black -= 1
                self.black[1][dice] += 1
            return

        if self.endGame(color):
            self.remove_piece(color, dice)
            return

        x, y = self.make_virtual_move(color, dice, pos)

        if self.check_possible(color, dice, pos) == False:
            return

        if color == w:
            self.white[pos[0]][pos[1]] -= 1
            if self.black[x][y] == 1:
                self.black[x][y] = 0
                self.inactive_black += 1
            self.white[x][y] += 1
        else:
            self.black[pos[0]][pos[1]] -= 1
            if self.white[x][y] == 1:
                self.white[x][y] = 0
                self.inactive_white += 1
            self.black[x][y] += 1

    # this function is used to check if we are at the end of the game where we only want to remove pieces
    def endGame(self, color):
        
        if self.is_forced(color):
            return False
    
        if color == w:
            if sum(self.white[0]) > 0:
                return False
            if sum(self.white[1][7:]) > 0:
                return False
            return True
        else:
            if sum(self.black[1]) > 0:
                return False
            if sum(self.black[0][7:]) > 0:
                return False
            return True

    # this function is used to check if there is a winner
    def win(self, color):
        if color == w:
            return self.collect_white == 15
        else:
            return self.collect_black == 15

    # this function is used to make a move in the end game
    def remove_piece(self, color, dice):
        
        assert self.endGame(color), "Not at the end of the game"
        
        if color == w:
            if self.white[1][dice] > 0:
                self.white[1][dice] -= 1
                self.collect_white += 1
            else:
                for i in range(6, 0, -1):
                    if self.white[1][i] > 0:
                        if i-dice < 1:
                            self.white[1][i] -= 1
                            self.collect_white += 1
                            break
                        else:
                            self.white[1][i] -= 1
                            self.white[1][i-dice] += 1
                            break
        else:
            if self.black[0][dice] > 0:
                self.black[0][dice] -= 1
                self.collect_black += 1
            else:
                for i in range(6, 0, -1):
                    if self.black[0][i] > 0:
                        if i-dice < 1:
                            self.black[0][i] -= 1
                            self.collect_black += 1
                            break
                        else:
                            self.black[0][i] -= 1
                            self.black[0][i-dice] += 1
                            break

    def get_possibleMovesGivenDice(self, color, dice):
        if self.is_forced(color):
            if color == w:
                if self.black[0][dice] > 1:
                    return []
                return [(-1, 0, -1, dice)]
            else:
                if self.white[1][dice] > 1:
                    return []
                return [(-1, 1, -1, dice)]
        
        if self.endGame(color):
            return [(-2, -2, color, dice)]
        
        ans = []
        for i in range(2):
            for j in range(1, 13):
                if self.check_possible(color, dice, (i, j)):
                    ans.append((-3, i, j, dice))
        return ans
      
    def undo(self):
        self.white, self.black, self.inactive_white, self.inactive_black, self.collect_white, self.collect_black = self.states.pop()

    def roll_dice(self):
        return (random.randint(1, 7), random.randint(1, 7))

board = Board()

def evaluate(color):
    # Check for wins
    if board.win(color):
        return 1_000_000 if color == WHITE else -1_000_000
    if board.win(1 - color):
        return -1_000_000 if color == WHITE else 1_000_000

    ans = 0

    if board.endGame(WHITE): ans += 6_00_000
    if board.endGame(BLACK): ans -= 6_00_000

    # do not let it put checkers alone
    # make it put checkers in places where it could double them and where it has captured opponent checkers

    single_checker_penalty = 70
    inactive_checker_reward = 0.5
    collect_checker_reward = 1000
    double_checker_reward = 2500
    double_checker_extra_reward = 1

    if color == WHITE:
        ans -= pow(single_checker_penalty, (sum(board.white[1][i] for i in range(5, 13) if board.white[1][i] == 1) + sum(board.white[0][i] for i in range(1, 13) if board.white[0][i] == 1) + log2(max(1, max(1, board.turn_num)*sum(int(board.white[1][i]==1) for i in range(1, 6))))))
        ans += max(inactive_checker_reward, board.inactive_black)*pow(7, sum(board.white[1][i] for i in range(1, 8) if board.white[1][i] > 1))
    else:
        ans += pow(single_checker_penalty, (sum(board.black[1][i] for i in range(1, 13) if board.black[1][i] == 1) + sum(board.black[0][i] for i in range(5, 13) if board.black[0][i] == 1)) + log2(max(1, max(1, board.turn_num)*sum(int(board.black[0][i]==1) for i in range(1, 6)))))
        ans -= max(inactive_checker_reward, board.inactive_white)*pow(7, sum(board.black[0][i] for i in range(1, 8) if board.black[0][i] > 1))

    # collecting more checkers is better
    ans += collect_checker_reward * (board.collect_white - board.collect_black)

    # encouraging it to make doubles
    ans += double_checker_reward * sum(board.white[1][i] * (13 - i) + double_checker_extra_reward*(2 == board.white[1][i]) for i in range(1, 13) if board.white[1][i] > 1) * max(1, abs(10 - board.turn_num))
    ans -= double_checker_reward * sum(board.black[0][i] * (13 - i) + double_checker_extra_reward*(2 == board.black[0][i]) for i in range(1, 13) if board.black[0][i] > 1) * max(1, abs(10 - board.turn_num))

    # make checkers closer to the end towards the end of the game
    if color == WHITE:
        ans -= pow(1.7, board.turn_num) * sum(board.white[0][i] for i in range(1, 13) if board.white[0][i] > 0)
        ans -= pow(1.3, board.turn_num) * sum(board.white[1][i] * i for i in range(6, 13) if board.white[1][i] > 0)
    else:
        ans += pow(1.7, board.turn_num) * sum(board.black[1][i] for i in range(1, 13) if board.black[1][i] > 0)
        ans += pow(1.3, board.turn_num) * sum(board.black[0][i] * i for i in range(6, 13) if board.black[0][i] > 0)
    return ans

def expecti_mini_max(turn, depth, dice):
    
    if depth == 0 or board.win(turn) or board.win(1 - turn):
        return evaluate(turn), []
    if len(dice) > 0:
        tt_moves = board.get_possibleMovesGivenDice(turn, dice[0])
        if len(tt_moves) == 0:
            return expecti_mini_max(turn if len(dice) > 1 else turn ^ 1, depth - 1, dice[1:])
        best_move = []
        best_eval = float('-inf') if turn == w else float('inf')
        for move in tt_moves:
            board.move(turn, (move[1], move[2]), move[3], 1)
            eval, moves = expecti_mini_max(turn if len(dice) > 1 else turn ^ 1, depth - 1, dice[1:])
            board.undo()
            if turn == w and (eval > best_eval or (move[0] == forced_put)):
                best_eval = eval
                best_move = [move] + moves
            elif turn != w and (eval < best_eval or (move[0] == forced_put)):
                best_eval = eval
                best_move = [move] + moves 
        return best_eval, best_move
    else:
        avg_eval = 0
        for i, j in possible_moves.keys():
            current_dice = rule((i, j))
            eval, _ = expecti_mini_max(turn, depth, current_dice)
            avg_eval += eval * possible_moves[(i, j)]

        return avg_eval / 36, []

def next_move(dice, turn):
    dice = rule(dice)
    eval, moves = expecti_mini_max(turn, max_depth, dice)
    if len(dice) == 2:
        eval2, moves2 = expecti_mini_max(turn, max_depth, dice[::-1])
        if (abs(eval2) > abs(eval) and len(moves) == len(moves2)) or len(moves2) > len(moves):
            moves = deepcopy(moves2)
    for a, b, x, y in moves:
        board.move(turn, (b, x), y)
        board.turn_num += 1
    return moves

while not board.win(w) and not board.win(b):
    print("White: ", end = "")
    d1 = tuple(map(int, input().split()))
    m1 = next_move(d1, w)
    for x in m1:
        x = list(x)
        x = x[1:]
        x[0] = 'up' if x[0] == 0 else 'down'
        print(*x, end = ' ')
    print()
    # c = int(input("Black Turn enter number of moves: "))
    # for _ in range(c):
    #     d = tuple(map(int, input("Enter move: ").split()))
    #     board.move(b, (d[0], d[1]), d[2])
    # board.turn_num += 1
    print("Black: ", end = "")
    d2 = tuple(map(int, input().split()))
    m2 = next_move(d2, b)
    for x in m2:
        x = list(x)
        x = x[1:]
        x[0] = 'up' if x[0] == 0 else 'down'
        print(*x, end = ' ')
    print()