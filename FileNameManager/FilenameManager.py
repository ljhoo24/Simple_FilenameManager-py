import os
import re
import shutil


class FilenameManager:
    """파일/폴더 이름 작업을 계획(plan)하고 적용(apply)하는 유틸리티.

    plan_* 메서드는 실제 파일을 건드리지 않고 변경 목록만 반환한다.
    변경 항목 형식:
        {"type": "delete", "src": 경로}
        {"type": "rename", "src": 경로, "dst": 경로}
        {"type": "move",   "src": 경로, "dst": 경로}
        {"type": "rmdir",  "src": 경로}
    """

    TRASH_EXTENSIONS = (".txt", ".url")

    # ---------- 계획(plan) ----------

    @staticmethod
    def plan_remove_files(folder_path, word):
        """이름에 word가 포함된 모든 파일 삭제 계획."""
        changes = []
        if not folder_path or not word:
            return changes
        for root, _dirs, files in os.walk(folder_path):
            for name in files:
                if word in name:
                    changes.append({"type": "delete", "src": os.path.join(root, name)})
        return changes

    @staticmethod
    def plan_remove_by_extension(folder_path, extensions=TRASH_EXTENSIONS):
        """지정 확장자 파일 전체 삭제 계획."""
        changes = []
        if not folder_path:
            return changes
        for root, _dirs, files in os.walk(folder_path):
            for name in files:
                if name.lower().endswith(extensions):
                    changes.append({"type": "delete", "src": os.path.join(root, name)})
        return changes

    @staticmethod
    def plan_replace(folder_path, old, new):
        """파일명·폴더명에서 old → new 치환 계획.

        하위 폴더부터(bottom-up) 처리해서 상위 폴더명이 먼저 바뀌어
        경로가 깨지는 문제를 방지한다.
        """
        changes = []
        if not folder_path or not old:
            return changes
        taken = set()
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                FilenameManager._plan_rename(root, name, name.replace(old, new), changes, taken)
            for name in dirs:
                FilenameManager._plan_rename(root, name, name.replace(old, new), changes, taken)
        return changes

    @staticmethod
    def plan_uppercase(folder_path):
        """파일명·폴더명 전부 대문자로 바꾸는 계획."""
        changes = []
        if not folder_path:
            return changes
        taken = set()
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                FilenameManager._plan_rename(root, name, name.upper(), changes, taken)
            for name in dirs:
                FilenameManager._plan_rename(root, name, name.upper(), changes, taken)
        return changes

    @staticmethod
    def plan_seven_digits(folder_path, prefix):
        """파일명에 포함된 7자리 숫자를 찾아 '접두어+숫자.확장자'로 정규화하는 계획."""
        changes = []
        if not folder_path:
            return changes
        taken = set()
        for root, _dirs, files in os.walk(folder_path):
            for name in files:
                match = re.search(r"\b\d{7}\b", name)
                if not match:
                    continue
                extension = os.path.splitext(name)[1]
                new_name = f"{prefix}{match.group()}{extension}"
                FilenameManager._plan_rename(root, name, new_name, changes, taken)
        return changes

    @staticmethod
    def plan_flatten(folder_path):
        """파일 1개만 들어 있는 폴더의 파일을 상위로 올리고 빈 폴더를 지우는 계획."""
        changes = []
        if not folder_path:
            return changes
        taken = set()
        for root, dirs, files in os.walk(folder_path, topdown=False):
            if os.path.normcase(root) == os.path.normcase(folder_path):
                continue
            if len(files) == 1 and not dirs:
                src = os.path.join(root, files[0])
                dst = os.path.join(os.path.dirname(root), files[0])
                dst = FilenameManager._avoid_collision(dst, taken)
                taken.add(os.path.normcase(dst))
                changes.append({"type": "move", "src": src, "dst": dst})
                changes.append({"type": "rmdir", "src": root})
        return changes

    # ---------- 적용(apply) ----------

    @staticmethod
    def apply(changes):
        """계획된 변경 목록을 순서대로 적용. (성공 건수, 오류 목록) 반환."""
        done = 0
        errors = []
        for change in changes:
            try:
                kind = change["type"]
                if kind == "delete":
                    os.remove(change["src"])
                elif kind == "rename":
                    os.rename(change["src"], change["dst"])
                elif kind == "move":
                    shutil.move(change["src"], change["dst"])
                elif kind == "rmdir":
                    os.rmdir(change["src"])
                done += 1
            except OSError as exc:
                errors.append(f"{change['src']}: {exc}")
        return done, errors

    # ---------- 내부 도우미 ----------

    @staticmethod
    def _plan_rename(root, old_name, new_name, changes, taken):
        new_name = new_name.strip()
        # 치환 결과가 빈 이름이면 건너뛴다 (예: 단어 제거로 이름 전체가 사라지는 경우)
        if not new_name or new_name == old_name:
            return
        src = os.path.join(root, old_name)
        dst = os.path.join(root, new_name)
        # 대소문자만 바뀌는 경우는 Windows에서 자기 자신과 충돌로 보이므로 그대로 허용
        if os.path.normcase(dst) != os.path.normcase(src):
            dst = FilenameManager._avoid_collision(dst, taken)
        taken.add(os.path.normcase(dst))
        changes.append({"type": "rename", "src": src, "dst": dst})

    @staticmethod
    def _avoid_collision(dst, taken):
        if not os.path.exists(dst) and os.path.normcase(dst) not in taken:
            return dst
        base, ext = os.path.splitext(dst)
        counter = 1
        while True:
            candidate = f"{base}_{counter}{ext}"
            if not os.path.exists(candidate) and os.path.normcase(candidate) not in taken:
                return candidate
            counter += 1
