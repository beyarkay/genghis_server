"""
TODO Add colours based on what the icon is

"""
import os
from curses import wrapper
import sys
import time
PADDING = 2

def main(stdscr):
    stdscr.nodelay(1)
    games = sorted(os.listdir("games"))
    files = os.listdir(os.path.join("games", games[-1]))
    log_files = [os.path.join("games", games[-1], f) for f in files if f[0].isdigit()]
    key = ''
    while key != ord('q'):
        key = stdscr.getch()
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
        bg_cols = cols // max_cols
        i = 0
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
