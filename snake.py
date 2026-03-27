#!/usr/bin/env python3
"""Snake game — terminal version using curses."""

import curses
import random
import time

COLS = 40
ROWS = 20
TICK = 0.12  # seconds between frames


def place_food(snake_set):
    while True:
        pos = (random.randint(1, ROWS - 2), random.randint(1, COLS - 2))
        if pos not in snake_set:
            return pos


def draw_border(win):
    h, w = win.getmaxyx()
    win.border()


def game(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    # Color setup
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # snake
    curses.init_pair(2, curses.COLOR_RED, -1)     # food
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # score
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # border / text

    max_r, max_c = stdscr.getmaxyx()
    if max_r < ROWS + 2 or max_c < COLS + 2:
        stdscr.addstr(0, 0, f"Terminal too small! Need {COLS+2}x{ROWS+2}, have {max_c}x{max_r}.")
        stdscr.getch()
        return

    win = curses.newwin(ROWS, COLS, (max_r - ROWS) // 2, (max_c - COLS) // 2)
    win.keypad(True)
    win.nodelay(True)

    def show_overlay(title, sub):
        win.clear()
        win.border()
        cy, cx = ROWS // 2, COLS // 2
        win.addstr(cy - 1, cx - len(title) // 2, title, curses.color_pair(1) | curses.A_BOLD)
        win.addstr(cy + 1, cx - len(sub) // 2, sub, curses.color_pair(4))
        win.refresh()
        win.nodelay(False)
        while True:
            k = win.getch()
            if k in (10, 13, ord(" ")):  # Enter or Space
                break
            if k == ord("q"):
                return False
        win.nodelay(True)
        return True

    # Start screen
    if not show_overlay("  S N A K E  ", "Press ENTER to start  (q to quit)"):
        return

    while True:
        # ---- initialise round ----
        mid_r, mid_c = ROWS // 2, COLS // 2
        snake = [(mid_r, mid_c), (mid_r, mid_c - 1), (mid_r, mid_c - 2)]
        snake_set = set(snake)
        direction = (0, 1)   # moving right
        next_dir = direction
        food = place_food(snake_set)
        score = 0
        last_tick = time.monotonic()

        while True:
            now = time.monotonic()

            # --- input (non-blocking, collect all pending keys) ---
            k = win.getch()
            while k != -1:
                dr, dc = direction
                if k in (curses.KEY_UP, ord("w")) and dr != 1:
                    next_dir = (-1, 0)
                elif k in (curses.KEY_DOWN, ord("s")) and dr != -1:
                    next_dir = (1, 0)
                elif k in (curses.KEY_LEFT, ord("a")) and dc != 1:
                    next_dir = (0, -1)
                elif k in (curses.KEY_RIGHT, ord("d")) and dc != -1:
                    next_dir = (0, 1)
                elif k == ord("q"):
                    return
                k = win.getch()

            # --- update on tick ---
            if now - last_tick >= TICK:
                last_tick = now
                direction = next_dir
                hr, hc = snake[0]
                dr, dc = direction
                new_head = (hr + dr, hc + dc)

                # Collision
                if (
                    new_head in snake_set
                    or not (1 <= new_head[0] < ROWS - 1)
                    or not (1 <= new_head[1] < COLS - 1)
                ):
                    break  # game over

                snake.insert(0, new_head)
                snake_set.add(new_head)

                if new_head == food:
                    score += 10
                    food = place_food(snake_set)
                else:
                    removed = snake.pop()
                    snake_set.discard(removed)

                # --- draw ---
                win.erase()
                win.border()

                # Food
                fr, fc = food
                win.addch(fr, fc, "@", curses.color_pair(2) | curses.A_BOLD)

                # Snake
                for i, (sr, sc) in enumerate(snake):
                    ch = "O" if i == 0 else "o"
                    attr = curses.color_pair(1) | (curses.A_BOLD if i == 0 else 0)
                    win.addch(sr, sc, ch, attr)

                # Score
                score_str = f" Score: {score} "
                win.addstr(0, (COLS - len(score_str)) // 2, score_str,
                           curses.color_pair(3) | curses.A_BOLD)

                win.refresh()

            else:
                time.sleep(0.005)

        # Game over
        cont = show_overlay(
            f"  Game Over!  {score} pts  ",
            "ENTER to play again  |  q to quit",
        )
        if not cont:
            return


def main():
    curses.wrapper(game)


if __name__ == "__main__":
    main()
