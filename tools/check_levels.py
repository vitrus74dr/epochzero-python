"""Reachability check for platformer text levels (lesson 6.3 format).

    python tools/check_levels.py curriculum/week6/stubs/t6.3-platformer/levels/*.txt

A 'stand' cell is an empty cell with a wall directly below. From a stand you can
walk to adjacent stands at the same height, drop down anywhere within 4 columns,
or jump up at most UP rows within 3 columns (needs headroom). Items (C, F) are
reachable if within JUMP rows above a reachable stand in the same/adjacent column."""
import sys
from collections import deque
UP, REACH = 2, 3

def check(text):
    g = [l.rstrip() for l in text.strip("\n").split("\n")]
    R, C = len(g), len(g[0])
    solid = lambda c, r: r >= R or (0 <= c < C and g[r][c] == "#")
    stands = {(c, r) for r in range(R) for c in range(C) if g[r][c] != "#" and solid(c, r + 1)}
    start = next((c, r) for r in range(R) for c in range(C) if g[r][c] == "P")
    # player falls to the first stand below the start
    while start not in stands: start = (start[0], start[1] + 1)
    seen, q = {start}, deque([start])
    while q:
        c, r = q.popleft()
        for (c2, r2) in stands:
            if (c2, r2) in seen: continue
            dc, dr = abs(c2 - c), r - r2          # dr > 0: target higher
            ok = (dr == 0 and dc == 1) or (dr < 0 and dc <= 4) or (0 < dr <= UP and dc <= REACH and
                 all(not solid(c, rr) for rr in range(r2 - 1, r)))
            if ok: seen.add((c2, r2)); q.append((c2, r2))
    problems = []
    for r in range(R):
        for c in range(C):
            ch = g[r][c]
            if ch in "CF" and not any(abs(sc - c) <= 1 and 0 <= sr - r <= 2 for sc, sr in seen):
                problems.append(f"{ch} at col {c+1} row {r+1} unreachable")
            if ch == "E" and not solid(c, r + 1):
                problems.append(f"E at col {c+1} row {r+1} has no ground")
    return problems

if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        probs = check(open(p).read()); bad += bool(probs)
        print(p.split("/")[-1], "OK" if not probs else probs)
    sys.exit(bad)
