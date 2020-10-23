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
# FIXME how to make this the correct utils?
import util

# RE_SN = re.compile(r'(\w{6}\d{3})')
# gm_dir = '/' + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])
# battleground = []
# SPAWN_LOCS = []
# PORT_LOCS = []
# game_dir = ''
# SLEEP_DURATION = 0.5


def main():
    # Read in the Game object from game.pkl
    with open("game.pkl", "r") as gamefile:
        game = pickle.load(gamefile)
    # Figure out a global order
    random.shuffle(game.bots)
    # Start stepping through the bots
    while game_continues():
        step(game)
        game.iteration += 1



def step(game):
    # For each bot:
    for bot in game.bots:
        # Setup

        #  Run the bot's script with given environment variables and such
        try:
            result = subprocess.run(
                ['python3', os.path.join(bot.username, bot.bot_filename)],
                timeout=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if not result.returncode:
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


# Deprecated
def __step():
    update_dirs()


def port_bot(bot_sn, from_sn, to_sn):
    from_node = os.path.join(game_dir, from_sn)
    to_node = os.path.join(game_dir, to_sn)
    shutil.move(
        os.path.join(from_node, bot_sn), os.path.join(to_node, bot_sn),
    )
    # First remove the bot from the current port
    with open(os.path.join(from_node, 'state.json'), 'r+') as from_state_file:
        from_state = json.load(from_state_file)

    for x, col in enumerate(from_state['map']):
        for y, item in enumerate(col):
            if item == from_state['bots'][bot_sn]['icon']:
                from_state['map'][x][y] = ' '
                break

    bot_to_port = copy.deepcopy(from_state['bots'][bot_sn])
    del from_state['bots'][bot_sn]

    with open(os.path.join(from_node, 'state.json'), 'w+') as from_state_file:
        json.dump(from_state, from_state_file)

    # Then spawn in the bot into the new port
    with open(os.path.join(to_node, 'state.json'), 'r+') as to_state_file:
        to_state = json.load(to_state_file)
    to_state['bots'][bot_sn] = bot_to_port

    random.shuffle(to_state['spawn_locs'])
    count = 0
    while True:
        assert count <= len(to_state['spawn_locs']), to_state['spawn_locs']
        spawn_x, spawn_y = to_state['spawn_locs'][count]

        if to_state['map'][spawn_x][spawn_y] == ' ':
            to_state['map'][spawn_x][spawn_y] = to_state['bots'][bot_sn]['icon']
            break
        count += 1

    with open(os.path.join(to_node, 'state.json'), 'w+') as to_state_file:
        json.dump(to_state, to_state_file)


def game_continues():
    return True


if __name__ == "__main__":
    main()
