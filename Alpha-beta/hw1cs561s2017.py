import argparse

__author__ = 'ameya'

neighboring_pos = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


class Game:
    def __init__(self, player_start, max_depth, game_state):
        self.player_start = player_start
        self.max_depth = max_depth
        self.board = []
        self.positions = {"X": [], "O": []}
        self.save_board(game_state)
        self.generate_moves(player_start)

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

    def generate_moves(self, player):
        moves = []
        for pos in self.positions[player]:
            moves.extend(self.check_neighboring_moves(pos[0], pos[1], player))
        moves = sorted(moves)
        print moves


class Node:
    def __init__(self, depth):
        self.depth = depth
        self.alpha = -999999
        self.beta = 999999


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
    reversi_game = Game(lines[0], int(lines[1]), lines[2: len(lines)])