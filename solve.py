#!/usr/bin/env python3
# vim: set foldmethod=marker

import kanren as kn
from itertools import combinations
from vision import crop_to_puzzle, find_text_regions, extract_puzzle
from pprint import pprint
import cv2
import subprocess
import time


fp = open("/usr/share/dict/words", "r")
RAW_WORDS = set(map(lambda x: str.lower(str.strip(x)), fp.readlines()))
fp.close()


def ranked_solutions(puzzle, candidates):
    """
    Rank solutions by how many of the characters in a column of
    the puzzle are in the set of characters at that same position
    in the solution words.
    """
    puzzle = list(map(lambda x: list(map(str.lower, x)), puzzle))
    rs = dict()
    for c in combinations(candidates, len(max(puzzle, key=len))):
        score = 0
        for i, v in enumerate(puzzle):
            score += len(set(v) - set([x[i] for x in c]))
        rs[c] = score
    return [k for k, _ in sorted(rs.items(), key=lambda item: item[1])]


def logic_solve(puzzle):
    """First attempt to solve the puzzle using membero. Works but SLOW..."""
    words = set()
    for word in RAW_WORDS:
        words.add(tuple(word))
    vs = kn.vars(len(puzzle))
    gs = []
    for i, v in enumerate(vs):
        print(tuple(map(str.lower, puzzle[i])))
        gs.append(kn.membero(v, tuple(map(str.lower, puzzle[i]))))
    gs.append(kn.membero(vs, words))
    return kn.run(0, vs, *gs)


def solve(puzzle):
    """
    Starting from a large word list, find all the candidate words
    that match the requirements of the puzzle in terms of having
    the right character at the right position. A position in a word
    corresponds to a column in the puzzle.
    """
    words = set()
    puzzle = list(map(lambda x: list(map(str.lower, x)), puzzle))
    for word in RAW_WORDS:
        if len(word) == len(puzzle) and (
            all([word[i] in puzzle[i] for i in range(len(puzzle))])
        ):
            words.add(tuple(word))
    return ranked_solutions(puzzle, words)


def step(transitions, initial, next_):
    """
    Identify a single step along on a column, -n means to get
    from initial to next_ you need to move up n steps, +n means
    move down n steps.
    """
    i = transitions.index(initial)
    n = transitions.index(next_)
    steps = i - n
    return steps, n


def play(pz):
    """
    Find the moves up/down that are required to enter
    the words of the solution into the game.
    """
    puzzle = [[x[0] for x in i] for i in pz]
    solutions = solve(puzzle)  # find the possible solutions
    best = solutions.pop()  # extract the best one
    mid = [i[-2] for i in pz]
    res = []
    for word in best:
        prog = []
        for (i, c) in enumerate(word):
            trans = puzzle[i]
            steps, n = step(trans, mid[i][0], c.upper())
            mid[i] = pz[i][n]
            prog.append(steps)
        res.append(prog)
    return res


def send_commands(prog, mid):
    """
    Send the sequence of up/down movements needed to
    enter a word to a connected device running the game with
    adb
    """
    for p in prog:
        for k, c in enumerate(p):
            x1, y1 = mid[k]
            x2, y2 = x1, y1 + (100 * (-1 if c < 0 else 1))
            positions = map(str, [x1, y1, x2, y2])
            for _ in range(abs(c)):
                subprocess.run(["adb", "shell", "input", "swipe", *positions])
                time.sleep(0.5)
            time.sleep(0.5)
        time.sleep(1)
    return


def main():
    subprocess.run(["adb", "shell", "screencap", "/sdcard/ts.png"])
    subprocess.run(["adb", "pull", "/sdcard/ts.png", "/tmp/input.png"])
    im = cv2.imread("/tmp/input.png")
    resized = crop_to_puzzle(im)
    cols, gray = find_text_regions(resized)
    puzzle_grid = extract_puzzle(cols, gray)
    pprint(puzzle_grid)
    mid = [i[-2][1] for i in puzzle_grid]
    prog = play(puzzle_grid)
    send_commands(prog, mid)
    return


if __name__ == "__main__":
    main()
