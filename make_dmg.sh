#!/bin/bash
# Build a standalone copy of the app to send to other Macs.
#   ./make_dmg.sh          dist/LearningCantonese.dmg        Apple Silicon (M-series)
#   ./make_dmg.sh intel    dist/LearningCantonese-Intel.dmg  Intel; built with an x86_64 Python under Rosetta
# It uses its own build/ environment, so .venv, data/ and the app from make_app.sh are left alone.
# Only the songs and the song index are bundled, never the word book or practice progress.
set -euo pipefail

PROJECT="$(cd "$(dirname "$0")" && pwd)"
NAME="Learning Cantonese"

case "${1:-arm}" in
    arm)
        BUILD="$PROJECT/build"; DMG_NAME=LearningCantonese.dmg
        PYTHON=3.12; RUN=(); PLATFORM=() ;;
    intel)
        # Rosetta runs the x86_64 Python, pip picks x86_64 wheels and PyInstaller builds an x86_64 app
        arch -x86_64 /usr/bin/true 2>/dev/null || { echo "Rosetta is needed: softwareupdate --install-rosetta" >&2; exit 1; }
        BUILD="$PROJECT/build/intel"; DMG_NAME=LearningCantonese-Intel.dmg
        PYTHON=cpython-3.12-macos-x86_64-none; RUN=(arch -x86_64)
        # pick wheels that run on macOS 10.15+ (the Python build's own minimum), not just on this Mac's macOS
        export MACOSX_DEPLOYMENT_TARGET=10.15
        PLATFORM=(--python-platform x86_64-apple-darwin) ;;
    *)
        echo "usage: $0 [arm|intel]" >&2; exit 1 ;;
esac

DIST="$PROJECT/dist"
VENV="$BUILD/venv"
DMG="$DIST/$DMG_NAME"

# PyInstaller needs lipo; use Xcode's if the default command line tools are missing
if ! lipo -info /bin/ls >/dev/null 2>&1; then
    export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
fi
export PYINSTALLER_CONFIG_DIR="$BUILD/pyinstaller-cache"

cd "$PROJECT"
rm -rf "$BUILD/pyinstaller" "$DMG"
mkdir -p "$BUILD" "$DIST"

[ -x "$VENV/bin/python" ] || uv venv --python "$PYTHON" "$VENV"
uv pip install --quiet --python "$VENV/bin/python" ${PLATFORM[@]+"${PLATFORM[@]}"} -r requirements.txt pyinstaller
# same Tcl/Tk link as the README's setup, needed for uv's standalone Python
PY_LIB="$(${RUN[@]+"${RUN[@]}"} "$VENV/bin/python" -c 'import sys; print(sys.base_prefix)')/lib"
ln -sfn "$PY_LIB/tcl8.6" "$VENV/lib/tcl8.6"
ln -sfn "$PY_LIB/tk8.6" "$VENV/lib/tk8.6"

${RUN[@]+"${RUN[@]}"} "$VENV/bin/pyinstaller" --noconfirm --clean --windowed \
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
echo "Built: $DMG ($(file -b "$STAGE/$NAME.app/Contents/MacOS/$NAME" | grep -o 'arm64\|x86_64'))"
