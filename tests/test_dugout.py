from copy import deepcopy
import unittest

import gobblet


class DugoutTestCase(unittest.TestCase):

    def setUp(self):
        player = 'sally'
        sizes = gobblet.Sizes.all
        num_stacks = 2
        self.dugout = gobblet.Dugout(player, sizes, num_stacks)

    def assertPieces(self, pieces, expected):
        for piece, expect in zip(pieces, expected):
            player, size = expect
            self.assertEqual(piece.player, player)
            self.assertEqual(piece.size, size)

    def test_init(self):
        expected_stack = [
            ('sally', gobblet.Sizes.xs),
            ('sally', gobblet.Sizes.sm),
            ('sally', gobblet.Sizes.lg),
            ('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(len(self.dugout.stacks), 2)
        self.assertPieces(self.dugout.stacks[0], expected_stack)
        self.assertPieces(self.dugout.stacks[1], expected_stack)

    def test_available_pieces(self):
        expected_pieces = [
            ('sally', gobblet.Sizes.xl),
            ('sally', gobblet.Sizes.xl),
        ]
        self.assertPieces(self.dugout.available, expected_pieces)

        self.dugout.stacks[0].pop()

        expected_pieces = [
            ('sally', gobblet.Sizes.lg),
            ('sally', gobblet.Sizes.xl),
        ]
        self.assertPieces(self.dugout.available, expected_pieces)

    def test_use_piece(self):
        piece = self.dugout.available[0]
        self.dugout.use_piece(piece)

        expected_pieces = [
            ('sally', gobblet.Sizes.lg),
            ('sally', gobblet.Sizes.xl),
        ]
        self.assertPieces(self.dugout.available, expected_pieces)

        piece = self.dugout.available[1]
        self.dugout.use_piece(piece)

        expected_pieces = [
            ('sally', gobblet.Sizes.lg),
            ('sally', gobblet.Sizes.lg),
        ]
        self.assertPieces(self.dugout.available, expected_pieces)

        self.dugout.stacks[0] = []

        expected_pieces = [
            ('sally', gobblet.Sizes.lg),
        ]
        self.assertPieces(self.dugout.available, expected_pieces)

    def test_NoSuchPiece(self):
        # Get a piece from the bottom of a stack
        piece = self.dugout.stacks[0][0]

        with self.assertRaises(self.dugout.NoSuchPiece):
            self.dugout.use_piece(piece)


if __name__ == '__main__':
    unittest.main()
