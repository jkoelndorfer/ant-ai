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
    horizontal_border: The character used for rendering horizontal borders.
    vertical_border: The character used for rendering vertical borders.
    top_left_corner: The character used when rendering the top left corner
    of the board (border).
    top_right_corner: The character used when rendering the top right corner
    of the board (border).
    bottom_left_corner: The character used when rendering the bottom left corner
    of the board (border).
    bottom_right_corner: The character used when rendering the bottom right corner
    of the board (border).
    """
    def __init__(
        self, visible_tile='.', invisible_tile=' ',
        wall='X', friendly_hill='*', enemy_hill='^',
        friendly_ant='@', enemy_ant='A', food='F',
        horizontal_border='-', vertical_border='|',
        top_left_corner='+', top_right_corner='+',
        bottom_left_corner='+', bottom_right_corner='+'
    ):
        properties = locals()
        for p in properties:
            if p == 'self':
                continue
            setattr(self, p, properties[p])
        self.overlay = lambda tile, gamestate: None

    def display(self, gamestate):
        print('\n\n' + self.render(gamestate))

    def register_overlay(self, overlay):
        self.overlay = overlay

    def render(self, gamestate):
        board = self.top_left_corner + \
            (self.horizontal_border * gamestate.get_gameboard().width) + \
            self.bottom_left_corner + '\n'
        for y in range(0, gamestate.get_gameboard().height):
            board += self.vertical_border
            for x in range(0, gamestate.get_gameboard().width):
                board += self.render_tile(
                    gamestate.get_gameboard().tiles[x][y], gamestate
                )
            board += self.vertical_border + '\n'
        board += self.bottom_left_corner + \
            self.horizontal_border * gamestate.get_gameboard().width + \
            self.bottom_left_corner
        if gamestate.game_over:
            board += '\n' + 'GAME OVER'
        return board

    def render_tile(self, tile, gamestate):
        char = self.overlay(tile, gamestate)
        if char is not None:
            return char

        char = self.visible_tile
        if tile.type == gameboard.TileType.wall:
            char = self.wall
        elif tile.type == gameboard.TileType.ant_hill:
            if gamestate.get_gameboard().tile_is_friendly(tile):
                char = self.friendly_hill
            else:
                char = self.enemy_hill
        elif not gamestate.get_gameboard().tile_is_visible(tile):
            char = self.invisible_tile
        elif isinstance(tile.get_entity(), gameboard.Ant):
            if gamestate.get_gameboard().tile_is_friendly(tile):
                char = self.friendly_ant
            else:
                char = self.enemy_ant
        elif isinstance(tile.get_entity(), gameboard.Food):
            char = self.food
        return char
