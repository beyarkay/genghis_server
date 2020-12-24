#!/usr/bin/python3
from pprint import pprint
import datetime
import json
import os
import requests
import shutil
import subprocess
import sys
import traceback
import util

JUDGE_SYSTEM_SCRIPT = 'judge.py'


def main(server_state_path='server_state.json'):
    """Start a game from scratch
    * create a directory in ./games/
    * Build up a game config file
    * Add in all the players to the game.
    * Add in all the nodes to the game.
    * copy over the judge system script
    * start the game going
    """
    with open(server_state_path, 'r') as server_state_file:
        server_state = json.load(server_state_file)
    need_777 = [
        server_state_path
    ]
    need_permissions = [
        'diff_match_patch.js',
        'follow.html',
        'get_gamestate.php',
        'index.html',
        'register_client.php',
        'script.js',
        'sse.php',
        'styles.css',
    ]
    for f in need_777:
        os.chmod(f, 0o777)

    for f in need_permissions:
        os.chmod(f, 0o755)
    clients = []
    # Create the game directory
    iso_str = datetime.datetime.now().isoformat()
    game = util.Game(os.path.join("games", iso_str), server_state['endpoint'])

    # TODO if there are more than 4 battlegrounds / bots, split them off to seperate games
    for client_obj in server_state['clients']:
        try:
            print(client_obj)
            c = util.Client(
                client_obj['username'],
                client_obj['url'],
                client_obj['abbreviations'],
                game.game_dir
            )
            clients.append(c)
            # Add in the bots to the game
            for bot in clients[-1].bots:
                game.add_bot(bot)

            # Add in the battlegrounds to the game
            for battleground in clients[-1].battlegrounds:
                game.add_battleground(battleground)
        except:
            traceback.print_exc()
            print("Client failed to build, ommiting client at url {} from the game".format(client_obj['url']))

    game.init_game()

    # copy over the judge system script
    shutil.copy2(JUDGE_SYSTEM_SCRIPT, game.game_dir)

    # start the game going
    subprocess.call([
        'sh',
        './start_game.sh',
        game.game_dir.split('/')[-1]
    ])


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()

