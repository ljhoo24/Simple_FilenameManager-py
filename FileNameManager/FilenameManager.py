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