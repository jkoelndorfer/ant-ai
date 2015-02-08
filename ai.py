import functools
import itertools
import logging
from queue import PriorityQueue

import gameboard
import pathfinding
from client import AntMove
from gridutils import Coordinate as C

_gamestate = None

def surrounding_tiles(tile, radius):
    for x in range(-1 * radius, radius + 1):
        for y in range(-1 * radius, radius + 1):
            if x == 0 and y == 0:
                continue
            coordinate = C(tile.coordinate.x + x, tile.coordinate.y + y)
            yield _gamestate.get_gameboard().get_tile(coordinate)

def nearby_enemy_ants(coordinate, radius):
    gb = _gamestate.get_gameboard()
    tile = gb.get_tile(coordinate)
    enemy_ant_count = 0
    for nearby_tile in surrounding_tiles(tile, radius):
        entity = nearby_tile.get_entity()
        if isinstance(entity, gameboard.Ant) and \
                not gb.tile_is_friendly(tile):
            enemy_ant_count += 1
    return enemy_ant_count

def is_food(tile):
    return isinstance(tile.get_entity(), gameboard.Food)


class JohnAI(object):
    def __init__(self, renderer=None):
        self.logger = logging.getLogger('ants.ai.JohnAI')
        self.ant_manager = AntManager()
        self.objective_manager = ObjectiveManager()
        self.renderer = renderer

    def initialize(self, gamestate):
        global _gamestate
        _gamestate = gamestate
        self.gamestate = gamestate
        self.gameboard = self.gamestate.get_gameboard()
        self.pathfinder = pathfinding.Pathfinder(self.gameboard)

    def execute(self, gamestate):
        self.logger.info('Executing for turn %d', gamestate.turn_number)
        self.ant_manager.update_ants()
        self.disband_obsolete_squads()
        self.update_objectives()
        prioritized_objectives = self.objective_manager.prioritize_by(
            self.objective_priority
        )
        while self.ant_manager.ants_available() and \
                prioritized_objectives.qsize() > 0:
            objective = prioritized_objectives.get()
            ant_prioritizer = self.make_ant_prioritizer(objective)
            squad = self.ant_manager.create_squad(
                ant_prioritizer, self.objective_needed_ants(objective)
            )
            self.assign_objective(objective, squad)
        ai_moves = self.calculate_ant_moves()
        return [move.as_antmove() for move in ai_moves]

    def assign_objective(self, objective, squad):
        self.objective_manager.assign_objective(
            objective.objective_id, squad.squad_id
        )
        squad.objective = objective
        self.logger.info('Assigned objective %s', str(objective))

    def disband_obsolete_squads(self):
        squads_to_delete = list()
        for squad in self.ant_manager.itersquads():
            if squad.objective is None or squad.objective.obsolete or \
                    len(squad.members) == 0:
                squads_to_delete.append(squad.squad_id)
        for squad_id in squads_to_delete:
            self.ant_manager.disband_squad(squad_id)

    def make_ant_prioritizer(self, objective):
        def f(ant_id):
            ant_coordinate = self.gameboard.get_ant(ant_id).coordinate
            return self.pathfinder.heuristic_cost(
                ant_coordinate, objective.coordinate
            )
        return f

    def update_objectives(self):
        """
        Updates the objectives known to the ObjectiveManager.
        """
        potential_objectives = itertools.chain(
            self.gameboard.food, (self.gameboard.enemy_ant_hill, )
        )
        current_objective_coordinates = set()
        objectives_to_remove = []
        for o in self.objective_manager.iterobjectives():
            if o.obsolete:
                objectives_to_remove.append(o.objective_id)
            else:
                current_objective_coordinates.add(o.coordinate)

        for objective_id in objectives_to_remove:
            self.objective_manager.remove_objective(objective_id)

        for o in potential_objectives:
            if o is None or o.coordinate in current_objective_coordinates:
                continue
            tile = self.gameboard.get_tile(o.coordinate)
            self.objective_manager.make_objective(tile)

    def objective_priority(self, objective):
        if isinstance(objective, FoodObjective):
            return self.food_objective_priority(objective)
        elif isinstance(objective, AntHillObjective):
            return self.ant_hill_objective_priority(objective)

    def food_objective_priority(self, objective):
        objective_priority = objective.DEFAULT_PRIORITY
        objective_priority += self.pathfinder.heuristic_cost(
            self.gameboard.friendly_ant_hill.coordinate,
            objective.coordinate
        ) * 100
        tile = self.gameboard.get_tile(objective.coordinate)
        multiplier = 1
        # Examine the tiles surrounding food. Food that is close to other
        # food is more important, since we can grab a lot of it quickly.
        for tile in surrounding_tiles(tile, 4):
            if isinstance(tile.get_entity(), gameboard.Food):
                objective_priority -= (100 * multiplier)
                multiplier *= 2
        return objective_priority

    def ant_hill_objective_priority(self, objective):
        objective_priority = objective.DEFAULT_PRIORITY
        objective_priority += 500
        nearby_enemy_count = nearby_enemy_ants(objective.coordinate, 3)
        objective_priority += (nearby_enemy_count * 200)
        if nearby_enemy_count == 0:
            objective_priority -= 2000
        return objective_priority

    def objective_needed_ants(self, objective):
        # TODO: Implement objective_needed_ants().
        return 1

    def calculate_ant_moves(self):
        gameboard = _gamestate.get_gameboard()
        nontraversable_coordinates = set((
            self.gameboard.get_ant(ant_id).coordinate \
            for ant_id in self.ant_manager.all_ants
        ))
        moves = []
        for squad in self.ant_manager.itersquads():
            squad_moves = squad.report_moves(
                self.gameboard, self.pathfinder, nontraversable_coordinates
            )
            moves.extend(squad_moves)
        if self.renderer is not None:
            self.renderer.register_overlay(
                self.renderer_path_overlay([x.path for x in moves])
            )
        return moves

    def renderer_path_overlay(self, paths):
        path_chars = 'ov+=&!?%'
        def overlay(tile, gamestate):
            for index, path in enumerate(paths):
                if tile.coordinate in path:
                    return path_chars[index % len(path_chars)]
            return None
        return overlay



class AIMove(object):
    def __init__(self, ant_id, to):
        self.ant_id = ant_id
        self.to = to
        self.logger = logging.getLogger('ants.ai.AIMove')
        self.path = ()

    @property
    def frm(self):
        return _gamestate.get_gameboard().get_ant(self.ant_id).coordinate

    @property
    def direction(self):
        self.logger.debug(
            'Getting direction for ant %d; %s -> %s', self.ant_id, self.frm,
            self.to
        )
        gb = _gamestate.get_gameboard()
        direction_map = {
            gb.get_tile(C(self.frm.x - 1, self.frm.y)).coordinate: AntMove.LEFT,
            gb.get_tile(C(self.frm.x + 1, self.frm.y)).coordinate: AntMove.RIGHT,
            gb.get_tile(C(self.frm.x, self.frm.y - 1)).coordinate: AntMove.UP,
            gb.get_tile(C(self.frm.x, self.frm.y + 1)).coordinate: AntMove.DOWN,
        }
        direction = direction_map[self.to]
        self.logger.debug('Direction is %s', direction)
        return direction

    def as_antmove(self):
        return AntMove(self.ant_id, self.direction)

class AntManager(object):
    def __init__(self):
        # A dict mapping squad ID numbers to ant squads
        self.squads = {}
        # A set containing the IDs of ants not assigned to a squad
        self.unassigned_ants = set()
        self.all_ants = set()
        # A map of ant IDs to assigned squad
        self.ant_squad_assignments = {}
        self.next_squad_id = 0
        self.logger = logging.getLogger('ants.ai.AntManager')

    def ants_available(self):
        return (len(self.unassigned_ants) > 0)

    def select_ideal_ants(self, measure, count=1, use_assigned_ants=False):
        """
        Selects count ants from the list of unassigned ants based on measure.

        Measure should be a function that takes a single argument, an ant ID,
        and returns an integer representing the suitability of that ant for
        selection.

        Lower integers indicate better suitability.
        """
        potential_ants = self.unassigned_ants
        if use_assigned_ants:
            potential_ants = self.all_ants
        ants = sorted(potential_ants, key=measure)
        if len(ants) == 0:
            return None
        elif len(ants) > count:
            ants = ants[0:count]
        return ants

    def create_squad(self, measure, count, use_assigned_ants=False):
        self.next_squad_id += 1
        squad_members = self.select_ideal_ants(
            measure, count, use_assigned_ants
        )
        squad = AntSquad(self.next_squad_id, squad_members)
        self.logger.debug(
            'Created squad %d with members: %s', squad.squad_id,
            ', '.join(map(lambda x: str(x), squad_members))
        )
        self.squads[self.next_squad_id] = squad
        for ant_id in squad_members:
            ant_current_squad = self.ant_squad_assignments.get(ant_id)
            if ant_current_squad is not None:
                ant_current_squad.remove_members((ant_id, ))
            self.ant_squad_assignments[ant_id] = squad
            self.unassigned_ants.remove(ant_id)
        squad.add_members(squad_members)
        self.logger.debug('Created squad %d', squad.squad_id)
        return squad

    def disband_squad(self, squad_id):
        self.logger.debug('Disbanding squad %d', squad_id)
        for ant_id in self.squads[squad_id].members:
            self.unassigned_ants.add(ant_id)
        del self.squads[squad_id]

    def itersquads(self):
        for squad in self.squads.values():
            yield squad

    def update_ants(self):
        """
        Updates unassigned ants and ant squads from current gamestate.
        """
        current_ant_ids = set(map(
            lambda x: x.get_entity().ant_id,
            _gamestate.get_gameboard().friendly_ants
        ))
        self.all_ants = current_ant_ids
        self.logger.debug('All ants: %s', str(self.all_ants))
        seen_ants = set()
        self.unassigned_ants &= current_ant_ids
        seen_ants |= self.unassigned_ants
        for squad in self.squads.values():
            seen_ants |= squad.members
            squad.members &= current_ant_ids
        new_ants = current_ant_ids - seen_ants
        self.unassigned_ants |= new_ants
        self.logger.debug('Unassigned ants: %s', str(self.unassigned_ants))


class ObjectiveManager(object):
    def __init__(self):
        self._next_objective_id = 0
        self._objectives = {}
        self.logger = logging.getLogger('ants.ai.ObjectiveManager')

    def _objective_id(self):
        objective_id = self._next_objective_id
        self._next_objective_id += 1
        return objective_id

    def iterobjectives(self):
        for objective in self._objectives.values():
            yield objective

    def make_objective(self, tile):
        self.logger.debug('Creating objective for tile %s', tile.coordinate)
        entity = tile.get_entity()
        objective_id = self._objective_id()
        if tile.type == gameboard.TileType.ant_hill:
            o = AntHillObjective(objective_id, tile.coordinate)
        elif isinstance(entity, gameboard.Food):
            o = FoodObjective(objective_id, tile.coordinate)
        else:
            raise ValueError(
                'Tile should be an ant hill or Food'
            )
        self._objectives[objective_id] = o

    def remove_objective(self, objective_id):
        del self._objectives[objective_id]

    def assign_objective(self, objective_id, squad_id):
        self._objectives[objective_id].assigned_squad_id = squad_id

    def prioritize_by(self, measure):
        """
        Prioritizes objectives by measure.

        Measure should be a function that takes one argument, the objective,
        and returns a number representing its priority.

        A lower number indicates a higher priority.

        Returns a priority queue containing objectives.
        """
        queue = PriorityQueue()
        for objective in self._objectives.values():
            objective.priority = measure(objective)
            queue.put(objective)
        return queue


class AntSquad(object):
    def __init__(self, squad_id, members):
        self.squad_id = squad_id
        self.objective = None
        self.members = set()
        self.logger = logging.getLogger('ants.ai.AntSquad')

    def add_members(self, members):
        self.members |= set(members)

    def remove_members(self, members):
        self.members -= set(members)

    def report_moves(self, gameboard, pathfinder, nontraversable):
        self.logger.info('Reporting moves for squad %d', self.squad_id)
        if self.objective is None:
            self.logger.debug('No objective; no moves to report')
            return ()
        moves = []
        self.logger.info(str(self.objective))
        for ant_id in self.members:
            move = self.ant_move(ant_id, gameboard, pathfinder, nontraversable)
            if move is not None:
                moves.append(move)
        return moves

    def ant_move(self, ant_id, gameboard, pathfinder, nontraversable):
        ant = gameboard.get_ant(ant_id)
        max_food_dist = 3
        nearby_food = filter(is_food, surrounding_tiles(ant, max_food_dist))
        targets = filter(
            lambda x: x.coordinate not in nontraversable,
            itertools.chain(nearby_food, (self.objective ,))
        )
        # If the actual distance to our food is too far away, check the next
        # potential target.
        while True:
            try:
                target = next(targets)
            except StopIteration:
                return None
            path = pathfinder.find_path(
                ant.coordinate, target.coordinate, nontraversable
            )
            if path is None:
                continue
            if (target.coordinate == self.objective.coordinate or
                    len(path) < max_food_dist):
                break
        if path is None:
            return None
        move = AIMove(ant_id, path[0])
        move.path = path
        self.logger.debug(
            'Moving ant %d %s -> %s (%s)', ant_id, str(move.frm),
            str(move.to), str(move.direction)
        )
        # Update the list of coordinates we aren't allowed to move to
        # We don't want to be killing our own ants!
        nontraversable.remove(move.frm)
        nontraversable.add(move.to)
        return move


@functools.total_ordering
class Objective(object):
    DEFAULT_PRIORITY = 1000000
    DEFAULT_THREAT = 0

    def __init__(self, objective_id):
        self.objective_id = objective_id
        self.assigned_squad_id = None
        self.priority = self.DEFAULT_PRIORITY
        self.threat = self.DEFAULT_THREAT

    def __lt__(self, other):
        return (self.priority < other.priority)

    def __eq__(self, other):
        return (self.priority == other.priority)

    def __repr__(self):
        fmtstr = (
            'OBJECTIVE[{objective_id}: C={coord}, S={squad}, '
             'P={priority}]'
        )
        return fmtstr.format(
            objective_id=self.objective_id, coord=str(self.coordinate),
            squad=self.assigned_squad_id, priority=self.priority
        )

    @property
    def is_assigned(self):
        return (self.assigned_squad_id is not None)

    @property
    def obsolete(self):
        """
        True if an objective is no longer present, else False.
        """
        raise NotImplementedError()


class FoodObjective(Objective):
    def __init__(self, objective_id, coordinate):
        super().__init__(objective_id)
        self.coordinate = coordinate

    @property
    def obsolete(self):
        return not isinstance(
            _gamestate.get_gameboard().get_tile(self.coordinate).get_entity(),
            gameboard.Food
        )


class AntHillObjective(Objective):
    def __init__(self, objective_id, coordinate):
        super().__init__(objective_id)
        self.coordinate = coordinate

    @property
    def obsolete(self):
        return False
