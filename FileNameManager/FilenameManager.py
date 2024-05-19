import os

class FilenameManager:
    def __init__(self):
        pass

    @staticmethod
    def remove_files(folder_path, word_to_remove):
        if folder_path:
            # 폴더 내의 모든 파일 검색
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if word_to_remove in file:
                        os.remove(file_path)

    @staticmethod
    def remove_string_from_filename(folder_path, word_to_remove):
        if folder_path:
            # 폴더 내의 모든 파일 및 폴더 검색
            for root, dirs, files in os.walk(folder_path):
                # 폴더명 변경
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    new_dir_name = dir.replace(word_to_remove, "")
                    if new_dir_name != dir:
                        new_dir_path = os.path.join(root, new_dir_name)
                        os.rename(dir_path, new_dir_path)

                # 파일명 변경
                for file in files:
                    file_path = os.path.join(root, file)
                    new_file_name = file.replace(word_to_remove, "")
                    if new_file_name != file:
                        new_file_path = os.path.join(root, new_file_name)
                        os.rename(file_path, new_file_path)

    @staticmethod
    def change_string_from_filename(folder_path, word_to_remove, word_to_change):
        if folder_path and word_to_change:
            # 폴더 내의 모든 파일 및 폴더 검색
            for root, dirs, files in os.walk(folder_path):
                # 폴더명 변경
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    new_dir_name = dir.replace(word_to_remove, word_to_change)
                    if new_dir_name != dir:
                        new_dir_path = os.path.join(root, new_dir_name)
                        os.rename(dir_path, new_dir_path)
             # 파일명 변경
                for file in files:
                    file_path = os.path.join(root, file)
                    new_file_name = file.replace(word_to_remove, word_to_change)
                    if new_file_name != file:
                        new_file_path = os.path.join(root, new_file_name)
                        os.rename(file_path, new_file_path)

    @staticmethod
    def rename_to_uppercase(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            # 파일명을 대문자로 변경
            for name in files:
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, name.upper())
                os.rename(old_path, new_path)
            # 폴더명을 대문자로 변경
            for name in dirs:
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, name.upper())
                os.rename(old_path, new_path)