import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports
import subprocess
import threading
import shutil
import os
import sys

class ESPFlasherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KANTRAN_PLAY(M5Stack Core3 SE) Flash Tool")
        self.geometry("600x400")

        # COMポート自動検出
        self.com_var = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.com_var, values=self.get_com_ports())
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
        return [p.device for p in ports]

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
        cmd = [
            sys.executable, # Use the current Python interpreter
            "-m", "esptool",
            "--chip", "esp32s3",
            "--port", com,
            "write_flash",
            self.offset,
            file
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

        progress_re = re.compile(r'(\d+(\.\d+)?)%')

        for line in proc.stdout:
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)

            match = progress_re.search(line)
            if match:
                percent = float(match.group(1))
                self.progress.after(0, lambda p=percent: self.progress.config(value=p))

        proc.wait()
        self.log_text.insert(tk.END, f"\n終了コード: {proc.returncode}\n")
        self.progress.after(0, lambda: self.progress.config(value=0))

if __name__ == "__main__":
    app = ESPFlasherGUI()
    app.mainloop()
