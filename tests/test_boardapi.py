import unittest

import gobblet


class BoardAPITestCase(unittest.TestCase):
    def test_BoardAPI(self):
        board = gobblet.Board(4)
        api = gobblet.BoardAPI(board)

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


if __name__ == '__main__':
    unittest.main()
