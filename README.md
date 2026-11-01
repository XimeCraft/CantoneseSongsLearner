# Learning Cantonese 粤语歌学习

通过粤语歌练习粤语拼音。 / Learn Jyutping through Cantonese songs.

## 开始之前 / Before you start

使用前请先了解粤语拼音。 / Please learn the basics of Jyutping first.

- YouTube: https://www.youtube.com/watch?v=y0D7j03GWXc&t=14s
- Bilibili（无法访问 YouTube 时 / if YouTube is unavailable）: https://www.bilibili.com/video/BV1kU4y1r7qR/

## 安装 / Install

仅支持 M 系列芯片的 Mac。 / Apple Silicon Macs only.

**[下载 / Download LearningCantonese.dmg](https://github.com/XimeCraft/CantoneseSongsLearner/releases/latest/download/LearningCantonese.dmg)**

1. 打开 DMG，把应用拖到 Applications。 / Open the DMG and drag the app to Applications.
2. 双击打开应用。macOS 会拦下，点“完成”。 / Open the app. macOS will block it; click "Done".
3. 打开“系统设置 → 隐私与安全性”，点“仍要打开”。 / In System Settings → Privacy & Security, click "Open Anyway".

## 使用 / How to use

1. **Select Songs**：选一首歌，看着歌词输入拼音。 / Pick a song and type the Jyutping for each line.
2. **Word Book**：查看打错的字。 / Review the words you got wrong.
3. **Flashcards**：用闪卡复习这些字。 / Practise those words with flashcards.

你的练习记录只保存在自己的电脑上。 / Your progress stays on your own Mac.

<details>
<summary>开发者 / Developers</summary>

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
# uv's standalone Python can't locate Tcl/Tk from inside a venv; link them in:
PY_LIB="$(.venv/bin/python -c 'import sys; print(sys.base_prefix)')/lib"
ln -s "$PY_LIB/tcl8.6" "$PY_LIB/tk8.6" .venv/lib/

.venv/bin/python app.py
```

- `./make_app.sh`: creates `~/Applications/Learning Cantonese.app`, which runs `app.py` from this folder.
- `./make_dmg.sh`: builds `dist/LearningCantonese.dmg`, without your word book or progress.

</details>
