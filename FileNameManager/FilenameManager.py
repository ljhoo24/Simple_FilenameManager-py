import os
import re
import shutil
import stat


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
    def plan_remove_small_files(folder_path, size_kb):
        """지정 크기(KB) 미만 파일 전체 삭제 계획."""
        changes = []
        if not folder_path:
            return changes
        try:
            limit = float(size_kb) * 1024
        except (TypeError, ValueError):
            return changes
        if limit <= 0:
            return changes
        for root, _dirs, files in os.walk(folder_path):
            for name in files:
                path = os.path.join(root, name)
                try:
                    if os.path.getsize(path) < limit:
                        changes.append({"type": "delete", "src": path})
                except OSError:
                    pass
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

    @staticmethod
    def plan_collect_files(folder_path, dest_folder):
        """입력 폴더를 재귀 탐색해 모든 파일을 출력 폴더 한곳으로 모으고,
        비게 된 하위 폴더를 삭제하는 계획."""
        changes = []
        if not folder_path or not dest_folder:
            return changes
        dest_norm = os.path.normcase(os.path.abspath(dest_folder))
        taken = set()
        for root, _dirs, files in os.walk(folder_path):
            # 이미 출력 폴더 바로 안에 있는 파일은 옮길 필요 없음
            if os.path.normcase(os.path.abspath(root)) == dest_norm:
                continue
            for name in files:
                src = os.path.join(root, name)
                dst = FilenameManager._avoid_collision(os.path.join(dest_folder, name), taken)
                taken.add(os.path.normcase(dst))
                changes.append({"type": "move", "src": src, "dst": dst})
        moved = {os.path.normcase(os.path.abspath(c["src"])) for c in changes}
        FilenameManager._plan_removable_dirs(folder_path, moved, dest_norm, changes)
        return changes

    @staticmethod
    def plan_remove_empty_dirs(folder_path):
        """빈 하위 폴더 전체 삭제 계획 (빈 폴더만 담고 있는 폴더 포함)."""
        changes = []
        if not folder_path:
            return changes
        FilenameManager._plan_removable_dirs(folder_path, frozenset(), None, changes)
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
                    try:
                        os.remove(change["src"])
                    except PermissionError:
                        # 읽기 전용 파일이면 속성 해제 후 재시도
                        os.chmod(change["src"], stat.S_IWRITE)
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
    def _plan_removable_dirs(folder_path, moved, protect_norm, changes):
        """이동(moved) 적용 후 비게 되는 하위 폴더의 rmdir 계획을 changes에 추가.

        protect_norm(출력 폴더)과 그 상위 폴더는 보존한다.
        bottom-up 순회라 깊은 폴더가 먼저 삭제된다.
        """
        base_norm = os.path.normcase(os.path.abspath(folder_path))
        removable = set()
        for root, dirs, files in os.walk(folder_path, topdown=False):
            norm = os.path.normcase(os.path.abspath(root))
            if norm == base_norm:
                continue
            if protect_norm and (
                norm == protect_norm or protect_norm.startswith(norm + os.sep)
            ):
                continue
            files_gone = all(
                os.path.normcase(os.path.abspath(os.path.join(root, f))) in moved
                for f in files
            )
            dirs_gone = all(
                os.path.normcase(os.path.abspath(os.path.join(root, d))) in removable
                for d in dirs
            )
            if files_gone and dirs_gone:
                removable.add(norm)
                changes.append({"type": "rmdir", "src": root})

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
