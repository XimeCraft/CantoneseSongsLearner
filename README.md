# README
## Introduction
This application is designed to help users improve their Cantonese prounciation skills of Cantonese songs by providing a way to practice Cantonese pinyin for Chinese lyrics. The application allows users to search for a song by its name, and then displays the Chinese lyrics sentence by sentence along with a text box for the user to type in the corresponding Cantonese pinyin. The application also keeps track of the user's incorrect pinyin inputs, allowing them to review and practice those specific sentences.

## Features
1. Use web crawling to get lyrics online by searching sonngs by name.
2. Display Chinese lyrics sentence by sentence with a text box for the user to type in the corresponding Cantonese pinyin
3. Keep track of incorrect pinyin inputs for review and practice
4. Display the whole Chinese lyrics and corresponding Cantonese pinyin.

## Usage
1. Open the application from app.py
2. Select Songs: 
   1. Place to store all the incorrect for further review and self-correction
3. Learn New Words:
   1. display the Chinese lyrics sentence by sentence along with a text box for the user to type in the corresponding Cantonese pinyin
   2. track of any incorrect pinyin inputs for review and practice

## Note
Please be aware that the application uses web crawling to get Chinese lyrics and corresponding Cantonese pinyin from a website which already contains that information and it's not 100% accurate. It's important to note that the application is for practice and reference only and should not be used as an official source for Cantonese pinyin.

## Setup
Requires [uv](https://docs.astral.sh/uv/) (macOS; the UI uses `tkmacosx`).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
# uv's standalone Python can't locate Tcl/Tk from inside a venv; link them in:
PY_LIB="$(.venv/bin/python -c 'import sys; print(sys.base_prefix)')/lib"
ln -s "$PY_LIB/tcl8.6" "$PY_LIB/tk8.6" .venv/lib/

.venv/bin/python app.py
```

To launch it like a normal Mac app (Launchpad, Spotlight, Dock), run `./make_app.sh` once.
It creates `~/Applications/Learning Cantonese.app`, which runs `app.py` from this folder,
so code changes apply immediately. Rerun it if you move the project folder.
Errors are logged to `~/Library/Logs/LearningCantonese.log`.
