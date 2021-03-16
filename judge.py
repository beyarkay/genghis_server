#!/usr/bin/python3
from contextlib import contextmanager
import copy
import datetime
import dill as pickle
import glob
import importlib
import json
import os
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

TIMEOUT_SECONDS = 2
# Used to timeout the bots if their main() methods take too long to execute
class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def timeout_signal_handler(signum, frame):
        raise TimeoutException("Bot Timed Out!")
    signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def main():
    def signal_handler(sig, frame):
        print(util.Colours.ENDC + '[E] Quitting Genghis...')
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
    print("[I] Game {:<35}".format(game.game_dir))
    while game_continues(game):
        step(game)
        game.iteration += 1

def timeout_signal_handler(signum, frame):
    raise Exception("Bot execution timed out")

def step(game):
    # For each bot:
    bot_scripts = []
    for bot in game.bots:
        module = bot.username + "." +  bot.bot_filename.replace(".py", "").replace('/', '.')
        cwd = os.getcwd()
        try:
            bot_scripts.append(importlib.import_module(module, package=__package__))
        except IndexError:
            # The bot isn't using bot_scripts and is instead using deprecated system calls
            bot_scripts.append(None)

    for bot, bot_script in zip(game.bots, bot_scripts):
        bot.tt_decision = None
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
        start_time = datetime.datetime.now()
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
                #module = "" + bot.username + "." +  bot.bot_filename.replace(".py", "").replace('/', '.')
                cwd = os.getcwd()
                try:
                    print(util.Colours.OKGREEN,end='')
                    #bot_script = importlib.import_module(module, package=__package__)
                    debug_log["start"] = datetime.datetime.now()
                    start_time = datetime.datetime.now()
                    # FIXME: This doesn't have any limit on bot execution time
                    try:
                        with time_limit(TIMEOUT_SECONDS):
                            bot_script.main(bot.username, bot.bot_icon, bg_icon)
                    except TimeoutException as e:
                        print("Bot {} took over {}s to execute. The bot will not move this turn.".format(bot.username, TIMEOUT_SECONDS))
                    end_time = datetime.datetime.now()
                    debug_log["stop"] = datetime.datetime.now()
                    bot.stderr = "Stderr not available for GitHub hosted bots"
                    bot.stdout = "Stdout not available for GitHub hosted bots"
                    debug_log["ret_code"] = "0"
                    # print("Ran bot {} the proper way".format(module))
                except (IndexError, AttributeError) as e:
                    print(util.Colours.OKBLUE, end='')
                    os.chdir(bot.username)

                    debug_log["start"] = datetime.datetime.now()
                    start_time = datetime.datetime.now()
                    result = subprocess.run(
                        ['python3', bot.bot_filename,
                        genghis_root_path,
                        bot.bot_icon,
                        bg_icon],
                        timeout=TIMEOUT_SECONDS,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    end_time = datetime.datetime.now()
                    debug_log["stop"] = datetime.datetime.now()
                    os.chdir(cwd)
                    bot.stdout = result.stdout.strip()
                    bot.stderr = result.stderr.strip()
                    debug_log["ret_code"] = result.returncode
                print(util.Colours.ENDC, end='')
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
            delta = end_time - start_time
            bot.tt_decision = delta.microseconds / 1000 + delta.seconds * 1000
           # if delta.microseconds/1000000 + delta.seconds < game.turn_time:
           #     print('[V] Sleeping for {}s'.format(game.turn_time - delta.microseconds/1000000 + delta.seconds))
           #     time.sleep(game.turn_time - delta.microseconds/1000000 + delta.seconds)

        for metric in game.metrics:
            metric.compute_and_add(game)

        debug_log["move"] = " {:<5} : {:<2}".format(bot_move["action"], bot_move["direction"])
        delta = debug_log["stop"] - debug_log["start"] 
        print("[D] {:<3} | {:<1} | {:<3} | {:<15.15} | {:<12} | {:<6.6} | {:<12} | {:<20} | {:<10} | {:<3}".format(
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
        print("[I] Ending the game, bot healths = {}".format({bot.bot_icon : bot.health for bot in game.bots}))
        game.continues = False

    if (datetime.datetime.now() - datetime.datetime.fromisoformat(game.start_time)) >= datetime.timedelta(minutes=10):
        print("[I] Ending the game, time limit reached")
        game.continues = False

    if not game.continues:
        game.log_state(diff_only=True)
    return game.continues

if __name__ == "__main__":
    main()
