# KANTAN Play Core Flash Tool for M5Stack CoreS3 SE

## 【重要】このツールについて

**このツールは、KANTAN Play Core の公式ツールではありません。**

作者が、個人でカスタマイズした **KANTAN Play Core のファームウェア** を **M5Stack CoreS3 SE** へ書き込むために作成した、**非公式（私家版）のツール**です。

公式のファームウェアや、他のデバイスへの書き込みは想定していません。ご使用の際は、この点を十分にご理解の上、自己責任でお願いします。

## 概要

M5Stack CoreS3 SE へ、KANTAN Play Core のファームウェアを書き込むためのGUIツールです。
`esptool` Pythonモジュールを内部で利用し、以下の機能を提供します。

-   接続されているCOMポートの自動検出
-   書き込むファームウェア（`.bin` ファイル）の選択
-   書き込み状況のプログレスバー表示
-   `esptool` からの出力ログのリアルタイム表示

## 使い方

1.  ダウンロードしたzipファイルを解凍します。
2.  解凍したフォルダを開き、`kantan_flash.exe` を実行します。
3.  ドロップダウンリストから、M5Stack CoreS3 SEが接続されているCOMポートを選択します。
4.  「ファイル選択」ボタンを押し、書き込みたいファームウェア（`.bin` ファイル）を選択します。
5.  「書き込み開始」ボタンを押すと、ファームウェアの書き込みが始まります。
6.  プログレスバーとログで進捗を確認できます。

## 開発者向け情報

### 動作環境

-   Python 3.x
-   pyserial
-   esptool

### セットアップ

1.  必要なライブラリをインストールします。
    ```shell
    pip install pyserial esptool
    ```
2.  ソースコードから直接実行する場合
    ```shell
    python src/kantan_flash.py
    ```

### ビルド方法

`pyinstaller` を使って、単一の実行ファイルを生成できます。

1.  `pyinstaller` をインストールします。
    ```shell
    pip install pyinstaller
    ```
2.  プロジェクトのルートディレクトリで以下のコマンドを実行し、ビルドします。
    ```shell
    pyinstaller --onefile --windowed src/kantan_flash.py
    ```
3.  ビルドが完了すると、`dist` フォルダ内に `kantan_flash.exe` が生成されます。

## ライセンス

このプロジェクトは **MIT License** の下で公開されています。

また、本ツールは `esptool` Pythonモジュールを内部に含んでいます。`esptool` のライセンスは `LICENSE_ESPTOOL.txt` に含まれています。
