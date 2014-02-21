from collections import namedtuple
import unittest

from mock import Mock

import gobblet


class GameTestCase(unittest.TestCase):
    def test_tick_calls_alternating_algorithms(self):
        white_alg = Mock()
        black_alg = Mock()

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
        white_alg = Mock()
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
            # TODO the algorithm API sucks
            piece = dugout.available_pieces()[0]
            dugout.use_piece(piece)
            board.set_move(None, (0, 0))

        black_alg = Mock()

        game = gobblet.Game(white_alg, black_alg)
        game._validate = Mock(wraps=game._validate)
        game._commit = Mock(wraps=game._commit)

        piece = game.white.dugout.available_pieces()[0]

        game.tick()

        BoardMove = namedtuple('Move', 'src dest')

        args = game.white, piece, BoardMove(None, (0, 0))
        game._validate.assert_called_once_with(*args)
        game._commit.assert_called_once_with(*args)

        self.assertEqual(game.board.cells, [
            [[piece], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])


if __name__ == '__main__':
    unittest.main()
