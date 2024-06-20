import string
import os
import glob
import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

def read_lyrics(dir):
    """ Read lyrics from local, clean lyrics
    """

    with open(dir) as file:
        content = file.read().splitlines()
    
    file.close()

    return [x for x in content if x != '' and 'https' not in x]

def show_lyrics(dir):
    """ Show lyrics of a song
    """

    lyrics = read_lyrics(dir)
    return '\n\n'.join(['\n'.join(x) for x in zip(lyrics[::2], lyrics[1::2])])
    
def read_new_words(dir):
    """ Read new words booklet, if it doesn't exist, create one.
    """
    if not os.path.isfile(dir):
        open(dir, 'a').close()

    with open(dir, 'r') as file:
        try:
            content = json.loads(file.read())
        except json.JSONDecodeError:
            content = {}

    return content

def clear_new_words(dir):
    """ Clear all new words.
    """
    os.remove(W_DIR)
    open(W_DIR, 'a').close()

def convert_new_words_to_dict(new_w):
    """ Convert new words list to dictionary
    """
    # return {y[0]: y[1] for y in [x.split(':') for x in new_w]}
    pass

def print_new_words(new_w):
    """TODO: remove when have tkinter
    """
    data = [[key] + values for key, values in new_w.items()]
    print(pd.DataFrame(data, columns=['Word', 'Pronunciation', 'Counts']))

def split_words_tones(en_l):
    dict_table = str.maketrans('', '', string.digits)
    return [x.translate(dict_table) for x in en_l]

def add_new_words(new_w, cn_w, en_w):
    """ If word exists in new word book, count add 1,
        else add new word to new word book
        TODO: add new words with tones to new word book
    """

    if cn_w in new_w:
        new_w[cn_w][1] += 1
    else:
        new_w[cn_w] = [en_w, 1, 0]

def output_new_words(w_dir, new_w):
    """output new words to file
    """

    with open(w_dir, 'w') as f:
        json.dump(new_w, f, indent=4, ensure_ascii=False)
    f.close()

def convert_new_words_to_df(new_w):
    """ Convert new words list to DataFrame
    """
    return {y[0]: y[1] for y in [x.split(':') for x in new_w]}

def check_lyrics(input_l, cn_l, en_l, new_w, w_dir):
    """ Check if input lyrics corrected
    """
    
    cn_w = list(cn_l.replace(' ', ''))
    en_l = en_l.split(' ')
    colored_en_l = en_l.copy()
    check_words = input_l.split(' ')

    for w in range(len(check_words)):
        if (check_words[w] != en_l[w]) and ('/' not in en_l[w] or check_words[w] not in en_l[w].split('/')):
            check_words[w] = RED + check_words[w] + RESET
            colored_en_l[w] = GREEN + en_l[w] + RESET

            # Add colored incorrect words to words books
            add_new_words(new_w, cn_w[w], colored_en_l[w])

            # Writing to words books
            output_new_words(w_dir, new_w)

    output_ls = ' '.join(check_words)    
    correct_ls = ' '.join(colored_en_l)  

    return output_ls, correct_ls

def display_lyrics(l_dir):
    """Display lyrics in app with specific format
    """

    # read ls
    clean_l = read_lyrics(l_dir)
    cn_l, en_l = clean_l[::2], split_words_tones(clean_l[1::2])

    # get length of ls
    l_s = [len(x) for x in en_l]
    t_cn_l = [list(re.sub('\s+', '', x)) for x in cn_l]

    o_l = [] 
    for i in range(len(t_cn_l)):
        o_s = ''.join(f'{t_cn_l[i][j].center(int(l_s[i]/(len(cn_l[i]))))}' for j in range(len(t_cn_l[i])))
        o_l.append(o_s)
    
    return '\n\n'.join(['\n'.join(x) for x in zip(o_l, en_l)])

def play_lyrics(l_dir, w_dir):
    """ Play lyrics learning.
    """

    # read ls
    clean_l = read_lyrics(l_dir)
    cn_l, en_l = clean_l[::2], split_words_tones(clean_l[1::2])

    # read words book
    new_w = read_new_words(w_dir)

    # check ls from input2
    for number_l in range(len(cn_l)):

        print(cn_l[number_l])
        input_l = input()
        output_ls, correct_ls = check_lyrics(input_l, cn_l[number_l], en_l[number_l], new_w, w_dir)

        print('Your input: ', output_ls)
        print(f'Correct lyrics: {correct_ls}\n')

def get_html_part(url, part):
    """ extract part from a url
    """
    link = url
    f = requests.get(link).content

    return BeautifulSoup(f, 'html.parser').find(part)

def download_lyric(song_info):

    with open(f'data/songs/{song_info[2]}.txt', 'w') as lyric_f:
        url = f'https://www.feitsui.com/zh-hans/lyrics/{song_info[0]}'
        parent = get_html_part(url, 'body')

        for p in parent.find('article').find_all('p'):
            for l in p.contents:
                if '<' not in str(l):
                    lyric_f.write(str(l).replace('翡翠粤语歌词', '').strip() + '\n')

def learn_new_words():
    """ Check new words book.
    """
    new_w = read_new_words(W_DIR)

    if len(new_w) > 0:
        print_new_words(new_w)
    else:
        print('There are no new words')

def ana_new_words():
    """ Analysis new words
    """

    new = read_new_words(W_DIR)

def get_all_songs(l_dir):
    """ Get names of all songs
    """

    return [f'{str(n+1)}.{x[11:-4]}' for n, x in enumerate(glob.glob(os.path.join(l_dir, '*.txt')))]

def select_songs(l_dir):
    """ Select a testing song
    """

    all_songs = get_all_songs(l_dir)
    song_n = int(input('Which song would you like to start?\n\t{}\n'.format('\n\t'.join(all_songs)))) - 1

    return all_songs[song_n].split(".")[1]

def game_start():
    """ Title of game
        TODO: remove when have tkinter
    """ 

    title_l1 = "Let's start to learn Cantonese!!!"

    game_start = f"+{'-'*(20+len(title_l1))}+\n|{' '*(20+len(title_l1))}|\n|{' '*10}{title_l1}{' '*10}|\n|{' '*(20+len(title_l1))}|\n+{'-'*(20+len(title_l1))}+\n"
    print(game_start)

def start_lyrics(l_dir):
    # Select songs
    selected_song = select_songs(l_dir)
    s_dir = f'{l_dir}/{selected_song}.txt'

    # Start to lyrics
    print(f"{'='*60}")
    print(selected_song)

    return s_dir

if __name__ == '__main__':

    RED = "\033[31m"
    GREEN = "\033[32m"
    RESET = "\033[39m"
    
    l_dir = 'data/songs'
    W_DIR = 'data/new words.json'

    # Game start
    game_start()
    method = input('What would you like to do today?\n\t1.Play songs\n\t2.Learn new words\n')

    # Lyrics
    if method == '1':
        option_s = input('What could we do with songs?\n\t1.Play Cantonese\n\t2.Show lyrics\n')

        if option_s == '1':
            s_dir = start_lyrics(l_dir)
            play_lyrics(s_dir, W_DIR)
        elif option_s == '2':
            s_dir = start_lyrics(l_dir)
            print(s_dir)
            print(show_lyrics(s_dir))

    # Check new words
    elif method == '2':
        option_w = input('What could we start with new words??\n\t1.Start learning\n\t2.Analysis new words\n\t3.Clear all new words\n')

        if option_w == '1':
            learn_new_words()
        elif option_w == '2':
            ana_new_words()
        elif option_w == '3':
            clear_new_words(W_DIR)
    
