import os
import subprocess
import sys
import esptool

def main():
    print("Building kantan_flash.exe...")

    # Dynamically get the path to esptool's targets directory
    esptool_path = os.path.dirname(esptool.__file__)
    esptool_targets_path = os.path.join(esptool_path, 'targets')

    # PyInstaller command
    # Use forward slashes for --add-data source path for consistency
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        f'--add-data={esptool_targets_path.replace(os.sep, "/")}:esptool/targets',
        'src/kantan_flash.py'
    ]

    print(f"Executing: {' '.join(pyinstaller_cmd)}")

    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("kantan_flash.exe built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error building kantan_flash.exe: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()