import functools
import math
from queue import PriorityQueue

from gameboard import Coordinate as C


class Pathfinder(object):
    def __init__(self, gameboard):
        self.gameboard = gameboard

    # Used http://web.mit.edu/eranki/www/tutorials/search as a reference for
    # this A* implementation.
    def find_path(self, start, end, nontraversable=()):
        """
        Given Coordinates start and end, finds the shortest path between them
        on the gameboard.
        """
        open_coords = PriorityQueue()
        parent_coords = dict()
        g_score = dict()
        f_score = dict()

        open_coords.put(QueueCoordinate(coordinate=start, f_score=0))
        f_score[start] = self.heuristic_cost(start, end)
        g_score[start] = 0

        while open_coords.qsize() > 0:
            q = open_coords.get().coordinate
            successors = self._get_neighboring_coordinates(q)
            for successor in successors:
                if successor == end:
                    parent_coords[successor] = q
                    return self.build_path(end, parent_coords)
                if successor in nontraversable:
                    continue
                # All traversals have equal cost
                successor_g = g_score[q] + 1
                successor_h = self.heuristic_cost(successor, end)
                successor_f = successor_g + successor_h
                if f_score.get(successor, successor_f + 1) > successor_f:
                    f_score[successor] = successor_f
                    g_score[successor] = successor_g
                    open_coords.put(QueueCoordinate(successor, successor_f))
                    parent_coords[successor] = q

    def build_path(self, end, parent_coords):
        current = end
        path = list()
        while True:
            parent = parent_coords.get(current, None)
            if parent is None:
                break
            path.insert(0, current)
            current = parent
        return path

    @classmethod
    def cartesian_distance(cls, start, end):
        return math.sqrt((start.x - end.x)**2 + (start.y - end.y)**2)

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
        return self.cartesian_distance(start, end)

    def _get_neighboring_coordinates(self, coordinate):
        gt = self.gameboard.get_tile
        neighbors = (
            gt(C(coordinate.x + 1, coordinate.y)),
            gt(C(coordinate.x - 1, coordinate.y)),
            gt(C(coordinate.x, coordinate.y + 1)),
            gt(C(coordinate.x, coordinate.y - 1))
        )
        return tuple((x.coordinate for x in neighbors if x.traversable))


@functools.total_ordering
class QueueCoordinate(object):
    def __init__(self, coordinate, f_score):
        self.coordinate = coordinate
        self.f_score = f_score

    def __lt__(self, other):
        return (self.f_score < other.f_score)

    def __eq__(self, other):
        return (self.f_score == other.f_score)
