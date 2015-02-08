from enum import Enum
import logging

from gridutils import Coordinate
import gridutils


class Gameboard(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gamestate = None
        self.friendly_ant_hill = None
        self.friendly_ants = []
        self.enemy_ant_hill = None
        self.enemy_ants = []
        self._ants_by_id = dict()
        self.food = []
        self.tiles = []
        self.visible_coordinates = set()
        self.logger = logging.getLogger('ants.gameboard.Gameboard')
        for row_number in range(self.height):
            row = []
            self.tiles.append(row)
            for column_number in range(self.width):
                coordinate = Coordinate(row_number, column_number)
                row.append(Tile(coordinate, self))

    def calculate_visible_coordinates(self):
        self.visible_coordinates = set()
        for ant_tile in self.friendly_ants:
            self.visible_coordinates |= \
                set(gridutils.get_filled_circle_coordinates(
                    ant_tile.coordinate, self.gamestate.view_distance,
                    modulo_x=self.width, modulo_y=self.height
                ))

    def clear_tile_entities(self):
        for tile in self.itertiles():
            tile.set_entity(None)
        self.friendly_ants = []
        self.enemy_ants = []
        self._ants_by_id = dict()
        self.food = []

    def itertiles(self):
        for row in self.tiles:
            for tile in row:
                yield tile

    def get_ant(self, ant_id):
        return self._ants_by_id[ant_id]

    def get_tile(self, coordinate):
        assert isinstance(coordinate, Coordinate)
        return self.tiles[coordinate.x % self.width][coordinate.y % self.height]

    def tile_is_friendly(self, tile):
        if tile.type == TileType.ant_hill:
            return self.gamestate.is_friendly(tile.metadata['owner'])
        elif isinstance(tile.get_entity(), Ant):
            return self.gamestate.is_friendly(tile.get_entity().owner)
        else:
            return False

    def tile_is_visible(self, tile):
        return tile.coordinate in self.visible_coordinates

    def register_entity_tile(self, tile):
        e = tile.get_entity()
        if e is None:
            return
        l = None
        if isinstance(e, Ant):
            if self.tile_is_friendly(tile):
                l = self.friendly_ants
            else:
                l = self.enemy_ants
            self._ants_by_id[tile.get_entity().ant_id] = tile
        elif isinstance(e, Food):
            l = self.food
        l.append(tile)

    def register_ant_hill(self, tile):
        if self.tile_is_friendly(tile):
            self.friendly_ant_hill = tile
        else:
            self.enemy_ant_hill = tile


TileType = Enum('TileType', ('basic', 'wall', 'ant_hill'))


class Tile(object):
    def __init__(self, coordinate, gameboard):
        self.coordinate = coordinate
        self.gameboard = gameboard
        self._entity = None
        self.type = TileType.basic
        self.metadata = dict()
        self.logger = logging.getLogger('ants.gameboard.Tile')

    def make_wall(self):
        self.type = TileType.wall

    def make_ant_hill(self, owner):
        self.type = TileType.ant_hill
        self.metadata = {'owner': owner}
        self.gameboard.register_ant_hill(self)

    def get_entity(self):
        return self._entity

    def set_entity(self, entity):
        assert isinstance(entity, TileEntity) or entity is None
        self._entity = entity
        self.gameboard.register_entity_tile(self)
        if entity is not None:
            entity.parent_tile = self

    @property
    def traversable(self):
        return self.type != TileType.wall


class TileEntity(object):
    def __init__(self):
        self.logger = logging.getLogger('ants.gameboard.TileEntity')


class Ant(TileEntity):
    def __init__(self, ant_id, owner):
        super().__init__()
        self.ant_id = ant_id
        self.owner = owner


class Food(TileEntity):
    pass
