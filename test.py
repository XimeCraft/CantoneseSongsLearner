from dis import dis
from tkinter import *
import learnCantonese as lc
from app import next_lyrics
from utils import *


ws = Tk()
ws.title('Check Cantonese')
center_window(ws)

lyric_dir = 'data/songs/寻找独角兽.txt'
W_DIR = 'data/new words.json'

clean_l = lc.read_lyrics(lyric_dir)
cn_l, en_l = clean_l[::2], lc.split_words_tones(clean_l[1::2])
N = 0

display_c_l = StringVar()
display_c_l.set(cn_l[N])

# components to input cantonese
frame = Frame(ws)

l = Label(frame, textvariable=display_c_l, bg='#323232', font=("arial", 14), height=2)

e = Entry(frame, bg='black')
e.focus_set()

t = Text(frame, height=2, font=("arial", 14))
t.tag_config('warning', foreground='#A6FF2E')
 
buttonframe = Frame(ws)
b1 = Button(buttonframe, text='Check', command=lambda: check_lyrics(e.get(), cn_l[N], en_l[N], W_DIR, t, t2), bg='#616161', fg='white', width=200)
b2 = Button(buttonframe, text='Next', command=lambda: next_lyrics(display_c_l, cn_l, t, e), bg='#616161', fg='white', width=200)

frame2 = Frame(ws)
t2 = Text(frame2, font=("Helvetica", 14))
t2.tag_config('warning', foreground='#A6FF2E')


# show components on screen
frame.pack()

l.pack(fill='x', padx=10, pady=5)
e.pack(fill='x', padx=10, pady=5)
t.pack(fill='x', padx=10, pady=5)

buttonframe.pack()
b1.pack(side=LEFT, padx=10, pady=5)
b2.pack(side=RIGHT, padx=10, pady=5)

frame2.pack()
t2.pack(fill='x', padx=10, pady=5)

def next_lyrics(display_c_l, cn_l, t, e):
    global N

    N += 1
    value = cn_l[N]
    display_c_l.set(value)

    t.delete("1.0", END)
    e.delete(0, END)
    e.focus_set()

def check_lyrics(input_l, cn_l, en_l, w_dir, t, t2):
    global N

    cn_w = list(cn_l.replace(' ', ''))
    en_l = en_l.split(' ')
    check_words = input_l.split(' ')
    new_w = lc.read_new_words(w_dir)

    for w in range(len(check_words)):
        if (check_words[w] != en_l[w]) and ('/' not in en_l[w] or check_words[w] not in en_l[w].split('/')):
            t.insert(END, en_l[w], 'warning')
            t.insert(END, '  ')

            # add to word book
            lc.add_new_words(new_w, cn_w[w], en_l[w])
            lc.output_new_words(w_dir, new_w)

            t2.insert(END, f'{cn_w[w]}: ')
            t2.insert(END, f'{en_l[w]}\t', 'warning')

        else:
            t.insert(END, f'{en_l[w]}\t')

ws.mainloop()
