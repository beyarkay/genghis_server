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

RE_SN = re.compile(r'(\w{6}\d{3})')
gm_dir = '/' + os.path.join(*os.path.abspath(__file__).split(os.sep)[:-1])
battleground = []
SPAWN_LOCS = []
PORT_LOCS = []
game_dir = ''
SLEEP_DURATION = 0.5


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

    #       Actually move the bot in the gamestate
        bot.move(bot_move, game)

    #       Log the movement to the logfiles

    #       Log the bots score to a json for graphing


def step():
    update_dirs()

    # node_dirs = sorted([d for d in glob.glob(os.path.join(game_dir, '*')) if RE_SN.search(d.split(os.sep)[-1])])
    # for node_dir in node_dirs:
    #     print(f'\n\n==========={node_dir.split(os.sep)[-1]}=================')
    #     bot_dirs = sorted([d for d in glob.glob(os.path.join(node_dir, '*')) if RE_SN.search(d.split(os.sep)[-1])])
    #     for bot_dir in bot_dirs:
    #         with open(os.path.join(node_dir, 'state.json'), 'r') as state_file:
    #             state = json.load(state_file)
    #
    #         # Split up the sleep duration to look better on the map
    #         time.sleep(SLEEP_DURATION / 2)
    #         state['curr_move'] = bot_dir.split('/')[-1]
    #         with open(os.path.join(node_dir, 'state.json'), 'w+') as statefile:
    #             json.dump(state, statefile, indent=2)
    #         time.sleep(SLEEP_DURATION / 2)
    #
    #         state['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         sn = bot_dir.split(os.sep)[-1]
    #
    #         # Save the changes made to the statefile
    #         with open(os.path.join(node_dir, 'state.json'), 'w+') as statefile:
    #             json.dump(state, statefile, indent=2)
    #
    #         # Dump the state file for the bot to read from
    #         with open(os.path.join(bot_dir, 'state.json'), 'w+') as statefile:
    #             json.dump(utils.prune_state(state, sn), statefile, indent=2)
    #
    #         # Backwards compatability for layout.txt files
    #         utils.write_deprecated(state, bot_dir)
    #         # Execute the bot file, make sure it doesn't take too long
    #         try:
    #             result = subprocess.run(
    #                 ['python3', os.path.join(bot_dir, 'bot.py')],
    #                 timeout=1,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 universal_newlines=True
    #             )
    #             if not result.returncode:
    #                 print(result.stderr)
    #             state['bots'][sn]['stdout'] = result.stdout.replace('\n', '<br>')
    #             state['bots'][sn]['stderr'] = result.stderr.replace('\n', '<br>')
    #
    #             with open(os.path.join(bot_dir, 'move.json'), 'r') as move_file:
    #                 bot_move = json.load(move_file)
    #         except Exception as e:
    #             print('Bot move for {} was unsuccessful, the bot will stand still'.format(bot_dir))
    #             bot_move = {
    #                 'action': 'walk',
    #                 'direction': ''
    #             }
    #             traceback.print_exc()
    #
    #         # Get the bot's current location
    #         bot_icon = state['bots'][sn]['icon']
    #         bot_loc = utils.find_icon(state['map'], bot_icon)
    #         assert bot_loc[0] is not None and bot_loc[1] is not None, state['map']
    #
    #         # Evaluate the bot's requested move
    #         if bot_move['action'] == 'walk':
    #             cell = utils.get_cell(bot_loc, bot_move['direction'], state['map'])
    #
    #             # If the bot is walking into air
    #             if cell == ' ':
    #                 utils.move_bot(bot_loc, bot_move['direction'], bot_icon, state['map'])
    #
    #             # If the bot is walking into a coin
    #             elif cell in game.coin_icons:
    #
    #                 utils.grab_coin(sn, cell, state)
    #                 utils.move_bot(bot_loc, bot_move['direction'], bot_icon, state['map'])
    #
    #             # If the bot is walking into a port
    #             elif cell in state['port_map'].values():
    #                 from_sn = node_dir.split('/')[-1]
    #                 to_sn = [k for k, v in state['port_map'].items() if v == cell][0]
    #                 port_bot(sn, from_sn, to_sn)
    #                 with open(os.path.join(node_dir, 'state.json'), 'r+') as state_file:
    #                     state = json.load(state_file)
    #
    #
    #         # If the bot is attacking another cell
    #         elif bot_move['action'] == 'attack' and bot_move['direction'] is not '':
    #             bot_icons = [bot['icon'] for bot in state['bots'].values()]
    #             if utils.get_cell(bot_loc, bot_move['direction'], state['map']) in bot_icons:
    #                 state = utils.attack(bot_loc, bot_move['direction'], bot_move['weapon'], state)
    #
    #         elif bot_move['action'] == '':
    #             pass
    #
    #         # Write every node's statefile to a mirror for the website to read from
    #         node_sn = node_dir.split('/')[-1]
    #         node_statefile_path = os.path.join(gm_dir, node_sn, 'state.json')
    #         with open(node_statefile_path, 'w+') as statefile:
    #             json.dump(state, statefile, indent=2)
    #         os.chmod(node_statefile_path, 0o755)  # Make sure the websites can read this file
    #
    #         # Save the changes made to the statefile
    #         with open(os.path.join(node_dir, 'state.json'), 'w+') as statefile:
    #             json.dump(state, statefile, indent=2)


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
