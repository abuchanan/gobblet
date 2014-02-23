import unittest

import gobblet


class DugoutAPITestCase(unittest.TestCase):
    def test_DugoutAPI(self):
        num_stacks = 2
        dugout = gobblet.Dugout('sally', gobblet.Sizes.all, num_stacks)
        api = gobblet.DugoutAPI(dugout)

        expected_pieces = [
            gobblet.Piece('sally', gobblet.Sizes.xl),
            gobblet.Piece('sally', gobblet.Sizes.xl),
        ]
        self.assertEqual(api.available_pieces(), expected_pieces)

        self.assertIsNone(api.move)

        piece = api.available_pieces()[0]
        # The piece is copied, so the API piece and the internal piece
        # are _not_ the same piece (identity-wise).
        # This prevents public modification of internal game state.
        self.assertIsNot(piece, dugout.available_pieces()[0])

        api.use_piece(piece)

        self.assertIs(api.move, piece)

        # No access to internal dugout
        with self.assertRaises(AttributeError):
            api.stacks


if __name__ == '__main__':
    unittest.main()
