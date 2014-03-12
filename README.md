Introduction
------------------------------------------------------------------------------

[Gobblet](http://en.wikipedia.org/wiki/Gobblet) is a strategy game.
This code is an experiment in creating a computer simulation of a
Gobblet game, and in writing various algorithms to control each
player's pieces.


Running a game
------------------------------------------------------------------------------

Here's an example of how to run a game simulation using the RandomPlayer
algorithm:

    from gobblet import Game, RandomPlayer

    white = RandomPlayer('white')
    black = RandomPlayer('black')
    game = Game(white, black)

    while True:
        game.tick()


Writing a player algorithm
------------------------------------------------------------------------------

Algorithms control the move of each player's pieces. Here's an example of
how an player algorithm is written:

    from gobblet import Player

    class MyPlayer(Player):
        def move(self, board, dugout):
            # Player.move() is called for each player's turn.
            # It must return a tuple:
            #     (piece_to_be_moved, coordinate_of_board_cell)
            # e.g.
            return dugout.available[0], (0, 1)


Tests
------------------------------------------------------------------------------

To run a test module, from the root directory run:

    # e.g. to run tests/test_board.py
    python -m tests.test_board
