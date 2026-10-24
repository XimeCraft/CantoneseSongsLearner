import glob
import os
from datetime import date, datetime
from tkinter import *
from tkinter import messagebox, ttk

import pandas as pd
from pinyin import get

import learnCantonese as lc
import theme
from progress import Progress
from theme import C, button, font, label
from utils import center_window, menubar


SONG_DIR = 'data/songs'
W_DIR = 'data/new words.json'
INFO_DIR = 'data/songs info.csv'
FLASHCARD_SESSION = 20


# ------------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------------

def song_path(name):
    return os.path.join(SONG_DIR, f'{name}.txt')

def get_all_songs():
    all_f = glob.glob(os.path.join(SONG_DIR, '*.txt'))
    return sorted([os.path.basename(x)[:-4] for x in all_f], key=get)

def load_song(name):
    """Return Chinese lines and jyutping lines (with tones), paired up."""
    clean_l = lc.read_lyrics(song_path(name))
    cn_l, en_l = clean_l[::2], clean_l[1::2]
    n = min(len(cn_l), len(en_l))
    return cn_l[:n], en_l[:n]

def tone_index():
    """Map each character to the jyutping (with tones) it has in the downloaded lyrics."""
    index = {}
    for name in get_all_songs():
        for cn, en in zip(*load_song(name)):
            chars, syllables = list(cn.replace(' ', '')), en.split()
            if len(chars) == len(syllables):
                for char, syllable in zip(chars, syllables):
                    index.setdefault(char, set()).add(syllable)
    return index

def with_tones(word, pinyin, index):
    """The word book stores jyutping without tones; look the tones up in the lyrics."""
    toned = sorted(x for x in index.get(word, ()) if lc.split_words_tones([x])[0] == pinyin)
    return ' / '.join(toned) or pinyin

def is_correct(word, answer):
    return word == answer or ('/' in answer and word in answer.split('/'))

def ago(iso):
    if not iso:
        return '—'
    days = (date.today() - datetime.fromisoformat(iso).date()).days
    return {0: 'today', 1: 'yesterday'}.get(days, f'{days} days ago')

def until(iso):
    if not iso:
        return 'new'
    days = (date.fromisoformat(iso) - date.today()).days
    if days <= 0:
        return 'today'
    return 'tomorrow' if days == 1 else f'in {days} days'

def level_dots(box):
    return '●' * box + '○' * (5 - box)


class Page(Frame):
    """A screen shown inside the main window. Global key bindings are removed when it closes."""

    def __init__(self, app):
        super().__init__(app, bg=C['bg'])
        self.app = app
        self._global_bindings = []

    def bind_global(self, sequence, func):
        self.app.bind_all(sequence, func)
        self._global_bindings.append(sequence)

    def destroy(self):
        for sequence in self._global_bindings:
            self.app.unbind_all(sequence)
        super().destroy()


def header(page, title, back):
    bar = Frame(page)
    bar.pack(side=TOP, fill=X, padx=16, pady=(14, 6))
    button(bar, 'Back', back, width=90).pack(side=LEFT)
    label(bar, title, size=18, weight='bold').pack(side=LEFT, padx=14)
    return bar


class SortableTree(Frame):
    """Treeview with a scrollbar; clicking a column header sorts by it."""

    def __init__(self, parent, columns, sort_keys, sort_state):
        super().__init__(parent)
        self.columns = columns
        self.sort_keys = sort_keys
        self.sort_state = sort_state       # dict {'col': ..., 'reverse': ...}, kept by the caller
        self.rows = []

        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns], show='headings', selectmode='browse')
        for col, title, width, anchor in columns:
            self.tree.heading(col, text=title, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=width, anchor=anchor, stretch=(anchor == W))

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.pack(side=RIGHT, fill=Y)

    def set_rows(self, rows):
        """rows: list of (iid, values dict, tags)"""
        self.rows = rows
        self.refresh()

    def sort_by(self, col):
        if col not in self.sort_keys:
            return
        if self.sort_state['col'] == col:
            self.sort_state['reverse'] = not self.sort_state['reverse']
        else:
            self.sort_state.update(col=col, reverse=False)
        self.refresh()

    def refresh(self, select=None):
        col, reverse = self.sort_state['col'], self.sort_state['reverse']
        rows = sorted(self.rows, key=lambda r: self.sort_keys[col](r[1]), reverse=reverse)

        for c, title, _, _ in self.columns:
            arrow = (' ▼' if reverse else ' ▲') if c == col else ''
            self.tree.heading(c, text=title + arrow)

        self.tree.delete(*self.tree.get_children())
        for n, (iid, values, tags) in enumerate(rows):
            shown = [n + 1 if c == 'no' else values[c] for c, *_ in self.columns]
            self.tree.insert('', END, iid=iid, values=shown, tags=tags)

        if select and self.tree.exists(select):
            self.tree.selection_set(select)
            self.tree.see(select)

    def selected(self):
        selection = self.tree.selection()
        return selection[0] if selection else None


# ------------------------------------------------------------------
#  Main Page
#  -- Continue last song, overview numbers, entry to every page
# ------------------------------------------------------------------

class HomePage(Page):

    def __init__(self, app):
        super().__init__(app)

        songs = get_all_songs()
        new_w = lc.read_new_words(W_DIR)
        due = len(app.progress.due_words(new_w))

        center = Frame(self)
        center.place(relx=0.5, rely=0.45, anchor=CENTER)

        label(center, 'Learning Cantonese', size=30, weight='bold').pack()
        label(center, f'{len(songs)} songs  ·  {len(new_w)} words in word book  ·  {due} due for review',
              size=14, color='muted').pack(pady=(6, 28))

        last = app.progress.data['last_song']
        if last in songs:
            total = len(load_song(last)[0])
            s = app.progress.song_summary(last, total)
            button(center, f'Continue  {last}   ·   line {s["position"] + 1} / {total}',
                   lambda: app.show(PracticePage, song=last, start=s['position']),
                   width=480, accent=True).pack(pady=(0, 12))

        row = Frame(center)
        row.pack()
        button(row, 'Select Songs', lambda: app.show(SongsPage), width=150).pack(side=LEFT, padx=8)
        button(row, 'Word Book', lambda: app.show(WordsPage), width=150).pack(side=LEFT, padx=8)
        button(row, f'Flashcards ({due})', lambda: app.show(FlashcardPage), width=150).pack(side=LEFT, padx=8)


# ------------------------------------------------------------------
#  Select Song Page
#  -- Table of all songs with practice statistics, sortable by column
#  -- Search local songs, search songs info.csv and download, delete
# ------------------------------------------------------------------

class SongsPage(Page):

    COLUMNS = [
        ('no', '#', 50, CENTER),
        ('song', 'Song', 220, W),
        ('sessions', 'Practiced', 95, CENTER),
        ('completion', 'Completed', 105, CENTER),
        ('error', 'Error rate', 100, CENTER),
        ('last', 'Last practiced', 130, CENTER),
    ]

    SORT_KEYS = {
        'song': lambda v: get(v['song']),
        'sessions': lambda v: v['_sessions'],
        'completion': lambda v: v['_completion'],
        'error': lambda v: -1 if v['_error'] is None else v['_error'],
        'last': lambda v: v['_last'] or '',
    }

    def __init__(self, app, select=None):
        super().__init__(app)

        bar = header(self, 'Select Songs', lambda: app.show(HomePage))
        button(bar, 'Search Online', self.search_online, width=130).pack(side=RIGHT)
        self.search = StringVar()
        self.search.trace_add('write', lambda *_: self.load_rows())
        search_box = Entry(bar, textvariable=self.search, width=22)
        search_box.pack(side=RIGHT, padx=10, ipady=4)
        label(bar, 'Search', size=13, color='muted').pack(side=RIGHT)

        self.table = SortableTree(self, self.COLUMNS, self.SORT_KEYS, app.song_sort)
        self.table.pack(fill=BOTH, expand=1, padx=16, pady=6)
        self.table.tree.bind('<Double-1>', lambda e: self.play())
        self.table.tree.bind('<Return>', lambda e: self.play())

        label(self, 'Click a column header to sort  ·  double-click a song to practise',
              size=12, color='muted').pack()

        buttonframe = Frame(self)
        buttonframe.pack(pady=(6, 14))
        button(buttonframe, 'Play Cantonese', self.play, accent=True).pack(side=LEFT, padx=8)
        button(buttonframe, 'Show Lyrics', self.show_lyrics).pack(side=LEFT, padx=8)
        button(buttonframe, 'Delete Song', self.delete_song).pack(side=LEFT, padx=8)

        self.load_rows(select)
        search_box.focus_set()

    def load_rows(self, select=None):
        query = self.search.get().strip().lower()
        rows = []

        for name in get_all_songs():
            if query and query not in name.lower():
                continue

            total = len(load_song(name)[0])
            s = self.app.progress.song_summary(name, total)
            values = {
                'song': name,
                'sessions': s['sessions'],
                'completion': f'{s["done"]}/{total}  {s["completion"]:.0%}',
                'error': '—' if s['error_rate'] is None else f'{s["error_rate"]:.0%}',
                'last': ago(s['last']),
                '_sessions': s['sessions'], '_completion': s['completion'],
                '_error': s['error_rate'], '_last': s['last'],
            }
            rows.append((name, values, ()))

        self.table.rows = rows
        self.table.refresh(select)

    def selected_song(self):
        name = self.table.selected()
        if name is None:
            messagebox.showinfo('Select a song', 'Please select a song first.', parent=self)
        return name

    def play(self):
        name = self.selected_song()
        if name:
            self.app.show(PracticePage, song=name)

    def show_lyrics(self):
        name = self.selected_song()
        if name:
            self.app.show(LyricsPage, song=name)

    def delete_song(self):
        name = self.selected_song()
        if name and messagebox.askyesno('Delete song', f'Delete “{name}” and its practice statistics?',
                                        icon='warning', parent=self):
            os.remove(song_path(name))
            self.app.progress.remove_song(name)
            self.load_rows()

    def search_online(self):
        query = self.search.get().strip()
        if not query:
            messagebox.showinfo('Search Online', 'Type a song name in the search box first.', parent=self)
            return
        DownloadDialog(self, query, on_done=lambda name: (self.search.set(''), self.load_rows(select=name)))


class DownloadDialog(Toplevel):
    """Show songs info.csv matches for a song name and download the chosen one."""

    def __init__(self, page, query, on_done):
        super().__init__(page.app, bg=C['bg'])
        self.title('Search Online')
        self.transient(page.app)
        self.resizable(False, False)
        self.on_done = on_done

        song_df = pd.read_csv(INFO_DIR).drop_duplicates(subset='song id').drop_duplicates(subset=['singer', 'song'])
        self.results = song_df[song_df['song'] == query][['song id', 'singer', 'song']].values.tolist()

        label(self, f'Results for “{query}”', size=16, weight='bold').pack(anchor=W, padx=16, pady=(14, 6))

        if not self.results:
            label(self, 'No song with this exact name in songs info.csv.', color='muted').pack(padx=16, pady=10)
            button(self, 'Close', self.destroy, width=100).pack(pady=(4, 14))
            return

        self.lb = Listbox(self, height=min(len(self.results), 8), width=40, activestyle='none')
        for song_id, singer, song in self.results:
            self.lb.insert(END, f'{song}  —  {singer}')
        self.lb.selection_set(0)
        self.lb.pack(padx=16, pady=4)
        self.lb.bind('<Double-1>', lambda e: self.download())

        self.status = label(self, '', size=13, color='muted')
        self.status.pack(pady=4)

        buttonframe = Frame(self)
        buttonframe.pack(pady=(0, 14))
        button(buttonframe, 'Download Lyric', self.download, width=140, accent=True).pack(side=LEFT, padx=6)
        button(buttonframe, 'Cancel', self.destroy, width=100).pack(side=LEFT, padx=6)

        self.grab_set()

    def download(self):
        if self.lb.curselection() == ():
            return

        song_id, singer, song = self.results[self.lb.curselection()[0]]
        if os.path.exists(song_path(song)) and not messagebox.askyesno(
                'Song exists', f'“{song}” is already downloaded. Download it again?', parent=self):
            return

        self.status.config(text='Downloading…', fg=C['muted'])
        self.update_idletasks()

        try:
            lc.download_lyric((song_id, singer, song))
        except Exception as e:
            self.status.config(text='Download failed', fg=C['bad'])
            messagebox.showerror('Download failed', f'Could not download “{song}”:\n{e}', parent=self)
            return

        messagebox.showinfo('Downloaded', f'“{song}” by {singer} is ready to practise.', parent=self)
        self.destroy()
        self.on_done(song)


# ------------------------------------------------------------------
#  Lyrics Page
#  -- Jyutping (with tones) above each character
#  -- Characters in the word book are highlighted
# ------------------------------------------------------------------

class ScrollFrame(Frame):

    def __init__(self, page):
        super().__init__(page)
        self.canvas = Canvas(self, bg=C['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.inner = Frame(self.canvas, bg=C['surface'])
        window = self.canvas.create_window(0, 0, window=self.inner, anchor=NW)

        self.inner.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(ALL)))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(window, width=e.width))
        page.bind_global('<MouseWheel>', lambda e: self.canvas.yview_scroll(-e.delta, UNITS))

        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.pack(side=RIGHT, fill=Y)


class LyricsPage(Page):

    MAX_COLUMNS = 14

    def __init__(self, app, song):
        super().__init__(app)
        self.song = song

        bar = header(self, song, lambda: app.show(SongsPage, select=song))
        button(bar, 'Play Cantonese', lambda: app.show(PracticePage, song=song), width=140, accent=True).pack(side=RIGHT)
        self.tones = BooleanVar(value=True)
        ttk.Checkbutton(bar, text='Show tones', variable=self.tones, command=self.update_tones).pack(side=RIGHT, padx=14)

        label(self, 'Green characters = words in your word book (ones you got wrong before)', size=12, color='muted').pack(anchor=W, padx=16)

        scroll = ScrollFrame(self)
        scroll.pack(fill=BOTH, expand=1, padx=16, pady=(4, 14))

        new_w = lc.read_new_words(W_DIR)
        self.pinyin_labels = []
        cn_l, en_l = load_song(song)

        for cn, en in zip(cn_l, en_l):
            line = Frame(scroll.inner, bg=C['surface'])
            line.pack(anchor=W, padx=20, pady=8)

            chars, syllables = list(cn.replace(' ', '')), en.split()

            # Characters and syllables don't line up: show the two lines as they are
            if len(chars) != len(syllables):
                self.add_pinyin(line, en).pack(anchor=W)
                Label(line, text=cn, bg=C['surface'], font=font(20)).pack(anchor=W)
                continue

            for j, (char, syllable) in enumerate(zip(chars, syllables)):
                cell = Frame(line, bg=C['surface'])
                cell.grid(row=j // self.MAX_COLUMNS, column=j % self.MAX_COLUMNS, padx=3, pady=2)
                self.add_pinyin(cell, syllable).pack()
                color = C['answer'] if char in new_w else C['fg']
                Label(cell, text=char, bg=C['surface'], fg=color, font=font(22)).pack()

    def add_pinyin(self, parent, text):
        l = Label(parent, text=text, bg=C['surface'], fg=C['muted'], font=font(12))
        self.pinyin_labels.append((l, text))
        return l

    def update_tones(self):
        for l, text in self.pinyin_labels:
            l.config(text=text if self.tones.get() else lc.split_words_tones([text])[0])


# ------------------------------------------------------------------
#  Game Page
#  -- A label to display a line of Cantonese lyric
#  -- An Entry to input Cantonese, Enter checks and Enter again goes on
#  -- Wrong syllables show the answer in green and go to the word book
# ------------------------------------------------------------------

class PracticePage(Page):

    def __init__(self, app, song, start=0):
        super().__init__(app)
        self.song = song
        self.cn_l, en_l = load_song(song)
        self.en_l = lc.split_words_tones(en_l)
        self.total = len(self.cn_l)
        self.N = max(0, min(start, self.total - 1))
        self.checked_input = None
        self.session_words = set()

        bar = header(self, song, lambda: app.show(SongsPage, select=song))
        if self.total == 0:
            label(self, 'This song has no lyrics.', color='muted').pack(pady=40)
            return

        app.progress.start_session(song)

        self.position = label(bar, '', size=14, color='muted')
        self.position.pack(side=RIGHT)

        self.bar = ttk.Progressbar(self, maximum=self.total)
        self.bar.pack(fill=X, padx=16, pady=(2, 4))
        self.stats = label(self, '', size=12, color='muted')
        self.stats.pack(anchor=W, padx=16)

        frame = Frame(self)
        frame.pack(fill=X, padx=16, pady=6)

        self.display_c_l = StringVar()
        Label(frame, textvariable=self.display_c_l, bg=C['surface2'], font=font(22), height=2).pack(fill=X, pady=5)

        self.e = Entry(frame, font=font(16))
        self.e.pack(fill=X, pady=5, ipady=6)
        self.e.bind('<Return>', lambda e: self.on_return())
        self.e.bind('<Left>', lambda e: self.on_arrow(-1))
        self.e.bind('<Right>', lambda e: self.on_arrow(1))

        self.t = Text(frame, width=1, height=2, font=font(16), wrap=WORD)
        self.t.tag_config('warning', foreground=C['answer'])
        self.t.pack(fill=X, pady=5)

        self.result = label(frame, '', size=14)
        self.result.pack(anchor=W)

        buttonframe = Frame(self)
        buttonframe.pack(pady=6)
        button(buttonframe, '←', lambda: self.move(-1), width=90).pack(side=LEFT, padx=8)
        button(buttonframe, 'Check', self.check_lyrics, width=180, accent=True).pack(side=LEFT, padx=8)
        button(buttonframe, '→', lambda: self.move(1), width=90).pack(side=LEFT, padx=8)

        label(self, 'Words to review from this session', size=13, color='muted').pack(anchor=W, padx=16, pady=(8, 0))
        self.t2 = Text(self, width=1, height=4, font=font(14), wrap=WORD)
        self.t2.tag_config('warning', foreground=C['answer'])
        self.t2.pack(fill=BOTH, expand=1, padx=16, pady=(4, 6))

        label(self, 'Enter: check, Enter again: next line  ·  ← →: change line (empty input)',
              size=12, color='muted').pack(pady=(0, 12))

        self.display_new_lyrics()

    def update_stats(self):
        s = self.app.progress.song_summary(self.song, self.total)
        error = '—' if s['error_rate'] is None else f'{s["error_rate"]:.0%}'
        self.stats.config(text=f'Completed {s["done"]}/{self.total} lines ({s["completion"]:.0%})  ·  '
                               f'error rate {error}  ·  practised {s["sessions"]} time{"s" if s["sessions"] != 1 else ""}')

    def display_new_lyrics(self):
        self.display_c_l.set(self.cn_l[self.N])
        self.position.config(text=f'Line {self.N + 1} / {self.total}')
        self.bar.config(value=self.N + 1)
        self.update_stats()

        self.t.delete('1.0', END)
        self.e.delete(0, END)
        self.result.config(text='')
        self.checked_input = None
        self.e.focus_set()

    def move(self, step):
        if 0 <= self.N + step < self.total:
            self.N += step
            self.app.progress.set_position(self.song, self.N)
            self.display_new_lyrics()

    def on_arrow(self, step):
        # with text in the box, arrows move the cursor as usual
        if self.e.get() == '':
            self.move(step)
            return 'break'

    def on_return(self):
        if self.checked_input is not None and self.e.get() == self.checked_input:
            if self.N < self.total - 1:
                self.move(1)
            else:
                self.result.config(text='🎉 You reached the end of the song', fg=C['good'])
        else:
            self.check_lyrics()

    def check_lyrics(self):
        input_l = self.e.get()
        if input_l.strip() == '':
            self.result.config(text='There is no input', fg=C['muted'])
            return

        self.t.delete('1.0', END)

        cn_w = list(self.cn_l[self.N].replace(' ', ''))
        en_l = self.en_l[self.N].split()
        check_words = input_l.lower().split()
        new_w = lc.read_new_words(W_DIR)
        wrong = 0

        # Compare against every syllable of the answer; missing input counts as wrong
        for w in range(len(en_l)):
            word = check_words[w] if w < len(check_words) else ''
            if is_correct(word, en_l[w]):
                self.t.insert(END, f'{en_l[w]}  ')
                continue

            wrong += 1
            self.t.insert(END, en_l[w], 'warning')
            self.t.insert(END, '  ')

            # some lyric lines have more syllables than characters
            if w >= len(cn_w):
                continue

            # add to word book
            lc.add_new_words(new_w, cn_w[w], en_l[w])
            self.app.progress.demote(cn_w[w])

            if cn_w[w] not in self.session_words:
                self.session_words.add(cn_w[w])
                self.t2.insert(END, f'{cn_w[w]}: ')
                self.t2.insert(END, f'{en_l[w]}\t', 'warning')

        if wrong:
            lc.output_new_words(W_DIR, new_w)
            self.result.config(text=f'✗ {wrong} wrong — answers in green  ·  Enter for next line', fg=C['bad'])
        else:
            self.result.config(text='✓ All correct  ·  Enter for next line', fg=C['good'])

        self.app.progress.record_check(self.song, self.N, len(en_l), wrong)
        self.checked_input = input_l
        self.update_stats()


# ------------------------------------------------------------------
#  New Words Page
#  -- Word book with mistakes and flashcard level, sortable by column
#  -- Highlight, delete, clear, start flashcards
# ------------------------------------------------------------------

class WordsPage(Page):

    COLUMNS = [
        ('no', '#', 50, CENTER),
        ('word', 'Word', 80, CENTER),
        ('pinyin', 'Pinyin', 140, W),
        ('count', 'Mistakes', 100, CENTER),
        ('level', 'Level', 120, CENTER),
        ('due', 'Next review', 130, CENTER),
    ]

    SORT_KEYS = {
        'no': lambda v: v['_order'],
        'word': lambda v: get(v['word']),
        'pinyin': lambda v: v['pinyin'],
        'count': lambda v: v['count'],
        'level': lambda v: v['_box'],
        'due': lambda v: v['_due'] or '',
    }

    def __init__(self, app):
        super().__init__(app)
        self.new_w = lc.read_new_words(W_DIR)
        self.tones = tone_index()

        bar = header(self, 'Word Book', lambda: app.show(HomePage))
        button(bar, 'Flashcards', lambda: app.show(FlashcardPage), width=130, accent=True).pack(side=RIGHT)
        self.summary = label(bar, '', size=13, color='muted')
        self.summary.pack(side=RIGHT, padx=14)

        self.table = SortableTree(self, self.COLUMNS, self.SORT_KEYS, app.word_sort)
        self.table.tree.tag_configure('highlight', foreground=C['answer'])
        self.table.pack(fill=BOTH, expand=1, padx=16, pady=6)

        label(self, 'Click a column header to sort  ·  highlighted words come first in flashcards',
              size=12, color='muted').pack()

        buttonframe = Frame(self)
        buttonframe.pack(pady=(6, 14))
        button(buttonframe, 'Highlight', self.highlight_item).pack(side=LEFT, padx=8)
        button(buttonframe, 'Delete', self.delete_item).pack(side=LEFT, padx=8)
        button(buttonframe, 'Clear', self.clear_items).pack(side=LEFT, padx=8)

        self.load_rows()

    def load_rows(self, select=None):
        rows = []
        for n, (word, (pinyin, count, highlight)) in enumerate(self.new_w.items()):
            state = self.app.progress.word_state(word)
            values = {
                'word': word, 'pinyin': with_tones(word, pinyin, self.tones), 'count': count,
                'level': level_dots(state['box']), 'due': until(state['due']),
                '_order': n, '_box': state['box'], '_due': state['due'],
            }
            rows.append((word, values, ('highlight',) if highlight == 1 else ()))

        self.table.rows = rows
        self.table.refresh(select)

        due = len(self.app.progress.due_words(self.new_w))
        self.summary.config(text=f'{len(self.new_w)} words  ·  {due} due today')

    def highlight_item(self):
        word = self.table.selected()
        if word is None:
            return

        self.new_w[word][-1] = 0 if self.new_w[word][-1] == 1 else 1
        lc.output_new_words(W_DIR, self.new_w)
        self.load_rows(select=word)

    def delete_item(self):
        word = self.table.selected()
        if word is None:
            return

        self.new_w.pop(word)
        self.app.progress.remove_word(word)
        lc.output_new_words(W_DIR, self.new_w)
        self.load_rows()

    def clear_items(self):
        if self.new_w and messagebox.askyesno('Clear word book', f'Delete all {len(self.new_w)} words?',
                                              icon='warning', parent=self):
            self.new_w.clear()
            self.app.progress.clear_words()
            lc.output_new_words(W_DIR, self.new_w)
            self.load_rows()


# ------------------------------------------------------------------
#  Flashcard Page
#  -- Shows a character, type its jyutping (no tones)
#  -- Leitner boxes decide when a word comes back (see progress.py)
#  -- Words answered wrong come back again later in the same session
# ------------------------------------------------------------------

class FlashcardPage(Page):

    def __init__(self, app, review_all=False):
        super().__init__(app)
        self.new_w = lc.read_new_words(W_DIR)
        self.tones = tone_index()

        words = app.progress.order_words(self.new_w) if review_all else app.progress.due_words(self.new_w)
        self.queue = words[:FLASHCARD_SESSION]
        self.idx = 0
        self.answered = set()           # words already scheduled in this session
        self.first_try_correct = 0
        self.missed = []
        self.revealed = False

        bar = header(self, 'Flashcards', lambda: app.show(WordsPage))
        self.position = label(bar, '', size=14, color='muted')
        self.position.pack(side=RIGHT)

        if not self.queue:
            self.empty_state()
            return

        self.bar = ttk.Progressbar(self)
        self.bar.pack(fill=X, padx=16, pady=(2, 10))

        card = Frame(self, bg=C['surface'])
        card.pack(fill=BOTH, expand=1, padx=60, pady=10)
        self.char = Label(card, bg=C['surface'], font=font(110))
        self.char.pack(pady=(30, 0))
        self.info = Label(card, bg=C['surface'], fg=C['muted'], font=font(13))
        self.info.pack()

        self.e = Entry(card, font=font(20), justify=CENTER, width=18)
        self.e.pack(pady=(24, 8), ipady=6)
        self.e.bind('<Return>', lambda e: self.on_return())

        self.result = Label(card, bg=C['surface'], font=font(18))
        self.result.pack(pady=(4, 24))

        buttonframe = Frame(self)
        buttonframe.pack(pady=6)
        button(buttonframe, "Don't know", self.reveal, width=130).pack(side=LEFT, padx=8)
        self.main_button = button(buttonframe, 'Check', self.on_return, width=180, accent=True)
        self.main_button.pack(side=LEFT, padx=8)

        label(self, 'Jyutping without tones  ·  Enter: check / next  ·  empty Enter: show answer', size=12, color='muted').pack(pady=(4, 14))

        self.show_card()

    def empty_state(self):
        center = Frame(self)
        center.place(relx=0.5, rely=0.45, anchor=CENTER)

        if not self.new_w:
            label(center, 'Your word book is empty', size=20, weight='bold').pack()
            label(center, 'Words you get wrong while practising songs show up here.',
                  color='muted').pack(pady=(6, 20))
            button(center, 'Select Songs', lambda: self.app.show(SongsPage), accent=True).pack()
            return

        label(center, 'Nothing to review today 🎉', size=20, weight='bold').pack()
        label(center, f'Next review: {until(self.app.progress.next_due(self.new_w))}',
              color='muted').pack(pady=(6, 20))
        button(center, 'Review all words anyway', lambda: self.app.show(FlashcardPage, review_all=True),
               width=220, accent=True).pack()

    def show_card(self):
        word = self.queue[self.idx]
        state = self.app.progress.word_state(word)

        self.position.config(text=f'Card {self.idx + 1} / {len(self.queue)}')
        self.bar.config(maximum=len(self.queue), value=self.idx)
        self.char.config(text=word)
        self.info.config(text=f'Wrong {self.new_w[word][1]} times in songs  ·  level {level_dots(state["box"])}')
        self.result.config(text='')
        self.main_button.config(text='Check')
        self.e.config(state=NORMAL)
        self.e.delete(0, END)
        self.e.focus_set()
        self.revealed = False

    def on_return(self):
        if self.revealed:
            self.next_card()
        elif self.e.get().strip() == '':
            self.reveal()
        else:
            self.check()

    def check(self):
        word = self.queue[self.idx]
        answer = self.new_w[word][0]
        typed = self.e.get().strip().lower()

        toned = with_tones(word, answer, self.tones)

        if is_correct(typed, answer):
            self.result.config(text=f'✓ {toned}', fg=C['good'])
            self.grade(word, True)
        else:
            self.result.config(text=f'✗ {toned}    (you typed {typed})', fg=C['bad'])
            self.grade(word, False)

    def reveal(self):
        if self.revealed:
            return
        word = self.queue[self.idx]
        self.result.config(text=f'Answer: {with_tones(word, self.new_w[word][0], self.tones)}', fg=C['bad'])
        self.grade(word, False)

    def grade(self, word, correct):
        # only the first answer in a session moves the word between boxes
        if word not in self.answered:
            self.answered.add(word)
            self.app.progress.review(word, correct)
            if correct:
                self.first_try_correct += 1
            else:
                self.missed.append(word)

        # a missed word comes back at the end of the queue until it is answered right
        if not correct:
            self.queue.append(word)

        self.revealed = True
        self.e.config(state='readonly')
        self.main_button.config(text='Next')

    def next_card(self):
        self.idx += 1
        if self.idx < len(self.queue):
            self.show_card()
        else:
            self.finish()

    def finish(self):
        for child in self.winfo_children()[1:]:
            child.destroy()
        self.position.config(text='')

        total = len(self.answered)
        center = Frame(self)
        center.place(relx=0.5, rely=0.45, anchor=CENTER)
        label(center, 'Session complete', size=22, weight='bold').pack()
        label(center, f'Correct on the first try: {self.first_try_correct} / {total}  '
                      f'({self.first_try_correct / total:.0%})', color='muted').pack(pady=(8, 4))
        if self.missed:
            label(center, 'To review again: ' + '  '.join(self.missed), color='answer').pack(pady=4)

        row = Frame(center)
        row.pack(pady=(20, 0))
        button(row, 'Next round', lambda: self.app.show(FlashcardPage), width=140, accent=True).pack(side=LEFT, padx=8)
        button(row, 'Word Book', lambda: self.app.show(WordsPage), width=140).pack(side=LEFT, padx=8)
        button(row, 'Home', lambda: self.app.show(HomePage), width=140).pack(side=LEFT, padx=8)


# ------------------------------------------------------------------
#  Excution
#  -- One window; pages are swapped inside it
# ------------------------------------------------------------------

class App(Tk):

    def __init__(self):
        super().__init__()
        self.title('Learning Cantonese')
        theme.apply(self)
        center_window(self)

        self.progress = Progress()
        self.song_sort = {'col': 'song', 'reverse': False}
        self.word_sort = {'col': 'no', 'reverse': False}
        self.page = None

        menubar(self, [
            ('Home', lambda: self.show(HomePage)),
            ('Select Songs', lambda: self.show(SongsPage)),
            ('Word Book', lambda: self.show(WordsPage)),
            ('Flashcards', lambda: self.show(FlashcardPage)),
        ])
        self.show(HomePage)

    def show(self, page_cls, **kwargs):
        if self.page is not None:
            self.page.destroy()
        self.page = page_cls(self, **kwargs)
        self.page.pack(fill=BOTH, expand=1)


if __name__ == '__main__':
    App().mainloop()
