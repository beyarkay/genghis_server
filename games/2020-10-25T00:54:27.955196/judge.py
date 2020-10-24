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
        time.sleep(1)
        #  Run the bot's script with given environment variables and such
        try:
            #print(os.path.join(bot.username, bot.bot_filename))
            cwd = os.getcwd()
            os.chdir(bot.username)
            result = subprocess.run(
                ['python3', bot.bot_filename],
                timeout=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            os.chdir(cwd)
            if result.returncode != 0:
                print("Error running bot with stderr={}".format(result.stderr))

            bot.stdout = result.stdout.replace('\n', '<br>')
            bot.stderr = result.stderr.replace('\n', '<br>')
            
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

        #       M move the bot in the gamestate
        bot.perform_action(bot_move, game)

        #  Log the movement to the logfiles
        game.log_state()

    #       Log the bots score to a json for graphing

def game_continues():
    # TODO Add an end condition for the game
    return True

if __name__ == "__main__":
    main()
