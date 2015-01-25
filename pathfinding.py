import math

from gameboard import Coordinate as C


class Pathfinder(object):
    def __init__(self, gameboard):
        self.gameboard = gameboard

    def find_path(start, end):
        """
        Given Coordinates start and end, finds the shortest path between them
        on the gameboard.
        """
        raise NotImplementedError()

    @classmethod
    def distance(cls, start, end):
        return math.sqrt(
            (start.x - end.x)**2 + (start.y - end.y)**2
        )

    def heuristic_cost(self, start, end):
        """
        Given Coordinates start and end, estimates the distance between them.
        """
        # Gameboards allow wrapping around, so we need to account for that.
        new_end_x = end.x
        new_end_y = end.y
        if math.fabs((start.x - end.x)) > (self.gameboard.width / 2):
            if start.x > end.x:
                new_end_x = end.x + self.gameboard.width
            else:
                new_end_x = end.x - self.gameboard.width
        if math.fabs((start.y - end.y)) > (self.gameboard.height / 2):
            if start.y > end.y:
                new_end_y = end.y + self.gameboard.height
            else:
                new_end_y = end.y - self.gameboard.height
        end = C(new_end_x, new_end_y)
        return self.distance(start, end)

    def _get_neighboring_tiles(self, tile):
        gt = self.gameboard.get_tile
        coordinate = tile.coordinate
        return [
            gt(C(coordinate.x + 1, coordinate.y)),
            gt(C(coordinate.x - 1, coordinate.y)),
            gt(C(coordinate.x, coordinate.y + 1)),
            gt(C(coordinate.x, coordinate.y - 1))
        ]
