import unittest

import gobblet


class BoardTestCase(unittest.TestCase):

    def test_init(self):
        board = gobblet.Board(4)
        self.assertEqual(len(board.cells), 4)

        row_lens = [len(row) for row in board.cells]
        self.assertEqual(row_lens, [4, 4, 4, 4])

    def test_default_item(self):
        board = gobblet.Board(4)
        self.assertEqual(board.cells[0][0], [])

    def test_get_column(self):
        board = gobblet.Board(4)
        board.cells[0][1].append('foo')
        board.cells[3][1].append('bar')
        self.assertEqual(board._get_column(1), [['foo'], [], [], ['bar']])

    def test_get_cell(self):
        board = gobblet.Board(4)
        board.cells[0][1].append('foo')
        self.assertEqual(board.get_cell((0, 1)), ['foo'])

    def test_cell_append(self):
        board = gobblet.Board(4)
        board.cells[0][0].append(1)
        self.assertEqual(board.cells, [
            [[1], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])


if __name__ == '__main__':
    unittest.main()
