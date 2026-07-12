#!/bin/bash
# 台本 大きい文字ビューアを .app にビルドする（Mac専用・1回だけ実行）
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/Desktop/アプリ"
APP_NAME="シンちゃん台本 大きい文字.app"

mkdir -p "$APP_DIR"

rm -rf "$APP_DIR/$APP_NAME"
osacompile -o "$APP_DIR/$APP_NAME" "$REPO_DIR/scripts/large_script_viewer_launcher.applescript"

# osacompileはCFBundleIdentifierを付けないことがあり、
# その場合LaunchServicesがアプリを認識できず「開けません」エラーになる。
PLIST="$APP_DIR/$APP_NAME/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Delete :CFBundleIdentifier" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.ipadbiyori.script-viewer" "$PLIST"

# 隔離属性を除去し、LaunchServicesに再登録する
xattr -cr "$APP_DIR/$APP_NAME"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_DIR/$APP_NAME"

echo "完成: $APP_DIR/$APP_NAME"
echo "Finderでダブルクリックして動作確認してください。"
