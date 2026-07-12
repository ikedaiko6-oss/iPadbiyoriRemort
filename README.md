# iPadbiyoriRemort

台本テレプロンプターアプリ（「大きい文字の台本アプリ」）の**バックアップ・相談用リポジトリ**。

## このリポジトリの役割

アプリ本体（Automator/AppleScript `.app`、ローカルPythonサーバー）はMacローカル完結で作る（GitHub・外部公開は使わない）。
このリポジトリはあくまで以下の2つの用途に限定する。

1. **台本の元データ（`.txt`）のバックアップ・共有**
   Macローカルの `iPad日和/03_台本/*.txt` と、このリポジトリの `03_台本/` を手動で同期する。
2. **HTMLデザイン・文言のクラウド相談用**
   `ipadbiyori_script_teleprompter.html` はデザイン確認・文言レビュー用の参考ファイル。実際にMacで動かすアプリの実体ではない（実体はMacローカルのPythonサーバー＋AppleScript/`osacompile`で作る）。

## フォルダ構成

```
03_台本/                              台本テキスト（.txt）のバックアップ
ipadbiyori_script_teleprompter.html   デザイン・文言相談用の参考HTML
```

## 実際のアプリの作り方（Macローカル側・参考）

1. 台本は `iPad日和/03_台本` の `.txt` で管理
2. その台本を、大きい文字のHTMLに変換
3. Macローカルの小さなPythonサーバーが、そのHTMLを表示・編集する
4. サーバーを起動してブラウザを開くAppleScriptを `osacompile` で `.app` にする
5. 完成したアプリは `~/Desktop/アプリ/` に置く

この作業自体はMacローカルのClaude Code（シンちゃん）が行う。GitHub連携は不要。

## 同期の流れ（このリポジトリを使う場面）

- 台本を新規追加・修正したら、Macの `03_台本/*.txt` をこのリポジトリの `03_台本/` にコピーして `git push`（バックアップ）
- HTMLデザインや台本文言についてクラウド側（このリポジトリ経由）に相談したいときは、`ipadbiyori_script_teleprompter.html` を更新してpush → 相談 → 確定したらMacローカル側にも反映
