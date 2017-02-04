import argparse
from copy import deepcopy

__author__ = 'ameya'

neighboring_pos = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
board_value = [[99, -8, 8, 6, 6, 8, -8, 99], [-8, -24, -4, -3, -3, -4, -24, -8], [8, -4, 7, 4, 4, 7, -4, 8],
               [6, -3, 4, 0, 0, 4, -3, 6], [6, -3, 4, 0, 0, 4, -3, 6], [8, -4, 7, 4, 4, 7, -4, 8],
               [-8, -24, -4, -3, -3, -4, -24, -8], [99, -8, 8, 6, 6, 8, -8, 99]]


class Game:
    def __init__(self, player, player_start, max_depth, game_state=None, **kwargs):
        self.player = player
        self.player_start = player_start
        self.board = []
        self.positions = {"X": [], "O": []}
        if "root" in kwargs:
            self.save_board(game_state)
            self.max_depth = max_depth
        else:
            self.board = deepcopy(kwargs['game'].get_board())
            self.positions = deepcopy(kwargs['game'].get_positions())
            self.max_depth = deepcopy(kwargs['game'].get_depth())
            if "move" in kwargs:
                self.update_board(kwargs['move'])  # update X position and board
                # print self.board
                # self.start_game()
                # self.generate_moves(player_start)

    def get_board(self):
        return self.board

    def get_positions(self):
        return self.positions

    def get_depth(self):
        return self.max_depth

    def save_board(self, game_state):
        for i in range(len(game_state)):
            row = []
            for j in range(len(game_state[i])):
                char = game_state[i][j]
                if char == "*":
                    row.append(None)
                else:
                    self.positions[char].append((i, j))
                    row.append(char)
            self.board.append(row)

    def update_board(self, move):
        global neighboring_pos
        if self.player == "O":
            # first update enclosing positions
            affected_pos = []
            for direction in neighboring_pos:
                affected_pos.extend(self.get_affected_pos(move, direction, check_player="O"))

            for pos in affected_pos:
                self.board[pos[0]][pos[1]] = "O"
                self.positions["X"].remove((pos[0], pos[1]))
                self.positions["O"].append((pos[0], pos[1]))
            # move is O's move
            self.board[move[0]][move[1]] = "O"
            self.positions["O"].append((move[0], move[1]))
        else:
            # first update enclosing positions
            affected_pos = []
            for direction in neighboring_pos:
                affected_pos.extend(self.get_affected_pos(move, direction, check_player="X"))

            for pos in affected_pos:
                self.board[pos[0]][pos[1]] = "X"
                self.positions["O"].remove((pos[0], pos[1]))
                self.positions["X"].append((pos[0], pos[1]))
            # move is X's move
            self.board[move[0]][move[1]] = "X"
            self.positions["X"].append((move[0], move[1]))

    def get_affected_pos(self, move, direction, check_player):
        flip_positions = []
        while self.board[move[0]][move[1]] != check_player:
            move = [move[0] + direction[0], move[1] + direction[1]]
            i = move[0]
            j = move[1]
            if i < 0 or i > 7 or j < 0 or j > 7:
                return []
            if self.board[i][j] is None:
                return []
            flip_positions.append(move)
        return flip_positions[:-1]

    def get_valid_move(self, i, j, player, direction, found):
        if i < 0 or i > 7 or j < 0 or j > 7:
            return False
        if player == "X":
            if self.board[i][j] == "O":
                return self.get_valid_move(i + direction[0], j + direction[1], player, direction, found=True)
            elif self.board[i][j] == "X":
                return False
            else:
                if found:
                    return [i, j]
                else:
                    return False
        if player == "O":
            if self.board[i][j] == "X":
                return self.get_valid_move(i + direction[0], j + direction[1], player, direction, found=True)
            elif self.board[i][j] == "O":
                return False
            else:
                if found:
                    return [i, j]
                else:
                    return False

    def check_neighboring_moves(self, i, j, player):
        moves = []
        top = self.get_valid_move(i, j + 1, player, direction=[0, 1], found=False)  # check Top neighbor
        if top:
            moves.append(top)
        top_right = self.get_valid_move(i + 1, j + 1, player, direction=[1, 1], found=False)  # check Top Right neighbor
        if top_right:
            moves.append(top_right)
        right = self.get_valid_move(i + 1, j, player, direction=[1, 0], found=False)  # check Right neighbor
        if right:
            moves.append(right)
        bottom_right = self.get_valid_move(i + 1, j - 1, player, direction=[1, -1],
                                           found=False)  # check Bottom Right neighbor
        if bottom_right:
            moves.append(bottom_right)
        bottom = self.get_valid_move(i, j - 1, player, direction=[0, -1], found=False)  # check Bottom neighbor
        if bottom:
            moves.append(bottom)
        bottom_left = self.get_valid_move(i - 1, j - 1, player, direction=[-1, -1],
                                          found=False)  # check Bottom Left neighbor
        if bottom_left:
            moves.append(bottom_left)
        left = self.get_valid_move(i - 1, j, player, direction=[-1, 0], found=False)  # check Left neighbor
        if left:
            moves.append(left)
        top_left = self.get_valid_move(i - 1, j + 1, player, direction=[-1, 1],
                                       found=False)  # check Top Left neighbor
        if top_left:
            moves.append(top_left)
        return moves

    def start_game(self):
        current_player = self.player_start
        all_moves = []
        if current_player == "X":
            players = ["X", "O"]
        else:
            players = ["O", "X"]
        moves = self.generate_moves(players[0])
        for move in moves:
            players = players[::-1]
            g = Game(players[0], self.max_depth - 1, self.board, root=False, move=move)
        for i in range(1, self.max_depth):
            all_moves.append(self.generate_moves(players[0]))
            players = players[::-1]
            self.update_board()

    def generate_moves(self, player):
        moves = []
        for pos in self.positions[player]:
            moves.extend(self.check_neighboring_moves(pos[0], pos[1], player))
        moves = sorted(moves)
        return moves

    def evaluate_value(self):
        global board_value
        score = 0
        for pos in self.positions[self.player_start]:
            score += board_value[pos[0]][pos[1]]
        if self.player_start == "X":
            for pos in self.positions["O"]:
                score -= board_value[pos[0]][pos[1]]
        else:
            for pos in self.positions["X"]:
                score -= board_value[pos[0]][pos[1]]
        return score


class Node:
    def __init__(self, depth):
        self.depth = depth
        self.alpha = -999999
        self.beta = 999999


def get_pretty_node(node):
    if isinstance(node, list):
        display_node = chr(node[1] + 97) + str(node[0] + 1)
        return display_node
    return node


def check_infinity(val):
    if val == -999999:
        return "-Infinity"
    if val == 999999:
        return "Infinity"
    return val


def alpha_beta(game, player, player_start, depth, max_depth, alpha, beta):
    logs = []
    value = max_value(game, player, player_start, depth, max_depth, alpha, beta, "root", logs)

    for log in logs:
        print log
    return value


def max_value(game, player, player_start, depth, max_depth, alpha, beta, node, logs):
    if max_depth - depth == 0 or len(game.get_positions()[player]) == 0:
        value = game.evaluate_value()
        logs.append(
            [get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        return value
    value = -999999
    moves = game.generate_moves(player)
    # print moves
    logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    if len(moves) == 0:
        if node != "pass":
            new_game = Game(player, player_start, depth, game=game)
            if player == "X":
                player = "O"
            else:
                player = "X"
            value = max(value,
                        min_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, "pass", logs))
            if value >= beta:
                logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
                return value
            alpha = max(alpha, value)
            logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    original_player = deepcopy(player)
    if player == "X":
        player = "O"
    else:
        player = "X"
    for move in moves:
        new_game = Game(original_player, player_start, depth, move=move, game=game)
        value = max(value, min_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, move, logs))
        """
        logs.append(
            [get_pretty_node(move), depth + 1, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        """
        if value >= beta:
            logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
            return value
        alpha = max(alpha, value)
        logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    if node == "root" and value == -999999:
        logs[-1][2] = game.evaluate_value()
    return value


def min_value(game, player, player_start, depth, max_depth, alpha, beta, node, logs):
    if max_depth - depth == 0 or len(game.get_positions()[player]) == 0:
        value = game.evaluate_value()
        logs.append(
            [get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        return value
    value = 999999
    moves = game.generate_moves(player)
    # print moves
    logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    if len(moves) == 0:
        if node != "pass":
            new_game = Game(player, player_start, depth, game=game)
            if player == "X":
                player = "O"
            else:
                player = "X"
            value = max(value,
                        min_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, "pass", logs))
            if value <= alpha:
                logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
                return value
            beta = min(beta, value)
            logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    original_player = deepcopy(player)
    if player == "X":
        player = "O"
    else:
        player = "X"
    for move in moves:
        new_game = Game(original_player, player_start, depth, move=move, game=game)
        value = min(value, max_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, move, logs))
        """
        logs.append(
            [get_pretty_node(move), depth + 1, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        """
        if value <= alpha:
            logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
            return value
        beta = min(beta, value)
        logs.append([get_pretty_node(node), depth, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
    return value


def get_command_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help='Input file of Initial game state')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    # args = get_command_args()
    lines = []
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [line.strip() for line in lines]
    reversi_game = Game(lines[0], lines[0], int(lines[1]), lines[2: len(lines)], root=True)
    alpha_beta(reversi_game, lines[0], lines[0], 0, int(lines[1]), -999999, 999999)