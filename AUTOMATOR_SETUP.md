# Automatorアプリ化手順（台本テレプロンプター）

`ipadbiyori_script_teleprompter.html` を、Macでダブルクリックすれば開くアプリにする手順。

## 前提

このリポジトリをホームディレクトリ直下にcloneしておく。

```bash
cd ~
git clone https://github.com/ikedaiko6-oss/iPadbiyoriRemort.git
```

これで `~/iPadbiyoriRemort/ipadbiyori_script_teleprompter.html` に配置される。

## 手順

1. **Automator.app** を起動（Launchpad または Spotlight検索）
2. 「新規書類」→「アプリケーション」を選んで作成開始
3. 左のアクション検索欄で「シェルスクリプトを実行」を検索し、右側の作業エリアにドラッグ
4. 「シェルスクリプトを実行」内のシェルを `/bin/zsh`（または `/bin/bash`）に設定
5. スクリプト欄に以下を入力

   ```bash
   open -a Safari "$HOME/iPadbiyoriRemort/ipadbiyori_script_teleprompter.html"
   ```

6. `Cmd+S` で保存
   - 保存場所：アプリケーションフォルダ、または任意の場所（Dockに登録したい場合はアプリケーションフォルダ推奨）
   - ファイル名：`AI台本 大きい文字`
   - ファイル形式：「アプリケーション」

## 動作確認

保存した `AI台本 大きい文字.app` をFinderでダブルクリックし、Safariで台本テレプロンプターが正常に開くことを確認する。

## 注意

- リポジトリを `~/iPadbiyoriRemort` 以外の場所にcloneした場合は、手順5のパスをその場所に合わせて書き換えること。
- HTMLファイル自体の内容（デザイン・台本内容）は変更不要。
