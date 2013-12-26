import unittest

import gobblet


class BoardTestCase(unittest.TestCase):

    def test_init(self):
        board = gobblet.Board(4)
        self.assertEqual(len(board.cells), 4)

        row_lens = [len(row) for row in board.cells]
        self.assertEqual(row_lens, [4, 4, 4, 4])

        self.assertEqual(board._next_move, None)
        self.assertFalse(board.has_valid_move())
        self.assertFalse(board.is_win())

    def test_default_item(self):
        board = gobblet.Board(4)
        self.assertEqual(board.cells[0][0], [])

    def test_get_column(self):
        board = gobblet.Board(4)
        board.cells[0][1].append('foo')
        board.cells[3][1].append('bar')
        self.assertEqual(board._get_column(1), [['foo'], [], [], ['bar']])

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
        


if __name__ == '__main__':
    unittest.main()
