# iPadbiyoriRemort

台本テレプロンプターアプリ（「大きい文字の台本アプリ」・シンちゃん版）一式。

このリポジトリには、ナギちゃん（Codex）版のスクリプトも同居しているが、
**シンちゃん版はデータ・ポートともに完全に独立**しており、ナギちゃん版の変更やアプリの起動状態には影響を受けない。

## 使い方（Mac側・最初の1回だけ）

```bash
cd ~
git clone https://github.com/ikedaiko6-oss/iPadbiyoriRemort.git
cd iPadbiyoriRemort
python3 --version   # Python3が入っていることを確認（Mac標準で入っています）
bash build_app.sh
```

これで `~/Desktop/アプリ/シンちゃん台本 大きい文字.app` が作られる。
以降はこの`.app`をダブルクリックするだけで起動する。

`build_app.sh` の中身は `osacompile`（AppleScript→アプリ変換、macOS標準コマンド）を1回呼ぶだけ。
このコマンドはmacOS上でしか動かないため、ビルドの最終ステップだけはMac実機での実行が必要（クラウド環境からは実行できない）。

### 以降の更新について（ターミナル不要）

`.app`は**起動するたびに自動で`git pull`してから最新コードで起動する**ようになっている。
そのため、Pythonサーバー側の機能追加・修正は、この`bash build_app.sh`を最初の1回実行しておけば、
以後は`.app`をダブルクリックするだけで自動的に最新版になる（ターミナル操作は不要）。

ただし以下の場合は今回のように再度`bash build_app.sh`（ターミナル操作）が必要：
- `build_app.sh`自体や`scripts/large_script_viewer_launcher.applescript`（起動の仕組みそのもの）を変更したとき
- Macが完全にネットに繋がっていない環境で、`git pull`が失敗する場合（失敗時は今あるコードのまま起動するので使えなくなることはない）

## アプリの中身・仕組み

```
build_app.sh                                       .appをビルドするスクリプト（Mac専用・最初の1回だけ実行）
scripts/large_script_viewer_launcher.applescript   起動用AppleScript（build_app.shがこれを.appにコンパイルする）
scripts/large_script_editor_server.py              シンちゃん版サーバー本体（127.0.0.1のみでLISTEN、外部公開なし）
03_台本_シンちゃん版/*.txt                            シンちゃん版専用の台本データ（ナギちゃん版の03_台本とは別物）
```

起動すると `python3 scripts/large_script_editor_server.py` がバックグラウンドで立ち上がる。
ポートは`8801`〜`8850`の範囲で空いているものを自動で探すので、ナギちゃん版と衝突しない。
実際に使ったポートは`/tmp/ipadbiyori_shinchan.port`に書き出される。

台本を1本の縦スクロールで表示し、本文をタップするとその場で直接編集でき、
フォーカスを外すと自動保存される（別ページの編集画面はなし）。

## 台本を追加するとき

`03_台本_シンちゃん版/` に `.txt` を追加して `git push` すれば、Mac側で `git pull` するだけで一覧に反映される
（アプリの再ビルドは不要、サーバーはフォルダの中身をそのつど読む）。

アプリ上で直接編集した内容も同じフォルダに書き戻されるので、GitHub側に反映したい場合は
Mac側で `git add 03_台本_シンちゃん版 && git commit && git push` する。

## デザイン相談用の参考ファイル

`ipadbiyori_script_teleprompter.html` は、パワポ風スライドデザインの元ネタ。
クラウド側（Claude）とHTMLデザイン・文言について相談するときの参考資料として残してある。
実際にMacで動くアプリの実体ではない（実体は `scripts/large_script_editor_server.py` の簡易HTML生成）。

## 旧`03_台本/`について

初期に作った共有フォルダ。ナギちゃん版と共有していたため編集が混ざる問題があり、
シンちゃん版は`03_台本_シンちゃん版/`に切り替えた。バックアップとしてそのまま残してある。
