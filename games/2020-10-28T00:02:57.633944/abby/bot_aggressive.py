#!/usr/bin/python3
"""
Date: 2020-10-24
Author: Boyd Kane: https://github.com/beyarkay
This is the bare-bones, default bot for the genghis battle system. (https://github.com/beyarkay/genghis_client)
"""

import json
import pickle
import os
import sys
import random
# add the server directory to the PATH so we can import the utilities file
sys.path.append(sys.argv[1])
import util

# MOTION_ASTRAY Move randomly in one of the 8 directions. Doesn't check for obstructions
MOTION_ASTRAY = "ASTRAY"
# MOTION_BLOODTHIRSTY Move towards the nearest bot and fight. Passes to the next priority if there are no bot on the current battleground
MOTION_BLOODTHIRSTY = "BLOODTHIRSTY"
# MOTION_CURIOUS Always move towards the nearest port and go through it
MOTION_CURIOUS = "CURIOUS"
# MOTION_GENEROUS First finds a battleground with another bot, then cycles between picking up and dropping in front of some bot
MOTION_GENEROUS = "CLUMSY"
# MOTION_GREEDY Always move towards the nearest coin. Passes to the next priority if there are no coins on the current battleground
MOTION_GREEDY = "GREEDY"
# MOTION_LAZY Do nothing.
MOTION_LAZY = "LAZY"
# MOTION_SCARED If there's another bot on the battleground, run towards the nearest port.
MOTION_SCARED = "SCARED"
# MOTION_NULL A non-motion, this motion type will always get passed onto the next in the priorities list.
MOTION_NULL = "NULL"

motion_priorities = [MOTION_BLOODTHIRSTY, MOTION_CURIOUS, MOTION_ASTRAY]

def main():
    move_dict = {
        "action": "",
        "direction": ""
    }
    # Go through each motion type. If that motion type can't be completed, move on to the next motion type.
    # Read in the Game object from game.pickle
    with open("game.pickle", "rb") as gamefile:
        game = pickle.load(gamefile)
    # Figure out which bot in the Game object represents this script
    this_bot = None
    for game_bot in game.bots:
        if game_bot.bot_icon == sys.argv[2]:
            this_bot = game_bot
            break

    # Figure out which battleground in the Game the bot is on
    this_battleground = None
    for bg in game.battlegrounds:
        if bg.port_icon == sys.argv[3]:
            this_battleground = bg
            break
    bot_x, bot_y = this_battleground.find_icon(this_bot.bot_icon)[0]

    # Go through the different motions, attempting each one in order:
    for motion in motion_priorities:
        print("\tMaking motion {}, bot is at ({}, {})".format(motion, bot_x, bot_y))
        if motion == MOTION_ASTRAY:
            # Just make a random move
            move_dict = {
                    "action": "walk",
                    "direction": random.choice(["l", "lu", "u", "ru", "r", "rd", "d", "ld"])
                }
            break
        elif motion == MOTION_BLOODTHIRSTY:
            trying_to_attack = False
            for bg_bot in this_battleground.bots:
                if bg_bot.bot_icon != this_bot.bot_icon:
                    # First find the location of the bot
                    loc = this_battleground.find_icon(bg_bot.bot_icon)
                    assert len(loc) == 1, bg_bot.bot_icon
                    loc = loc[0]
                    move_dict['direction'] = get_direction([bot_x, bot_y], loc)
                    if get_dist([bot_x, bot_y], loc) <= 1:
                        # Close enough to fight
                        move_dict['action'] = 'attack'
                    else:
                        # Move until close enough to fight
                        move_dict['action'] = 'walk'
                    trying_to_attack = True
                    break
            if trying_to_attack:
                break

        elif motion == MOTION_CURIOUS:
            if this_battleground.port_locations:
                # 1. Find the nearest port
                closest_dist = 999999999
                closest_loc = [None, None]
                for loc in this_battleground.port_locations:
                    if get_dist([bot_x, bot_y], loc) < closest_dist:
                        closest_loc = loc[:]
                        closest_dist = get_dist([bot_x, bot_y], loc)
                print("\tclosest port is at {}, {}".format(closest_loc[0], closest_loc[1]))
                # 2. Path towards it
                move_dict['action'] = 'walk'
                move_dict['direction'] = get_direction([bot_x, bot_y], closest_loc)
                break
        elif motion == MOTION_GENEROUS:
            GIVING_THRESHOLD = 3
            trying_to_give = False
            # 1. If you've got any coins, either move close enough or give them to another bot
            for bg_bot in this_battleground.bots:
                if bg_bot.bot_icon != this_bot.bot_icon:
                    # First find the location of the bot
                    loc = this_battleground.find_icon(bg_bot.bot_icon)
                    assert len(loc) == 1, bg_bot.bot_icon
                    loc = loc[0]
                    # Check if we've got any coins to give
                    if sum([coin.value for coin in this_bot.coins]) > 0:
                        move_dict['direction'] = get_direction([bot_x, bot_y], loc)
                        if get_dist([bot_x, bot_y], loc) <= GIVING_THRESHOLD:
                            move_dict['action'] = 'drop'
                            
                        else:
                            move_dict['action'] = 'walk'
                    trying_to_give = True
                    break
            if trying_to_give:
                # If we've found a bot to give to, then we've got a gameplan
                break
            # If not, then move on to the next priority movement

            
        elif motion == MOTION_GREEDY:
            # 1. Always move towards the nearest coin.
            # 2. If there are no coins, move on to the next priority motion
            coin_locations = [this_battleground.find_icon(coin_icon) for coin_icon in game.coin_icons]
            # Flatten the list from 2d to 1d:
            coin_locations = [coin for sublist in coin_locations for coin in sublist]
            if coin_locations:
                # # 1. Find the nearest coin
                closest_dist = 999999999
                closest_loc = [None, None]
                for loc in coin_locations:
                    if get_dist([bot_x, bot_y], loc) < closest_dist:
                        closest_loc = loc[:]
                        closest_dist = get_dist([bot_x, bot_y], loc)
                # 2. Path towards it
                move_dict['action'] = 'walk'
                move_dict['direction'] = get_direction([bot_x, bot_y], closest_loc)
                break
        elif motion == MOTION_LAZY:
            # 1. Do nothing
            move_dict['action'] = ''
            move_dict['direction'] = ''
            break
        elif motion == MOTION_SCARED:
            print("\t{} not implemented yet".format(motion))
            break
        elif motion == MOTION_NULL:
            pass

    with open("move.json", "w+") as movefile:
        json.dump(move_dict, movefile)

def get_dist(here, there):
   delta_x = abs(there[0] - here[0])
   delta_y = abs(there[1] - here[1])
   return max(delta_x, delta_y)

def get_direction(here, there):
   delta_x = min(1, max(-1, there[0] - here[0]))
   delta_y = min(1, max(-1, there[1] - here[1]))
   move_array = [
       ['lu', 'u', 'ru'],
       ['l', '', 'r'],
       ['ld', 'd', 'rd']
   ]
   return move_array[delta_y + 1][delta_x + 1]


if __name__ == '__main__':
    main()
