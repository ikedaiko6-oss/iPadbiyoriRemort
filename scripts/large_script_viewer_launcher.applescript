-- 台本 大きい文字ビューアの起動用AppleScript
-- osacompileで .app にコンパイルして使う（build_app.sh 参照）

set repoPath to (POSIX path of (path to home folder)) & "iPadbiyoriRemort"
set serverScript to repoPath & "/scripts/large_script_editor_server.py"

-- 自分のサーバーだけを対象にする（他アプリの同名スクリプトを誤って止めないよう、リポジトリの絶対パスで指定）
do shell script "pkill -f " & quoted form of serverScript & "; exit 0"
do shell script "nohup python3 " & quoted form of serverScript & " > /tmp/ipadbiyori_shinchan_server.log 2>&1 &"
delay 1
do shell script "open http://127.0.0.1:8801/"
