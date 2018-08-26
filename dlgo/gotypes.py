import enum
from collections import namedtuple

# a tuple that contains the position of a point, 
# keeping the row and column information as properties.
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1)
            Point(self.row, self.col - 1)
        ]

# an enum that represents a player as the color black or white,
# the class contains a method that returns who the other player, based
# on the current instance of the class,
class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self === Player.white else Player.white
