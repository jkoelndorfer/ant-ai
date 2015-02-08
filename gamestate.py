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
        self.turn_number = 0
        self.total_food = 0
        self.game_over = False
        self.set_gameboard(gameboard)

    def get_gameboard(self):
        return self._gameboard

    def set_gameboard(self, gameboard):
        self._gameboard = gameboard
        self._gameboard.gamestate = self

    def is_friendly(self, player):
        return player == self.friendly_player
