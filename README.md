# iPadbiyoriRemort

台本テレプロンプターアプリ（「大きい文字の台本アプリ」）一式。

## 使い方（Mac側・最初の1回だけ）

```bash
cd ~
git clone https://github.com/ikedaiko6-oss/iPadbiyoriRemort.git
cd iPadbiyoriRemort
python3 --version   # Python3が入っていることを確認（Mac標準で入っています）
bash build_app.sh
```

これで `~/Desktop/アプリ/iPad日和台本 大きい文字.app` が作られる。
以降はこの`.app`をダブルクリックするだけで起動する。

`build_app.sh` の中身は `osacompile`（AppleScript→アプリ変換、macOS標準コマンド）を1回呼ぶだけ。
このコマンドはmacOS上でしか動かないため、ビルドの最終ステップだけはMac実機での実行が必要（クラウド環境からは実行できない）。

## アプリの中身・仕組み

```
build_app.sh                                .appをビルドするスクリプト（Mac専用・最初の1回だけ実行）
scripts/large_script_viewer_launcher.applescript   起動用AppleScript（build_app.shがこれを.appにコンパイルする）
scripts/large_script_editor_server.py       ローカルPythonサーバー本体（127.0.0.1のみでLISTEN、外部公開なし）
03_台本/*.txt                                台本の元データ
```

起動すると `python3 scripts/large_script_editor_server.py` がバックグラウンドで立ち上がり、
`http://127.0.0.1:8765/` をブラウザで開く。台本一覧 → クリックで大きい文字のスライド表示 → 「編集」から本文を直接書き換えて保存できる。

## 台本を追加するとき

`03_台本/` に `.txt` を追加して `git push` すれば、Mac側で `git pull` するだけで一覧に反映される
（アプリの再ビルドは不要、サーバーはフォルダの中身をそのつど読む）。

## デザイン相談用の参考ファイル

`ipadbiyori_script_teleprompter.html` は、パワポ風スライドデザインの元ネタ。
クラウド側（Claude）とHTMLデザイン・文言について相談するときの参考資料として残してある。
実際にMacで動くアプリの実体ではない（実体は `scripts/large_script_editor_server.py` の簡易HTML生成）。
