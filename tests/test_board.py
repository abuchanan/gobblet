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
        self.assertEqual(type(board[0, 0]), gobblet.Stack)
        self.assertEqual(len(board[0, 0]), 0)

    def test_get_column(self):
        board = gobblet.Board(4)
        board[0, 1].push('foo')
        board[3, 1].push('bar')
        col = board.get_column(1)
        self.assertEqual(col[0].pieces, ['foo'])
        self.assertEqual(col[1].pieces, [])
        self.assertEqual(col[2].pieces, [])
        self.assertEqual(col[3].pieces, ['bar'])

    def test_getitem(self):
        board = gobblet.Board(4)
        board.cells[0][1].push('foo')
        self.assertEqual(board[0, 1].pieces, ['foo'])

    def test_cell_push(self):
        board = gobblet.Board(4)
        board[0, 0].push(1)

        cells = []
        for row in board.cells:
            cell_row = []
            cells.append(cell_row)
            for stack in row:
                cell_row.append(stack.pieces)

        self.assertEqual(cells, [
            [[1], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
            [[], [], [], []],
        ])


if __name__ == '__main__':
    unittest.main()
