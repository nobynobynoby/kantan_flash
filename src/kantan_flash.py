import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports
import subprocess
import threading
import shutil
import os
import sys
import io
import esptool

class TextRedirector(io.TextIOBase):
    def __init__(self, widget, progress_bar, tag="stdout"):
        self.widget = widget
        self.progress_bar = progress_bar
        self.tag = tag
        self.progress_re = re.compile(r'(\d+(\.\d+)?)%')

    def write(self, s):
        self.widget.insert(tk.END, s, (self.tag,))
        self.widget.see(tk.END)

        match = self.progress_re.search(s)
        if match:
            percent = float(match.group(1))
            self.progress_bar.after(0, lambda p=percent: self.progress_bar.config(value=p))

    def flush(self):
        pass # No-op for this simple redirector

class ESPFlasherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KANTRAN_PLAY(M5Stack Core3 SE) Flash Tool")
        self.geometry("600x400")

        # COMポート自動検出
        self.com_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.com_var, values=self.get_com_ports(), width=50)
        self.combobox.pack(pady=10)

        # ファイル選択
        self.filepath = tk.StringVar()
        tk.Entry(self, textvariable=self.filepath, width=50).pack(padx=10)
        tk.Button(self, text="ファイル選択", command=self.select_file).pack(pady=5)

        # 進捗バー
        self.progress = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate', maximum=100)
        self.progress.pack(pady=10)

        # ログ表示テキスト
        self.log_text = tk.Text(self, height=10)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 書き込み開始ボタン
        tk.Button(self, text="書き込み開始", command=self.start_flash).pack(pady=5)

        # M5Stack Core3 SE 固定オフセット（例）
        self.offset = "0x10000"

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        # より詳細な情報を含む文字列を生成
        return [f"{p.device} - {p.description}" for p in ports]

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if filename:
            self.filepath.set(filename)

    def start_flash(self):
        com = self.com_var.get()
        file = self.filepath.get()
        if not com:
            messagebox.showwarning("エラー", "COMポートを選択してください")
            return
        if not file:
            messagebox.showwarning("エラー", "書き込むファイルを選択してください")
            return

        # ログクリア・進捗リセット
        self.log_text.delete(1.0, tk.END)
        self.progress['value'] = 0

        # 書き込み処理を別スレッドで実行
        threading.Thread(target=self.flash_task, args=(com, file), daemon=True).start()

    def flash_task(self, com, file):
        # 標準出力をリダイレクト
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = TextRedirector(self.log_text, self.progress, "stdout")
        sys.stderr = TextRedirector(self.log_text, self.progress, "stderr")

        try:
            # esptool.main() に渡す引数を準備
            args = [
                "--chip", "esp32s3",
                "--port", com,
                "--baud", "1500000",
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash",
                "-z",
                "--flash_mode", "qio",
                "--flash_freq", "80m",
                "--flash_size", "16MB",
                self.offset,
                file
            ]
            
            # esptool.main() を呼び出す
            # esptool.main() は sys.exit() を呼び出す可能性があるため、SystemExit を捕捉する
            try:
                esptool.main(args)
                self.log_text.insert(tk.END, "\n書き込みが完了しました。\n")
            except SystemExit as e:
                if e.code != 0:
                    self.log_text.insert(tk.END, f"\nエラーが発生しました: {e.code}\n", "error")
                else:
                    self.log_text.insert(tk.END, "\n書き込みが完了しました。\n")

        except Exception as e:
            self.log_text.insert(tk.END, f"\n予期せぬエラー: {e}\n", "error")
        finally:
            # 標準出力を元に戻す
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.progress.after(0, lambda: self.progress.config(value=0))

if __name__ == "__main__":
    app = ESPFlasherGUI()
    app.mainloop()
