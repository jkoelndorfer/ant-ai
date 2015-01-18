import gameboard


class BoardTextRenderer(object):
    """
    Renders a Board object in text using the provided characters.

    friendly_name: The name of player considered friendly.
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
        self, friendly_name,
        visible_tile='.', invisible_tile='#',
        wall='X', friendly_hill='*', enemy_hill='^',
        friendly_ant='@', enemy_ant='A', food='F'
    ):
        properties = locals()
        for p in properties:
            if p == 'self':
                continue
            setattr(self, p, properties[p])

    def render(self, board):
        return '\n'.join(
            (''.join(self.render_tile(tile) for tile in row))
            for row in board.tiles
        )

    def render_tile(self, tile):
        char = self.visible_tile
        if isinstance(tile, gameboard.Wall):
            char = self.wall
        elif isinstance(tile, gameboard.AntHill):
            if self.tile_is_friendly(tile):
                char = self.friendly_hill
            else:
                char = self.enemy_hill
        elif not tile.is_visible():
            char = self.invisible_tile
        elif isinstance(tile.entity, gameboard.Ant):
            if self.tile_is_friendly(tile):
                char = self.friendly_ant
            else:
                char = self.enemy_ant
        elif isinstance(tile.entity, gameboard.Food):
            char = self.food
        return char

    def tile_is_friendly(self, tile):
        if isinstance(tile, gameboard.AntHill):
            return tile.owner == self.friendly_name
        elif isinstance(tile.entity, gameboard.Ant):
            return tile.entity.owner == self.friendly_name
        else:
            return False
