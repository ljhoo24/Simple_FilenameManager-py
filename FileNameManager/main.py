import tkinter as tk
from tkinter import filedialog
import os
import subprocess

def remove_files():
    word_to_remove = word_entry.get()
    if word_to_remove:
        folder_path = filedialog.askdirectory()
        if folder_path:
            # ���� ���� ��� ���� �˻�
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file == word_to_remove:
                        os.remove(file_path)
            
            # �۾� �Ϸ� �˸� â ǥ��
            show_done_window("���� ���� �Ϸ�")

def remove_string_from_filename():
    word_to_remove = word_entry.get()
    if word_to_remove:
        folder_path = filedialog.askdirectory()
        if folder_path:
            # ���� ���� ��� ���� �˻�
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    new_file_name = file.replace(word_to_remove, "")
                    if new_file_name != file:
                        new_file_path = os.path.join(root, new_file_name)
                        os.rename(file_path, new_file_path)
            
            # �۾� �Ϸ� �˸� â ǥ��
            show_done_window("���ϸ� ���� �Ϸ�")

def show_done_window(message):
    done_window = tk.Toplevel(root)
    done_window.title("�۾� �Ϸ�")
    label = tk.Label(done_window, text=message)
    label.pack(padx=20, pady=20)
    done_window.mainloop()
    
root = tk.Tk()
root.title("���� ������")

window_width = 300
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

word_label = tk.Label(root, text="���ϸ� �Ǵ� �ܾ�:")
word_label.pack(pady=5)

word_entry = tk.Entry(root)
word_entry.pack(pady=5)

remove_file_button = tk.Button(root, text="���� ����", command=remove_files)
remove_file_button.pack(pady=10)

remove_string_button = tk.Button(root, text="���ϸ��� ���� ����", command=remove_string_from_filename)
remove_string_button.pack(pady=10)

root.mainloop()