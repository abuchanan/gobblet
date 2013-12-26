from enum import Enum
import math


#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4


class Board(object):

    def __init__(self, size):
        self.size = size
        # This probably looks funny, but it's simply creating a square board,
        # with "size" columns and row, where each cell is a list.
        self.cells = [[[]] * size for x in range(size)]

        self.public_API = self._make_public_API()

    def _make_public_API(board):
        # This is providing a read-only public API that can be used by Players
        # instances. Probably not really necessary, but it is nice to not worry
        # about the players potentially messing with the board data structure.
        #
        # ...I wonder, is there a way around this scope closure?
        # Not that it's important, but now I'm curious...
        class BoardAPI(object):
            def __getitem__(api, key):
                row, col = key
                return board.cells[row][col]

            # TODO
            # TODO allow only one move until the game resets
            def move(api, d):
                pass

            @property
            def size(api):
                return board.size

        return BoardAPI()

    def _get_column(self, col):
        return [self.cells[row][col] for row in range(self.size)]
        
    def is_win(self):
        def check_cells(cells):
            row = self.cells[row_i]
            first = row[0]
            # Compare every cell after the first with the first cell
            # If they are all the same as the first, they'll all be True,
            # so all() will return True, meaning it's a win.
            return all(cell == first for cell in row[1:])

        def gen_cells_to_check():
            # Generate the groups of cells that need to be checked:
            # each row, each column, and the two diagonals.
            diagonal_a = []
            diagonal_b = []

            for i in range(self.size):
                # Rows
                yield self.cells[i]
                # Columns
                yield self._get_column(i)

                diagonal_a.append(self.cells[i][i])
                diagonal_b.append(self.cells[self.size - i][i])

            # The two diagonals
            yield diagonal_a
            yield diagonal_b


        for cells in gen_cells_to_check():
            if check_cells(cells):
                return True


class Player(object):
    def __init__(self, dugout, board):
        self.dugout = dugout
        self.board = board

    def move(self):
        raise NotImplemented()


class RandomPlayer(Player):
    def move(self):
        pass
        

class Dugout(object):
    def __init__(self, sizes, num_each):
        # The "dugout" represents a player's pieces that are not on the board.
        # To start, this is...
        #
        #     dugout = [
        #         ['xsmall', 'xsmall', 'xsmall'],
        #         ['small', 'small', 'small'],
        #         ['large', 'large', 'large'],
        #         ['xlarge', 'xlarge', 'xlarge'],
        #     ]
        #
        # i.e. each player has four different sizes of pieces, three of each.
        self.pieces = [[size] * num_each for size in sizes]

        self.public_API = self._make_public_API()

    def _make_public_API(self):
        class DugoutAPI(object): pass
        return DugoutAPI()


class Forfeit(Exception): pass


def game(White, Black):
    BOARD_SIZE = 4
    PIECE_SIZES = 'xsmall small large xlarge'.split()
    NUM_PIECES = 3

    board = Board(BOARD_SIZE)

    white = White(Dugout().public_API, board.public_API)
    black = Black(Dugout().public_API, board.public_API)

    on_deck = white
    not_on_deck = lambda white if black is on_deck else white

    while True:
        try:
            on_deck.move()
        except Forfeit:
            return not_on_deck()

        if board.is_win():
            return on_deck
        else:
            on_deck = not_on_deck()
