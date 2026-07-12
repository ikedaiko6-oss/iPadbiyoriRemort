-- 台本 大きい文字ビューアの起動用AppleScript
-- osacompileで .app にコンパイルして使う（build_app.sh 参照）

set repoPath to (POSIX path of (path to home folder)) & "iPadbiyoriRemort"
set serverScript to repoPath & "/scripts/large_script_editor_server.py"
set portFile to "/tmp/ipadbiyori_shinchan.port"

-- 起動のたびに最新版へ自動更新する（失敗しても無視して今あるコードのまま起動を続ける）
try
  do shell script "cd " & quoted form of repoPath & " && git pull --ff-only 2>&1"
end try

-- 既に古いサーバーが動いていたら止めて、常に最新コードで起動し直す
do shell script "pkill -f " & quoted form of serverScript & "; exit 0"
do shell script "rm -f " & quoted form of portFile

do shell script "nohup python3 " & quoted form of serverScript & " > /tmp/ipadbiyori_shinchan_server.log 2>&1 &"
