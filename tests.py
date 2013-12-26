from copy import deepcopy
import unittest

import gobblet


class BoardTestCase(unittest.TestCase):

    def test_init(self):
        board = gobblet.Board(4)
        self.assertEqual(len(board.cells), 4)

        row_lens = [len(row) for row in board.cells]
        self.assertEqual(row_lens, [4, 4, 4, 4])

    def test_default_item(self):
        board = gobblet.Board(4)
        self.assertEqual(board.cells[0][0], [])

    def test_get_column(self):
        board = gobblet.Board(4)
        board.cells[0][1].append('foo')
        board.cells[3][1].append('bar')
        self.assertEqual(board._get_column(1), [['foo'], [], [], ['bar']])

    def test_get_cell(self):
        board = gobblet.Board(4)
        board.cells[0][1].append('foo')
        self.assertEqual(board.get_cell((0, 1)), ['foo'])


class PieceTestCase(unittest.TestCase):

    def test_piece(self):
        large = gobblet.Piece('player', 'large', 3)
        large_2 = gobblet.Piece('player two', 'large two', 3)
        small = gobblet.Piece('player', 'small', 1)
        # TODO maybe remove total_ordering on Pieces
        #      could just use the more explicit "a.size > b.size"
        self.assertTrue(large > small)
        self.assertTrue(small < large)
        self.assertTrue(large_2 == large)


class PieceAssertions(object):
    def assertPieces(self, piece_list, player, names, sizes):
        self.assertEqual(len(piece_list), len(names))

        names = []
        size_values = []
        for piece in piece_list:
            names.append(piece.name)
            size_values.append(piece.size)
            self.assertEqual(piece.player, player)

        self.assertEqual(names, names)
        self.assertEqual(size_values, sizes)

    def assertAvailable(self, dugout, *args):
        available = dugout.available_pieces()
        self.assertPieces(available, *args)


class DugoutTestCase(unittest.TestCase, PieceAssertions):

    def setUp(self):
        player = 'sally'
        size_names = ['small', 'medium', 'large']
        num_stacks = 2
        self.dugout = gobblet.Dugout(player, size_names, num_stacks)

    def assertAvailable(self, *args):
        PieceAssertions.assertAvailable(self, self.dugout, 'sally', *args)
        
    def test_init(self):
        expected_names = ['small', 'medium', 'large']
        expected_sizes = [0, 1, 2]
        for stack in self.dugout.pieces:
            self.assertPieces(stack, 'sally', expected_names, expected_sizes)

    def test_available_pieces(self):
        self.assertAvailable(['large', 'large'], [2, 2])

        self.dugout.pieces[0].pop()
        self.assertAvailable(['medium', 'large'], [1, 2])

    def test_use_piece(self):
        self.dugout.use_piece(2)
        self.assertAvailable(['medium', 'large'], [1, 2])

        self.dugout.use_piece(2)
        self.assertAvailable(['medium', 'medium'], [1, 1])

        self.dugout.use_piece(self.dugout.available_pieces()[0])
        self.assertAvailable(['small', 'medium'], [0, 1])

        self.dugout.use_piece(self.dugout.available_pieces()[0])
        self.assertAvailable(['medium'], [1])

    def test_use_piece_copy(self):
        # The Player class has a DugoutAPI that copies the pieces to avoid
        # public modification of internal game state, so it's important
        # that the Player class can call Dugout.use_piece() with a copy
        # of the original piece.
        piece = self.dugout.available_pieces()[0]
        piece_copy = deepcopy(piece)

        self.dugout.use_piece(piece_copy)

        self.assertAvailable(['medium', 'large'], [1, 2])

    def test_NoSuchPiece(self):
        with self.assertRaises(self.dugout.NoSuchPiece):
            self.dugout.use_piece(3)

        self.dugout.pieces[0] = []
        with self.assertRaises(self.dugout.NoSuchPiece):
            self.dugout.use_piece(0)



class PlayerTestCase(unittest.TestCase, PieceAssertions):

    def noop(self): pass

    def setUp(self):
        self.board = gobblet.Board(4)
        self.sizes = ['small', 'large']
        self.player = gobblet.Player(self.noop, self.board, self.sizes, 2)
        
    def test_init(self):
        # The player given to the Dugout is an object ID. This allows
        # the Dugout pieces to be easily copied and still compare to
        # the original player.
        piece = self.player.dugout.pieces[0][0]
        self.assertEqual(piece.player, id(self.player))

    def test_DugoutAPI(self):
        api = self.player._DugoutAPI()

        expected_names = ['large', 'large']
        expected_sizes = [1, 1]
        self.assertAvailable(api, id(self.player), ['large'] * 2, [1] * 2)

        self.assertIsNone(api.move)

        piece = api.available_pieces()[0]
        # The piece is copied, so they API piece and the internal piece
        # are _not_ the same piece (identity-wise).
        # This prevents public modification of internal game state.
        self.assertIsNot(piece, self.player.dugout.available_pieces()[0])

        api.use_piece(piece)

        self.assertIs(api.move, piece)

        # No access to internal dugout
        with self.assertRaises(AttributeError):
            api.pieces

    def test_BoardAPI(self):
        board = self.board
        api = self.player._BoardAPI()

        self.assertEqual(api.size, 4)

        self.assertEqual(api.get_move(), (None, None))

        api.set_move((0, 0), (0, 1))
        self.assertEqual(api.get_move(), ((0, 0), (0, 1)))

        # Note that set_move() doesn't actually change the board.
        self.assertEqual(api.get_cell((0, 1)), [])

        board.cells[1][1].append(1)
        self.assertEqual(api.get_cell((1, 1)), [1])

        # Public modification of the internal board via the API is prevented.
        api.get_cell((2, 2)).append(3)
        self.assertEqual(board.cells[2][2], [])



'''
    def test_has_valid_move(self):
        board = gobblet.Board(4)

        # next_move defaults to None, so there is no valid move
        self.assertFalse(board.has_valid_move())

        # Set a valid move that adds piece of size 0 to an empty cell
        board.set_move((0, 0), 0, 'player')
        self.assertTrue(board.has_valid_move())

        # Set a valid move that adds a piece of size 1 to a cell with a
        # piece of size 0
        board.cells[0][0].append((0, 'player'))
        board.set_move((0, 0), 1, 'player')
        self.assertTrue(board.has_valid_move())

        # Now set an invalid move, where the piece is smaller than
        # the piece already in that cell.
        board.cells[0][0].append((2, 'player'))
        board.set_move((0, 0), 0, 'player')
        self.assertFalse(board.has_valid_move())

    def test_commit(self):
        board = gobblet.Board(4)
        board.set_move((0, 0), 3, 'player')
        board.commit()
        self.assertEqual(board.cells[0][0], [(3, 'player')])
'''
        


if __name__ == '__main__':
    unittest.main()
