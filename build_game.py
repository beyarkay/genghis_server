#!/usr/bin/python3
import requests
from pprint import pprint
import os
import datetime
import json
import shutil
import subprocess
import util

SERVER_STATE_FILE = 'server_state.json'
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
    # TODO Every time this runs, reset the file permissions to 0o755 where needed

    with open(SERVER_STATE_FILE, 'r') as server_state_file:
        server_state = json.load(server_state_file)

    need_permissions = ['www/script.js', 'get_gamestate.php', 'index.html', 'www', 'www/follow.html', 'www/styles.css', 'register_client.php', 'server_state.json']
    for f in need_permissions:
        os.chmod(f, 0o755)
    clients = []
    # Create the game directory
    iso_str = datetime.datetime.now().isoformat()
    game = util.Game(os.path.join("games", iso_str))

    for client_obj in server_state['clients']:
        clients.append(util.Client(
            client_obj['username'],
            client_obj['url'],
            client_obj['abbreviations'],
            game.game_dir
        ))

        # Add in the battlegrounds to the game
        for battleground in clients[-1].battlegrounds:
            game.add_battleground(battleground)

        # Add in the bots to the game
        for bot in clients[-1].bots:
            game.add_bot(bot)

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
