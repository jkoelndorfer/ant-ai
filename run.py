#!/usr/bin/env python3

import argparse
import logging
import sys

import ai
import client
import ui


class AntRunApp(object):
    def __init__(self):
        self.configure_argparse()

    def configure_argparse(self):
        a = argparse.ArgumentParser()
        a.add_argument(
            '--web-service-url',
            dest='web_service_url',
            default='http://antsgame.azurewebsites.net',
            help=('The web endpoint to use when connecting to the game. '
                  'Defaults to %(default)s.'),
        )
        a.add_argument(
            '--agent-name',
            dest='agent_name',
            default='JohnK',
            help=('When connecting, the name that will be used to identify '
                  'this client to the server. Defaults to %(default)s.')
        )
        a.add_argument(
            '--game-id',
            dest='game_id',
            default=None,
            help=('The game ID of the game to connect to. Defaults to '
                  'None, which means that a new game will be started.')
        )
        a.add_argument(
            '--log-level',
            dest='log_level',
            default='error',
            help=('Log messages greater or equal to this level will be '
                  'displayed. Defaults to %(default)s.'),
            choices=('debug', 'info', 'warning', 'error', 'critical')
        )
        a.add_argument(
            '--render-gameboard',
            dest='render_gameboard',
            action='store_true',
            default=False,
            help=('If specified, renders the gameboard after every turn. '
                  'By default, the gameboard is not rendered.')
        )
        self.argparser = a

    def run(self, argv):
        args = self.argparser.parse_args(argv)
        log_level = getattr(logging, args.log_level.upper())
        logger = logging.getLogger('ants')
        logging.basicConfig()
        logger.setLevel(log_level)
        gameclient = client.AntAIClient(args.agent_name, args.web_service_url)
        renderer = None
        if args.render_gameboard:
            renderer = ui.GameTextRenderer()
        gameai = ai.JohnAI()
        controller = client.AntGameController(gameclient, gameai, renderer)
        gameclient.login(args.game_id)
        controller.start()

if __name__ == '__main__':
    AntRunApp().run(sys.argv[1:])
