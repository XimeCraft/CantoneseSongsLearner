import glob
import os
import re
from datetime import date, datetime
from tkinter import *
from tkinter import font as tkfont, messagebox, ttk

import pandas as pd
from pinyin import get

import jyutping
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

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf'

def strip_marks(syllable):
    """Brackets and punctuation around a syllable: '(soeng2' -> 'soeng2'."""
    return syllable.strip('()[]{}（）【】,.!?;:~"\'')

def lyric_pairs(cn, en):
    """Characters and syllables of a lyric line, without brackets and punctuation.
    aligned is True when they pair up one to one. Otherwise (English words, odd lines) the raw
    characters are returned and the caller pairs them by position, skipping non-Chinese ones.
    """
    syllables = [s for s in (strip_marks(x).lower() for x in en.split()) if s]
    chars = [c for c in cn if is_chinese(c)]
    if len(chars) == len(syllables):
        return chars, syllables, True
    return list(cn.replace(' ', '')), syllables, False

def tone_index():
    """Map each character to the jyutping (with tones) it has in the downloaded lyrics."""
    index = {}
    for name in get_all_songs():
        for cn, en in zip(*load_song(name)):
            chars, syllables, aligned = lyric_pairs(cn, en)
            if aligned:
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

def sound_columns(pinyin, toned):
    """Initial, final and tone columns for a word book entry.
    Words with alternatives like sang/saang list every initial, final and tone.
    """
    parts = [p for p in (jyutping.split(x) for x in pinyin.split('/')) if p is not None]
    initials = list(dict.fromkeys(i for i, _ in parts)) or ['?']
    finals = list(dict.fromkeys(f for _, f in parts)) or ['?']
    tones = list(dict.fromkeys(re.findall(r'\d+', toned))) or ['']
    key = jyutping.sort_key(*parts[0]) if parts else jyutping.sort_key('?', '?')

    return {
        'initial': ' / '.join(i or '—' for i in initials),
        'final': ' / '.join(finals),
        'tone': ' / '.join(tones) or '—',
        '_initials': initials, '_finals': finals, '_tones': tones,
        '_initial_key': key[0], '_final_key': key[1],
        '_tone_key': int(tones[0]) if tones[0] else 99,
    }

def level_dots(box):
    return '●' * box + '○' * (5 - box)


ALL_SONGS = 'All songs'

def songs_label(songs):
    """Text for a song filter: a set of song names, '' standing for words recorded without a song."""
    if not songs:
        return ALL_SONGS
    if len(songs) == 1:
        return next(iter(songs)) or '—'
    return f'{len(songs)} songs'

def song_picker(parent, app, songs, command):
    """Dropdown of the songs that have missed words. command gets {song} or None for all songs."""
    names = sorted(app.progress.songs_with_misses(), key=get)
    var = StringVar(value=songs_label(songs))
    box = ttk.Combobox(parent, textvariable=var, values=[ALL_SONGS] + names, state='readonly',
                       width=14, font=font(13))

    def on_select(e):
        box.selection_clear()
        command(None if var.get() == ALL_SONGS else {var.get()})

    box.bind('<<ComboboxSelected>>', on_select)
    return box, var

def words_in_songs(progress, new_w, songs):
    """Word book entries missed in any of the given songs ('' = recorded without a song)."""
    if not songs:
        return dict(new_w)
    by_word = progress.misses_by_word()
    return {w: v for w, v in new_w.items()
            if by_word.get(w, {}).keys() & songs or ('' in songs and w not in by_word)}


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


def header(page, title, back, home=False):
    """Title bar with a Back button; home=True adds a Home button for pages two or more steps from home."""
    bar = Frame(page)
    bar.pack(side=TOP, fill=X, padx=16, pady=(14, 6))
    button(bar, 'Back', back, width=90).pack(side=LEFT)
    if home:
        button(bar, 'Home', lambda: page.app.show(HomePage), width=80).pack(side=LEFT, padx=(8, 0))
    label(bar, title, size=18, weight='bold').pack(side=LEFT, padx=14)
    return bar


class SortableTree(Frame):
    """Treeview with a scrollbar.
    -- Click a header to sort by it, Shift-click to add it as the next sort level
    -- Right-click a header to filter by its values
    -- Drag a header border: the left column gets narrower and the right one wider
    """

    MIN_WIDTH = 36

    def __init__(self, parent, columns, sort_keys, view, default_sort,
                 filter_tokens=None, token_keys=None, on_change=None):
        super().__init__(parent)
        self.columns = columns
        self.titles = {c[0]: c[1] for c in columns}
        self.sort_keys = sort_keys
        self.default_sort = default_sort
        self.filter_tokens = filter_tokens or {}     # col -> values a row can be filtered by
        self.token_keys = token_keys or {}           # col -> order of those values in the filter list
        self.on_change = on_change
        self.rows = []
        self._drag = None
        self._pressed_heading = False

        # sorting, filters and widths are kept by the caller, so they survive page changes
        self.view = view
        view.setdefault('sort', list(default_sort))
        view.setdefault('filters', {})
        view.setdefault('widths', {})

        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns], show='headings', selectmode='browse')
        for col, title, width, anchor in columns:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=view['widths'].get(col, width), minwidth=self.MIN_WIDTH,
                             anchor=anchor, stretch=True)

        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree.bind('<ButtonPress-1>', self.on_press)
        self.tree.bind('<B1-Motion>', self.on_drag)
        self.tree.bind('<ButtonRelease-1>', self.on_release)
        for sequence in ('<Button-2>', '<Button-3>', '<Control-Button-1>'):
            self.tree.bind(sequence, self.on_right_click)

    # --------------------------------------------------------------
    #  Mouse on the header
    # --------------------------------------------------------------

    def column_at(self, x):
        n = int(self.tree.identify_column(x)[1:]) - 1
        return self.columns[n][0] if 0 <= n < len(self.columns) else None

    def border_at(self, x):
        """Index of the column whose right border is at x (the last column's border can't move)."""
        right = 0
        for n, (col, *_) in enumerate(self.columns[:-1]):
            right += self.tree.column(col, 'width')
            if abs(x - right) <= 6:
                return n
        return None

    def on_press(self, e):
        region = self.tree.identify_region(e.x, e.y)
        self._pressed_heading = region == 'heading'

        if region == 'separator':
            n = self.border_at(e.x)
            if n is not None:
                left, right = self.columns[n][0], self.columns[n + 1][0]
                self._drag = (left, right, e.x, self.tree.column(left, 'width'), self.tree.column(right, 'width'))
            return 'break'

    def on_drag(self, e):
        if self._drag is None:
            return
        left, right, x0, w_left, w_right = self._drag
        delta = max(self.MIN_WIDTH - w_left, min(e.x - x0, w_right - self.MIN_WIDTH))
        self.tree.column(left, width=w_left + delta)
        self.tree.column(right, width=w_right - delta)
        return 'break'

    def on_release(self, e):
        if self._drag is not None:
            self._drag = None
            self.view['widths'] = {c[0]: self.tree.column(c[0], 'width') for c in self.columns}
            return 'break'

        if self._pressed_heading and self.tree.identify_region(e.x, e.y) == 'heading':
            col = self.column_at(e.x)
            if col:
                self.sort_by(col, add=bool(e.state & 0x1))     # 0x1 = Shift held

    def on_right_click(self, e):
        if self.tree.identify_region(e.x, e.y) == 'heading':
            col = self.column_at(e.x)
            if col and col != 'no':
                FilterPopup(self, col, e.x_root, e.y_root)
            return 'break'

    # --------------------------------------------------------------
    #  Sorting and filtering
    # --------------------------------------------------------------

    def sort_by(self, col, add=False):
        """Click: sort by col only (again: reverse).
        Shift-click: add col as the next level (again: reverse, third time: remove it).
        """
        if col not in self.sort_keys:
            return
        sort = self.view['sort']
        cols = [c for c, _ in sort]

        if not add or sort == self.default_sort:
            if cols == [col]:
                sort[0] = (col, not sort[0][1])
            else:
                sort[:] = [(col, False)]
        elif col not in cols:
            sort.append((col, False))
        elif not sort[cols.index(col)][1]:
            sort[cols.index(col)] = (col, True)
        else:
            sort.pop(cols.index(col))
            if not sort:
                sort[:] = list(self.default_sort)

        self.refresh()

    def tokens(self, col, values):
        fn = self.filter_tokens.get(col)
        return fn(values) if fn else [str(values[col])]

    def token_key(self, col):
        return self.token_keys.get(col, lambda t: (0, int(t), '') if t.isdigit() else (1, 0, t))

    def visible_rows(self, skip=None):
        """Rows passing every filter (except the one on column skip)."""
        filters = {c: allowed for c, allowed in self.view['filters'].items() if c != skip}
        return [r for r in self.rows
                if all(any(t in allowed for t in self.tokens(c, r[1])) for c, allowed in filters.items())]

    def reset(self):
        self.view['sort'][:] = list(self.default_sort)
        self.view['filters'].clear()
        self.view['widths'].clear()
        for col, _, width, _ in self.columns:
            self.tree.column(col, width=width)
        self.refresh()

    def refresh(self, select=None):
        rows = self.visible_rows()

        # stable sorts from the last level to the first give a multi-level sort
        sort = self.view['sort']
        for col, reverse in reversed(sort):
            rows.sort(key=lambda r: self.sort_keys[col](r[1]), reverse=reverse)

        levels = {c: (n, reverse) for n, (c, reverse) in enumerate(sort)}
        for col, title, _, _ in self.columns:
            text = title
            if col in levels:
                n, reverse = levels[col]
                text += (' ▼' if reverse else ' ▲') + (str(n + 1) if len(sort) > 1 else '')
            if col in self.view['filters']:
                text += ' ●'
            self.tree.heading(col, text=text)

        self.tree.delete(*self.tree.get_children())
        for n, (iid, values, tags) in enumerate(rows):
            shown = [n + 1 if c == 'no' else values[c] for c, *_ in self.columns]
            self.tree.insert('', END, iid=iid, values=shown, tags=tags)

        if select and self.tree.exists(select):
            self.tree.selection_set(select)
            self.tree.see(select)

        if self.on_change:
            self.on_change(len(rows), len(self.rows))

    def selected(self):
        selection = self.tree.selection()
        return selection[0] if selection else None


class FilterPopup(Toplevel):
    """Checklist of a column's values; only rows with a checked value are shown."""

    def __init__(self, table, col, x, y):
        super().__init__(table, bg=C['bg'])
        self.table, self.col = table, col
        self.title('Filter')
        self.transient(table.winfo_toplevel())
        self.resizable(False, False)
        self.geometry(f'+{x}+{y}')

        # counts respect the other columns' filters, like a spreadsheet
        counts = {}
        for r in table.visible_rows(skip=col):
            for t in table.tokens(col, r[1]):
                counts[t] = counts.get(t, 0) + 1
        every = {t for r in table.rows for t in table.tokens(col, r[1])}
        self.order = sorted(every, key=table.token_key(col))
        self.counts = counts
        self.checked = set(table.view['filters'].get(col, every))

        label(self, f'Filter by {table.titles[col]}', size=15, weight='bold').pack(anchor=W, padx=14, pady=(12, 6))

        self.search = StringVar()
        self.search.trace_add('write', lambda *_: self.fill())
        search_box = Entry(self, textvariable=self.search, width=24)
        search_box.pack(fill=X, padx=14, ipady=3)

        row = Frame(self)
        row.pack(fill=X, padx=14, pady=6)
        button(row, 'All', lambda: self.set_all(True), width=70).pack(side=LEFT)
        button(row, 'None', lambda: self.set_all(False), width=70).pack(side=LEFT, padx=6)

        listframe = Frame(self)
        listframe.pack(padx=14)
        self.lb = Listbox(listframe, selectmode=MULTIPLE, exportselection=False, activestyle='none',
                          height=min(12, max(len(self.order), 3)), width=26)
        scrollbar = ttk.Scrollbar(listframe, orient=VERTICAL, command=self.lb.yview)
        self.lb.configure(yscrollcommand=scrollbar.set)
        self.lb.pack(side=LEFT)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.lb.bind('<<ListboxSelect>>', self.on_select)

        self.status = label(self, '', size=12, color='muted')
        self.status.pack(anchor=W, padx=14, pady=4)

        buttonframe = Frame(self)
        buttonframe.pack(pady=(2, 12))
        button(buttonframe, 'Apply', self.apply, width=90, accent=True).pack(side=LEFT, padx=5)
        button(buttonframe, 'Clear Filter', self.clear, width=110).pack(side=LEFT, padx=5)

        self.bind('<Return>', lambda e: self.apply())
        self.bind('<Escape>', lambda e: self.destroy())
        self.fill()
        search_box.focus_set()
        self.grab_set()

    @staticmethod
    def display(token):
        return token if token != '' else '—'

    def fill(self):
        query = self.search.get().strip().lower()
        self.shown = [t for t in self.order if query in self.display(t).lower()]
        self.lb.delete(0, END)
        for n, t in enumerate(self.shown):
            self.lb.insert(END, f'{self.display(t)}    ({self.counts.get(t, 0)})')
            if t in self.checked:
                self.lb.selection_set(n)
        self.update_status()

    def on_select(self, e=None):
        selected = set(self.lb.curselection())
        for n, t in enumerate(self.shown):
            if n in selected:
                self.checked.add(t)
            else:
                self.checked.discard(t)
        self.update_status()

    def set_all(self, on):
        """All / None act on the values currently listed (after search)."""
        for t in self.shown:
            if on:
                self.checked.add(t)
            else:
                self.checked.discard(t)
        self.fill()

    def update_status(self):
        self.status.config(text=f'{len(self.checked)} of {len(self.order)} values selected')

    def apply(self):
        if self.checked >= set(self.order):
            self.table.view['filters'].pop(self.col, None)
        else:
            self.table.view['filters'][self.col] = set(self.checked)
        self.destroy()
        self.table.refresh()

    def clear(self):
        self.table.view['filters'].pop(self.col, None)
        self.destroy()
        self.table.refresh()


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

        self.table = SortableTree(self, self.COLUMNS, self.SORT_KEYS, app.song_view, [('song', False)])
        self.table.pack(fill=BOTH, expand=1, padx=16, pady=6)
        self.table.tree.bind('<Double-1>', lambda e: self.play())
        self.table.tree.bind('<Return>', lambda e: self.play())

        label(self, 'Click header: sort  ·  Shift-click: add sort level  ·  right-click: filter  ·  drag header border: resize',
              size=12, color='muted').pack()

        buttonframe = Frame(self)
        buttonframe.pack(pady=(6, 14))
        button(buttonframe, 'Play Cantonese', self.play, accent=True).pack(side=LEFT, padx=8)
        button(buttonframe, 'Show Lyrics', self.show_lyrics).pack(side=LEFT, padx=8)
        button(buttonframe, 'Delete Song', self.delete_song).pack(side=LEFT, padx=8)
        button(buttonframe, 'Reset View', self.table.reset, width=110).pack(side=LEFT, padx=8)

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
                                        icon='warning', default='no', parent=self):
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
#  -- Jyutping (with tones) above each character; a long line wraps to fit the window
#  -- The jyutping of characters in the word book is highlighted
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

    PINYIN_FONT, CHAR_FONT = 22, 12

    def __init__(self, app, song):
        super().__init__(app)
        self.song = song

        bar = header(self, song, lambda: app.show(SongsPage, select=song), home=True)
        button(bar, 'Play Cantonese', lambda: app.show(PracticePage, song=song), width=140, accent=True).pack(side=RIGHT)
        self.tones = BooleanVar(value=True)
        ttk.Checkbutton(bar, text='Show tones', variable=self.tones, command=self.update_tones).pack(side=RIGHT, padx=14)

        label(self, 'Green jyutping = words in your word book (ones you got wrong before)', size=12, color='muted').pack(anchor=W, padx=16)

        scroll = ScrollFrame(self)
        scroll.pack(fill=BOTH, expand=1, padx=16, pady=(4, 14))

        new_w = lc.read_new_words(W_DIR)
        self.pinyin_labels = []
        cn_l, en_l = load_song(song)

        # room for a line of cells: window width less page padding, frame padding and the scrollbar
        avail = app.winfo_width() - 32 - 40 - 20
        measure = tkfont.Font(font=font(self.PINYIN_FONT)).measure
        probe = Label(self, text='probe', font=font(self.PINYIN_FONT))
        label_pad = probe.winfo_reqwidth() - measure('probe')      # label border and padding
        probe.destroy()

        for cn, en in zip(cn_l, en_l):
            line = Frame(scroll.inner, bg=C['surface'])
            line.pack(anchor=W, padx=20, pady=8)

            chars, syllables, aligned = lyric_pairs(cn, en)

            # Characters and syllables don't line up: show the two lines as they are
            if not aligned:
                self.add_pinyin(line, en, C['fg'], wraplength=avail, justify=LEFT).pack(anchor=W)
                Label(line, text=cn, bg=C['surface'], fg=C['muted'], font=font(self.CHAR_FONT),
                      wraplength=avail, justify=LEFT).pack(anchor=W)
                continue

            # one cell per syllable, packed left to right; a new row when the next one wouldn't fit
            row, used = None, 0
            for char, syllable in zip(chars, syllables):
                width = measure(syllable) + label_pad + 6            # cell padx 3 on each side
                if row is None or used + width > avail:
                    row = Frame(line, bg=C['surface'])
                    row.pack(anchor=W)
                    used = 0
                cell = Frame(row, bg=C['surface'])
                cell.pack(side=LEFT, padx=3, pady=2)
                self.add_pinyin(cell, syllable, C['answer'] if char in new_w else C['fg']).pack()
                Label(cell, text=char, bg=C['surface'], fg=C['muted'], font=font(self.CHAR_FONT)).pack()
                used += width

    def add_pinyin(self, parent, text, color, **kw):
        l = Label(parent, text=text, bg=C['surface'], fg=color, font=font(self.PINYIN_FONT), **kw)
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
#  -- Words missed in this session can be reviewed in the word book
# ------------------------------------------------------------------

class PracticePage(Page):

    def __init__(self, app, song, start=0):
        super().__init__(app)
        self.song = song
        self.cn_l, en_l = load_song(song)
        # per line: characters, syllables without tones, whether they pair up one to one
        self.lines = [lyric_pairs(cn, lc.split_words_tones([en])[0]) for cn, en in zip(self.cn_l, en_l)]
        self.total = len(self.cn_l)
        self.N = max(0, min(start, self.total - 1))
        self.checked_input = None
        self.session_words = {}         # word -> [pinyin, times missed in this session]

        bar = header(self, song, lambda: app.show(SongsPage, select=song), home=True)
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
        self.restart_button = button(buttonframe, 'Back to line 1', self.restart, width=130)    # shown at the end

        row = Frame(self)
        row.pack(fill=X, padx=16, pady=(8, 0))
        label(row, 'Words to review from this session', size=13, color='muted').pack(side=LEFT)
        self.review_button = button(row, 'Review in Word Book (0)', self.review_session, width=200)
        self.review_button.config(disabledbackground=C['surface2'], disabledforeground=C['muted'], state=DISABLED)
        self.review_button.pack(side=RIGHT)
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
        self.restart_button.pack_forget()
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
                self.finish_song()
        else:
            self.check_lyrics()

    def restart(self):
        self.N = 0
        self.app.progress.set_position(self.song, 0)
        self.display_new_lyrics()

    def finish_song(self):
        self.restart_button.pack(side=LEFT, padx=8)
        n = len(self.session_words)
        if n:
            self.result.config(text=f'🎉 You reached the end of the song  ·  {n} word{"s" if n != 1 else ""} missed this time',
                               fg=C['good'])
            self.review_button.focus_set()
        else:
            self.result.config(text='🎉 You reached the end of the song  ·  nothing missed this time', fg=C['good'])

    def check_lyrics(self):
        input_l = self.e.get()
        if input_l.strip() == '':
            self.result.config(text='There is no input', fg=C['muted'])
            return

        self.t.delete('1.0', END)

        cn_w, en_l, _ = self.lines[self.N]
        check_words = input_l.lower().split()
        new_w = lc.read_new_words(W_DIR)
        wrong = 0
        missed = []

        # Compare against every syllable of the answer; missing input counts as wrong
        for w in range(len(en_l)):
            word = check_words[w] if w < len(check_words) else ''
            if is_correct(word, en_l[w]):
                self.t.insert(END, f'{en_l[w]}  ')
                continue

            wrong += 1
            self.t.insert(END, en_l[w], 'warning')
            self.t.insert(END, '  ')

            # lines that don't pair up (English words, odd lines) are paired by position
            if w >= len(cn_w) or not is_chinese(cn_w[w]):
                continue

            # add to word book
            lc.add_new_words(new_w, cn_w[w], en_l[w])
            self.app.progress.demote(cn_w[w])
            missed.append(cn_w[w])
            self.session_words.setdefault(cn_w[w], [en_l[w], 0])[1] += 1

        if wrong:
            lc.output_new_words(W_DIR, new_w)
            self.result.config(text=f'✗ {wrong} wrong — answers in green  ·  Enter for next line', fg=C['bad'])
        else:
            self.result.config(text='✓ All correct  ·  Enter for next line', fg=C['good'])

        self.app.progress.record_check(self.song, self.N, len(en_l), wrong, missed)
        self.checked_input = input_l
        self.show_session_words()
        self.update_stats()

    def show_session_words(self):
        self.t2.delete('1.0', END)
        for word, (pinyin, n) in self.session_words.items():
            self.t2.insert(END, f'{word}: ')
            self.t2.insert(END, pinyin, 'warning')
            self.t2.insert(END, (f' ×{n}' if n > 1 else '') + '\t')

        n = len(self.session_words)
        self.review_button.config(text=f'Review in Word Book ({n})', state=NORMAL if n else DISABLED)

    def review_session(self):
        if self.session_words:
            misses = {word: n for word, (_, n) in self.session_words.items()}
            self.app.show(WordsPage, session=(self.song, misses))


# ------------------------------------------------------------------
#  New Words Page
#  -- Word book with mistakes and flashcard level, sortable by column
#  -- Songs column: which songs a word was missed in; dropdown filters by song
#  -- Right after practising a song: only the words missed in that session
#  -- Highlight, delete, clear, start flashcards
# ------------------------------------------------------------------

class WordsPage(Page):

    COLUMNS = [
        ('no', '#', 40, CENTER),
        ('word', 'Word', 56, CENTER),
        ('pinyin', 'Pinyin', 96, W),
        ('initial', '声母', 54, CENTER),
        ('final', '韵母', 64, CENTER),
        ('tone', '声调', 50, CENTER),
        ('count', 'Mistakes', 80, CENTER),
        ('songs', 'Songs', 150, W),
        ('level', 'Level', 84, CENTER),
        ('due', 'Next review', 96, CENTER),
    ]

    # shown before Songs right after practising a song: times missed in that session
    SESSION_COLUMN = ('session', 'This time', 80, CENTER)

    SORT_KEYS = {
        'no': lambda v: v['_order'],
        'word': lambda v: get(v['word']),
        'pinyin': lambda v: v['pinyin'],
        # initials and finals in Jyutping table order
        'initial': lambda v: v['_initial_key'],
        'final': lambda v: v['_final_key'],
        'tone': lambda v: v['_tone_key'],
        'count': lambda v: v['count'],
        'session': lambda v: v['session'],
        'level': lambda v: v['_box'],
        'due': lambda v: v['_due'] or '',
    }

    FILTER_TOKENS = {
        'initial': lambda v: v['_initials'],
        'final': lambda v: v['_finals'],
        'tone': lambda v: v['_tones'],
        'songs': lambda v: v['_songs'] or [''],
    }

    TOKEN_KEYS = {
        'initial': lambda t: jyutping.sort_key(t, '')[0],
        'final': lambda t: jyutping.sort_key('b', t)[1],
        'songs': lambda t: (t == '', get(t)),
        'level': lambda t: t.count('●'),
        'due': lambda t: {'new': -2, 'today': -1, 'tomorrow': 1}.get(t) or int(re.sub(r'\D', '', t) or 0),
    }

    def __init__(self, app, songs=None, session=None):
        """songs: show only words missed in these songs; a set, empty for all (None keeps the last filter).
        session: (song, {word: times missed}) right after practising a song: only those words.
        """
        super().__init__(app)
        self.new_w = lc.read_new_words(W_DIR)
        self.tones = tone_index()
        self.session = session

        if session:
            bar = header(self, f'{session[0]}  ·  missed this time',
                         lambda: app.show(SongsPage, select=session[0]), home=True)
            columns = list(self.COLUMNS)
            columns.insert([c[0] for c in columns].index('songs'), self.SESSION_COLUMN)
            view, default_sort = app.session_view, [('session', True)]
        else:
            bar = header(self, 'Word Book', lambda: app.show(HomePage))
            columns, view, default_sort = self.COLUMNS, app.word_view, [('no', False)]
            filters = view.setdefault('filters', {})
            if songs:
                filters['songs'] = set(songs)
            elif songs is not None:
                filters.pop('songs', None)
            if 'songs' in filters:
                filters['songs'] &= set(app.progress.songs_with_misses()) | {''}     # a song deleted since
                if not filters['songs']:
                    filters.pop('songs')
            self.song_box, self.song_var = song_picker(bar, app, filters.get('songs'), self.select_songs)
            self.song_box.pack(side=LEFT)

        button(bar, 'Flashcards', self.flashcards, width=130, accent=True).pack(side=RIGHT)
        self.summary = label(bar, '', size=13, color='muted')
        self.summary.pack(side=RIGHT, padx=14)

        sort_keys = {**self.SORT_KEYS, 'songs': self.songs_key}
        self.table = SortableTree(self, columns, sort_keys, view, default_sort,
                                  self.FILTER_TOKENS, self.TOKEN_KEYS, on_change=self.update_summary)
        self.table.tree.tag_configure('highlight', foreground=C['answer'])
        self.table.pack(fill=BOTH, expand=1, padx=16, pady=6)

        label(self, 'Click header: sort  ·  Shift-click: add sort level  ·  right-click: filter  ·  drag header border: resize',
              size=12, color='muted').pack()

        buttonframe = Frame(self)
        buttonframe.pack(pady=(6, 14))
        button(buttonframe, 'Highlight', self.highlight_item).pack(side=LEFT, padx=8)
        button(buttonframe, 'Delete', self.delete_item).pack(side=LEFT, padx=8)
        button(buttonframe, 'Clear', self.clear_items).pack(side=LEFT, padx=8)
        button(buttonframe, 'Reset View', self.table.reset, width=110).pack(side=LEFT, padx=8)

        self.load_rows()

    def selected_song(self):
        """The one song the table is filtered to, if any."""
        songs = self.table.view['filters'].get('songs', set()) - {''}
        return next(iter(songs)) if len(songs) == 1 else None

    def songs_key(self, v):
        """Sort key of the Songs column: mistakes in the chosen song, else the first song's name."""
        song = self.selected_song()
        if song:
            return v['_counts'].get(song, 0)
        return (not v['_songs'], get(v['_songs'][0]) if v['_songs'] else '')

    def load_rows(self, select=None):
        by_word = self.app.progress.misses_by_word()
        chosen = self.selected_song()
        rows = []
        for n, (word, (pinyin, count, highlight)) in enumerate(self.new_w.items()):
            if self.session and word not in self.session[1]:
                continue

            state = self.app.progress.word_state(word)
            toned = with_tones(word, pinyin, self.tones)
            songs = by_word.get(word, {})
            if chosen in songs:                 # the chosen song first
                songs = {chosen: songs[chosen], **songs}
            values = {
                'word': word, 'pinyin': toned, 'count': count,
                'songs': ', '.join(f'{s} ×{k}' for s, k in songs.items()) or '—',
                'level': level_dots(state['box']), 'due': until(state['due']),
                '_order': n, '_songs': list(songs), '_counts': songs, '_box': state['box'], '_due': state['due'],
                **sound_columns(pinyin, toned),
            }
            if self.session:
                values['session'] = self.session[1][word]
            rows.append((word, values, ('highlight',) if highlight == 1 else ()))

        self.table.rows = rows
        self.table.refresh(select)

    def update_summary(self, shown, total):
        due = sum(self.app.progress.is_due(word) for word, *_ in self.table.visible_rows())
        count = f'{shown} of {total} words shown' if shown != total else f'{total} words'
        self.summary.config(text=f'{count}  ·  {due} due today')
        if not self.session:
            self.song_var.set(songs_label(self.table.view['filters'].get('songs')))

    def select_songs(self, songs):
        filters, sort = self.table.view['filters'], self.table.view['sort']
        if songs:
            filters['songs'] = set(songs)
        else:
            filters.pop('songs', None)

        # one song chosen: its most missed words first; back to all songs: drop that sort again
        if self.selected_song():
            sort[:] = [('songs', True)]
        elif sort[0][0] == 'songs':
            sort[:] = list(self.table.default_sort)
        self.load_rows()

    def flashcards(self):
        if self.session:
            self.app.show(FlashcardPage, session=self.session)
        else:
            self.app.show(FlashcardPage, songs=self.table.view['filters'].get('songs'))

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
        if not self.new_w:
            messagebox.showinfo('Clear word book', 'The word book is already empty.', parent=self)
            return

        if messagebox.askyesno('Clear word book',
                               f'Delete all {len(self.new_w)} words from the word book?\n'
                               'Their flashcard progress and song records are removed too.',
                               icon='warning', default='no', parent=self):
            self.new_w.clear()
            self.app.progress.clear_words()
            lc.output_new_words(W_DIR, self.new_w)
            self.load_rows()


# ------------------------------------------------------------------
#  Flashcard Page
#  -- Shows a character, type its jyutping (no tones)
#  -- Leitner boxes decide when a word comes back (see progress.py)
#  -- Words answered wrong come back again later in the same session
#  -- Can be limited to the words missed in chosen songs, or in the song just practised
# ------------------------------------------------------------------

class FlashcardPage(Page):

    def __init__(self, app, review_all=False, songs=None, session=None):
        """songs: only words missed in these songs (a set; None or empty for all).
        session: (song, {word: times missed}) right after practising a song: only those words.
        """
        super().__init__(app)
        self.new_w = lc.read_new_words(W_DIR)
        self.tones = tone_index()
        self.songs, self.session = songs, session

        if session:
            self.pool = {w: v for w, v in self.new_w.items() if w in session[1]}
        else:
            self.pool = words_in_songs(app.progress, self.new_w, songs)

        words = app.progress.order_words(self.pool) if review_all else app.progress.due_words(self.pool)
        self.queue = words[:FLASHCARD_SESSION]
        self.idx = 0
        self.answered = set()           # words already scheduled in this session
        self.first_try_correct = 0
        self.missed = []
        self.revealed = False

        bar = header(self, 'Flashcards', self.back, home=True)
        if session:
            label(bar, f'{session[0]}  ·  missed this time', size=13, color='muted').pack(side=LEFT)
        else:
            song_picker(bar, app, songs, lambda s: app.show(FlashcardPage, songs=s))[0].pack(side=LEFT)
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

    def back(self):
        if self.session:
            self.app.show(WordsPage, session=self.session)
        else:
            self.app.show(WordsPage, songs=self.songs or set())

    def restart(self, review_all=False):
        self.app.show(FlashcardPage, review_all=review_all, songs=self.songs, session=self.session)

    def empty_state(self):
        center = Frame(self)
        center.place(relx=0.5, rely=0.45, anchor=CENTER)

        if not self.new_w:
            label(center, 'Your word book is empty', size=20, weight='bold').pack()
            label(center, 'Words you get wrong while practising songs show up here.',
                  color='muted').pack(pady=(6, 20))
            button(center, 'Select Songs', lambda: self.app.show(SongsPage), accent=True).pack()
            return

        if not self.pool:
            label(center, 'No missed words here', size=20, weight='bold').pack()
            label(center, 'Pick another song, or review the whole word book.',
                  color='muted').pack(pady=(6, 20))
            button(center, 'All songs', lambda: self.app.show(FlashcardPage), width=160, accent=True).pack()
            return

        label(center, 'Nothing to review today 🎉', size=20, weight='bold').pack()
        label(center, f'Next review: {until(self.app.progress.next_due(self.pool))}',
              color='muted').pack(pady=(6, 20))
        button(center, 'Review all words anyway', lambda: self.restart(review_all=True),
               width=220, accent=True).pack()

    def show_card(self):
        word = self.queue[self.idx]
        state = self.app.progress.word_state(word)

        self.position.config(text=f'Card {self.idx + 1} / {len(self.queue)}')
        self.bar.config(maximum=len(self.queue), value=self.idx)
        self.char.config(text=word)
        info = f'Wrong {self.new_w[word][1]} times in songs  ·  level {level_dots(state["box"])}'
        if self.session:
            info = f'Missed {self.session[1][word]}× this time  ·  ' + info
        self.info.config(text=info)
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
        button(row, 'Next round', self.restart, width=140, accent=True).pack(side=LEFT, padx=8)
        button(row, 'Word Book', self.back, width=140).pack(side=LEFT, padx=8)
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
        self.song_view = {}
        self.word_view = {}
        self.session_view = {}
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
