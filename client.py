#!/usr/bin/env python3

import json
import requests


class AntAIClient(object):
    _HTTP_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    _METHOD_GET = 'get'
    _METHOD_POST = 'post'

    def __init__(self, name, web_service_url, ai):
        self.name = name
        self.web_service_url = web_service_url
        self.ai = ai
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
        return self.request(url, None, self.METHOD_GET)

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
