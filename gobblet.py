from collections import namedtuple
from copy import deepcopy
from functools import total_ordering


#import math
#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4

class Winner(Exception):
    def __init__(self, player):
        self.player = player


class Board(object):

    """
    Represents the game board, grid of cells,
    with each cell represented as a stack of players' pieces.
    """

    def __init__(self, size):
        self.size = size

        # Create the grid of cells, each cell is a stack (python list).
        self.cells = []
        for row_i in range(size):
            row = []
            self.cells.append(row)

            for col in range(size):
                row.append([])

    def get_column(self, col):
        return [self.cells[row][col] for row in range(self.size)]

    def get_cell(self, pos):
        row, col = pos
        return self.cells[row][col]


@total_ordering
class Piece(object):

    """
    Represents a player's piece.
    
    A piece has a player and a size.
    Pieces are comparable by size:

    >>> a = Piece('player 1', 10)
    >>> b = Piece('player 1', 20)
    >>> b > a
    True
    """

    def __init__(self, player, size):
        self.player = player
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

    """
    Represents a player's pieces that are not on the board.

    Dugout creates the Piece instances.

    Dugout stores pieces as a list of stacks,
    (which in Python is a list of lists really):
    
        sizes = [extra_small, small, large, extra_large]
        num_stacks = 3
        pieces = [
            [extra_small, small, large, extra_large],
            [extra_small, small, large, extra_large],
            [extra_small, small, large, extra_large],
        ]
    
    The example dugout has four sizes, and three stacks holding pieces of
    those sizes, so twelve total pieces in the dugout.
    
    Pieces must be accessed in order, from largest to smallest,
    i.e. popped off each stack.
    """

    Piece = Piece

    class NoSuchPiece(Exception): pass

    def __init__(self, player, sizes, num_stacks):
        self.pieces = []
        for x in range(num_stacks):
            stack = []
            self.pieces.append(stack)

            for size in sizes:
                piece = self.Piece(player, size)
                stack.append(piece)

    def available_pieces(self):
        available = []
        for stack in self.pieces:
            if stack:
                available.append(stack[-1])
        return available

    def use_piece(self, piece):
        if piece not in self.available_pieces():
            raise self.NoSuchPiece(piece)

        for stack in self.pieces:
            if stack and stack[-1] == piece:
                return stack.pop()


def DugoutAPI(dugout):
    """
    Provides a public API that can be used by Players instances.

    While not strictly necessary, it's nice to not worry about the players
    messing with the board data structure.
    """
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
    """
    Provides a public API that can be used by Players instances.

    While not strictly necessary, it's nice to not worry about the players
    messing with the board data structure.
    """

    Move = namedtuple('Move', 'src dest')

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
    # 0 is the smallest, 3 the biggest
    PIECE_SIZES = [0, 1, 2, 3]
    NUM_STACKS = 3

    DugoutAPI = DugoutAPI
    BoardAPI = BoardAPI

    def _Player(self, ID, algorithm):
        """
        Represents a player.

        A player is given an algorithm, which is called on the player's turn,
        and determines how the player's pieces will be moved during that turn.

        A player is given a reference to a Board and a Dugout.

        Player provides a public API to it's algorithm, that allows the algorithm
        to inspect the board and dugout, and make a move without having full access
        to the game data. Hopefully this prevents algorithms for cheating and from
        making invalid moves (whether purposefully or accidentally).
        """
        dugout = self.Dugout(ID, algorithm, self.PIECE_SIZES, self.NUM_STACKS)

        def move():
            # TODO do I need to create an API every move?
            dugout_API = self.DugoutAPI(dugout)
            board_API = self.BoardAPI(self.board)

            algorithm(dugout_API, board_API)

            dugout_move = dugout_API.move
            board_move = board_API.get_move()

            return dugout_move, board_move

        return move

    def __init__(self, white, black):
        self.board = Board(BOARD_SIZE)

        self.white = self._Player('white', white)
        self.black = self._Player('black', black)

        self.on_deck = self.white


    def _not_on_deck(self):
        return self.white if self.black is self.on_deck else self.black


    def _validate(self, dugout_move, board_move):
        """
        Validate the given moves.
        """
        def _invalid(msg):
            raise InvalidMove(msg)

        if board_move.src is not None and dugout_move is not None:
            _invalid("Can't have both a board source and a dugout source")

        if board_move.src is not None:
            src = self.board.get_cell(board_move.src)

            if not src:
                _invalid("Board source is empty")

            src_piece = src[-1]

            if src_piece.player != self.ID:
                _invalid("Can't move other player's piece")

        elif dugout_move is not None:
            if dugout_move not in self.dugout.available_pieces():
                _invalid("Invalid dugout piece")

            src_piece = dugout_move

        else:
            _invalid("No source given.")

        if board_move.dest is None:
            _invalid("No destination given.")

        dest = self.board.get_cell(board_move.dest)

        if dest and dest[-1] >= src_piece:
            _invalid("Can't cover a piece of equal or larger size")


    def _check_win(self, board):
        """
        Check for a win by either player.
        """

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

                diagonal_a.append(board.cells[i][i])
                diagonal_b.append(board.cells[board.size - i - 1][i])

            # The two diagonals
            yield diagonal_a
            yield diagonal_b

        for cells in gen_cells_to_check():
            winner = check_cells(cells)
            if winner:
                return winner


    def _commit(self, dugout_move, board_move):
        """
        Commit the moves to the board.

        This does *not* validate moves.

        This checks for a win. It's necessary to check for a win here
        because a win can come during the middle of a move.
        """
        # Commit dugout
        if dugout_move is not None:
            self.dugout.use_piece(dugout_move)
            piece = dugout_move

        # Commit board
        if board_move.src is not None:
            piece = self.board.get_cell(board_move.src).pop()

        # It's possible for a player to win in the middle of a move,
        # if the piece being moved exposes a win for the other player.
        # TODO or is it *either* player?
        # TODO check for opponent win only?
        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)

        self.board.get_cell(board_move.dest).append(piece)

        winner = self._check_win(self.board)
        if winner:
            raise Winner(winner)


    def tick(self):
        """
        Invoke one move from the current player.
        """
        try:
            self.on_deck()
        except Forfeit:
            return self._not_on_deck()
        except Winner as e:
            return e.player

        self.on_deck = self._not_on_deck()


    def play(self):
        """
        Invoke moves until the game is won.
        """
        # TODO this doesn't protect against moves that take too long.
        while True:
            self.tick()


def random_player(board, dugout): pass
