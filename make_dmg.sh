#!/bin/bash
# Build dist/LearningCantonese.dmg, a standalone copy of the app to send to other Macs (Apple Silicon).
# It uses its own build/ environment, so .venv, data/ and the app from make_app.sh are left alone.
# Only the songs and the song index are bundled, never the word book or practice progress.
set -euo pipefail

PROJECT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$PROJECT/build"
DIST="$PROJECT/dist"
VENV="$BUILD/venv"
NAME="Learning Cantonese"
DMG="$DIST/LearningCantonese.dmg"

# PyInstaller needs lipo; use Xcode's if the default command line tools are missing
if ! lipo -info /bin/ls >/dev/null 2>&1; then
    export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
fi
export PYINSTALLER_CONFIG_DIR="$BUILD/pyinstaller-cache"

cd "$PROJECT"
rm -rf "$BUILD/pyinstaller" "$DIST"
mkdir -p "$BUILD" "$DIST"

[ -x "$VENV/bin/python" ] || uv venv --python 3.12 "$VENV"
uv pip install --quiet --python "$VENV/bin/python" -r requirements.txt pyinstaller
# same Tcl/Tk link as the README's setup, needed for uv's standalone Python
PY_LIB="$("$VENV/bin/python" -c 'import sys; print(sys.base_prefix)')/lib"
ln -sfn "$PY_LIB/tcl8.6" "$VENV/lib/tcl8.6"
ln -sfn "$PY_LIB/tk8.6" "$VENV/lib/tk8.6"

"$VENV/bin/pyinstaller" --noconfirm --clean --windowed \
    --name "$NAME" \
    --icon "$PROJECT/assets/windowIcon.icns" \
    --osx-bundle-identifier com.ximecraft.learningcantonese.dist \
    --python-option "X utf8_mode=1" \
    --collect-all tkmacosx \
    --collect-data pinyin \
    --add-data "$PROJECT/data/songs:seed/data/songs" \
    --add-data "$PROJECT/data/songs info.csv:seed/data" \
    --distpath "$BUILD/pyinstaller/dist" \
    --workpath "$BUILD/pyinstaller/work" \
    --specpath "$BUILD/pyinstaller" \
    packaged_app.py

STAGE="$BUILD/pyinstaller/stage"
mkdir -p "$STAGE"
cp -R "$BUILD/pyinstaller/dist/$NAME.app" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
cat > "$STAGE/首次打开必读.txt" <<'TXT'
安装：把 Learning Cantonese 拖到 Applications 文件夹。

首次打开：这个应用没有经过 Apple 公证，第一次打开会被 macOS 拦下。
1. 双击应用，看到提示后点“完成”（不要点“移到废纸篓”）。
2. 打开“系统设置 → 隐私与安全性”，拉到“安全性”一栏。
3. 点 Learning Cantonese 旁边的“仍要打开”，再输入开机密码确认。
之后就可以正常打开了。

你的生词和练习记录保存在：
~/Library/Application Support/Learning Cantonese/
TXT

hdiutil create -quiet -volname "$NAME" -srcfolder "$STAGE" -format UDZO -ov "$DMG"
echo "Built: $DMG"
