from collections import namedtuple
import unittest

from mock import Mock

import gobblet


class GameTestCase(unittest.TestCase):
    def test_tick_calls_alternating_algorithms(self):

        def white_alg(board, dugout):
            return dugout.available_pieces()[0], (0, 0)

        def black_alg(board, dugout):
            return dugout.available_pieces()[0], (0, 1)

        white_alg = Mock(wraps=white_alg)
        black_alg = Mock(wraps=black_alg)

        game = gobblet.Game(white_alg, black_alg)
        self.assertEqual(game.on_deck, game.white)

        # Mock out Game._validate and Game._commit
        # because we don't really care about valid moves in this test,
        # only that the current player's algorithm gets called.
        game._validate = Mock()
        game._commit = Mock()

        game.tick()

        self.assertTrue(white_alg.called)
        self.assertFalse(black_alg.called)

        white_alg.reset_mock()
        black_alg.reset_mock()
        game.tick()

        self.assertTrue(black_alg.called)
        self.assertFalse(white_alg.called)

    def test_winner(self):
        white_alg = Mock()
        black_alg = Mock()

        game = gobblet.Game(white_alg, black_alg)

        # Mock out the Game.move() function
        # because we don't really care about valid moves in this test,
        # only what happens when that function declares a winner.
        game.move = Mock()
        self.assertEqual(game.tick(), None)

        black_winner = gobblet.Winner(game.black)
        game.move.side_effect = black_winner

        self.assertEqual(game.tick(), game.black)

    def test_forfeit(self):
        def white_alg(board, dugout):
            return dugout.available_pieces()[0], (0, 0)

        white_alg = Mock(wraps=white_alg)

        # When it's black's turn, the player will forfeit and white should win
        black_alg = Mock(side_effect=gobblet.Forfeit)

        game = gobblet.Game(white_alg, black_alg)

        # Mock out Game._validate and Game._commit
        # because we don't really care about valid moves in this test,
        # only what happens when an algorithm declares a forfeit.
        game._validate = Mock()
        game._commit = Mock()

        self.assertEqual(game.tick(), None)
        self.assertEqual(game.tick(), game.white)

    def test_simple_valid_move(self):

        def white_alg(board, dugout):
            return dugout.available_pieces()[0], (0, 0)

        black_alg = Mock()

        game = gobblet.Game(white_alg, black_alg)
        game._validate = Mock(wraps=game._validate)
        game._commit = Mock(wraps=game._commit)

        piece = game.white.dugout.available_pieces()[0]

        game.tick()

        args = game.white, piece, (0, 0)
        game._validate.assert_called_once_with(*args)
        game._commit.assert_called_once_with(*args)

        self.assertEqual(game.board.cells, [
            [[piece], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])


class ValidationTestCase(unittest.TestCase):

    def test_invalid_return_value(self):
        pass

    def test_invalid_source_piece_is_None(self):
        def alg(board, dugout):
            return None, (0, 0)

        game = gobblet.Game(alg, Mock())

        regexp = 'Must provide a source piece'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_invalid_destination_is_None(self):
        def alg(board, dugout):
            return dugout.available_pieces()[0], None

        game = gobblet.Game(alg, Mock())

        regexp = 'Must provide a destination'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_invalid_destination_out_of_bounds(self):
        def alg(board, dugout):
            return dugout.available_pieces()[0], (5, 5)

        game = gobblet.Game(alg, Mock())

        regexp = 'Invalid destination'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_move_piece_to_same_cell(self):
        def alg(board, dugout):
            # Try to move a piece to the same cell
            return board.cells[0][0][0], (0, 0)

        game = gobblet.Game(alg, Mock())

        # Place a piece at (0, 0)
        piece = game.white.dugout.stacks[0].pop()
        game.board.cells[0][0].append(piece)

        regexp = "Cannot move a piece to the same cell"
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_invalid_cover_piece_of_equal_or_larger_size(self):
        def alg(board, dugout):
            # Try to move a smaller piece at (0, 0)
            # to cover a larger piece at (0, 1)
            return board.cells[0][0][0], (0, 1)

        game = gobblet.Game(alg, Mock())

        # Place the largest piece at (0, 1)
        piece = game.white.dugout.stacks[0].pop()
        game.board.cells[0][1].append(piece)

        # Now place a smaller piece at (0, 0)
        piece = game.white.dugout.stacks[0].pop()
        game.board.cells[0][0].append(piece)

        regexp = "Can't cover a piece of equal or larger size"
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_invalid_dugout_source_piece(self):
        def alg(board, dugout):
            piece = dugout.stacks[0][0]
            return piece, (0, 0)

        game = gobblet.Game(alg, Mock())

        regexp = 'Source piece is not available'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_invalid_move_other_players_piece(self):
        piece = None

        def alg(board, dugout):
            return piece, (0, 0)

        game = gobblet.Game(alg, Mock())

        piece = game.black.dugout.available_pieces()[0]

        regexp = 'Source piece is not available'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def todo(self):
        # Invalid dugout piece
        bottom_piece = self.player.dugout.pieces[0][0]

        self.assertInvalidMove(bottom_piece, None, (0, 0),
                               "Invalid dugout piece")

        # No source 
        self.assertInvalidMove(None, None, None, 'No source')

        # Move a piece from the dugout to the board
        piece = self.player.dugout.available_pieces()[0]
        self.player.dugout.use_piece(piece)

        board.cells[0][0].append(piece)

        # No destination
        self.assertInvalidMove(None, (0, 0), None, 'No destination')

        # Make a piece owned by some other player and add it to the board
        other_players_piece = deepcopy(piece)
        other_players_piece.player = 'foo'

        board.cells[1][1].append(other_players_piece)

        self.assertInvalidMove(None, (1, 1), (2, 2), "other player's piece")

        # Add a small piece to the board
        small_piece = deepcopy(piece)
        small_piece.size = piece.size - 1

        board.cells[2][2].append(small_piece)

        self.assertInvalidMove(None, (2, 2), (0, 0),
                               'piece of equal or larger size')

        # Source and destination cannot be the same

        self.assertInvalidMove(None, (0, 0), (0, 0),
                               'piece of equal or larger size')

        # Valid moves
        # Remember, these moves don't modify the state of the board,
        # so try not to think of these as actually moving pieces,
        # just validating possible moves.

        # Take a large piece from the dugout and place it on an empty cell
        self.assertValidMove(1, None, (0, 1))

        # Take a small piece from the dugout and place it on an empty cell
        self.assertValidMove(0, None, (0, 2))

        # Move a large piece to an empty cell
        self.assertValidMove(None, (0, 0), (0, 3))

        # Move a small piece to an empty cell
        self.assertValidMove(None, (2, 2), (0, 3))

        # Move a large piece over an small piece
        self.assertValidMove(None, (0, 0), (2, 2))


if __name__ == '__main__':
    unittest.main()
