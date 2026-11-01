"""Attribute the word book's past mistakes to songs (one-off, run from the project folder).

Per-song misses are recorded from the "Review in Word Book" feature onwards. For earlier practice,
this reconstructs them from git snapshots of the word book and progress.json:
in each window between two snapshots, a mistake on a character is attributed to the song that was
practised in that window whose checked lines contain the character. Words with no candidate song,
or more than one, are left without a song (they still show in the word book under "All songs").

Usage:  .venv/bin/python tools/backfill_song_misses.py [-o OUTPUT]
Writes data/progress.json in place unless -o is given; refuses while the app is running.
"""
import argparse
import json
import os
import subprocess
import sys

SNAPSHOTS = [        # (word book commit, progress.json commit or None), oldest first; None = live file
    ('3a2f287', None),
    ('21258d2', '21258d2'),
    ('f3588ee', 'f3588ee'),
    (None, None),
]
WORDS = 'data/new words.json'
PROGRESS = 'data/progress.json'


def snapshot(commit, path):
    if commit is None:
        return json.load(open(path))
    return json.loads(subprocess.check_output(['git', 'show', f'{commit}:{path}'], text=True))

def lyric_lines(song):
    raw = [x for x in open(f'data/songs/{song}.txt').read().splitlines() if x and 'https' not in x]
    return raw[::2]

def added_counts(before, after):
    return {w: after[w][1] - before.get(w, [0, 0])[1] for w in after if after[w][1] > before.get(w, [0, 0])[1]}

def practised(before, after):
    """{song: set of characters in its checked lines} for songs practised between two progress snapshots."""
    songs = {}
    for name, s in after.get('songs', {}).items():
        if s['checked'] > before.get('songs', {}).get(name, {}).get('checked', 0) and os.path.exists(f'data/songs/{name}.txt'):
            lines = lyric_lines(name)
            songs[name] = set(''.join(lines[i] for i in s['done'] if i < len(lines)).replace(' ', ''))
    return songs

def compute():
    misses, unattributed = {}, {}
    words = [snapshot(c, WORDS) for c, _ in SNAPSHOTS]
    progress = [snapshot(c, PROGRESS) if c or w is None else {} for w, c in SNAPSHOTS]

    for n in range(1, len(SNAPSHOTS)):
        candidates = practised(progress[n - 1], progress[n])
        for word, count in added_counts(words[n - 1], words[n]).items():
            found = [name for name, chars in candidates.items() if word in chars]
            if len(found) == 1:
                misses.setdefault(found[0], {})[word] = misses.get(found[0], {}).get(word, 0) + count
            else:
                unattributed[word] = unattributed.get(word, 0) + count
    return misses, unattributed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default=PROGRESS)
    args = parser.parse_args()

    if args.output == PROGRESS and subprocess.run(['pgrep', '-f', 'app.py'], capture_output=True).returncode == 0:
        sys.exit('The app is running and would overwrite the result: quit it first.')

    misses, unattributed = compute()
    live = json.load(open(PROGRESS))
    for name, s in live['songs'].items():
        if s.get('misses'):
            sys.exit(f'{name} already has per-song misses: nothing to do.')
        s['misses'] = misses.get(name, {})
        if s['misses']:
            print(f'{name}: {len(s["misses"])} words, {sum(s["misses"].values())} misses (recorded wrong: {s["wrong"]})')
    if unattributed:
        print(f'not attributed: {sum(unattributed.values())} misses on {len(unattributed)} words')

    tmp = args.output + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(live, f, indent=4, ensure_ascii=False)
    os.replace(tmp, args.output)
    print(f'wrote {args.output}')

if __name__ == '__main__':
    main()
