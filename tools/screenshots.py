"""Render the README screenshots into docs/screenshots/ (run from the project folder).

    uv run --python 3.12 --with-requirements requirements.txt --with pyobjc-framework-Cocoa tools/screenshots.py

The app is driven through its pages inside this process and each page is rendered with AppKit,
so no screen-recording permission is needed. It works on a copy of data/ in a temporary folder:
your word book and practice progress are never touched. The screenshots follow the system's
light or dark appearance.
"""
import os
import shutil
import sys
import tempfile
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJECT, 'docs', 'screenshots')
SONG = '一生中最爱'
TITLE = 'Learning Cantonese'

# uv's standalone Python only finds the Tcl/Tk scripts next to the interpreter itself
_lib = os.path.join(sys.base_prefix, 'lib')
os.environ.setdefault('TCL_LIBRARY', os.path.join(_lib, 'tcl8.6'))
os.environ.setdefault('TK_LIBRARY', os.path.join(_lib, 'tk8.6'))

from tkinter import END, NORMAL                                         # noqa: E402
from AppKit import NSApplication, NSBitmapImageRep, NSCalibratedRGBColorSpace   # noqa: E402
from Foundation import NSMakeSize                                        # noqa: E402

PNG = 4     # NSBitmapImageFileTypePNG


def ns_window():
    for w in NSApplication.sharedApplication().windows():
        if w.title() == TITLE and w.isVisible():
            return w
    raise RuntimeError(f'no visible window titled {TITLE!r}')


def render(path):
    """Draw the whole window (title bar included) into a PNG at 1x."""
    view = ns_window().contentView().superview()
    b = view.bounds()
    w, h = int(b.size.width), int(b.size.height)
    rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, w, h, 8, 4, True, False, NSCalibratedRGBColorSpace, 0, 0)
    rep.setSize_(NSMakeSize(w, h))
    view.cacheDisplayInRect_toBitmapImageRep_(b, rep)
    rep.representationUsingType_properties_(PNG, None).writeToFile_atomically_(path, True)


def main():
    work = tempfile.mkdtemp(prefix='learning-cantonese-shots-')
    for name in ('data', 'assets'):
        shutil.copytree(os.path.join(PROJECT, name), os.path.join(work, name),
                        ignore=shutil.ignore_patterns('.DS_Store', 'new words copy.json'))
    os.chdir(work)
    sys.path.insert(0, PROJECT)
    import app as A

    root = A.App()
    root.update()
    root.lift()
    root.focus_force()

    def settle(n=4):
        for _ in range(n):
            root.update_idletasks()
            root.update()
            time.sleep(0.2)

    settle()
    win = ns_window()
    if win.tabGroup() is not None and win.tabGroup().isTabBarVisible():     # "prefer tabs" setting
        win.toggleTabBar_(None)
        settle(8)

    os.makedirs(OUT, exist_ok=True)

    def shoot(name):
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)     # active title bar
        settle()
        render(os.path.join(OUT, f'{name}.png'))
        print('wrote', os.path.relpath(os.path.join(OUT, f'{name}.png'), PROJECT))

    # song table
    root.show(A.SongsPage)
    shoot('songs')

    # practice: a few lines in, the current line checked with two mistakes
    root.show(A.PracticePage, song=SONG)
    p = root.page
    for text in ['jyu gwo ci ci dik dang mou jat',                        # 某 wrong
                 'zung jyu ho dang dou jat sang zung zeoi oi',
                 'seoi gaai ji nei ngo ze dyun cing']:
        p.e.delete(0, END)
        p.e.insert(0, text)
        p.check_lyrics()
        root.update()
        p.move(1)
    p.e.insert(0, 'mui mui pong soeng liu ji oi bat cing co mei loi')      # 碰, 外 wrong
    p.check_lyrics()
    shoot('practice')

    # the words missed in that session
    p.review_session()
    shoot('session')

    root.show(A.LyricsPage, song=SONG)
    shoot('lyrics')

    root.show(A.WordsPage)
    shoot('wordbook')

    # flashcards: the first card answered correctly
    root.show(A.FlashcardPage)
    f = root.page
    f.e.insert(0, f.new_w[f.queue[0]][0].split('/')[0])
    f.check()
    shoot('flashcards')

    # finish the round with three misses
    wrong_left, guard = 3, 0
    while f.idx < len(f.queue) and guard < 200:
        guard += 1
        if not f.revealed:
            word = f.queue[f.idx]
            f.e.config(state=NORMAL)
            f.e.delete(0, END)
            if wrong_left and word not in f.answered:
                f.e.insert(0, 'xx')
                wrong_left -= 1
            else:
                f.e.insert(0, f.new_w[word][0].split('/')[0])
            f.check()
        f.next_card()
    shoot('flashcards-done')

    root.show(A.HomePage)
    shoot('home')

    root.destroy()
    shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
