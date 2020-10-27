#!/usr/bin/python3
from pprint import pprint
import json
import requests
import os
import pickle
import random

PORT_ICONS = [str(i) for i in range(1, 10)] + ["!", "@", "$", "%", "^", "&", "*", "(", ")"]
ACTION_WALK = "walk"
ACTION_DROP = "drop"
ACTION_ATTACK = "attack"
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
        self.iteration = 0
        self.turn_time = 0.1
        os.mkdir(self.game_dir)
        with open('server_state.json', 'r+') as ss_file:
            server_state = json.load(ss_file)
        server_state['games'].append(self.json())
        with open('server_state.json', 'w+') as ss_file:
            json.dump(server_state, ss_file)
            
    def json(self):
        json = {}
        json['port_graph'] = self.port_graph
        json['bots'] = [bot.json() for bot in self.bots]
        json['battlegrounds'] = [bg.json() for bg in self.battlegrounds]
        json['game_dir'] = self.game_dir
        json['coin_icons'] = self.coin_icons 
        json['bot_icons'] = self.bot_icons 
        json['port_icons'] = self.port_icons 
        json['iteration'] = self.iteration
        json['turn_time'] = self.turn_time 
        return json
    
    def add_bot(self, bot):
        bot.game_dir = self.game_dir
        self.bots.append(bot)

    def add_battleground(self, battleground):
        battleground.game_dir = self.game_dir
        battleground.parse_battleground_path()
        self.battlegrounds.append(battleground)

    def log_state(self):
        """ Log the entire gamestate for debugging
        This is called from the game directory so needs no prefix other
        than the filename
        """
        for bg in self.battlegrounds:
            # write out the visual representation of every bg map to a file
            lines = [''.join(list(i)) + '\n' for i in zip(*bg.bg_map)]
            with open(bg.port_icon + ".log", "w+") as bg_file:
                bg_file.writelines(lines)
            # write out the current state of every bg json to a file
            with open(bg.port_icon + ".json", "w+") as bg_file:
                json.dump(bg.json(), bg_file)

        # write out the current state of every bot to a file
        for bot in self.bots:
            with open(bot.bot_icon + ".json", "w+") as bot_file:
                # write out the current state of the bg map to a file
                json.dump(bot.json(), bot_file, indent=2)

        # Pickle the game object so it can be used by the monitoring system
        with open("game.pickle", "wb") as game_pkl:
            pickle.dump(self, game_pkl)

    def print_logs(self):
        # print out the current state of every bg map to stdout
        for bg in self.battlegrounds:
            lines = [''.join(list(i)) + '\n' for i in zip(*bg.bg_map)]
            print("============ BATTLE GROUND {} ============\n{}".format(bg.port_icon, ''.join(lines)))

        for bot in self.bots:
            print(" Bot {}: \n{}".format(bot.bot_icon, json.dumps(bot.json(), indent=2)))

    def init_game(self):

        # go through every bot and add it to a random battleground (trying to only have 1 bot / battleground)
        random.shuffle(self.battlegrounds)
        num_battlegrounds = len(self.battlegrounds)
        #        print("num_bg", num_battlegrounds)
        for i, bot in enumerate(self.bots):
            #            print("i ", i, "bot icon: ", bot.bot_icon)
            for bg in [bg for bg in self.battlegrounds if len(bg.bots) == 0]:
                #                print("Added to empty battleground")
                bg.add_bot(bot)
                break
            else:
                #                print("added to occupied battleground")
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
            self.port_graph['nodes'].append({
                "id": PORT_ICONS[i],
                "label": battleground.username + "/" + battleground.name
            })

        # connect the individual nodes together with links in a way that d3.js will work with
        for i, port_icon in enumerate(self.port_icons):
            self.port_graph['links'].append({
                "source": port_icon,
                "target": self.port_icons[(i + 1) % len(self.port_icons)],
                "value": 1
            })

        # assign bot icons
        self.bot_icons = []
        all_icons = [chr(i) for i in range(65, 91)]
        for bot1 in [bot for bot in self.bots if not bot.bot_icon]:
            index = 0
            while len(bot1.abbreviations) > index:
                #                print("bot1.abbr length is {}, index is {}".format(', '.join(bot1.abbreviations), index))
                for bot2 in [bot for bot in self.bots if bot.bot_icon]:
                    # if this icon is already taken, increment index
                    if bot2.bot_icon == bot1.abbreviations[index]:
                        #                        print("icon {} is taken by bot at {}".format(bot2.bot_icon, bot2.bot_filename))
                        index += 1
                        break
                else:  # no other bot has this icon, so use it
                    bot1.bot_icon = bot1.abbreviations[index]
                    bot1.coin_icon = bot1.abbreviations[index].lower()
                    #                    print("bot at {} is now using icon {}".format(bot1.bot_filename, bot1.bot_icon))
                    break
            else:
                # we've gone through all the abbreviations and they're all taken.
                # so choose one from a list of the english letters
                remaining_icons = [ic for ic in all_icons if ic not in self.bot_icons]
                assert remaining_icons
                bot1.bot_icon = remaining_icons[0]
                bot1.coin_icon = remaining_icons[0].lower()
            #                print("bot at {} forced to use icon {}".format(bot1.bot_filename, bot1.bot_icon))
            self.bot_icons.append(bot1.bot_icon)
            self.coin_icons.append(bot1.coin_icon)

        # now that we know which bots are where & which ports go where,
        # initialise the bg_maps with actual bot icons
        # instead of the placeholder icons
        for battleground in self.battlegrounds:
            battleground.init_bg_map(self.port_graph, self.battlegrounds)

        # Log the graph network to a json file for graphing
        with open(os.path.join(self.game_dir, "port_graph.json"), "w+") as graphfile:
            json.dump(self.port_graph, graphfile)

        # Pickle the game object so it can be used by the judge system
        with open(os.path.join(self.game_dir, "game.pickle"), "wb") as game_pkl:
            pickle.dump(self, game_pkl)


class Bot:
    def __init__(self, game_dir, username, bot_filename, bot_url, name, owner_abbreviations):
        self.game_dir = game_dir
        self.username = username
        self.bot_filename = bot_filename
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
        self.move_dict = {}
        self.coins = []  # an array of Coin objects

    def json(self):
        json = {}
        json['game_dir'] = self.game_dir
        json['username'] = self.username
        json['bot_path'] = self.bot_path
        json['abbreviations'] = self.abbreviations
        json['bot_url'] = self.bot_url
        json['name'] = self.name
        json['coin_icon'] = self.coin_icon
        json['bot_icon'] = self.bot_icon
        json['stderr'] = self.stderr
        json['stdout'] = self.stdout
        json['move_dict'] = self.move_dict
        json['len(coins)'] = len(self.coins)
        return json

    def add_coins(self, new_coins):
        """ Add new coins to the bot.
        If coins from that originating bot already exist, simply increment
        that existing coins object. Otherwise add a new coins object
        """
        for coin in self.coins:
            if coin.originator == new_coins.originator:
                coin.value += new_coins.value
                break
        else:
            self.coins.append(new_coins)

    def perform_action(self, bot_move, game):
        """ Given a requested bot move and game state,
        attempt to perform that move (if it's legal)
        """
        self.move_dict = bot_move
        # print("Bot {} wants to do action {}".format(self.bot_filename, str(bot_move)))
        # Figure out which battleground the bot is on
        curr_bg = None
        for bg in game.battlegrounds:
            for bot in bg.bots:
                if bot.bot_path == self.bot_path:
                    curr_bg = bg

        # Get the bot's current location on the battleground
        bot_locs = curr_bg.find_icon(self.bot_icon)
        assert len(bot_locs) == 1, ", ".join(bot_locs) + " icon: " + self.bot_icon
        bot_loc = list(bot_locs[0])

        # If the bot is just walking around (possibly into a port or air)
        if bot_move['action'] == ACTION_WALK:
            cell = curr_bg.get_cell(bot_loc, bot_move['direction'])

            # If the bot is walking into air
            if cell == IC_AIR:
                # print("\tBot is walking to air")
                # Replace the current spot with air
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = IC_AIR
                # Calculate the new location
                cmd = ''.join(set(bot_move['direction']))  # Remove all duplicated characters
                for c in cmd:
                    bot_loc[0] += CMD_DICT[c][0]
                    bot_loc[1] += CMD_DICT[c][1]

                # Replace the new spot with the bot's icon
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = self.bot_icon

            # If the bot is walking into a coin
            elif cell in game.coin_icons:
                print("\tBot is walking into a coin")
                # Figure out what the coin associated with the given coin_icon is
                for bot in game.bots:
                    if bot.coin_icon == cell:
                        self.add_coins(Coin(bot, 1))
                        break
                # Replace the current spot with air
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = IC_AIR
                # Calculate the new location
                cmd = ''.join(set(bot_move['direction']))  # Remove all duplicated characters
                for c in cmd:
                    bot_loc[0] += CMD_DICT[c][0]
                    bot_loc[1] += CMD_DICT[c][1]

                # Replace the new spot with the bot's icon
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = self.bot_icon

            # If the bot is walking into a port
            elif cell in game.port_icons:
                # Figure out the next battleground
                next_bg = None
                for bg in game.battlegrounds:
                    if bg.port_icon == cell:
                        next_bg = bg
                        break
                print("\tBot is walking into a port going to {}".format(next_bg.port_icon))
                # Figure out the index of the current bot so as to pop it from the
                # Current battlegrounds list of bots
                for i, bot in enumerate(curr_bg.bots):
                    if bot.bot_path == self.bot_path:
                        remove_idx = i
                        break
                # Remove the current bot from the current battleground, and add
                # it to the next battleground.
                next_bg.spawn_bot(curr_bg.bots.pop(remove_idx))
                # And remove the bot's icon from the current battleground
                curr_bg.bg_map[bot_loc[0]][bot_loc[1]] = IC_AIR
            else:
                # If the bot tries to walk anywhere illegal, don't allow it and
                # just stay still
                pass

        # If the bot is attacking another cell
        elif bot_move['action'] == ACTION_ATTACK and bot_move['direction'] is not '':
            # print("\tBot is attacking")
            defender_icon = curr_bg.get_cell(bot_loc, bot_move['direction'])
            attacker_icon = curr_bg.get_cell(bot_loc, '')
            print("\t\t {} attacks  {}".format(attacker_icon, defender_icon))

            is_hit = random.random() < 0.5
            #  check that there's actually a bot at the defending location
            if is_hit and defender_icon in [bot.bot_icon for bot in curr_bg.bots]:
                print("\t\t {} hits  {}".format(attacker_icon, defender_icon))
                attacker, defender = None, None
                for bot in curr_bg.bots:
                    if bot.bot_icon == defender_icon:
                        defender = bot

                    elif bot.bot_icon == attacker_icon:
                        attacker = bot
                    if attacker and defender:
                        break
                # Check that the defender actually has coins to give
                if defender.coins and sum([coin.value for coin in defender.coins]):
                    # Choose a random coin to remove
                    dropped = None
                    random.shuffle(defender.coins)
                    for coin in defender.coins:
                        if coin.value > 0:
                            coin.value -= 1
                            dropped = Coin(coin.originator, 1)
                            print("\t\t {} removes coin({}) from  {}".format(attacker_icon, coin.originator.coin_icon, defender_icon))
                            break
                    # Add that dropped coin onto the map
                    all_deltas = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx != 0 or dy != 0]
                    defender_location = curr_bg.find_icon(defender_icon)
                    assert len(defender_location) == 1
                    defender_location = defender_location[0]

                    legal_deltas = []
                    droppable_icons = [bot.bot_icon for bot in curr_bg.bots] + [IC_AIR]
                    for delta in all_deltas:
                        if curr_bg.get_cell(defender_location, delta) in droppable_icons:
                            legal_deltas.append(delta)
                    coin_delta = random.choice(legal_deltas)
                    coin_loc = [
                        defender_location[0] + coin_delta[0],
                        defender_location[1] + coin_delta[1]
                    ]
                    landed_icon = curr_bg.get_cell(defender_location, coin_delta)
                    print("\t\t coin({}) lands at {}".format(coin.originator.coin_icon, coin_loc))
                    # Check to see if the coin landed on a bot
                    if landed_icon is not IC_AIR:
                        # Add the coin immediately to the bot that it landed on
                        for bot in curr_bg.bots:
                            if bot.bot_icon == landed_icon:
                                bot.add_coins(Coin(dropped.originator, 1))
                                break
                    else:
                        # The coin landed on air, so just add it to the map
                        curr_bg.bg_map[coin_loc[0]][coin_loc[1]] = dropped.originator.coin_icon

        # If the bot is dropping a coin on the floor (to trade possibly)
        elif bot_move.get('action') == ACTION_DROP and \
                bot_move.get('direction') is not '' and \
                bot_move.get('type') is not '':
            """Drop the coin specified in bot_move['type'] onto the ground in the 
            direction of bot_move['direction']
            """
            coin_type = bot_move.get('type')
            # Check that there is empty space / a bot in the direction of bot_move['direction']
            cell = curr_bg.get_cell(bot_loc, bot_move['direction'])
            droppable_icons = [IC_AIR] + [bg_bot.bot_icon for bg_bot in curr_bg.bots]
            if cell in droppable_icons:
                for coin in self.coins:
                    # Check that the bot actually has the coin they want to drop
                    if coin.originator.coin_icon == coin_type and coin.value > 0:
                        # Remove the coin from the bot's inventory
                        coin.value -= 1
                        # Add the bot to the ground / to the adjacent bot
                        for bg_bot in curr_bg.bots:
                            if bg_bot.bot_icon == cell:
                                bg_bot.add_coins(Coin(coin.originator.coin_icon, 1))
                                break
                        else:  # cell is IC_AIR
                            # Calculate the new location
                            cmd = ''.join(set(bot_move['direction']))  # Remove all duplicated characters
                            coin_position = bot_loc[:]
                            for c in cmd:
                                coin_position[0] += CMD_DICT[c][0]
                                coin_position[1] += CMD_DICT[c][1]
                            # Replace the new spot with the coin's icon
                            curr_bg.bg_map[coin_position[0]][coin_position[1]] = coin.originator.coin_icon

                        break


class Coin:
    def __init__(self, originator, value):
        self.originator = originator
        self.value = value


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
        self.num_coins = 1
        self.spawn_locations = []
        self.port_spawn_locations = []
        self.port_locations = []
        self.port_icon = ""

        r = requests.get(self.battleground_url)
        assert r.ok, "request for {} not ok: {}".format(self.battleground_url, r.text)
        # add in the battleground file to the local system
        with open(self.battleground_path, 'w+') as battleground_file:
            battleground_file.write(r.text)

        self.bg_map = [[]]
        self.bots = []

    def json(self):
        json_dict = {}
        json_dict['game_dir'] = self.game_dir
        json_dict['username'] = self.username
        json_dict['battleground_path'] = self.battleground_path
        json_dict['battleground_url'] = self.battleground_url
        json_dict['name'] = self.name
        json_dict['spawn_locations'] = self.spawn_locations
        json_dict['port_spawn_locations'] = self.port_spawn_locations
        json_dict['port_locations'] = self.port_locations
        json_dict['port_icon'] = self.port_icon
        json_dict['bot_icons'] = [bot.bot_icon for bot in self.bots]

        return json_dict

    def find_icon(self, icon):
        returner = []
        for x, col in enumerate(self.bg_map):
            for y, item in enumerate(col):
                if item == icon:
                    returner.append((x, y))
        return returner

    def get_cell(self, bot_loc, cmd):
        pos = list(bot_loc[:])
        if type(cmd) is str:
            # cmd is a string made up of l, r, u, d characters
            cmd = ''.join(set(cmd))  # Remove all duplicated characters
            for c in cmd:
                pos[0] += CMD_DICT[c][0]
                pos[1] += CMD_DICT[c][1]
        elif type(cmd) is tuple and len(cmd) == 2:
            # cmd is a 2-tuple indicating the change in position from bot_loc
            pos[0] += cmd[0]
            pos[1] += cmd[1]

        if not (0 <= pos[0] < len(self.bg_map) or 0 <= pos[1] < len(self.bg_map[0])):
            return None  # trying to walk off the map
        return self.bg_map[pos[0]][pos[1]]

    def add_bot(self, bot):
        """
        add a bot to the battleground's bots array, but don't spawn it in
        to the actual map
        """
        self.bots.append(bot)

    def spawn_bot(self, bot):
        self.bots.append(bot)
        random.shuffle(self.spawn_locations)
        for x, y in self.spawn_locations:
            if self.bg_map[x][y] == IC_AIR:
                self.bg_map[x][y] = bot.bot_icon
                break

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
        Also add in coins
        """

        # Go through the entire map and cache the interesting locations
        for x, col in enumerate(self.bg_map):
            for y, item in enumerate(col):
                if item == IC_SPAWN:
                    self.spawn_locations.append((x, y))
                elif item == IC_PORT:
                    self.port_spawn_locations.append((x, y))
                    self.bg_map[x][y] = IC_AIR
                elif item not in [IC_SPAWN, IC_PORT, IC_WALLS, IC_AIR]:
                    self.bg_map[x][y] = IC_AIR

        # Add in bots to some random spawning locations
        bot_index = 0
        random.shuffle(self.spawn_locations)
        for x, y in self.spawn_locations:
            if bot_index < len(self.bots):
                self.bg_map[x][y] = self.bots[bot_index].bot_icon
                bot_index += 1
            else:
                self.bg_map[x][y] = IC_AIR

        # Add in ports to the map at random locations
        random.shuffle(self.port_spawn_locations)
        # pprint(port_graph)
        relevant_targets = [port['target'] for port in port_graph['links'] if port['source'] == self.port_icon]
        assert len(self.port_spawn_locations) >= len(relevant_targets)
        for i, target in enumerate(relevant_targets):
            x, y == self.port_spawn_locations[i]
            self.bg_map[x][y] = target
            self.port_locations.append((x, y))
            # Add in some coins at random air locations:
        coin_icons = [bot.coin_icon for bot in self.bots]
        # print("num coins: " + str(self.num_coins))
        for i in range(self.num_coins):
            while True:
                rand_row = random.randrange(len(self.bg_map))
                rand_col = random.randrange(len(self.bg_map[0]))
                # print(rand_row, rand_col, len(self.bg_map), len(self.bg_map[0]))
                if self.bg_map[rand_row][rand_col] == IC_AIR:
                    # print("added coin at {}, {}".format(rand_row, rand_col))
                    self.bg_map[rand_row][rand_col] = random.choice(coin_icons)
                    break


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
