#!/usr/bin/python3
from pprint import pprint
import datetime
import json
import os
import requests
import shutil
import subprocess
import sys
import util

SERVER_STATE_FILE = 'server_state.json' if len(sys.argv) < 2 else sys.argv[1]
JUDGE_SYSTEM_SCRIPT = 'judge.py'


def main():
    """Start a game from scratch
    create a directory in ./games/
    Build up a game config file
    Add in all the players to the game.
    Add in all the nodes to the game.
    copy over the judge system script
    start the game going
    """
    with open(SERVER_STATE_FILE, 'r') as server_state_file:
        server_state = json.load(server_state_file)
    need_777 = [
        SERVER_STATE_FILE
    ]
    need_permissions = [
        'index.html',
        'follow.html',
        'diff_match_patch.js',
        'script.js',
        'styles.css',
        'register_client.php',
        'get_gamestate.php',
    ]
    for f in need_777:
        os.chmod(f, 0o777)

    for f in need_permissions:
        os.chmod(f, 0o755)
    clients = []
    # Create the game directory
    iso_str = datetime.datetime.now().isoformat()
    game = util.Game(os.path.join("games", iso_str))

    for client_obj in server_state['clients']:
        try:
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
    main()
