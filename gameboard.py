from enum import Enum


class Gameboard(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        for row_number in range(self.height):
            row = []
            self.tiles.append(row)
            for column_number in range(self.width):
                coordinate = Coordinate(row_number, column_number)
                row.append(Tile(coordinate, self))

    def get_tile(self, coordinate):
        assert isinstance(coordinate, Coordinate)
        return self.tiles[coordinate.x][coordinate.y]


class Coordinate(object):
    def __init__(self, x, y):
        assert isinstance(x, int)
        assert isinstance(y, int)
        super().__setattr__('x', x)
        super().__setattr__('y', y)

    def __hash__(self):
        return int(str(self.x) + str(self.y))

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)

    def __delattr__(self, name):
        raise TypeError('Instances are immutable.')

    def __setattr__(self, name, value):
        raise TypeError('Instances are immutable.')


TileType = Enum('TileType', ('basic', 'wall', 'ant_hill'))


class Tile(object):
    def __init__(self, coordinate, gameboard):
        self.coordinate = coordinate
        self.gameboard = gameboard
        self._entity = None
        self.type = TileType.basic
        self.metadata = dict()

    def make_wall(self):
        self.type = TileType.wall

    def make_anthill(self, owner):
        self.type = TileType.ant_hill
        self.metadata = {'owner': owner}

    def get_entity(self):
        return self._entity

    def set_entity(self, entity):
        assert isinstance(entity, TileEntity)
        self._entity = entity
        entity.parent_tile = self

    @property
    def traversable(self):
        return self.type != TileType.wall


class TileEntity(object):
    pass


class Ant(TileEntity):
    def __init__(self, ant_id, owner):
        super().__init__()
        self.ant_id = ant_id
        self.owner = owner


class Food(TileEntity):
    pass
