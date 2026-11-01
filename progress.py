import json
import os
from datetime import date, datetime, timedelta


P_DIR = 'data/progress.json'

# Flashcards use Leitner boxes 1-5 (0 = never reviewed).
# A correct answer moves a word up one box; the next review is this many days later.
# A wrong answer sends it back to box 1, due again today.
INTERVALS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 15}
MAX_BOX = 5


def new_word_state():
    return {'box': 0, 'due': None, 'reviews': 0, 'correct': 0}


class Progress:
    """Practice statistics per song and flashcard state per word, saved as JSON.

    {
        "last_song": "一生中最爱",
        "songs": {"一生中最爱": {"sessions": 3, "position": 5, "done": [0, 1, 2],
                                 "checked": 40, "wrong": 6, "last": "2026-10-24T12:00:00",
                                 "misses": {"讲": 2, "会": 1}}},
        "words": {"讲": {"box": 2, "due": "2026-10-26", "reviews": 3, "correct": 2}}
    }
    """

    def __init__(self, path=P_DIR):
        self.path = path

        try:
            with open(path) as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

        self.data.setdefault('last_song', None)
        self.data.setdefault('songs', {})
        self.data.setdefault('words', {})

    def save(self):
        tmp = self.path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        os.replace(tmp, self.path)

    # --------------------------------------------------------------
    #  Songs
    # --------------------------------------------------------------

    def _song(self, name):
        return self.data['songs'].setdefault(
            name, {'sessions': 0, 'position': 0, 'done': [], 'checked': 0, 'wrong': 0, 'last': None,
                   'misses': {}})

    def start_session(self, name):
        s = self._song(name)
        s['sessions'] += 1
        s['last'] = datetime.now().isoformat(timespec='seconds')
        self.data['last_song'] = name
        self.save()

    def set_position(self, name, line):
        self._song(name)['position'] = line
        self.save()

    def record_check(self, name, line, checked, wrong, missed=()):
        """missed: the characters got wrong on this line, one entry per wrong syllable."""
        s = self._song(name)
        if line not in s['done']:
            s['done'].append(line)
        s['checked'] += checked
        s['wrong'] += wrong
        misses = s.setdefault('misses', {})
        for word in missed:
            misses[word] = misses.get(word, 0) + 1
        self.save()

    def remove_song(self, name):
        self.data['songs'].pop(name, None)
        if self.data['last_song'] == name:
            self.data['last_song'] = None
        self.save()

    def song_misses(self, name):
        """{word: times got wrong} while practising this song."""
        return self.data['songs'].get(name, {}).get('misses', {})

    def songs_with_misses(self):
        return [name for name, s in self.data['songs'].items() if s.get('misses')]

    def misses_by_word(self):
        """{word: {song: times got wrong}}, songs with the most mistakes first."""
        by_word = {}
        for name, s in self.data['songs'].items():
            for word, n in s.get('misses', {}).items():
                by_word.setdefault(word, {})[name] = n
        return {w: dict(sorted(songs.items(), key=lambda x: -x[1])) for w, songs in by_word.items()}

    def song_summary(self, name, total):
        s = self.data['songs'].get(name)
        if s is None:
            return {'sessions': 0, 'position': 0, 'done': 0, 'completion': 0.0,
                    'error_rate': None, 'last': None}

        done = len({i for i in s['done'] if i < total})
        return {
            'sessions': s['sessions'],
            'position': min(s['position'], max(total - 1, 0)),
            'done': done,
            'completion': done / total if total else 0.0,
            'error_rate': s['wrong'] / s['checked'] if s['checked'] else None,
            'last': s['last'],
        }

    # --------------------------------------------------------------
    #  Words (flashcards)
    # --------------------------------------------------------------

    def word_state(self, word):
        return self.data['words'].get(word, new_word_state())

    def is_due(self, word, today=None):
        today = today or date.today()
        state = self.word_state(word)
        return state['box'] == 0 or state['due'] is None or state['due'] <= today.isoformat()

    def review(self, word, correct, today=None):
        today = today or date.today()
        state = self.data['words'].setdefault(word, new_word_state())
        state['reviews'] += 1

        if correct:
            state['correct'] += 1
            state['box'] = min(state['box'] + 1, MAX_BOX)
            state['due'] = (today + timedelta(days=INTERVALS[state['box']])).isoformat()
        else:
            state['box'] = 1
            state['due'] = today.isoformat()

        self.save()

    def demote(self, word, today=None):
        """Got the word wrong again while practising a song: review it again today."""
        state = self.data['words'].get(word)
        if state is None:
            return
        due = (today or date.today()).isoformat()
        if state['box'] > 1 or (state['box'] == 1 and (state['due'] or '') > due):
            state['box'] = 1
            state['due'] = due
            self.save()

    def order_words(self, new_w):
        """Highlighted words first, then words already in review (least known first),
           then never-reviewed words with the most mistakes.
        """
        def key(w):
            box = self.word_state(w)['box']
            return (-new_w[w][-1], box == 0, box, -new_w[w][1], self.word_state(w)['due'] or '')

        return sorted(new_w, key=key)

    def due_words(self, new_w, today=None):
        return [w for w in self.order_words(new_w) if self.is_due(w, today)]

    def next_due(self, new_w):
        dates = [self.word_state(w)['due'] for w in new_w if self.word_state(w)['due']]
        return min(dates) if dates else None

    def remove_word(self, word):
        self.data['words'].pop(word, None)
        for s in self.data['songs'].values():
            s.get('misses', {}).pop(word, None)
        self.save()

    def clear_words(self):
        self.data['words'] = {}
        for s in self.data['songs'].values():
            s['misses'] = {}
        self.save()
