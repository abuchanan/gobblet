# Gobblet

[Gobblet](http://en.wikipedia.org/wiki/Gobblet) is a two-player board game emphasizing strategy and memory.

The game is played on a 4x4 board. There are two players, one black, one white. Each player has 12 pieces: 3 sets of 4 blocks, with 4 different sizes. Larger blocks may cover smaller blocks. The goal is to get four of your blocks in a row. Please read the official game rules for a complete description.

This code is a framework for simulating a game of Gobblet. Basically, you provide an algorithm that will decide how a player moves their pieces.

```python
def player_algorithm(board, dugout):
    ...your code here can inspect the board and dugout, and make a move...

def other_algorithm(board, dugout):
    ...your code here can inspect the board and dugout, and make a move...

game = gobblet.Game(player_algorithm, other_algorithm)
game.play()
```


TODO document the APIs given to the player algorithms
