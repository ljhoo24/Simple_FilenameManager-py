import tkinter as tk
from tkinter import filedialog
import os
import subprocess

def remove_files():
    word_to_remove = word_entry.get()
    if word_to_remove:
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 폴더 내의 모든 파일 검색
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file == word_to_remove:
                        os.remove(file_path)
            
            # 작업 완료 알림 창 표시
            show_done_window("파일 삭제 완료")

def remove_string_from_filename():
    word_to_remove = word_entry.get()
    if word_to_remove:
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 폴더 내의 모든 파일 검색
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    new_file_name = file.replace(word_to_remove, "")
                    if new_file_name != file:
                        new_file_path = os.path.join(root, new_file_name)
                        os.rename(file_path, new_file_path)
            
            # 작업 완료 알림 창 표시
            show_done_window("파일명 변경 완료")

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