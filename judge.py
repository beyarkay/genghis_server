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
import signal

import requests
import sys
# add the server directory to the PATH so we can import the utilities file
sys.path.append("/home/k/knxboy001/public_html/genghis_server")
import util

def main():
    def signal_handler(sig, frame):
        print('Quitting Genghis...')
        try:
            game.continues = False
            game.log_state(diff_only=True)
        except:
            pass
        sys.exit(1)
 
    signal.signal(signal.SIGINT, signal_handler)
    # Read in the Game object from game.pickle
    with open("game.pickle", "rb") as gamefile:
        game = pickle.load(gamefile)
    # Figure out a global order
    random.shuffle(game.bots)
    # Start stepping through the bots
    print("Game {:<35}".format(game.game_dir))
    while game_continues(game):
        step(game)
        game.iteration += 1

def step(game):
    # For each bot:
    for bot in game.bots:
        debug_log = {
            "bot_icon": "",
            "start": "",
            "stop": "",
            "duration": "",
            "move": "",
            "has_errors": "",
        }
        game.moving = bot.bot_icon
        debug_log["bot_icon"] = bot.bot_icon
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
            debug_log["start"] = datetime.datetime.now()
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
            debug_log["stop"] = datetime.datetime.now()
            bot.stdout = result.stdout.strip()
            bot.stderr = result.stderr.strip()
            debug_log["has_errors"] = bool(bot.stderr)
            debug_log["ret_code"] = result.returncode

            with open(os.path.join(bot.username, 'move.json'), 'r') as move_file:
                bot_move = json.load(move_file)
        except Exception as e:
            os.chdir(cwd)
            debug_log["stop"] = datetime.datetime.now()
            print('\n\tBot move for {} was unsuccessful'.format(
                os.path.join(bot.username, bot.bot_filename)
            ))
            bot_move = {
                'action': 'walk',
                'direction': ''
            }
            print("start traceback")
            traceback.print_exc()
            print("end traceback")


        # Move the bot in the gamestate
        bot.perform_action(bot_move, game)
        debug_log["bot_username"] = bot.username
        debug_log["move"] = " {:<5} : {:<2}".format(bot_move["action"], bot_move["direction"])
        game.log_state(diff_only=True)
        game.tick += 1
        delta = debug_log["stop"] - debug_log["start"]
        print("{:<3} | {:<1} | {:<15.15} | {:<12} | {:<6.6} | {:<12} | {:<20} | {:<10} | {:<3}".format(
            game.tick,
            debug_log["bot_icon"],
            debug_log["bot_username"],
            debug_log["start"].strftime("%H:%M:%S.%f"),
            str(delta.seconds +  delta.microseconds / 1_000_000) + "s",
            debug_log["stop"].strftime("%H:%M:%S.%f"),
            debug_log["move"],
            "Has errors" if debug_log["has_errors"] else "No errors",
            debug_log.get("ret_code", "")
        ))

def game_continues(game):
    game.continues = game.tick < len(game.bots) * 100
    if not game.continues:
        game.log_state(diff_only=True)
    return game.continues

if __name__ == "__main__":
    main()
