import gameboard


class GameTextRenderer(object):
    """
    Renders a Board object in text using the provided characters.

    visible_tile: The character to use when rendering open tiles that are visible.
    invisible_tile: The character to use when rendering tiles that are invisible.
    wall: The character to use when rendering walls.
    friendly_hill: The character to use when rendering friendly ant hills.
    enemy_hill: The character to use when rendering enemy ant hills.
    friendly_ant: The character to use when rendering friendly ants.
    enemy_ant: The character to use when rendering enemy ants.
    food: The character to use when rendering visible food.
    """
    def __init__(
        self, visible_tile='.', invisible_tile='#',
        wall='X', friendly_hill='*', enemy_hill='^',
        friendly_ant='@', enemy_ant='A', food='F'
    ):
        properties = locals()
        for p in properties:
            if p == 'self':
                continue
            setattr(self, p, properties[p])

    def render(self, gamestate):
        return '\n'.join(
            (''.join(self.render_tile(tile, gamestate) for tile in row))
            for row in gamestate.gameboard.tiles
        )

    def render_tile(self, tile, gamestate):
        char = self.visible_tile
        if tile.type == gameboard.TileType.wall:
            char = self.wall
        elif tile.type == gameboard.TileType.ant_hill:
            if gamestate.tile_is_friendly(tile):
                char = self.friendly_hill
            else:
                char = self.enemy_hill
        elif not gamestate.tile_is_visible(tile):
            char = self.invisible_tile
        elif isinstance(tile.entity, gameboard.Ant):
            if gamestate.tile_is_friendly(tile):
                char = self.friendly_ant
            else:
                char = self.enemy_ant
        elif isinstance(tile.entity, gameboard.Food):
            char = self.food
        return char
