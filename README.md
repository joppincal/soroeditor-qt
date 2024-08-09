[README-en.md](README-en.md)

# SoroEditor - 並列同期テキストエディタ

![splash](soroeditor_qt/src/splash.png)

SoroEditorは並列同期テキストエディタです。

複数のテキストボックスを並べて同期スクロールし、それぞれの内容を編集することができます。

## 使い方

準備中

## 開発状況

### 実装済み機能

- **同期スクロール**
- メニューバー・ツールバー
- テキストエディタの設定
  - フォント
- プロジェクトファイル
- 設定ファイル

### 実装予定機能

- メニューバー・ツールバーからの編集
- 検索
  - ファイル内検索
  - ウェブ検索
- しおり
- 定型文
- インポート
- エクスポート
- ヘルプ
- 自動保存
- バックアップ
- テキストエディタの設定
  - 列数
  - 列幅
- テーマ

## その他

このリポジトリは、私の前作 SoroEditor (tkinter + ttkbootstrap で作成) を PySide6 を使って作り直したものです。当面の目標は、前作の機能を再現することです。

再制作の目的は2つあります。第一に、tkinterでの作業に限界を感じたこと。第二に、よりモダンなGUIキットを試してみたかったことです。

私、Joppincalはプログラミングに関しても、Githubに関しても全くの初心者です。指摘・助言があれば、是非よろしくお願いします。
