#!/bin/bash
# Build "Learning Cantonese.app" in ~/Applications.
# The app runs app.py from this project folder with its .venv, so code changes
# take effect immediately and data stays in data/. Rerun if you move the project.
set -euo pipefail

PROJECT="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Applications/Learning Cantonese.app"

if [ ! -x "$PROJECT/.venv/bin/python" ]; then
    echo "No .venv found. Set up the environment first (see README)." >&2
    exit 1
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$PROJECT/assets/windowIcon.icns" "$APP/Contents/Resources/AppIcon.icns"

cat > "$APP/Contents/MacOS/LearningCantonese" <<EOF
#!/bin/bash
cd "$PROJECT" || exit 1
exec .venv/bin/python app.py >> "\$HOME/Library/Logs/LearningCantonese.log" 2>&1
EOF
chmod +x "$APP/Contents/MacOS/LearningCantonese"

cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Learning Cantonese</string>
    <key>CFBundleDisplayName</key>
    <string>Learning Cantonese</string>
    <key>CFBundleIdentifier</key>
    <string>com.ximecraft.learningcantonese</string>
    <key>CFBundleExecutable</key>
    <string>LearningCantonese</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# refresh Finder's icon cache for the bundle
touch "$APP"
echo "Built: $APP"
