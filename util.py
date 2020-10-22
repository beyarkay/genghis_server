import json
import requests
import os
import pickle
import random

PORT_ICONS = [str(i) for i in range(1, 10)] + ["!", "@", "$", "%", "^", "&", "*", "(", ")"]
IC_SPAWN = '_'
IC_PORT = '0'
IC_WALLS = '#'
IC_AIR = ' '
CMD_DICT = {
    'u': (0, -1),
    'r': (1, 0),
    'd': (0, 1),
    'l': (-1, 0),
    '': (0, 0)
}


class Game:
    def __init__(self, game_dir):
        self.port_graph = {
            "links": [],
            "nodes": []
        }
        self.bots = []
        self.battlegrounds = []
        self.game_dir = game_dir
        self.coin_icons = []
        self.bot_icons = []
        self.port_icons = []
        os.mkdir(self.game_dir)

    def add_bot(self, bot):
        bot.game_dir = self.game_dir
        self.bots.append(bot)

    def add_battleground(self, battleground):
        battleground.game_dir = self.game_dir
        battleground.parse_battleground_path()
        self.battlegrounds.append(battleground)

    def init_game(self):
        # setup the ports network
        for i, battleground in enumerate(self.battlegrounds):
            self.port_graph['nodes'].append({
                "id": i,
                "label": battleground.username + "/" + battleground.name
            })
        # and connect the individual nodes together with links in a way that d3.js will work with
        for i, node in enumerate(self.port_graph['nodes']):
            self.port_graph['links'].append({
                "source": i,
                "target": (i + 1) % len(self.port_graph['nodes']),
                "value": 1
            })

        # go through every bot and add it to a random battleground (trying to only have 1 bot / battleground)
        random.shuffle(self.battlegrounds)
        num_battlegrounds = len(self.battlegrounds)
        for i, bot in enumerate(self.bots):
            for bg in [bg for bg in self.battlegrounds if len(bg.bots)]:
                bg.add_bot(bot)
                break
            else:
                # all battlegrounds 
                random_bg = random.choice(self.battlegrounds)
                random_bg.add_bot(bot)

        # go through the ports, bots, coins and assign non-conflicting icons for them
        random.shuffle(self.bots)
        # assign port icons
        self.port_icons = []
        assert len(self.battlegrounds) <= len(PORT_ICONS)
        for i, battleground in enumerate(self.battlegrounds):
            battleground.port_icon = PORT_ICONS[i]
            self.port_icons.append(PORT_ICONS[i])

        # assign bot icons
        self.bot_icons = []
        all_icons = [chr(i) for i in range(65, 91)]
        for bot1 in [bot for bot in self.bots if not bot.bot_icon]:
            index = 0
            while len(bot1.abbreviations) > index:
                for bot2 in [bot for bot in self.bots if bot.bot_icon]:
                    # if this icon is already taken, increment index
                    if bot2.bot_icon == bot1.abbreviations[index]:
                        index += 1
                        break
                else:  # no other bot has this icon, so use it
                    bot1.bot_icon = bot1.abbreviations[index]
                    bot1.coin_icon = bot1.abbreviations[index].lower()
                    break
            else:
                # we've gone through all the abbreviations and they're all taken.
                # so choose one from a list of the english letters
                remaining_icons = [ic for ic in all_icons if ic not in self.bot_icons]
                assert remaining_icons
                bot1.bot_icon = remaining_icons[0]
                bot1.coin_icon = remaining_icons[0].lower()
            self.bot_icons.append(bot1.bot_icon)
            self.coin_icons.append(bot1.coin_icon)
        # now that we know which bots are where & which ports go where,
        # initialise the bg_maps with actual bot icons
        # instead of the placeholder icons
        for battleground in self.battlegrounds:
            battleground.init_bg_map(self.port_graph, self.battlegrounds)

        # Log the graph network to a json file for graphing
        with open(os.path.join(self.game_dir, "port_graph.json", "w+")) as graphfile:
            json.dump(self.port_graph, graphfile)

        # Pickle the game object so it can be used by the judge system
        with open(os.path.join(self.game_dir, "game.pkl", "w+")) as game_pkl:
            json.dump(self, game_pkl)


class Bot:
    def __init__(self, game_dir, username, bot_filename, bot_url, name, owner_abbreviations):
        self.game_dir = game_dir
        self.username = username

        self.bot_path = os.path.join(self.game_dir, username, bot_filename)
        # make sure the path exists
        if not os.path.exists(os.path.join(self.game_dir, self.username)):
            os.mkdir(os.path.join(self.game_dir, username))
        self.abbreviations = [abbr.upper() for abbr in owner_abbreviations]
        self.bot_url = bot_url
        self.name = name
        self.coin_icon = ""
        self.bot_icon = ""
        r = requests.get(self.bot_url)
        assert r.ok, "request for {} not ok: {}".format(self.bot_url, r.text)
        # add in the bot file to the local system
        with open(self.bot_path, 'w+') as bot_file:
            bot_file.write(r.text)
        # Give a stderr, stdout for debugging
        self.stderr = ""
        self.stdout = ""
        self.coins = {

        }

    def move(self, bot_move, game):
        return
        # TODO figure out how to move the bot properly
        # Figure out which battleground the bot is on
        curr_bg = None
        for bg in game.battlegrounds:
            for bot in bg.bots:
                if bot.bot_path == self.bot_path:
                    curr_bg = bg

        # Get the bot's current location on the battleground
        bot_locs = curr_bg.find_icon(self.bot_icon)
        assert len(bot_locs) == 1
        bot_loc = bot_locs[0]

        # Evaluate the bot's requested move
        if bot_move['action'] == ACTION_WALK:
            cell = curr_bg.get_cell(bot_loc, bot_move['direction'])

            # If the bot is walking into air
            if cell == IC_AIR:
                # Replace the current spot with air
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = IC_AIR
                # Calculate the new location
                cmd = ''.join(set(bot_move['direction']))  # Remove all duplicated characters
                for c in cmd:
                    bot_loc[0] += CMD_DICT[c][0]
                    bot_loc[1] += CMD_DICT[c][1]

                # Replace the new spot with the bot's icon
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = bot.bot_icon

            # If the bot is walking into a coin
            elif cell in state['coin_map'].values():
                # Figure out what the coin associated with the given coin_icon is
                index = list(state['coin_map'].values()).index(icon)
                coin_id = list(state['coin_map'].keys())[index]

                if 'coins' not in state['bots'][sn].keys():
                    state['bots'][sn]['coins'] = {}

                if coin_id in state['bots'][sn]['coins'].keys():
                    state['bots'][sn]['coins'][coin_id] += 1
                else:
                    state['bots'][sn]['coins'][coin_id] = 1

                # utils.grab_coin(sn, cell, state)
                utils.move_bot(bot_loc, bot_move['direction'], bot_icon, state['map'])

            # If the bot is walking into a port
            elif cell in state['port_map'].values():
                from_sn = node_dir.split('/')[-1]
                to_sn = [k for k, v in state['port_map'].items() if v == cell][0]
                port_bot(sn, from_sn, to_sn)
                with open(os.path.join(node_dir, 'state.json'), 'r+') as state_file:
                    state = json.load(state_file)
            else:
                # If the bot tries to walk anywhere else, don't allow it and
                # just stay still
                pass


        # If the bot is attacking another cell
        elif bot_move['action'] == ACTION_ATTACK and bot_move['direction'] is not '':
            bot_icons = [bot['icon'] for bot in state['bots'].values()]
            if utils.get_cell(bot_loc, bot_move['direction'], state['map']) in bot_icons:
                state = utils.attack(bot_loc, bot_move['direction'], bot_move['weapon'], state)


class Battleground:
    def __init__(self, game_dir, username,
                 battleground_filename, battleground_url,
                 name):
        self.game_dir = game_dir
        self.username = username
        self.battleground_path = os.path.join(self.game_dir, username, battleground_filename)
        # make sure the path exists
        if not os.path.exists(os.path.join(self.game_dir, self.username)):
            os.mkdir(os.path.join(self.game_dir, username))
        self.battleground_url = battleground_url
        self.name = name
        self.spawn_locations = []
        self.port_locations = []
        self.port_icon = ""

        r = requests.get(self.battleground_url)
        assert r.ok, "request for {} not ok: {}".format(self.battleground_url, r.text)
        # add in the battleground file to the local system
        with open(self.battleground_path, 'w+') as battleground_file:
            battleground_file.write(r.text)

        self.bg_map = [[]]
        self.iteration = 0
        self.bots = []

    def find_icon(self, icon):
        returner = []
        for x, col in enumerate(self.bg_map):
            for y, item in enumerate(col):
                if item == icon:
                    returner.append((x, y))
        return returner

    def get_cell(self, bot_loc, cmd):
        cmd = ''.join(set(cmd))  # Remove all duplicated characters
        pos = bot_loc[:]
        for c in cmd:
            pos[0] += CMD_DICT[c][0]
            pos[1] += CMD_DICT[c][1]

        if not (0 <= pos[0] < len(self.bg_map) or 0 <= pos[1] < len(self.bg_map[0])):
            return None  # trying to walk off the map
        return self.bg_map[pos[0]][pos[1]]

    def add_bot(self, bot):
        """
        add a bot to the battleground's bots array, but don't spawn it in
        to the actual map
        """
        self.bots.append(bot)
        pass

    def parse_battleground_path(self, path=""):
        """
        convert the raw text of the battleground at the location of
        path (or self.battleground_path) into a 2d array,
        stored in self.bg_map
        """
        if path == "":
            path = self.battleground_path

        with open(path, 'r') as battleground_file:
            parsed = [line.strip() for line in battleground_file.readlines()]
        self.bg_map = [list(i) for i in zip(*parsed)]

    def init_bg_map(self, port_graph, battlegrounds):
        """
        take the raw template input of the battleground, the bots and ports,
        and replace instances of ic_spawn with bots and ic_port with ports.
        """
        for x, col in enumerate(self.bg_map):
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
                self.bg_map[x][y] = IC_AIR

        port_index = 0
        random.shuffle(self.port_locations)
        bg_label = self.username + "/" + self.name
        relevant_ports = [port for port in port_graph['links'] if port['source'] == bg_label]
        for x, y in self.port_locations:
            if port_index < len(relevant_ports):
                target_node = [node for node in port_graph['nodes'] if node['id'] == relevant_ports['target']][0]
                username, name = target_node['label'].split('/')
                # FIXME assert that battleground username/name combos are unique in a game
                icon = ""
                for battleground in battlegrounds:
                    if battleground.name == name and battleground.username == username:
                        icon = battleground.port_icon
                        break
                else:
                    assert False, "Battleground for {}/{} not found".format(username, name)
                self.bg_map[x][y] = icon
                print("port icon {} for battleground {}".format(icon, self.battleground_url))
                port_index += 1
            else:
                self.bg_map[x][y] = IC_AIR


class Client:
    def __init__(self, username, url, abbreviations, game_dir):
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
                game_dir, self.username, item['path'],
                self.url + '/' + item['path'], item['name'],
                json_result['abbreviations']
            ))

        self.battlegrounds = []
        for item in json_result['battlegrounds']:
            path = self.url + '/' + item['path']
            r = requests.get(path)
            assert r.ok, path + r.text
            self.battlegrounds.append(Battleground(
                game_dir, self.username,
                item['path'], self.url + '/' + item['path'],
                item['name'],
            ))
