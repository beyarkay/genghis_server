from curses import wrapper
import sys
import time


def main(stdscr):
    assert len(sys.argv) > 1, "File input path required"
    while True:
        with open(sys.argv[1], 'r') as file:
            parsed = [line.strip() for line in file.readlines()]
        bg = [list(i) for i in zip(*parsed)]

        # Clear screen
        stdscr.clear()
        for i, row in enumerate(bg):
            stdscr.addstr(i, 0, ''.join(row))
        stdscr.refresh()
        time.sleep(1)

wrapper(main)
