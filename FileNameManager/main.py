from textwrap import fill
import tkinter as tk
from tkinter import Menubutton, filedialog
import subprocess
from FilenameManager import *

def remove_files():
    word_to_remove = word_entry1.get()

    if word_to_remove:
        folder_path = filedialog.askdirectory()

        FilenameManager.remove_files(folder_path,word_to_remove)

        # 작업 완료 알림 창 표시
        show_done_window("파일 삭제 완료")

def remove_string_from_filename():
    word_to_remove = word_entry1.get()

    if word_to_remove:
        folder_path = filedialog.askdirectory()

        FilenameManager.remove_string_from_filename(folder_path, word_to_remove)

        # 작업 완료 알림 창 표시
        show_done_window("파일명 및 폴더명 변경 완료")

def change_string_from_filename():
    word_to_remove = word_entry1.get()
    word_to_change = word_entry2.get()

    if word_to_remove:
        folder_path = filedialog.askdirectory()

        FilenameManager.change_string_from_filename(folder_path, word_to_remove, word_to_change)

        # 작업 완료 알림 창 표시
        show_done_window("파일명 및 폴더명 변경 완료")

def show_done_window(message):
    done_window = tk.Toplevel(root)
    done_window.title("작업 완료")
    label = tk.Label(done_window, text=message)
    label.pack(padx=20, pady=20)
    done_window.mainloop()

def makeupper():
    folder_path = filedialog.askdirectory()

    FilenameManager.rename_to_uppercase(folder_path)

    # 작업 완료 알림 창 표시
    show_done_window("파일명 및 폴더명 변경 완료")

def makereg():
    folder_path = filedialog.askdirectory()
    word_to_add = word_entry2.get()

    FilenameManager.rename_files_with_seven_digits(folder_path, word_to_add)

    # 작업 완료 알림 창 표시
    show_done_window("파일명 변경 완료")

def filemoveandclean():
    folder_path = filedialog.askdirectory()
    FilenameManager.move_and_cleanup_files(folder_path)

    # 작업 완료 알림 창 표시
    show_done_window("파일 정리 완료")
    
root = tk.Tk()
root.title("파일 관리기")

window_width = 200
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

# 그리드 행 구성
for i in range(3):
    root.grid_rowconfigure(i, weight=1, minsize=window_height//3)

# 그리드 열 구성
for i in range(2):
    root.grid_columnconfigure(i, weight=1, minsize=window_width//2)

word_label1 = tk.Label(root, text="목표 단어 : ")
word_label1.grid(row=0, column=0, pady=5, sticky="e")

word_entry1 = tk.Entry(root)
word_entry1.grid(row=0, column=1, pady=5, sticky="w")

word_label2 = tk.Label(root, text="변경될 단어 : ")
word_label2.grid(row=1, column=0, pady=5, sticky="e")

word_entry2 = tk.Entry(root)
word_entry2.grid(row=1, column=1, pady=5, sticky="w")

menubutton = tk.Menubutton(root, text="기능",relief="raised")
menubutton.grid(row=2, column=0, columnspan=2, ipady=5)

topMenu = tk.Menu(menubutton, tearoff=0)
menubutton.configure(menu=topMenu)

topMenu.add_command(label="파일 삭제", command=remove_files)
topMenu.add_command(label="파일명에서 문자 제거", command=remove_string_from_filename)
topMenu.add_command(label="파일명에서 문자 변경", command=change_string_from_filename)
topMenu.add_command(label="파일명 및 폴더명 대문자로", command=makeupper)
topMenu.add_command(label="파일명 정규화", command=makereg)
topMenu.add_command(label="파일 리스트 정리",command=filemoveandclean)

root.mainloop()