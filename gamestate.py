import gameboard as gb


class GameState(object):
    """
    Represents the current state of the Ants game.
    """

    def __init__(self, friendly_player, enemy_player, gameboard, view_distance):
        assert isinstance(gameboard, gb.Gameboard)
        assert isinstance(view_distance, int)

        self.friendly_player = friendly_player
        self.enemy_player = enemy_player
        self.view_distance = view_distance
        self.gameboard = gameboard
        self.turn_number = 0

    def tile_is_friendly(self, tile):
        if tile.type == gb.TileType.ant_hill:
            return tile.metadata['owner'] == self.friendly_player
        elif isinstance(tile.get_entity(), gb.Ant):
            return tile.get_entity().owner == self.friendly_player
        else:
            return False

    def tile_is_visible(self, tile):
        # TODO: Implement this.
        return True
