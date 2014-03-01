from collections import namedtuple
from functools import total_ordering


@total_ordering
class Size(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Size) and self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return 'Size({}, {})'.format(self.name, self.value)
        
        
class Sizes:
    xs = Size('extra small', 0)
    sm = Size('small', 1)
    lg = Size('large', 2)
    xl = Size('extra large', 3)

    all = [xs, sm, lg, xl]

#import math
#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4


class Piece(object):
    def __init__(self, player, size):
        self.player = player
        self.size = size


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

    @property
    def available(self):
        available = []
        for row in self.cells:
            for cell in row:
                if cell:
                    available.append(cell[-1])
        return available

    def find(self, piece):
        for row_i, row in enumerate(self.cells):
            for col_i, cell in enumerate(row):
                if cell and cell[-1] is piece:
                    return row_i, col_i


class Dugout(object):

    Piece = Piece

    class NoSuchPiece(Exception): pass

    def __init__(self, player, sizes, num_stacks):
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
        self.stacks = []
        for stack_i in range(num_stacks):
            stack = []
            self.stacks.append(stack)

            for size in sizes:
                piece = self.Piece(player, size)
                stack.append(piece)

    @property
    def available(self):
        available = []
        for stack in self.stacks:
            if stack:
                available.append(stack[-1])
        return available

    def use_piece(self, piece):
        if piece not in self.available:
            raise self.NoSuchPiece(piece)

        for stack in self.stacks:
            if stack and stack[-1] == piece:
                return stack.pop()



class Player(object):

    def __init__(self, name, algorithm, dugout):
        self.name = name
        self.algorithm = algorithm
        self.dugout = dugout


class Forfeit(Exception): pass

class InvalidMove(Exception): pass

class Winner(Exception):
    def __init__(self, player):
        self.player = player


class Game(object):

    BOARD_SIZE = 4
    NUM_STACKS = 3

    def __init__(self, white_algorithm, black_algorithm):
        self.board = Board(self.BOARD_SIZE)

        white_dugout = Dugout('white', Sizes.all, self.NUM_STACKS)
        self.white = Player('white', white_algorithm, white_dugout)

        black_dugout = Dugout('black', Sizes.all, self.NUM_STACKS)
        self.black = Player('black', black_algorithm, black_dugout)

        self.on_deck, self.off_deck = self.white, self.black

    def _validate(self, player, piece, dest):

        if piece is None:
            raise InvalidMove("Must provide a source piece")

        if dest is None:
            raise InvalidMove('Must provide a destination')

        try:
            dest = int(dest[0]), int(dest[1])
        except ValueError:
            raise InvalidMove("Invalid destination")

        # TODO possibly the algoritm just made a mistake referencing the piece
        #      like I just did with board.cells[0][0]
        #      (what I really wanted was board.cells[0][0][-1])
        #      make the API easier, but also give more informative errors
        #      such as "You didn't return a piece"
        if (piece not in player.dugout.available and
            piece not in self.board.available):
            raise InvalidMove("Source piece is not available")

        try:
            dest_cell = self.board.get_cell(dest)
        except IndexError:
            raise InvalidMove("Invalid destination")

        source_pos = self.board.find(piece)

        if source_pos and source_pos == dest:
            raise InvalidMove("Cannot move a piece to the same cell")

        if dest_cell and piece.size <= dest_cell[-1].size:
            raise InvalidMove("Can't cover a piece of equal or larger size")
            

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

    def _commit(self, player, piece, dest):
        try:
            player.dugout.use_piece(piece)
        except player.dugout.NoSuchPiece:
            pos = self.board.find(piece)
            self.board.get_cell(pos).pop()

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

        self.board.get_cell(dest).append(piece)

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

    def move(self, player):
        piece, dest = player.algorithm(self.board, player.dugout)

        self._validate(player, piece, dest)
        self._commit(player, piece, dest)

    def tick(self):
        try:
            self.move(self.on_deck)
        except Forfeit:
            return self.off_deck
        except Winner as e:
            return e.player

        self.on_deck, self.off_deck = self.off_deck, self.on_deck


def random_player(board, dugout): pass
