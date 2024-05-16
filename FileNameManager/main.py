import tkinter as tk
from tkinter import filedialog
import subprocess
from FilenameManager import *

def remove_files():
    word_to_remove = word_entry.get()

    if word_to_remove:
        folder_path = filedialog.askdirectory()

        FilenameManager.remove_files(folder_path,word_to_remove)

        # 작업 완료 알림 창 표시
        show_done_window("파일 삭제 완료")

def remove_string_from_filename():
    word_to_remove = word_entry.get()

    if word_to_remove:
        folder_path = filedialog.askdirectory()

        FilenameManager.remove_string_from_filename(folder_path, word_to_remove)

        # 작업 완료 알림 창 표시
        show_done_window("파일명 및 폴더명 변경 완료")

def show_done_window(message):
    done_window = tk.Toplevel(root)
    done_window.title("작업 완료")
    label = tk.Label(done_window, text=message)
    label.pack(padx=20, pady=20)
    done_window.mainloop()
    
root = tk.Tk()
root.title("파일 관리기")

window_width = 300
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

word_label = tk.Label(root, text="파일명 또는 단어:")
word_label.pack(pady=5)

word_entry = tk.Entry(root)
word_entry.pack(pady=5)

remove_file_button = tk.Button(root, text="파일 삭제", command=remove_files)
remove_file_button.pack(pady=10)

remove_string_button = tk.Button(root, text="파일명에서 문자 제거", command=remove_string_from_filename)
remove_string_button.pack(pady=10)

root.mainloop()