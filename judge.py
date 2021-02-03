#!/usr/bin/python3
import copy
import importlib
import datetime
import glob
import json
import os
import pickle
import random
import re
import requests
import shutil
import signal
import subprocess
import sys
import time
import traceback

# add the server directory to the PATH so we can import the utilities file
genghis_root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(genghis_root_path)
import util

def main():
    def signal_handler(sig, frame):
        print(util.Colours.ENDC + 'Quitting Genghis...')
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
        start_time = datetime.datetime.now()
        bot_move = {
            'action': '',
            'direction': ''
        }
        debug_log = {
            "bot_icon": bot.bot_icon,
            "bot_username": bot.username,
            "start": datetime.datetime.now(),
            "stop": datetime.datetime.now(),
            "duration": "",
            "move": "",
            "has_errors": bool(bot.stderr),
            "bot_health": bot.health,
        }
        if bot.health > 0:
            game.moving = bot.bot_icon

            # pickle the current Game object for the bot to use
            with open(os.path.join(bot.username, "game.pickle"),"wb") as game_pkl:
                pickle.dump(game, game_pkl)

            # Figure out the port icon of the current bot's battleground
            bg_icon = ""
            for bg in game.battlegrounds:
                if bot.bot_icon in [bg_bot.bot_icon for bg_bot in bg.bots]:
                    bg_icon = bg.port_icon

            try:

                # Execute the bot's script
                debug_log["start"] = datetime.datetime.now()
                module = "" + bot.username + "." +  bot.bot_filename.replace(".py", "").replace('/', '.')
                cwd = os.getcwd()
                try:
                    print(util.Colours.OKGREEN,end='')
                    bot_script = importlib.import_module(module, package=__package__)
                    bot_script.main(bot.username, bot.bot_icon, bg_icon)
                    bot.stderr = "Feature Unimplemented"
                    bot.stdout = "Feature Unimplemented"
                    debug_log["ret_code"] = "0"
                    # print("Ran bot {} the proper way".format(module))
                except IndexError:
                    print(util.Colours.OKBLUE, end='')
                    os.chdir(bot.username)

                    result = subprocess.run(
                        ['python3', bot.bot_filename,
                        genghis_root_path,
                        bot.bot_icon,
                        bg_icon],
                        timeout=5,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    os.chdir(cwd)
                    bot.stdout = result.stdout.strip()
                    bot.stderr = result.stderr.strip()
                    debug_log["ret_code"] = result.returncode
                print(util.Colours.ENDC, end='')
                debug_log["stop"] = datetime.datetime.now()
                debug_log["has_errors"] = bool(bot.stderr)

                with open(os.path.join(bot.username, 'move.json'), 'r') as move_file:
                    bot_move = json.load(move_file)
            except Exception as e:
                os.chdir(cwd)
                debug_log["stop"] = datetime.datetime.now()

                print(util.Colours.FAIL)
                traceback.print_exc()
                print(util.Colours.ENDC, end='')
                bot_move = {
                    'action': 'walk',
                    'direction': ''
                }
            print(util.Colours.ENDC, end='')

            # Move the bot in the gamestate
            bot.perform_action(bot_move, game)
            game.log_state(diff_only=True)
            game.tick += 1
            delta = datetime.datetime.now() - start_time
            if delta.microseconds/1000000 + delta.seconds < game.turn_time:
                print('Sleeping for {}s'.format(game.turn_time - delta.microseconds/1000000 + delta.seconds))
                time.sleep(game.turn_time - delta.microseconds/1000000 + delta.seconds)

        debug_log["move"] = " {:<5} : {:<2}".format(bot_move["action"], bot_move["direction"])
        delta = debug_log["stop"] - debug_log["start"] 
        print("{:<3} | {:<1} | {:<3} | {:<15.15} | {:<12} | {:<6.6} | {:<12} | {:<20} | {:<10} | {:<3}".format(
            game.tick,
            debug_log["bot_icon"],
            debug_log["bot_health"],
            debug_log["bot_username"],
            debug_log["start"].strftime("%H:%M:%S.%f"),
            str(delta.seconds +  delta.microseconds / 1_000_000) + "s",
            debug_log["stop"].strftime("%H:%M:%S.%f"),
            debug_log["move"],
            "Has errors" if debug_log["has_errors"] else "No errors",
            debug_log.get("ret_code", "")
        ))

def game_continues(game):
    # If all but one of the bots are dead
    if len([bot for bot in game.bots if bot.health > 0]) <= 1:
        print("Ending the game, bot healths = {}".format({bot.bot_icon:bot.health for bot in game.bots}))
        game.continues = False
    # If the game has gone on for too long
    if game.tick >= len(game.bots) * 250:
        print("Ending the game, game.tick {} >= len(game.bots) {} * 100".format(game.tick, len(game.bots)))
        game.continues = False

    if not game.continues:
        game.log_state(diff_only=True)
    return game.continues

if __name__ == "__main__":
    main()
