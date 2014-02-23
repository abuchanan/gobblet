class PieceAssertions(object):
    def assertPieces(self, piece_list, player, names, sizes):
        self.assertEqual(len(piece_list), len(names))

        names = []
        size_values = []
        for piece in piece_list:
            names.append(piece.name)
            size_values.append(piece.size)
            self.assertEqual(piece.player, player)

        self.assertEqual(names, names)
        self.assertEqual(size_values, sizes)

    def assertAvailable(self, dugout, *args):
        available = dugout.available_pieces()
        self.assertPieces(available, *args)
