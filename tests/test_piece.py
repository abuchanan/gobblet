import unittest

import gobblet


# TODO should be SizeTestCase
class PieceTestCase(unittest.TestCase):

    def test_piece(self):
        large = gobblet.Piece('player', gobblet.Sizes.lg)
        large_2 = gobblet.Piece('player two', gobblet.Sizes.lg)
        small = gobblet.Piece('player', gobblet.Sizes.sm)

        self.assertTrue(large.size > small.size)
        self.assertTrue(small.size < large.size)


if __name__ == '__main__':
    unittest.main()
