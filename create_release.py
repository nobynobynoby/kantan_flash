import os
import shutil
import glob
import sys

# --- 設定 ---
# 出力するzipファイルの名前
RELEASE_NAME = "kantan_flash_release"
# zip内に作成するフォルダ名
FOLDER_IN_ZIP = "kantan_flash"
# 各ファイルが格納されているディレクトリ
DIST_DIR = "dist"
TOOLS_DIR = "tools"
FIRMWARE_DIR = "firmware"
# 出力先ディレクトリ
RELEASE_DIR = "release"


def find_file(search_path, file_description):
    """指定されたパスでファイルを探し、見つからなければエラーで終了する"""
    if not os.path.exists(search_path):
        print(f"エラー: {file_description}が見つかりません。")
        print(f"パス: {os.path.abspath(search_path)}")
        sys.exit(1)
    return search_path

def find_firmware(search_dir):
    """ファームウェアディレクトリから.binファイルを探す"""
    firmware_files = glob.glob(os.path.join(search_dir, '*.bin'))
    if not firmware_files:
        print(f"エラー: '{search_dir}' フォルダに .bin ファイルが見つかりません。")
        sys.exit(1)
    # 最初に見つかったものを返す
    return firmware_files[0]

def main():
    """リリース用のzipファイルを作成する"""
    print("リリースパッケージの作成を開始します...")

    # --- 必要なファイルのパスを特定 ---
    exe_path = find_file(os.path.join(DIST_DIR, 'kantan_flash.exe'), "メイン実行ファイル")
    esptool_path = find_file(os.path.join(TOOLS_DIR, 'esptool.exe'), "esptool実行ファイル")
    firmware_path = find_firmware(FIRMWARE_DIR)
    # 追加: ライセンスファイルのパスを特定
    main_license_path = find_file("LICENSE", "メインライセンスファイル")
    esptool_license_path = find_file(os.path.join(TOOLS_DIR, "LICENSE.txt"), "esptoolライセンスファイル")
    # 追加: READMEファイルのパスを特定
    readme_path = find_file("README.md", "READMEファイル")

    print("以下のファイルをパッケージします:")
    print(f"  - {exe_path}")
    print(f"  - {esptool_path}")
    print(f"  - {firmware_path}")
    # 追加: ライセンスファイルとREADMEファイルの表示
    print(f"  - {main_license_path}")
    print(f"  - {esptool_license_path}")
    print(f"  - {readme_path}")

    # --- 一時的なステージングディレクトリを作成 ---
    staging_dir = os.path.join(RELEASE_DIR, "staging")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    
    # zip内に作成するディレクトリのパス
    archive_content_dir = os.path.join(staging_dir, FOLDER_IN_ZIP)
    os.makedirs(archive_content_dir)

    # --- ファイルをステージングディレクトリにコピー ---
    shutil.copy(exe_path, archive_content_dir)
    shutil.copy(esptool_path, archive_content_dir)
    # .binファイルは "firmware.bin" という固定の名前にしてコピーする
    shutil.copy(firmware_path, os.path.join(archive_content_dir, "firmware.bin"))
    # 追加: ライセンスファイルをコピー
    shutil.copy(main_license_path, archive_content_dir)
    shutil.copy(esptool_license_path, os.path.join(archive_content_dir, "LICENSE_esptool.txt"))
    # 追加: READMEファイルをコピー
    shutil.copy(readme_path, archive_content_dir)
    print(f"\nファイルを '{archive_content_dir}' にコピーしました。")

    # --- zipファイルを作成 ---
    zip_output_path = os.path.join(RELEASE_DIR, RELEASE_NAME)
    shutil.make_archive(zip_output_path, 'zip', root_dir=staging_dir)
    print(f"'{zip_output_path}.zip' を作成しました。")

    # --- ステージングディレクトリをクリーンアップ ---
    shutil.rmtree(staging_dir)
    print("一時ファイルをクリーンアップしました。")

    print("\nリリースパッケージの作成が完了しました。")
    print(f"出力先: {os.path.abspath(RELEASE_DIR)}")


if __name__ == '__main__':
    # 出力ディレクトリがなければ作成
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)
    main()