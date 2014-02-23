from copy import deepcopy
import unittest

import gobblet


class DugoutTestCase(unittest.TestCase):

    def setUp(self):
        player = 'sally'
        sizes = gobblet.Sizes.all
        num_stacks = 2
        self.dugout = gobblet.Dugout(player, sizes, num_stacks)

    def test_init(self):
        expected_stack = [
            gobblet.Piece('sally', gobblet.Sizes.xs),
            gobblet.Piece('sally', gobblet.Sizes.sm),
            gobblet.Piece('sally', gobblet.Sizes.lg),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        expected_stacks = [expected_stack] * 2
        self.assertEqual(self.dugout.stacks, expected_stacks)

    def test_available_pieces(self):
        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.xl),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

        self.dugout.stacks[0].pop()

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.lg),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

    def test_use_piece(self):
        piece = gobblet.Piece('sally', gobblet.Sizes.xl)
        self.dugout.use_piece(piece)

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.lg),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

        piece = gobblet.Piece('sally', gobblet.Sizes.xl)
        self.dugout.use_piece(piece)

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.lg),
            gobblet.Piece('sally', gobblet.Sizes.lg),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

        self.dugout.stacks[0] = []

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.lg),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

    def test_use_piece_copy(self):
        # The Player class has a DugoutAPI that copies the pieces to avoid
        # public modification of internal game state, so it's important
        # that the Player class can call Dugout.use_piece() with a copy
        # of the original piece.
        piece = self.dugout.available_pieces()[0]
        piece_copy = deepcopy(piece)

        self.dugout.use_piece(piece_copy)

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.lg),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(self.dugout.available_pieces(), expected_pieces)

    def test_NoSuchPiece(self):
        piece = gobblet.Piece('sally', gobblet.Sizes.xs)

        with self.assertRaises(self.dugout.NoSuchPiece):
            self.dugout.use_piece(piece)


if __name__ == '__main__':
    unittest.main()
