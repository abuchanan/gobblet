from collections import namedtuple
from copy import deepcopy

from mock import Mock


class PlayerTestCase(unittest.TestCase, PieceAssertions):

    def noop(self): pass

    def assertAvailable(self, dugout, *args):
        PieceAssertions.assertAvailable(self, dugout, id(self.player), *args)

    def setUp(self):
        self.BoardMove = namedtuple('Move', 'src dest')
        self.board = gobblet.Board(4)
        self.sizes = ['small', 'large']
        self.player = gobblet.Player(self.noop, self.board, self.sizes, 2)
        
    def test_init(self):
        # The player given to the Dugout is an object ID. This allows
        # the Dugout pieces to be easily copied and still compare to
        # the original player.
        piece = self.player.dugout.pieces[0][0]
        self.assertEqual(piece.player, id(self.player))

    def assertInvalidMove(self, dugout_src, board_src, board_dest, regexp):
        with self.assertRaisesRegexp(gobblet.InvalidMove, regexp):
            board_move = self.BoardMove(board_src, board_dest)
            self.player._validate(dugout_src, board_move)

    def assertValidMove(self, dugout_src, board_src, board_dest):
        board_move = self.BoardMove(board_src, board_dest)
        self.player._validate(dugout_src, board_move)

    def test_validate(self):
        board = self.board

        # Two sources
        self.assertInvalidMove(1, 2, None,
                               'both a board source and a dugout source')

        # Empty source
        self.assertInvalidMove(None, (0, 0), None, 'Board source is empty')

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

    def test_check_horizontal_win(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        for x in range(board.size):
            board.cells[0][x].append(piece)

        self.assertTrue(self.player._check_win(board))

    def test_check_vertical_win(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        for x in range(board.size):
            board.cells[x][0].append(piece)

        self.assertTrue(self.player._check_win(board))

    def test_diagonal_a_win(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        board.cells[0][0].append(piece)
        board.cells[1][1].append(piece)
        board.cells[2][2].append(piece)
        board.cells[3][3].append(piece)

        self.assertTrue(self.player._check_win(board))

    def test_diagonal_b_win(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        board.cells[0][3].append(piece)
        board.cells[1][2].append(piece)
        board.cells[2][1].append(piece)
        board.cells[3][0].append(piece)

        self.assertTrue(self.player._check_win(board))

    def test_not_win(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]
        self.assertFalse(self.player._check_win(board))

        player_a = deepcopy(piece)
        player_a.player = 'player a'

        player_b = deepcopy(piece)
        player_b.player = 'player b'

        board.cells[0][0].append(player_a)
        board.cells[0][1].append(player_a)
        board.cells[0][2].append(player_a)
        board.cells[0][3].append(player_b)

        self.assertFalse(self.player._check_win(board))

    def test_commit(self):
        piece = self.player.dugout.available_pieces()[0]

        self.player._commit(piece, self.BoardMove(None, (0, 0)))

        self.assertAvailable(self.player.dugout, ['small', 'large'], [0, 1])

        self.assertEqual(self.board.cells, [
            [[piece], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])

        self.player._commit(None, self.BoardMove((0, 0), (0, 1)))

        self.assertAvailable(self.player.dugout, ['small', 'large'], [0, 1])

        self.assertEqual(self.board.cells, [
            [[], [piece], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])

    def test_commit_winner(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        for x in range(board.size - 1):
            board.cells[0][x].append(piece)

        with self.assertRaises(gobblet.Winner) as cm:
            self.player._commit(piece, self.BoardMove(None, (0, 3)))

        self.assertEqual(cm.exception.player, id(self.player))
            
    def test_commit_no_validation(self):
        piece = self.player.dugout.available_pieces()[0]

        self.player._commit(piece, self.BoardMove(None, (0, 0)))
        # This should fail because it's trying to cover a piece
        # of equal or larger size, but it won't because _commit() doesn't do
        # any validation.
        self.player._commit(piece, self.BoardMove(None, (0, 0)))

    def test_winner_in_middle_of_move(self):
        board = self.board
        piece = self.player.dugout.available_pieces()[0]

        player_a_piece = deepcopy(piece)
        player_a_piece.player = 'player A'

        player_b_piece = deepcopy(piece)
        player_b_piece.player = self.player

        board.cells[0][0].append(player_a_piece)
        board.cells[0][1].append(player_a_piece)
        board.cells[0][2].append(player_a_piece)

        # This is the important part. In this cell, player B is covering
        # player A's piece. When player B lifts up the piece, it will
        # reveal player A's win.
        board.cells[0][3].append(player_a_piece)
        board.cells[0][3].append(player_b_piece)

        with self.assertRaises(gobblet.Winner) as cm:
            # Here player B lifts up the piece at (0, 3) with the intention
            # of moving it somewhere else, but in the middle of the move
            # player A wins.
            self.player._commit(None, self.BoardMove((0, 3), (0, 0)))

        self.assertEqual(cm.exception.player, 'player A')

    def test_alg_called_with_APIs(self):
        alg = Mock()
        player = gobblet.Player(alg, self.board, self.sizes, 2)

        board_API = player._BoardAPI()
        dugout_API = player._DugoutAPI()

        player._BoardAPI = Mock(return_value=board_API)
        player._DugoutAPI = Mock(return_value=dugout_API)

        player._validate = Mock()
        player._commit = Mock()

        player.move()
        alg.assert_called_once_with(board_API, dugout_API)