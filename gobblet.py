from collections import namedtuple
from copy import copy
from functools import total_ordering
import random


@total_ordering
class Size(object):

    """Represents the size of a piece."""

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


class Piece(object):
    def __init__(self, player, size):
        self.player = player
        self.size = size


class Stack(object):

    """
    Data structure for a stack of pieces.

    Pieces come in various sizes and can be stacked on top of each other.
    Normally, the player only interacts with the top of the stack,
    either removing the top piece with stack.pop() or add a piece
    to the top of a stack with stack.push(piece).
    """

    def __init__(self, pieces=None):
        self.pieces = pieces or []

    def __len__(self):
        return len(self.pieces)

    def __getitem__(self, key):
        return self.pieces[key]

    def __copy__(self):
        return Stack(list(self.pieces))

    def top(self):
        return self.pieces[-1]

    def push(self, piece):
        self.pieces.append(piece)

    def pop(self):
        return self.pieces.pop()


class Dugout(object):

    """
    Data structure for the pieces a player starts with, which are not
    of the board. I nicknamed these stacks of pieces the player's "dugout".

    Each player as a number of stacks of pieces which they move from the
    dugout onto the board.
    """

    class NoSuchPiece(Exception): pass

    def __init__(self, stacks):
        self.stacks = stacks

    def __copy__(self):
        stacks = list(copy(stack) for stack in self.stacks)
        return Dugout(stacks)

    @property
    def available(self):
        available = []
        for stack in self.stacks:
            try:
                available.append(stack.top())
            except IndexError:
                pass
        return available

    def use_piece(self, piece):
        for stack in self.stacks:
            try:
                if stack.top() == piece:
                    return stack.pop()
            except IndexError:
                pass

        raise self.NoSuchPiece(piece)


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
                stack = Stack()
                row.append(stack)

    def __getitem__(self, key):
        row, col = key
        return self.cells[row][col]

    def __copy__(self):
        board = Board(self.size)
        for key, cell in self:
            row, col = key
            board.cells[row][col] = copy(cell)
        return board

    def __iter__(self):
        for row_i, row in enumerate(self.cells):
            for col_i, cell in enumerate(row):
                yield (row_i, col_i), cell

    @property
    def available(self):
        available = []
        for row in self.cells:
            for cell in row:
                if cell:
                    available.append(cell[-1])
        return available

    def get_column(self, col):
        return [self.cells[row][col] for row in range(self.size)]

    def find(self, piece):
        for key, cell in self:
            try:
                if cell.top() is piece:
                    return key
            except IndexError:
                pass


class Player(object):

    def __init__(self, name):
        self.name = name

    def move(self, board, dugout):
        raise NotImplementedError()

    def __call__(self, board, dugout):
        return self.move(board, dugout)


class Forfeit(Exception): pass

class InvalidMove(Exception): pass

class Winner(Exception):
    def __init__(self, player):
        self.player = player


class Game(object):

    BOARD_SIZE = 4
    NUM_STACKS = 3

    PlayerInfo = namedtuple('PlayerInfo', 'player dugout')

    def __init__(self, white, black):
        self.board = Board(self.BOARD_SIZE)

        white_stacks = create_stacks(white, Sizes.all, self.NUM_STACKS)
        self.white_dugout = Dugout(white_stacks)

        black_stacks = create_stacks(black, Sizes.all, self.NUM_STACKS)
        self.black_dugout = Dugout(black_stacks)

        self.white = self.PlayerInfo(white, self.white_dugout)
        self.black = self.PlayerInfo(black, self.black_dugout)

        self.on_deck, self.off_deck = self.white, self.black

    def _validate(self, player, dugout, piece, dest):

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
        if (piece not in dugout.available and
            piece not in self.board.available):
            raise InvalidMove("Source piece is not available")

        try:
            dest_cell = self.board[dest]
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
                yield board.get_column(i)

                diagonal_a.append(board[i, i])

                row = board.size - i - 1
                col = i
                diagonal_b.append(board[row, col])

            # The two diagonals
            yield diagonal_a
            yield diagonal_b

        for cells in gen_cells_to_check():
            winner = check_cells(cells)
            if winner:
                return winner

    def _commit(self, player, dugout, piece, dest):
        try:
            dugout.use_piece(piece)
        except dugout.NoSuchPiece:
            pos = self.board.find(piece)
            self.board[pos].pop()

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

        self.board[dest].push(piece)

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

    def move(self, player, dugout):
        piece, dest = player(self.board, dugout)

        self._validate(player, dugout, piece, dest)
        self._commit(player, dugout, piece, dest)

    def tick(self):
        try:
            self.move(self.on_deck.player, self.on_deck.dugout)
        except Forfeit:
            return self.off_deck.player
        except Winner as e:
            return e.player

        # Swap on_deck and off_deck
        self.on_deck, self.off_deck = self.off_deck, self.on_deck



def create_stacks(player, sizes, num_stacks):
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
    # Pieces must be accessed in order, from largest to smallest,
    # i.e. popped off each stack.
    stacks = []
    for stack_i in xrange(num_stacks):
        pieces = [Piece(player, size) for size in sizes]
        stack = Stack(pieces)
        stacks.append(stack)
    return stacks


class RandomPlayer(Player):
    """
    Random movement algorithm. Seems to get stuck around turn 30-50.
    """

    def _random_cell(self, board):
        return random.randrange(board.size), random.randrange(board.size)

    def move(self, board, dugout):

        if dugout.available:
            # TODO awkward API. I tripped over this because I wasn't actually
            #      supposed to call use_piece()
            # piece = dugout.use_piece(dugout.available[0])
            piece = dugout.available[0]

            dest = self._random_cell(board)
            while len(board[dest]) and board[dest].top().size >= piece.size:
                dest = self._random_cell(board)
                
            return piece, dest

        else:
            src = self._random_cell(board)
            while not len(board[src]) or board[src].top().player is not self:
                src = self._random_cell(board)

            piece = board[src].top()

            dest = self._random_cell(board)
            while len(board[dest]) and board[dest].top().size >= piece.size:
                dest = self._random_cell(board)

            return piece, dest


if __name__ == '__main__':
    white = RandomPlayer('white')
    black = RandomPlayer('black')
    game = Game(white, black)
    turn_count = 0
    while True:
        game.tick()
        turn_count += 1
        #if turn_count % 10 == 0:
        if True:
            print 'turn count: {}'.format(turn_count)

# Rough math for calculating number of possibilities in a game
# no idea if this is correct/complete, probably not
#import math
#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4


# TODO
# - documentation about how to write a player algorithm.
# - currently there is no protection against player algorithms messing with
#   the internals of the game, such as the board or opponents data structures.
#   it's not a big deal since no one is actually using this code besides me
#   but it would be nice to make this code complete by sandboxing the player's
#   access.
# - there's probably room for improvement of the player API. something like,
#   `dugout[0].pop().move_to(board.cell)`, I don't know.
#   Something with move_to()
#   The Dugout.use_piece() method is kinda weird I feel. It'd be nice if the
#   state of the board and pieces changed behind the scenes when you made
#   a call like Piece.move_to(destination).
#   It might also be nice if the player algorithm could catch InvalidMove
#   errors? That way a random algorithm could just keep calling random_dest()
#   until it didn't catch that error?
# - Maybe Stack should do some validation in push()?
