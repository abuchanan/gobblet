from collections import namedtuple
import unittest

from mock import Mock

import gobblet


class GameTestCase(unittest.TestCase):
    def test_tick_calls_alternating_algorithms(self):

        def white_alg(board, dugout):
            return dugout.available[0], (0, 0)

        def black_alg(board, dugout):
            return dugout.available[0], (0, 1)

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
            return dugout.available[0], (0, 0)

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

    def test_horizontal_win(self):
        game = gobblet.Game(Mock(), Mock())

        for x in range(game.board.size):
            piece = game.white.dugout.available.pop()
            game.white.dugout.use_piece(piece)
            game.board.cells[0][x].append(piece)

        self.assertTrue(game._check_win(game.board))

    def test_vertical_win(self):
        game = gobblet.Game(Mock(), Mock())

        for x in range(game.board.size):
            piece = game.white.dugout.available.pop()
            game.white.dugout.use_piece(piece)
            game.board.cells[x][0].append(piece)

        self.assertTrue(game._check_win(game.board))

    def test_diagonal_a_win(self):
        game = gobblet.Game(Mock(), Mock())
        board = game.board
        piece = game.white.dugout.available[0]

        board.cells[0][0].append(piece)
        board.cells[1][1].append(piece)
        board.cells[2][2].append(piece)
        board.cells[3][3].append(piece)

        self.assertTrue(game._check_win(board))

    def test_diagonal_b_win(self):
        game = gobblet.Game(Mock(), Mock())
        board = game.board
        piece = game.white.dugout.available[0]

        board.cells[0][3].append(piece)
        board.cells[1][2].append(piece)
        board.cells[2][1].append(piece)
        board.cells[3][0].append(piece)

        self.assertTrue(game._check_win(board))


    def test_not_win(self):
        game = gobblet.Game(Mock(), Mock())
        board = game.board
        piece = game.white.dugout.available[0]

        self.assertFalse(game._check_win(board))

        board.cells[0][0].append(piece)
        board.cells[0][1].append(piece)
        board.cells[0][2].append(piece)

        piece = game.black.dugout.available[0]
        board.cells[0][3].append(piece)

        self.assertFalse(game._check_win(board))

    def test_commit_winner(self):
        game = gobblet.Game(Mock(), Mock())
        board = game.board
        piece = game.white.dugout.available[0]

        for x in range(board.size - 1):
            board.cells[0][x].append(piece)

        with self.assertRaises(gobblet.Winner) as cm:
            game._commit(game.white, piece, (0, 3))

        self.assertEqual(cm.exception.player, 'white')
            
    def test_winner_in_middle_of_move(self):
        game = gobblet.Game(Mock(), Mock())
        board = game.board

        white_piece = game.white.dugout.available[0]

        board.cells[0][0].append(white_piece)
        board.cells[0][1].append(white_piece)
        board.cells[0][2].append(white_piece)
        board.cells[0][3].append(white_piece)

        # This is the important part. In this cell, black is covering
        # white's piece. When black lifts up the piece, it will
        # reveal white A's win.
        black_piece = game.black.dugout.available[0]
        game.black.dugout.use_piece(black_piece)
        board.cells[0][3].append(black_piece)

        with self.assertRaises(gobblet.Winner) as cm:
            # Here black lifts up the piece at (0, 3) with the intention
            # of moving it somewhere else, but in the middle of the move
            # white wins.
            game._commit(game.black, black_piece, (0, 0))

        self.assertEqual(cm.exception.player, 'white')


class InvalidTestCase(unittest.TestCase):
    """Test cases where the player algorithm returns an invalid move"""

    def test_bad_return_value(self):
        pass

    def test_source_piece_is_None(self):
        def alg(board, dugout):
            return None, (0, 0)

        game = gobblet.Game(alg, Mock())

        regexp = 'Must provide a source piece'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_destination_is_None(self):
        def alg(board, dugout):
            return dugout.available[0], None

        game = gobblet.Game(alg, Mock())

        regexp = 'Must provide a destination'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_destination_out_of_bounds(self):
        def alg(board, dugout):
            return dugout.available[0], (5, 5)

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

    def test_cover_piece_of_equal_or_larger_size(self):
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

    def test_dugout_source_piece_not_available(self):
        def alg(board, dugout):
            # Trying to move a piece from the bottom of a stack
            # i.e. you can only move the piece off the top of the stack.
            piece = dugout.stacks[0][0]
            return piece, (0, 0)

        game = gobblet.Game(alg, Mock())

        regexp = 'Source piece is not available'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()

    def test_move_other_players_piece(self):
        piece = None

        def alg(board, dugout):
            # White algorithm tries to use black's piece
            return piece, (0, 0)

        game = gobblet.Game(alg, Mock())

        piece = game.black.dugout.available[0]

        regexp = 'Source piece is not available'
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            game.tick()


class SimulationTestCase(unittest.TestCase):

    def _init_simulation(self):
        def player_algorithm(board, dugout):
            return self.next_move(board, dugout)

        game = gobblet.Game(player_algorithm, player_algorithm)
        return game

    def _recursive_copy_list(self, src):
        if isinstance(src, list):
            return list(map(self._recursive_copy_list, src))
        return src

    def test_simulation(self):

        game = self._init_simulation()

        # Get a copy of the dugout stacks for each player and the board
        # so we can use them in assertions to check game state.
        white_pieces = self._recursive_copy_list(game.white.dugout.stacks)
        black_pieces = self._recursive_copy_list(game.black.dugout.stacks)
        board = self._recursive_copy_list(game.board.cells)

        def tick_and_check_state():
            game.tick()

            # Check that the game's board matches our copy of the board
            # i.e. that the game's board matches what we expect
            self.assertEqual(game.board.cells, board)

            # Check the same for the player dugout stacks
            self.assertEqual(game.white.dugout.stacks, white_pieces)
            self.assertEqual(game.black.dugout.stacks, black_pieces)


        # White's turn. Move from dugout to (0, 0)
        self.next_move = lambda b, d: (d.available[0], (0, 0))
        moved_piece = white_pieces[0].pop()
        board[0][0].append(moved_piece)

        tick_and_check_state()

        # Black's turn. Move from dugout to (1, 1)
        self.next_move = lambda b, d: (d.available[0], (1, 1))
        moved_piece = black_pieces[0].pop()
        board[1][1].append(moved_piece)

        tick_and_check_state()

        # White's turn. Move from (0, 0) to (2, 2)
        # TODO wow, that board cell reference API sucks!
        self.next_move = lambda b, d: (b.cells[0][0][-1], (2, 2))
        moved_piece = board[0][0].pop()
        board[2][2].append(moved_piece)

        tick_and_check_state()



if __name__ == '__main__':
    unittest.main()
