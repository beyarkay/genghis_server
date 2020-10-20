import requests
import sys
from pprint import pprint
import os
import datetime
import json
import shutil
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
    # Build up a game-config file from the defaults
    config = {
        "root_urls": [],
        "bot_urls": [],
        "battleground_urls": [],
    }
    with open(SERVER_STATE_FILE, 'r') as server_state_file:
        server_state = json.load(server_state_file)

    clients = []
    for client_obj in server_state['clients']:
        print(c.url)
        clients.append(util.Client(
            client_obj['username'],
            client_obj['url'],
            client_obj['abbreviations']
        ))
        # Add in the bots to the game
        for bot_url in clients[-1].bots:
            bot_request = requests.get(bot_url)
            bot_path_str = (clients[-1].username + '_' + bot_url.replace(root_url + '/', '')).replace('/', '_')
            if bot_request.ok:
                bot_path = os.path.join(game_dir, bot_path_str)
                if not os.path.exists('/'.join(bot_path.split('/')[:-1])):
                    os.mkdir('/'.join(bot_path.split('/')[:-1]))
                with open(bot_path, 'w+') as botfile:
                    botfile.write(bot_request.text)

        # Add in the battlegrounds to the game
        for battleground_url in clients[-1].battlegrounds:
            battleground_request = requests.get(battleground_url)
            battleground_path_str = (clients[-1].username + '_' + battleground_url.replace(root_url + '/', '')).replace('/', '_')
            if battleground_request.ok:
                battleground_path = os.path.join(game_dir, battleground_path_str)
                if not os.path.exists('/'.join(battleground_path.split('/')[:-1])):
                    os.mkdir('/'.join(battleground_path.split('/')[:-1]))
                with open(battleground_path, 'w+') as battlegroundfile:
                    battlegroundfile.write(battleground_request.text)

    # Create the game directory
    iso_str = datetime.datetime.now().isoformat()
    game_dir = os.path.join("games", iso_str)
    os.mkdir(game_dir)

    # # Add in all the bots to the game
    # for bot_url, root_url in zip(config['bot_urls'], config['root_urls']):
    #     bot_request = requests.get(bot_url)
    #     bot_path_str = bot_url.replace(root_url + '/', '').replace('/', '_')
    # 
    #     if bot_request.ok:
    #         bot_path = os.path.join(game_dir, bot_path_str)
    #         if not os.path.exists('/'.join(bot_path.split('/')[:-1])):
    #             os.mkdir('/'.join(bot_path.split('/')[:-1]))
    #         with open(bot_path, 'w+') as botfile:
    #             botfile.write(bot_request.text)

    # Add in all the battlegrounds to the game
    # for battleground_url, root_url in zip(config['battleground_urls'], config['root_urls']):
    #     battleground_request = requests.get(battleground_url)
    #     battleground_path_str = battleground_url.replace(root_url + '/', '')
    #     if battleground_request.ok:
    #         battleground_path = os.path.join(game_dir, battleground_path_str)
    #         if not os.path.exists('/'.join(battleground_path.split('/')[:-1])):
    #             os.mkdir('/'.join(battleground_path.split('/')[:-1]))
    #         with open(battleground_path, 'w+') as battlegroundfile:
    #             battlegroundfile.write(battleground_request.text)

    # copy over the judge system script
    shutil.copy2(JUDGE_SYSTEM_SCRIPT, game_dir)

    # start the game going
    print("now the game is going...")


if __name__ == '__main__':
    main()
