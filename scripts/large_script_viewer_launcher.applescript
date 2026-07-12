-- 台本 大きい文字ビューアの起動用AppleScript
-- osacompileで .app にコンパイルして使う（build_app.sh 参照）

set repoPath to (POSIX path of (path to home folder)) & "iPadbiyoriRemort"
set serverScript to repoPath & "/scripts/large_script_editor_server.py"
set portFile to "/tmp/ipadbiyori_shinchan.port"

-- 自分のサーバー（このスクリプト）が既に起動済みかを確認する
set alreadyRunning to do shell script "pgrep -f " & quoted form of serverScript & " > /dev/null 2>&1; echo $?"

if alreadyRunning is "0" then
  -- 既に起動済みなら、そのサーバーのポートを読んでブラウザを開くだけ
  set thePort to do shell script "cat " & quoted form of portFile & " 2>/dev/null"
  do shell script "open http://127.0.0.1:" & thePort & "/"
else
  -- 未起動なら新規起動する（空きポートはPython側が自動で探す。起動後、自分でブラウザも開く）
  do shell script "rm -f " & quoted form of portFile
  do shell script "nohup python3 " & quoted form of serverScript & " > /tmp/ipadbiyori_shinchan_server.log 2>&1 &"
end if
