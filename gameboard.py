from itertools import chain

from gridutils import get_straight_line_coordinates as l
from gridutils import Coordinate as C


class Board(object):
    width = 30
    height = 30

    walls = (
        # Walls at y = 0 and y = 29 (corners, horizontal)
        l(C(0, 0), C(2, 0)), l(C(27, 0), C(29, 0)),
        l(C(0, 29), C(2, 29)), l(C(27, 29), C(29, 29)),

        # Walls at x = 0 and x = 29 (corners, vertical)
        l(C(0, 0), C(0, 2)), l(C(29, 0), C(29, 2)),
        l(C(0, 27), C(0, 29)), l(C(29, 27), C(29, 29)),

        # Walls at y = 14 and y = 15 (middle "+", horizontal)
        l(C(10, 14), C(19, 14)), l(C(10, 15), C(19, 15)),

        # Walls at x = 14 and x = 15 (middle "+", vertical)
        l(C(14, 10), C(14, 19)), l(C(15, 10), C(15, 19))
    )
    # The code above produces some nested tuples - let's convert it
    # to a flat set of Coordinate objects.
    walls = set(chain.from_iterable(walls))

    def __init__(self, view_distance):
        self.view_distance = view_distance
        self.tiles = []
        for row_number in range(self.height):
            row = []
            self.tiles.append(row)
            for column_number in range(self.width):
                coordinate = C(row_number, column_number)
                tile_type = Tile
                if coordinate in self.walls:
                    tile_type = Wall
                row.append(tile_type(coordinate, self))


class Tile(object):
    traversable = True

    def __init__(self, coordinate, gameboard):
        self.coordinate = coordinate
        self.gameboard = gameboard
        self.entity = None

    def is_visible(self):
        # TODO: Implement this.
        return True

class Wall(Tile):
    traversable = False

class AntHill(Tile):
    def __init__(self, coordinate, owner):
        super().__init__(coordinate)
        self.owner = owner

class TileEntity(object):
    def __init__(self, parent_tile):
        assert isinstance(parent_tile, Tile)
        self.parent_tile = parent_tile

class Ant(TileEntity):
    def __init__(self, parent_tile, ant_id, owner):
        super().__init__(parent_tile)
        self.ant_id = ant_id
        self.owner = owner

class Food(TileEntity): pass
