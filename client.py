#!/usr/bin/env python3

import json
import requests
import time

import gameboard as gb
import gamestate


class AntAIClient(object):
    _HTTP_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    _METHOD_GET = 'get'
    _METHOD_POST = 'post'

    def __init__(self, name, web_service_url):
        self.name = name
        self.web_service_url = web_service_url
        self.game_id = None
        self.auth_token = None

    def login(self, game_id=None):
        login_data = {
            'GameId': game_id,
            'AgentName': self.name
        }
        login_url = self._format_url('api/game/logon')
        data = self.request(login_url, login_data, self._METHOD_POST)
        self.game_id = data['GameId']
        self.auth_token = data['AuthToken']

    def get_game_info(self):
        url = self._format_url(
            'api/game/{0}/status/{1}',
            self.game_id, self.auth_token
        )
        return self.request(url, None, self._METHOD_POST)

    def get_turn_info(self):
        url = self._format_url(
            'api/game/{0}/turn',
            self.game_id
        )
        return self.request(url, None, self._METHOD_GET)

    def request(self, url, data, method):
        assert method in (self._METHOD_GET, self._METHOD_POST)
        json_data = json.dumps(data)
        method_func = getattr(requests, method)
        response = method_func(url, headers=self._HTTP_HEADERS, data=json_data)
        return response.json()

    def _format_url(self, path, *url_vars):
        return '/'.join((
            self.web_service_url,
            path.format(*url_vars)
        ))


class AntGameController(object):
    def __init__(self, client, ai, renderer=None):
        self.client = client
        self.ai = ai
        self.renderer = renderer
        self.gamestate = None

    def initialize_gamestate(self, game_info):
        self.gamestate = gamestate.GameState(
            friendly_player=self.client.name, enemy_player='?',
            gameboard=gb.Gameboard(game_info['Width'], game_info['Height']),
            view_distance=game_info['FogOfWar']
        )
        self.gamestate.turn_number = game_info['Turn']

    def update_gamestate(self, game_info):
        self.gamestate.gameboard.clear_tile_entities()
        info_types = (
            'FriendlyAnts', 'EnemyAnts', 'Walls', 'Hill', 'EnemyHills',
            'VisibleFood'
        )
        for info_name in info_types:
            objs = game_info[info_name]
            # Our hill is the only information we want that isn't iterable,
            # so let's make it iterable.
            if info_name == 'Hill':
                objs = (objs, )
            for obj in objs:
                obj_coordinate = gb.Coordinate(obj['X'], obj['Y'])
                tile = self.gamestate.gameboard.get_tile(obj_coordinate)
                if info_name in ('FriendlyAnts', 'EnemyAnts'):
                    tile.set_entity(gb.Ant(ant_id=obj['Id'], owner=obj['Owner']))
                elif info_name == 'Walls':
                    tile.make_wall()
                elif info_name == 'VisibleFood':
                    tile.set_entity(gb.Food())
                elif info_name in ('Hill', 'EnemyHills'):
                    tile.make_anthill(owner=obj['Owner'])

        self.gamestate.turn_number = game_info['Turn']
        self.gamestate.game_over = game_info['IsGameOver']

    def sleep_until_next_turn(self):
        turn_info = self.client.get_turn_info()
        while turn_info['Turn'] <= self.gamestate.turn_number:
            if turn_info['MillisecondsUntilNextTurn'] < 0:
                # XXX: Ran into a bug (?) where this value is negative
                return
            time.sleep(turn_info['MillisecondsUntilNextTurn']/1000)
            turn_info = self.client.get_turn_info()

    def start(self):
        game_info = self.client.get_game_info()
        self.initialize_gamestate(game_info)
        while not self.gamestate.game_over:
            game_info = self.client.get_game_info()
            self.update_gamestate(game_info)
            self.ai.execute(self.gamestate)
            if self.renderer:
                self.renderer.display(self.gamestate)
            self.sleep_until_next_turn()
