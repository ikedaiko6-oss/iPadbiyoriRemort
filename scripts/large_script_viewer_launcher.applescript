-- 台本 大きい文字ビューアの起動用AppleScript
-- osacompileで .app にコンパイルして使う（build_app.sh 参照）

set repoPath to (POSIX path of (path to home folder)) & "iPadbiyoriRemort"
set serverScript to repoPath & "/scripts/large_script_editor_server.py"

do shell script "pkill -f large_script_editor_server.py; exit 0"
do shell script "nohup python3 " & quoted form of serverScript & " > /tmp/ipadbiyori_server.log 2>&1 &"
delay 1
do shell script "open http://127.0.0.1:8766/"
