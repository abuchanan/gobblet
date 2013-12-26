import math


#print sum(math.factorial(24) / (math.factorial(x) * math.factorial(24 - x)) for x in range(1, 16)) / 4

class Winner(Exception): pass

class Board(object):

    def __init__(self, size):
        self.size = size
        # This probably looks funny, but it's simply creating a square board,
        # with "size" columns and row, where each cell is a list.
        self.cells = [[[]] * size for x in range(size)]

        self._next_move = None

    def _get_column(self, col):
        return [self.cells[row][col] for row in range(self.size)]
        
    def _is_win(self):
        def check_cells(cells):
            first = cells[0]
            # Compare every cell after the first with the first cell
            # If they are all the same as the first, they'll all be True,
            # so all() will return True, meaning it's a win.
            return first and all(cell == first for cell in cells[1:])

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
                diagonal_b.append(self.cells[self.size - i - 1][i])

            # The two diagonals
            yield diagonal_a
            yield diagonal_b

        for cells in gen_cells_to_check():
            if check_cells(cells):
                piece, player = cells[0]
                return player

    def set_move(self, cell, value, player):
        self._next_move = cell, value, player

    def has_valid_move(self):
        if self._next_move is None:
            return False

        cell, piece, player = self._next_move

        row, col = cell
        target = self.cells[row][col]

        if not target:
            return True
        else:
            target_piece, target_player = target[-1]
            return piece > target_piece

    def commit(self):
        # TODO next move doesn't account for where the piece is coming _from_
        if self._next_move:
            # TODO remove piece, check for win of opponent (of opponent only?),
            #      place piece, check for win

            # Commit the move to the cell
            cell, piece, player = self._next_move
            row, col = cell
            cell_value = piece, player
            self.cells[row][col].append(cell_value)

            # Reset the next move
            self._next_move = None

    def player_API(board, player):
        # This is providing a public API that can be used by Players instances;
        # not strictly necessary, but it's nice to not worry about the players
        # messing with the board data structure.
        #
        # ...now I'm curious, is there a way around this scope closure?
        class BoardAPI(object):
            def __getitem__(api, key):
                return board.cells[key]

            def __setitem__(api, key, value):
                board.set_move(key, value, player)

            @property
            def size(api):
                return board.size

        return BoardAPI()
        

class Dugout(object):

    class NoSuchPiece(Exception): pass

    def __init__(self, sizes, num_stacks):
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
        self.pieces = [[size] * num_stacks for size in sizes]

        self.next_move = None

    def available_sizes(self):
        available = []
        for stack in self.pieces:
            if stack:
                available.append(stack[-1])
        return available

    def use_piece(self, size):
        if size not in self.available_sizes():
            raise self.NoSuchPiece(size)

        for stack in self.pieces:
            if stack and stack[-1] == size:
                return stack.pop()

    # TODO doesn't __require__ a move
    def has_valid_move(self):
        return self.next_move and self.next_move in self.available_sizes()

    def commit(self):
        if self.next_move:
            self.use_piece(self.next_move)
            self.next_move = None

    def make_player_API(dugout):

        class DugoutAPI(object):
            def available_sizes(api):
                return dugout.available_sizes()
                
            def use_piece(api, piece):
                dugout.next_move = piece
                
        return DugoutAPI()


class Forfeit(Exception): pass

class InvalidMove(Exception):
    def __init__(self, algorithm, board, dugout):
        self.algorithm = algorithm
        self.board = board
        self.dugout = dugout


def game(white_algorithm, black_algorithm):
    BOARD_SIZE = 4
    # 0 is the smallest, 3 the biggest
    PIECE_SIZES = [0, 1, 2, 3]
    NUM_PIECES = 3

    board = Board(BOARD_SIZE)

    white_board = board.make_player_API(white_algorithm)
    black_board = board.make_player_API(black_algorithm)
    
    white_dugout = Dugout(PIECE_SIZES, NUM_PIECES).make_player_API()
    black_dugout = Dugout(PIECE_SIZES, NUM_PIECES).make_player_API()

    white = white_algorithm, white_board, white_dugout
    black = black_algorithm, black_board, black_dugout

    on_deck = white
    not_on_deck = lambda: white if black is on_deck else white

    while True:
        try:
            algorithm, board, dugout = on_deck
            algorithm(board, dugout)

            if board.has_valid_move() and dugout.has_valid_move():
                dugout.commit()
                board.commit()
            else:
                raise InvalidMove(algorithm, board, dugout)

        except Forfeit:
            return not_on_deck()
        except board.Winner as e:
            return e.player

        on_deck = not_on_deck()


def random_player(board, dugout): pass
