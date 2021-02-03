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

def allocate_permissions():
    need_777 = [
        'server_state.json',
        '.new_clients.json',
    ]
    for f in need_777:
        os.chmod(f, 0o777)
    need_755 = [
        'cgi-bin',
        'clients.json',
        'diff_match_patch.js',
        'favicon.ico',
        'follow.html',
        'index.html',
        'requests.php',
        'script.js',
        'sse.php',
        'styles.css',
    ]

    for f in need_755:
        os.chmod(f, 0o755)

def main(server_state_path='server_state.json'):
    """
    There are several tasks needed to build and start a new game.

    * Give files correct permissions
    * Read in the list of clients
    * Import the bots and battleground files from the clients
    * If required: setup a server on localhost
    * Create a game object from the util script
    * Initialise the game's battlegrounds, port networks, etc
    * Copy over the judge script to the game directory
    * Actually start the game
    """
    with open('clients.json', 'r') as clients_file:
        clients_json = json.load(clients_file).get('clients', [])

    with open(server_state_path, 'r') as server_state_file:
        server_state = json.load(server_state_file)

    allocate_permissions()


    # Create the game directory
    iso_str = datetime.datetime.now().isoformat()
    game = util.Game(os.path.join("games", iso_str), server_state['endpoint'])

    # TODO if there are more than 4 battlegrounds / bots, split them off to seperate games
    clients = []
    print(server_state.get('clients'))
    all_clients = server_state.get('clients', []) + clients_json
    print("Processing all clients:")
    for client_obj in all_clients:
        try:
            print(client_obj)
            c = util.Client(
                client_obj.get('username'),
                client_obj.get('url'),
                client_obj.get('abbreviations'),
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

