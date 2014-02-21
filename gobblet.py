from collections import namedtuple
from copy import deepcopy
from functools import total_ordering


#import math
#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4

class Winner(Exception):
    def __init__(self, player):
        self.player = player


class Board(object):

    def __init__(self, size):
        self.size = size
        # Create a square board with "size" columns and rows,
        # where each cell is a list.
        self.cells = []
        for row_i in range(size):
            row = []
            self.cells.append(row)

            for col_i in range(size):
                row.append([])

    def _get_column(self, col):
        return [self.cells[row][col] for row in range(self.size)]

    def get_cell(self, pos):
        row, col = pos
        return self.cells[row][col]


@total_ordering
class Piece(object):
    def __init__(self, player, name, size):
        self.player = player
        self.name = name
        self.size = size

    def __eq__(self, other):
        if isinstance(other, int):
            return self.size == other
        return self.size == other.size

    def __lt__(self, other):
        if isinstance(other, int):
            return self.size < other
        return self.size < other.size


class Dugout(object):

    class NoSuchPiece(Exception): pass

    def __init__(self):
        # The "dugout" represents a player's pieces that are not on the board,
        # stored as a list of lists, e.g.
        #
        #     sizes = [extra_small, small, large, extra_large]
        #     num_stacks = 3
        #     pieces = [
        #         [extra_small, small, large, extra_large],
        #         [extra_small, small, large, extra_large],
        #         [extra_small, small, large, extra_large],
        #     ]
        #
        # The example dugout has four sizes, and three stacks holding pieces of
        # those sizes, so twelve total pieces in the dugout.
        #
        # Pieces must be accessed in order, from largest to smallest, i.e.
        # popped off each stack.
        self._stacks = []

    def add_stack(self, stack):
        self._stacks.append(list(stack))

    def available_pieces(self):
        available = []
        for stack in self._stacks:
            if stack:
                available.append(stack[-1])
        return available

    def use_piece(self, piece):
        if piece not in self.available_pieces():
            raise self.NoSuchPiece(piece)

        for stack in self._stacks:
            if stack and stack[-1] == piece:
                return stack.pop()


class Player(object):

    def __init__(self, name, algorithm):
        self.name = name
        self.algorithm = algorithm
        self.dugout = Dugout()


def DugoutAPI(dugout):

    # This is providing a public API that can be used by Players instances;
    # not strictly necessary, but it's nice to not worry about the players
    # messing with the dugout data structure.
    class _API(object):
        def __init__(api):
            api.move = None

        def available_pieces(api):
            # Copy the pieces to prevent public modification.
            #
            # TODO a lightweight wrapper could be used instead
            #      if performance is needed, but for now it's too complex.
            return deepcopy(dugout.available_pieces())
            
        def use_piece(api, piece):
            api.move = piece
            
    return _API()


def BoardAPI(board):
    Move = namedtuple('Move', 'src dest')

    # This is providing a public API that can be used by Players instances;
    # not strictly necessary, but it's nice to not worry about the players
    # messing with the board data structure.
    class _API(object):
        def __init__(api):
            api.set_move(None, None)
            
        def get_cell(api, key):
            # Copy the cell to prevent public modification.
            #
            # TODO a lightweight wrapper could be used instead
            #      if performance is needed, but for now it's too complex.
            return deepcopy(board.get_cell(key))

        def get_move(api):
            return api._move

        def set_move(api, src, dest):
            api._move = Move(src, dest)

        @property
        def size(api):
            return board.size

    return _API()



class Forfeit(Exception): pass

class InvalidMove(Exception): pass


class Game(object):

    BOARD_SIZE = 4
    # 0 is the smallest, 3 the largest
    PIECE_SIZES = [
        ('smallest', 0),
        ('small', 1),
        ('large', 2),
        ('largest', 3),
    ]
    NUM_STACKS = 3

    def __init__(self, white_algorithm, black_algorithm):
        self.board = Board(self.BOARD_SIZE)
        self.white = self._make_player('white', white_algorithm)
        self.black = self._make_player('black', black_algorithm)
        self.on_deck, self.off_deck = self.white, self.black

    def _make_player(self, name, algorithm):
        player = Player(name, algorithm)

        for stack_i in range(self.NUM_STACKS):
            stack = []

            for name, size in self.PIECE_SIZES:
                piece = Piece(player, name, size)
                stack.append(piece)
            player.dugout.add_stack(stack)
        return player

    def _validate(self, player, dugout_move, board_move):

        def invalid(msg):
            raise InvalidMove(msg)

        if board_move.src is not None and dugout_move is not None:
            invalid("Can't have both a board source and a dugout source")

        if board_move.src is not None:
            src = self.board.get_cell(board_move.src)

            if not src:
                invalid("Board source is empty")

            src_piece = src[-1]

            if src_piece.player != player:
                invalid("Can't move other player's piece")

        elif dugout_move is not None:
            if dugout_move not in player.dugout.available_pieces():
                invalid("Invalid dugout piece")

            src_piece = dugout_move

        else:
            invalid("No source given.")

        if board_move.dest is None:
            invalid("No destination given.")

        dest = self.board.get_cell(board_move.dest)

        if dest and dest[-1] >= src_piece:
            invalid("Can't cover a piece of equal or larger size")

    def _check_win(self, board):

        def check_cells(cells):
            players = []
            for cell in cells:
                if cell:
                    players.append(cell[-1].player)
                else:
                    players.append(None)
                
            first = players[0]
            # Compare every cell after the first with the first cell
            # If they are all the same as the first, they'll all be True,
            # so all() will return True, meaning it's a win.
            if first and all(player == first for player in players):
                return first

        def gen_cells_to_check():
            # Generate the groups of cells that need to be checked:
            # each row, each column, and the two diagonals.
            diagonal_a = []
            diagonal_b = []

            for i in range(board.size):
                # Rows
                yield board.cells[i]
                # Columns
                yield board._get_column(i)

                diagonal_a.append(board.cells[i][i])
                diagonal_b.append(board.cells[board.size - i - 1][i])

            # The two diagonals
            yield diagonal_a
            yield diagonal_b

        for cells in gen_cells_to_check():
            winner = check_cells(cells)
            if winner:
                return winner

    def _commit(self, player, dugout_move, board_move):
        # Commit dugout
        if dugout_move is not None:
            player.dugout.use_piece(dugout_move)
            piece = dugout_move

        # Commit board
        if board_move.src is not None:
            piece = self.board.get_cell(board_move.src).pop()

        # TODO check for opponent win only?
        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

        self.board.get_cell(board_move.dest).append(piece)

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

    def move(self, player):
        board_API = BoardAPI(self.board)
        dugout_API = DugoutAPI(player.dugout)

        player.algorithm(board_API, dugout_API)

        board_move = board_API.get_move()
        dugout_move = dugout_API.move

        self._validate(player, dugout_move, board_move)
        self._commit(player, dugout_move, board_move)

    def tick(self):
        try:
            self.move(self.on_deck)
        except Forfeit:
            return self.off_deck
        except Winner as e:
            return e.player

        self.on_deck, self.off_deck = self.off_deck, self.on_deck


def random_player(board, dugout): pass
