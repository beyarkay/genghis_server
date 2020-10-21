import json
import requests
import os
import random

PORT_ICONS = [str(i) for i in range(1, 10)] + ["!", "@", "$", "%", "^", "&", "*", "(", ")"]


class Client:
    def __init__(self, username, url, abbreviations):
        self.username = username
        self.url = url
        self.abbreviations = abbreviations[:]
        r = requests.get(self.url + "/config.json")
        assert r.ok, self.url + "/config.json\n" + r.text
        self.bots = []
        json_result = r.json()
        for item in json_result['bots']:
            path = self.url + '/' + item['path']
            r = requests.get(path)
            assert r.ok, path + r.text
            self.bots.append(Bot(
                "", self.username, item['path'],
                self.url + '/' + item['path'], item['name'],
                json_result['abbreviations']
            ))

        self.battlegrounds = []
        for item in json_result['battlegrounds']:
            path = self.url + '/' + item['path']
            r = requests.get(path)
            assert r.ok, path + r.text
            self.battlegrounds.append(Battleground(
                "", self.username,
                item['path'], self.url + '/' + item['path'],
                item['name'],
            ))


class Game:
    def __init__(self, game_dir):
        self.port_graph = {
            "links": [],
            "nodes": []
        }
        self.bots = []
        self.battlegrounds = []
        self.game_dir = game_dir
        os.mkdir(self.game_dir)

    def add_user_dir(self, username):
        if not os.path.exists(os.path.join(self.game_dir, username)):
            os.mkdir(os.path.join(self.game_dir, username))

    def add_bot(self, bot: Bot):
        self.add_user_dir(bot.owner_username)
        bot.game_dir = self.game_dir
        self.bots.append(bot)

    def add_battleground(self, battleground: Battleground):
        self.add_user_dir(battleground.owner_username)
        battleground.game_dir = self.game_dir
        battleground.parse_battleground_path()
        self.battlegrounds.append(battleground)

    def init_game(self):
        # Setup the ports network
        for i, battleground in enumerate(self.battlegrounds):
            self.port_graph['nodes'].append({
                "id": i,
                "label": battleground.owner_username + "/" + battleground.name
            })
        # And connect the individual nodes together with links in a way that D3.js will work with
        for i, node in self.port_graph['nodes']:
            self.port_graph['links'].append({
                "source": i,
                "target": (i + 1) % len(self.port_graph['nodes']),
                "value": 1
            })

        # Go through every bot and add it to a random battleground (trying to only have 1 bot / battleground)
        num_battlegrounds = len(self.battlegrounds)
        for i, bot in enumerate(self.bots):
            battleground_index = random.randint(0, num_battlegrounds)
            final_index = battleground_index

            # Loop through all the battlegrounds, until you either find an empty one or have looped all the way through
            while len(self.battlegrounds[battleground_index % len(self.battlegrounds)].bots) > 0 \
                    and final_index > battleground_index - len(self.battlegrounds):
                print("bg_index = {}, final_index = {}".format(battleground_index, final_index))
                battleground_index += 1
            self.battlegrounds[battleground_index].add_bot(bot)

        # TODO Figure out a non-conflicting map of ports, coins, and bot-icon-abbreviations
        random.shuffle(self.battlegrounds)
        random.shuffle(self.bots)
        # Assign port icons
        assert len(self.battlegrounds) <= len(PORT_ICONS)
        for i, battleground in enumerate(self.battlegrounds):
            battleground.port_icon = PORT_ICONS[i]

        # Assign bot icons
        used_icons = []
        all_icons = [chr(i) for i in range(65, 91)]
        for bot1 in [bot for bot in self.bots if not bot.bot_icon]:
            index = 0
            while len(bot1.abbreviations) > index:
                for bot2 in [bot for bot in self.bots if bot.bot_icon]:
                    # If this icon is already taken, increment index
                    if bot2.bot_icon == bot1.abbreviations[index]:
                        index += 1
                        break
                else: # no other bot has this icon, so use it
                    bot1.bot_icon = icon
                    bot1.coin_icon = icon.lower()
                    used_icons.append(icon)
                    break
            else:
                # We've gone through all the abbreviations and they're all taken.
                # So choose one from a list of the english letters
                remaining_icons = [ic for ic in all_icons if ic not in used_icons]
                assert remaining_icons
                bot1.bot_icon = remaining_icons[0]
                bot1.coin_icon = remaining_icons[0].lower()
                used_icons.append(remaining_icons[0])
            print(bot1.bot_url, bot1.bot_icon)


        # Now that we know which bots are where & which ports go where,
        # initialise the bg_maps with actual bot icons
        # instead of the placeholder icons
        for battleground in self.battlegrounds:
            battleground.init_bg_map(self.port_graph, self.battlegrounds)


class Bot:
    def __init__(self, game_dir, owner_username, bot_filename, bot_url, name, owner_abbreviations):
        self.game_dir = game_dir
        self.owner_username = owner_username
        self.bot_path = os.path.join(self.game_dir, owner_username, bot_filename)
        self.abbreviations = [abbr.upper() for abbr in owner_abbreviations]
        self.bot_url = bot_url
        self.name = name
        self.coin_icon = ""
        self.bot_icon = ""
        r = requests.get(self.bot_url)
        assert r.ok, "Request for {} not ok: {}".format(self.bot_url, r.text)
        # Add in the bot file to the local system
        with open(self.bot_path, 'w+') as bot_file:
            bot_file.write(r.text)


class Battleground:
    def __init__(self, game_dir, owner_username,
                 battleground_filename, battleground_url,
                 name):
        self.game_dir = game_dir
        self.owner_username = owner_username
        self.battleground_path = os.path.join(self.game_dir, owner_username, battleground_filename)
        self.battleground_url = battleground_url
        self.name = name
        self.spawn_locations = []
        self.port_locations = []
        self.port_icon = ""

        r = requests.get(self.battleground_url)
        assert r.ok, "Request for {} not ok: {}".format(self.battleground_url, r.text)
        # Add in the battleground file to the local system
        with open(self.battleground_path, 'w+') as battleground_file:
            battleground_file.write(r.text)

        self.bg_map = [[]]
        self.iteration = 0
        self.bots = []

    def add_bot(self, bot: Bot):
        """
        Add a bot to the battleground's bots array, but don't spawn it in
        to the actual map
        """
        self.bots.append(bot)
        pass

    def parse_battleground_path(self, path=""):
        """
        Convert the raw text of the battleground at the location of
        path (or self.battleground_path) into a 2D array,
        stored in self.bg_map
        """
        if path == "":
            path = self.battleground_path

        with open(path, 'r') as battleground_file:
            parsed = [line.strip() for line in battleground_file.readlines()]
        self.bg_map = [list(i) for i in zip(*parsed)]

    def init_bg_map(self, port_graph, battlegrounds):
        """
        Take the raw template input of the battleground, the bots and ports,
        and replace instances of IC_SPAWN with bots and IC_PORT with ports.
        """
        IC_SPAWN = '_'
        IC_PORT = '0'
        IC_WALLS = '#'
        IC_AIR = ' '
        for x, col in enumerate(battleground.bg_map):
            for y, item in enumerate(col):
                if item == IC_SPAWN:
                    self.spawn_locations.append((x, y))
                elif item == IC_PORT:
                    self.port_locations.append((x, y))
                elif item not in [IC_SPAWN, IC_PORT, IC_WALLS, IC_AIR]:
                    item = IC_AIR

        bot_index = 0
        random.shuffle(self.spawn_locations)
        for x, y in self.spawn_locations:
            if bot_index < len(self.bots):
                self.bg_map[x][y] = self.bots[bot_index].bot_icon
                bot_index += 1
            else:
                battleground.bg_map[x][y] = IC_AIR

        port_index = 0
        random.shuffle(self.port_locations)
        bg_label = self.owner_username + "/" + self.name
        relevant_ports = [port for port in port_graph['links'] if port['source'] == bg_label]
        for x, y in self.port_locations:
            if port_index < len(relevant_ports):
                target_node = [node for node in port_graph['nodes'] if node['id'] == relevant_ports['target']][0]
                username, name = target_node['label'].split('/')
                # FIXME assert that battleground username/name combos are unique in a game
                icon = ""
                for battleground in battlegrounds:
                    if battleground.name == name and battleground.owner_username == username:
                        icon = battleground.port_icon
                        break
                else:
                    assert False, "Battleground for {}/{} not found".format(username, name)
                self.bg_map[x][y] = icon
                print("port icon {} for battleground {}".format(icon, battleground.battleground_url))
                port_index += 1
            else:
                battleground.bg_map[x][y] = IC_AIR
