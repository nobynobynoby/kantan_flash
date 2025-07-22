# esptool.py ファームウェア書き込みオプション調査結果

## 1. 目的

GUIベースのファームウェアアップロードツールを開発するにあたり、PlatformIOプロジェクト `KANTAN_Play_core-nori-fork` のファームウェアをM5Stack CoreS3に書き込むために `esptool.py` へ渡すべき、正確なコマンドラインオプションを特定する。

## 2. 調査対象環境

- **プロジェクト:** `KANTAN_Play_core-nori-fork`
- **PlatformIO環境:** `release_s3` (`platformio.ini` に定義)

## 3. 調査プロセス

1.  `platformio.ini` ファイルを静的に分析し、設定値を抽出。
2.  ビルド成果物（`.pio/build/release_s3/`）に残された引数ファイルの確認を試みるも、ファイルが存在せず失敗。
3.  ユーザーが `platformio.exe run --target upload --environment release_s3` を実行。
4.  アップロードはポート不在で失敗したが、その直前までのビルドログが生成された。
5.  成功したビルドログと `platformio.ini` の設定値を組み合わせ、最終的なオプションを確定させた。

## 4. 結論：esptool.py の正確なオプション一覧

`esptool.py write_flash` コマンドに渡すべきオプションは以下の通り。

| オプション | 値 | 根拠・解説 |
| :--- | :--- | :--- |
| `--chip` | `esp32s3` | ビルドログの `HARDWARE: ESP32S3` および `board: m5stack-cores3` 設定より確定。 |
| `--port` | (対象のCOMポート) | 書き込み対象のデバイスが接続されているシリアルポート。GUIツールではユーザーが選択できるようにする必要がある。 |
| `--baud` | `1500000` | `platformio.ini` の `upload_speed` 設定。高速書き込みを行う。 |
| `--before` | `default_reset` | 書き込み前にデバイスをリセットし、ブートローダーモードに移行させるための標準設定。 |
| `--after` | `hard_reset` | 書き込み完了後にデバイスをハードリセットし、新ファームウェアを起動させるための標準設定。 |
| `--flash_mode` | `qio` | `platformio.ini` の `board_build.flash_mode` 設定。 |
| `--flash_freq` | `80m` | `platformio.ini` の `board_build.f_flash = 80000000L` 設定より。 |
| `--flash_size` | `16MB` | ビルドログの `HARDWARE: ... 16MB Flash` およびパーティション設定より確定。 |

### 書き込むバイナリファイルとアドレス

以下の「アドレス」と「ファイルパス」のペアを、この順番で `write_flash` コマンドに渡す必要がある。

| アドレス | ファイルパス |
| :--- | :--- |
| `0x0000` | `.pio/build/release_s3/bootloader.bin` |
| `0x8000` | `.pio/build/release_s3/partitions.bin` |
| `0xe000` | `.pio/build/release_s3/boot_app0.bin` |
| `0x10000`| `.pio/build/release_s3/firmware.bin` |

**注意:** 上記ファイルのパスは、`KANTAN_Play_core-nori-fork` プロジェクトのルートディレクトリからの相対パス。GUIツールは、このプロジェクトの `.pio/build/release_s3/` ディレクトリ内にあるこれらのファイルを指定して `esptool.py` を実行する必要がある。

## 5. 完全なコマンドラインの例

COMポートが `COM3` である場合、実行されるべきコマンドの完全な形は以下のようになる。

```bash
esptool.py --chip esp32s3 --port COM3 --baud 1500000 --before default_reset --after hard_reset write_flash -z --flash_mode qio --flash_freq 80m --flash_size 16MB 0x0000 .pio/build/release_s3/bootloader.bin 0x8000 .pio/build/release_s3/partitions.bin 0xe000 .pio/build/release_s3/boot_app0.bin 0x10000 .pio/build/release_s3/firmware.bin
```
*(注: `esptool.py` へのパスは環境に合わせて解決する必要がある。`-z` は圧縮転送を行うための標準的なオプション)*
