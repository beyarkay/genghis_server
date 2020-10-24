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
        os.mkdir(self.game_dir)

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
        # write out the current state of every bg map to a file
        for bg in self.battlegrounds:
            lines = [''.join(list(i)) + '\n' for i in zip(*bg.bg_map)] 
            #lines.append(bg.json())
            with open(bg.port_icon + ".log", "w+") as bg_file:
                bg_file.writelines(lines)

        # write out the current state of every bot to a file
        for bot in self.bots:
            with open(bot.bot_icon + ".log", "w+") as bot_file:
                # write out the current state of the bg map to a file
                json.dump(bot.json(), bot_file, indent=2)

    def print_logs(self):
        # print out the current state of every bg map to stdout
        for bg in self.battlegrounds:
            lines = [''.join(list(i)) + '\n' for i in zip(*bg.bg_map)] 
            print("============ BATTLE GROUND {} ============\n{}".format(bg.port_icon, ''.join(lines))) 

        for bot in self.bots:
            print(" Bot {}: \n{}".format(bot.bot_icon, json.dumps(bot.json(), indent=2)))


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
        print("num_bg", num_battlegrounds)
        for i, bot in enumerate(self.bots):
            print("i ", i, "bot icon: ", bot.bot_icon)
            for bg in [bg for bg in self.battlegrounds if len(bg.bots) == 0]:
                print("Added to empty battleground")
                bg.add_bot(bot)
                break
            else:
                print("added to occupied battleground")
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
                print("bot1.abbr length is {}, index is {}".format(', '.join(bot1.abbreviations), index))
                for bot2 in [bot for bot in self.bots if bot.bot_icon]:
                    # if this icon is already taken, increment index
                    if bot2.bot_icon == bot1.abbreviations[index]:
                        print("icon {} is taken by bot at {}".format(bot2.bot_icon, bot2.bot_filename))
                        index += 1
                        break
                else:  # no other bot has this icon, so use it
                    bot1.bot_icon = bot1.abbreviations[index]
                    bot1.coin_icon = bot1.abbreviations[index].lower()
                    print("bot at {} is now using icon {}".format(bot1.bot_filename, bot1.bot_icon))
                    break
            else:
                # we've gone through all the abbreviations and they're all taken.
                # so choose one from a list of the english letters
                remaining_icons = [ic for ic in all_icons if ic not in self.bot_icons]
                assert remaining_icons
                bot1.bot_icon = remaining_icons[0]
                bot1.coin_icon = remaining_icons[0].lower()
                print("bot at {} forced to use icon {}".format(bot1.bot_filename, bot1.bot_icon))
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
        with open(os.path.join(self.game_dir, "game.pickle"),"wb") as game_pkl:
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
            self.coins.append(coins)

    def perform_action(self, bot_move, game):
        """ Given a requested bot move and game state,
        attempt to perform that move (if it's legal)
        """
        print("Bot {} wants to do action {}".format(self.bot_filename, str(bot_move)))
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
                print("\tBot is walking to air")
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
                print("\tBot is walking to a coin")
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
                print("\tBot is walking to a port")
                # Figure out the next battleground
                for bg in game.battlegrounds:
                    if bg.port_icon == cell:
                        next_bg = bg
                        break
                # Figure out the index of the current bot so as to pop it from the
                # Current battlegrounds list of bots
                for i, bot in enumerate(curr_bg.bots):
                    if bot.bot_path == self.bot_path:
                        remove_idx = i
                        break
                # Remove the current bot from the current battleground, and add
                # it to the next battleground.
                # TODO the game doesn't actually check for new bots that arenot on the bg
                next_bg.append(curr_bg.bots.pop(remove_idx))
            else:
                # If the bot tries to walk anywhere illegal, don't allow it and
                # just stay still
                pass

        # If the bot is attacking another cell
        elif bot_move['action'] == ACTION_ATTACK and bot_move['direction'] is not '':
            print("\tBot is attacking")
            defender_icon = curr_bg.get_cell(bot_loc, bot_move['direction'])
            attacker_icon = curr_bg.get_cell(bot_loc, '')

            is_hit = random.random() < 0.5
            #  check that there's actually a bot at the defending location
            if is_hit and defender_icon in [bot.bot_icon for bot in curr_bg.bots]:
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
                            break
                    # Add that dropped coin onto the map
                    all_deltas = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx != 0 or dy != 0]
                    defender_location = curr_bg.find_icon(defender_icon)
                    assert len(defender_location) == 1
                    defender_location = defender_location[0]

                    legal_locations = []
                    droppable_icons = [bot.bot_icon for bot in curr_bg.bots] + [IC_AIR]
                    for delta in all_deltas:
                        if curr_bg.get_cell(defender_location, delta) in droppable_icons:
                            legal_locations.append(delta)
                    coin_loc = random.choice(legal_locations)

                    landed_icon = curr_bg.get_cell(defender_location, coin_loc)
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

                else:
                    # The defender doesn't have any coins to drop...
                    pass

        # If the bot is dropping a coin on the floor (to trade possibly)
        elif bot_move['action'] == ACTION_DROP and bot_move['direction'] is not '':
            # TODO implement this
            pass


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
        self.spawn_locations = []
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
        jstring= {}
        jstring['game_dir'] = self.game_dir
        jstring['username'] = self.username
        jstring['battleground_path'] = self.battleground_path
        jstring['battleground_url'] = self.battleground_url
        jstring['name'] = self.name
        jstring['spawn_locations'] = self.spawn_locations
        jstring['port_locations'] = self.port_locations
        jstring['port_icon'] = self.port_icon
        jstring['bot_icons'] = [bot.bot_icon for bot in self.bots]

        return json.dumps(jstring, indent=2)




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
