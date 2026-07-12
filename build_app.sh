#!/bin/bash
# 台本 大きい文字ビューアを .app にビルドする（Mac専用・1回だけ実行）
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/Desktop/アプリ"
APP_NAME="iPad日和台本 大きい文字.app"

mkdir -p "$APP_DIR"

osacompile -o "$APP_DIR/$APP_NAME" "$REPO_DIR/scripts/large_script_viewer_launcher.applescript"

echo "完成: $APP_DIR/$APP_NAME"
echo "Finderでダブルクリックして動作確認してください。"
