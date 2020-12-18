#!/usr/bin/python3
"""
TODO Add colours based on what the icon is
TODO Add keycodes, so pressing 'A' will give better details on the bot with icon A
"""
import os
from curses import wrapper
import json
import pickle
import sys
import time
import itertools
# add the server directory to the PATH so we can import the utilities file
sys.path.append("/home/k/knxboy001/public_html/genghis_server")
import util

PADDING = 2
STATE_ALL = "STATE_ALL"
STATE_BOT = "STATE_BOT"
STATE_BG = "STATE_BG"
def main(stdscr):
    icon = ''
    state = STATE_ALL
    stdscr.nodelay(1)
    games = sorted(os.listdir("games"))
    files = os.listdir(os.path.join("games", games[-1]))
    log_files = sorted([os.path.join("games", games[-1], f) for f in files if f[0].isdigit() and '.log' in f])
    key = ''
    while key != ord('q'):
        key = stdscr.getch()

        # Read in the Game object from game.pickle
        with open(os.path.join("games", games[-1], "game.pickle"),"rb") as gamefile:
            game = pickle.load(gamefile)
        
        bgs = []
        max_rows, max_cols = 0, 0
        for log_file in log_files:
            with open(log_file, 'r') as file:
                parsed = [line.strip() for line in file.readlines()]
                if len(parsed) > max_cols:
                    max_cols = len(parsed)
            bgs.append([''.join(list(i)) for i in parsed])
            if len(bgs[-1]) > max_rows:
                max_rows = len(bgs[-1])


        # Clear screen
        stdscr.clear()
        # Add some padding to the sides of the battlegrounds
        max_cols += PADDING * 2
        max_rows += PADDING * 2

        rows, cols = stdscr.getmaxyx()
        if cols < max_cols:
            stdscr.addstr(0, 0, "Not enough columns, please resize your terminal")
            return
        if rows < max_rows:
            stdscr.addstr(0, 0, "Not enough rows, please resize your terminal")
            return
            
        bg_cols = cols // max_cols
        stdscr.addstr(0, 0, chr(key) if key in range(0x110000) else str(key))
        # Figure out which state the monitor should be in
        if key in [ord(str(c)) for c in range(10)]:
            state = STATE_BG
            icon = chr(key)
        elif key in [c for c in range(ord('A'), ord('Z')+1)]:
            state = STATE_BOT
            icon = chr(key)
        elif key == ord('~'):
            state = STATE_ALL

        
        if state == STATE_BG:
            bg = None
            for game_bg in game.battlegrounds:
                if game_bg.port_icon == icon:
                    bg = game_bg
                    break
            # Just show the one bg and it's json interpretation
            bg_lines = [''.join(row) for row in zip(*bg.bg_map)]
            json_dict = {}
            for dict_key, value in bg.to_dict().items():
                if type(value) is list:
                    json_dict[dict_key] = repr(value)
                else:
                    json_dict[dict_key] = value

            js_lines = json.dumps(json_dict, indent=2).encode('utf-8').decode('unicode_escape')
            js_lines = js_lines.split("\n")
            fmted_lines = []
            for line in js_lines:
                # Go through the current dict entry and make sure it doesn't overflow
                # on the screen by chopping it into smaller, \\n deliminated pieces
                overflow = cols-max_cols - PADDING 
                line_list = []
                while True: 
                    fmted_lines.append(line[:overflow])
                    line = line[overflow:]
                    if len(line) == 0:
                        break
            js_lines = fmted_lines[:rows - 3]
            i = 1
            fmt_bg = "{:^" + str(max_cols) + "}"
            fmt_js = "{:<" + str(cols - max_cols) + "}"
            fmt_title = "{:^" + str(cols) + "}"

            # add the title
            stdscr.addstr(i, 0, fmt_title.format("Battleground: {}".format(bg.port_icon))) 
            i += 1
            for bg_row, js_row in itertools.zip_longest(bg_lines, js_lines, fillvalue=''):
                print_str = fmt_bg.format(bg_row) + fmt_js.format(js_row)
                stdscr.addstr(i, 0, print_str)
                i += 1
            i += 1
            stdscr.refresh()


        elif state == STATE_BOT:
            bot = None
            for game_bot in game.bots:
                if game_bot.bot_icon == icon:
                    bot = game_bot
                    break
            # Just show the one bot and it's json interpretation
            # Figure out which battleground the bot is on
            bg_lines = []
            for game_bg in game.battlegrounds:
                """
                Traceback (most recent call last):
                    File "monitor.py", line 188, in <module>
                        wrapper(main)
                    File "/usr/lib/python3.6/curses/__init__.py", line 94, in wrapper
                        return func(stdscr, *args, **kwds)
                    File "monitor.py", line 131, in main
                        if bot.bot_icon in [bg_bot.bot_icon for bg_bot in game_bg.bots]:
                    AttributeError: 'NoneType' object has no attribute 'bot_icon'
                """
                if bot.bot_icon in [bg_bot.bot_icon for bg_bot in game_bg.bots]:
                    bg_lines = [''.join(row) for row in zip(*game_bg.bg_map)]
                    break
            json_dict = {}
            for dict_key, value in bot.to_dict().items():
                if type(value) is list:
                    json_dict[dict_key] = repr(value)
                else:
                    json_dict[dict_key] = value

            js_lines = json.dumps(json_dict, indent=2).encode('utf-8').decode('unicode_escape')
            js_lines = js_lines.split("\n")
            fmted_lines = []
            for line in js_lines:
                # Go through the current dict entry and make sure it doesn't overflow
                # on the screen by chopping it into smaller, \\n deliminated pieces
                overflow = cols-max_cols - PADDING 
                line_list = []
                while True: 
                    fmted_lines.append(line[:overflow])
                    line = line[overflow:]
                    if len(line) == 0:
                        break
            js_lines = fmted_lines[:rows - 3]
            i = 1
            fmt_bg = "{:^" + str(max_cols) + "}"
            fmt_js = "{:<" + str(cols - max_cols) + "}"
            fmt_title = "{:^" + str(cols) + "}"

            # add the title
            stdscr.addstr(i, 0, fmt_title.format("Bot: {}".format(bot.bot_icon))) 
            i += 1
            for bg_row, js_row in itertools.zip_longest(bg_lines, js_lines, fillvalue=''):
                print_str = fmt_bg.format(bg_row) + fmt_js.format(js_row)
                stdscr.addstr(i, 0, print_str)
                i += 1
            i += 1
            stdscr.refresh()
            
        elif state == STATE_ALL:
            i = 1
            fmt_str = "{:^" + str(max_cols) + "}"
            for j in range(0, len(bgs), bg_cols):
                logs = [log_files[j + idx] for idx in range(bg_cols) if len(log_files) > j + idx]
                title_str = ''.join([fmt_str.format(log_file.split('/')[-1]) for log_file in logs])
                stdscr.addstr(i, 0, title_str)
                
                i += 1
                items = [bgs[j + idx] for idx in range(bg_cols) if len(bgs) > j + idx]
                for rows in zip(*items):
                    print_str = ''.join([fmt_str.format(row) for row in rows]) 
                    stdscr.addstr(i, 0, print_str)
                    i += 1
                i += 1
                stdscr.refresh()
        time.sleep(0.5)
wrapper(main)
