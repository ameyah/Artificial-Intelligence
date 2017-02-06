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

    def update_single_pos(self, move, player_start):
        self.board[move[0]][move[1]] = player_start

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

    def generate_moves(self, player):
        moves = []
        for pos in self.positions[player]:
            single_move = self.check_neighboring_moves(pos[0], pos[1], player)
            for move in single_move:
                if move not in moves:
                    moves.append(move)
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
    return str(val)


def alpha_beta(game, player, player_start, depth, max_depth, alpha, beta):
    logs = []
    value = max_value(game, player, player_start, depth, max_depth, alpha, beta, "root", logs, pcount=0)
    if len(value) > 2:
        if value[2] != "pass" and value[2] is not None:
            game.update_board(value[2])
    output_file(game.get_board(), logs)
    """
    print value
    for log in logs:
        print log
    """
    return value


def max_value(game, player, player_start, depth, max_depth, alpha, beta, node, logs, **kwargs):
    if max_depth - depth <= 0:  # or len(game.get_positions()[player]) == 0:
        value = game.evaluate_value()
        logs.append(
            [get_pretty_node(node), str(depth), check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        return [value, node]
    value = [-999999, None]
    final_move = None
    moves = game.generate_moves(player)
    # print moves
    if "pcount" in kwargs:
        if kwargs['pcount'] == 2:
            value = [game.evaluate_value(), None]
    logs.append([get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    if len(moves) == 0:
        if "pcount" in kwargs:
            if kwargs['pcount'] < 2:
                if node == "root":
                    final_move = "pass"
                new_game = Game(player, player_start, depth, game=game)
                if player == "X":
                    player = "O"
                else:
                    player = "X"
                if "pcount" in kwargs:
                    pcount = kwargs['pcount'] + 1
                else:
                    pcount = 1
                new_value = min_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, "pass", logs, pcount=pcount)
                if value[0] < new_value[0]:
                    value[0] = new_value[0]
                    value[1] = new_value[1]
                if value[0] >= beta:
                    logs.append(
                        [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
                    value.extend([final_move])
                    return value
                alpha = max(alpha, value[0])
                logs.append(
                    [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    original_player = deepcopy(player)
    if player == "X":
        player = "O"
    else:
        player = "X"
    for move in moves:
        new_game = Game(original_player, player_start, depth, move=move, game=game)
        new_value = min_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, move, logs, pcount=0)
        if value[0] < new_value[0]:
            value[0] = new_value[0]
            value[1] = new_value[1]
            if node == "root":
                final_move = move
        """
        logs.append(
            [get_pretty_node(move), depth + 1, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        """
        if value[0] >= beta:
            logs.append(
                [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
            value.extend([final_move])
            return value
        alpha = max(alpha, value[0])
        logs.append([get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    if node == "root" and value[0] == -999999:
        logs[-1][2] = game.evaluate_value()
    value.extend([final_move])
    return value


def min_value(game, player, player_start, depth, max_depth, alpha, beta, node, logs, **kwargs):
    if max_depth - depth <= 0:  # or len(game.get_positions()[player]) == 0:
        value = game.evaluate_value()
        logs.append(
            [get_pretty_node(node), str(depth), check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        return [value, node]
    value = [999999, None]
    moves = game.generate_moves(player)
    # print moves
    if "pcount" in kwargs:
        if kwargs['pcount'] == 2:
            value = [game.evaluate_value(), None]
    logs.append([get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    if len(moves) == 0:
        if "pcount" in kwargs:
            if kwargs['pcount'] < 2:
                new_game = Game(player, player_start, depth, game=game)
                if player == "X":
                    player = "O"
                else:
                    player = "X"
                # logs.append(["pass", str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
                if "pcount" in kwargs:
                    pcount = kwargs['pcount'] + 1
                else:
                    pcount = 1
                new_value = max_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, "pass", logs, pcount=pcount)
                if value[0] > new_value[0]:
                    value[0] = new_value[0]
                    value[1] = new_value[1]
                if value[0] <= alpha:
                    logs.append(
                        [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
                    return value
                beta = min(beta, value[0])
                logs.append(
                    [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    original_player = deepcopy(player)
    if player == "X":
        player = "O"
    else:
        player = "X"
    for move in moves:
        new_game = Game(original_player, player_start, depth, move=move, game=game)
        new_value = max_value(new_game, player, player_start, depth + 1, max_depth, alpha, beta, move, logs, pcount=0)
        if value[0] > new_value[0]:
            value[0] = new_value[0]
            value[1] = new_value[1]
        """
        logs.append(
            [get_pretty_node(move), depth + 1, check_infinity(value), check_infinity(alpha), check_infinity(beta)])
        """
        if value[0] <= alpha:
            logs.append(
                [get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
            return value
        beta = min(beta, value[0])
        logs.append([get_pretty_node(node), str(depth), check_infinity(value[0]), check_infinity(alpha), check_infinity(beta)])
    return value


def output_file(board, logs):
    with open("output.txt", "w") as file_handler:
        for row in board:
            result_row = ""
            for col in row:
                if col is None:
                    result_row += "*"
                else:
                    result_row += col
            file_handler.write(result_row + "\n")
        file_handler.write("Node,Depth,Value,Alpha,Beta")
        for log in logs:
            result_row = ",".join(log)
            file_handler.write("\n" + result_row)


if __name__ == '__main__':
    lines = []
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [line.strip() for line in lines]
    reversi_game = Game(lines[0], lines[0], int(lines[1]), lines[2: len(lines)], root=True)
    alpha_beta(reversi_game, lines[0], lines[0], 0, int(lines[1]), -999999, 999999)