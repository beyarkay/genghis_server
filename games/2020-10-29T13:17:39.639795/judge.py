#!/usr/bin/python3
import copy
import datetime
import glob
import json
import os
import pickle
import random
import re
import shutil
import subprocess
import time
import traceback

import requests
import sys
# add the server directory to the PATH so we can import the utilities file
sys.path.append("/home/k/knxboy001/public_html/genghis_server")
import util

def main():
    # Read in the Game object from game.pickle
    with open("game.pickle", "rb") as gamefile:
        game = pickle.load(gamefile)
    # Figure out a global order
    random.shuffle(game.bots)
    # Start stepping through the bots
    while game_continues():
        print("Game {}, iteration {}".format(os.getcwd(), game.iteration))
       # game.print_logs()
        step(game)
        game.iteration += 1


def step(game):
    # For each bot:
    for bot in game.bots:
        # TODO add more sophisticated waiting so that longer bots don't always get longer turns
        time.sleep(game.turn_time)
        # pickle the current Game object for the bot to use
        with open(os.path.join(bot.username, "game.pickle"),"wb") as game_pkl:
            pickle.dump(game, game_pkl)

        # Figure out the port icon of the current bot's battleground
        bg_icon = ""
        for bg in game.battlegrounds:
            if bot.bot_icon in [bg_bot.bot_icon for bg_bot in bg.bots]:
                bg_icon = bg.port_icon

        try:
            # Move to the script's location
            cwd = os.getcwd()
            os.chdir(bot.username)

            # Execute the bot's script
            result = subprocess.run(
                ['python3', bot.bot_filename,
                 '/home/k/knxboy001/public_html/genghis_server',
                 bot.bot_icon,
                 bg_icon],
                timeout=5,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            os.chdir(cwd)
            if result.returncode != 0:
                print("Error running bot, stderr='{}'".format(result.stderr))

            bot.stdout = result.stdout.strip()
            bot.stderr = result.stderr.strip()
            if bot.stdout:
                print("Bot {} says: '{}'".format(bot.bot_icon, bot.stdout))
            
            with open(os.path.join(bot.username, 'move.json'), 'r') as move_file:
                bot_move = json.load(move_file)
        except Exception as e:
            print('Bot move for {} was unsuccessful'.format(
                os.path.join(bot.username, bot.bot_filename)
            ))
            bot_move = {
                'action': 'walk',
                'direction': ''
            }
            traceback.print_exc()

        # Move the bot in the gamestate
        bot.perform_action(bot_move, game)
        game.log_state()
        game.tick += 1

def game_continues():
    # TODO Add an end condition for the game
    return True

if __name__ == "__main__":
    main()
