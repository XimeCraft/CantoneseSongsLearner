import glob
import os
import pandas as pd
import re
from tkinter import *
from tkmacosx import Button
from distutils.command.clean import clean

from pinyin import get
from utils import center_window, menubar


def main_page(old_ws):
    """Create the main page of the app."""
    old_ws.destroy()

    ws = Tk()
    ws.title('Learning Cantonese')
    center_window(ws)

    # Create buttons
    menubar(ws, game_page, new_words_page)
    button_frame = Frame(ws)
    button_frame.focus_set()

    b1 = Button(button_frame, text='Select Songs', command=lambda: song_page(ws), width=200, bg='#616161', fg='white')
    b2 = Button(button_frame, text='Learn New Words', command=lambda: new_words_page(ws), width=200, bg='#616161', fg='white')
    
    button_frame.pack(expand=1)
    b1.pack(side=LEFT, padx=10, pady=5)
    b2.pack(side=RIGHT, padx=10, pady=5)

    ws.mainloop()


def game_page(ws, ws1, lb):
    """Create the game page of the app."""
    pass


def lyrics_page(ws, ws1):
    """Create the lyrics page of the app."""
    pass


def new_words_page(ws):
    """Create the new words page of the app."""
    pass


def get_song(lb):
    """Get the selected song from the listbox."""
    global song

    if lb.curselection() != ():
        value = lb.get(lb.curselection())
        song.set(value)
  

def song_page_2_main_page(ws, ws1):
    """Navigate from the song page to the main page."""
    ws1.destroy()
    main_page(ws)  


def song_page_2_game_page(ws, ws1, lb):
    """Navigate from the song page to the game page."""
    get_song(lb)

    if song.get() != '':
        game_page(ws, ws1, lb)


def song_page_2_lyrics_page(ws, ws1, lb):
    """Navigate from the song page to the lyrics page."""
    get_song(lb)

    if song.get() != '':
        lyrics_page(ws, ws1)


def get_all_songs():
    """Get a list of all songs in the app."""
    global song_list

    all_files = glob.glob('data/songs/*.txt')
    song_list = sorted([os.path.basename(x)[0:-4] for x in all_files], key=get)


def search_song(entry, data, lb):
    """Search for a song online and display the results in a listbox."""
    song_df = pd.read_csv('data/songs info.csv').drop_duplicates(subset='song id').drop_duplicates(subset=['singer', 'song
