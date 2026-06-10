import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from FilenameManager import FilenameManager

# 작업 정의: 이름 → (입력 필드 목록, 계획 함수, 파괴적 여부)
# 필드: (라벨, 키, 필수 여부)
OPERATIONS = {
    "단어가 포함된 파일 삭제": {
        "fields": [("찾을 단어", "word", True)],
        "plan": lambda folder, v: FilenameManager.plan_remove_files(folder, v["word"]),
        "destructive": True,
    },
    "파일·폴더명에서 단어 제거": {
        "fields": [("제거할 단어", "word", True)],
        "plan": lambda folder, v: FilenameManager.plan_replace(folder, v["word"], ""),
        "destructive": False,
    },
    "파일·폴더명에서 단어 바꾸기": {
        "fields": [("찾을 단어", "word", True), ("바꿀 단어", "replacement", False)],
        "plan": lambda folder, v: FilenameManager.plan_replace(folder, v["word"], v["replacement"]),
        "destructive": False,
    },
    "파일·폴더명 대문자로 변경": {
        "fields": [],
        "plan": lambda folder, v: FilenameManager.plan_uppercase(folder),
        "destructive": False,
    },
    "7자리 숫자 기준 파일명 정규화": {
        "fields": [("앞에 붙일 단어", "prefix", False)],
        "plan": lambda folder, v: FilenameManager.plan_seven_digits(folder, v["prefix"]),
        "destructive": False,
    },
    "파일 1개뿐인 폴더 정리": {
        "fields": [],
        "plan": lambda folder, v: FilenameManager.plan_flatten(folder),
        "destructive": False,
    },
    "쓰레기 파일 삭제 (.txt, .url)": {
        "fields": [],
        "plan": lambda folder, v: FilenameManager.plan_remove_by_extension(folder),
        "destructive": True,
    },
    "지정 크기 미만 파일 삭제": {
        "fields": [("기준 크기 (KB)", "size_kb", True)],
        "plan": lambda folder, v: FilenameManager.plan_remove_small_files(folder, v["size_kb"]),
        "destructive": True,
    },
    "모든 파일을 한 폴더로 모으기": {
        "fields": [],
        "needs_dest": True,
        "plan": lambda folder, v: FilenameManager.plan_collect_files(folder, v["dest"]),
        "destructive": False,
    },
}

ACTION_LABELS = {
    "delete": "삭제",
    "rename": "이름 변경",
    "move": "이동",
    "rmdir": "폴더 삭제",
}


class App:
    def __init__(self, root):
        self.root = root
        self.folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.operation = tk.StringVar(value=next(iter(OPERATIONS)))
        self.field_vars = {}
        self.plan = []

        self._build_ui()
        self._on_operation_change()

    # ---------- UI 구성 ----------

    def _build_ui(self):
        self.root.title("파일 관리기")
        self.root.minsize(640, 480)
        self._center_window(720, 540)

        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")

        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(3, weight=1)

        # 1. 폴더 선택
        folder_frame = ttk.LabelFrame(main, text=" 1. 대상 폴더 ", padding=8)
        folder_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        folder_frame.columnconfigure(0, weight=1)

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder, state="readonly")
        folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(folder_frame, text="찾아보기…", command=self._browse).grid(row=0, column=1)

        # 2. 작업 선택 + 입력 필드
        op_frame = ttk.LabelFrame(main, text=" 2. 작업 ", padding=8)
        op_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        op_frame.columnconfigure(1, weight=1)

        ttk.Label(op_frame, text="작업 종류").grid(row=0, column=0, sticky="w", padx=(0, 8))
        combo = ttk.Combobox(
            op_frame,
            textvariable=self.operation,
            values=list(OPERATIONS),
            state="readonly",
        )
        combo.grid(row=0, column=1, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda e: self._on_operation_change())

        self.fields_frame = ttk.Frame(op_frame)
        self.fields_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.fields_frame.columnconfigure(1, weight=1)

        # 3. 버튼
        button_frame = ttk.Frame(main)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.preview_button = ttk.Button(button_frame, text="미리보기", command=self._preview)
        self.preview_button.pack(side="left")
        self.apply_button = ttk.Button(
            button_frame, text="적용", command=self._apply, state="disabled"
        )
        self.apply_button.pack(side="left", padx=(8, 0))
        self.status = ttk.Label(button_frame, text="폴더를 선택하고 미리보기를 누르세요.")
        self.status.pack(side="left", padx=(16, 0))

        # 4. 미리보기 목록
        preview_frame = ttk.LabelFrame(main, text=" 3. 미리보기 ", padding=8)
        preview_frame.grid(row=3, column=0, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        columns = ("action", "src", "dst")
        self.tree = ttk.Treeview(preview_frame, columns=columns, show="headings")
        self.tree.heading("action", text="작업")
        self.tree.heading("src", text="대상")
        self.tree.heading("dst", text="변경 후")
        self.tree.column("action", width=80, stretch=False, anchor="center")
        self.tree.column("src", width=280)
        self.tree.column("dst", width=280)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    @staticmethod
    def _display_path(path, base):
        """대상 폴더 안이면 상대 경로, 밖(출력 폴더 등)이면 전체 경로로 표시."""
        rel = os.path.relpath(path, base)
        return path if rel.startswith("..") else rel

    def _center_window(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _on_operation_change(self):
        for child in self.fields_frame.winfo_children():
            child.destroy()
        self.field_vars = {}

        op = OPERATIONS[self.operation.get()]
        for i, (label, key, _required) in enumerate(op["fields"]):
            ttk.Label(self.fields_frame, text=label).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=(4, 0)
            )
            var = tk.StringVar()
            var.trace_add("write", lambda *a: self._invalidate_plan())
            ttk.Entry(self.fields_frame, textvariable=var).grid(
                row=i, column=1, sticky="ew", pady=(4, 0)
            )
            self.field_vars[key] = var

        # 출력 폴더가 필요한 작업이면 선택 행 추가
        self.dest_folder.set("")
        if op.get("needs_dest"):
            row = len(op["fields"])
            ttk.Label(self.fields_frame, text="출력 폴더").grid(
                row=row, column=0, sticky="w", padx=(0, 8), pady=(4, 0)
            )
            ttk.Entry(
                self.fields_frame, textvariable=self.dest_folder, state="readonly"
            ).grid(row=row, column=1, sticky="ew", pady=(4, 0))
            ttk.Button(
                self.fields_frame, text="찾아보기…", command=self._browse_dest
            ).grid(row=row, column=2, padx=(8, 0), pady=(4, 0))

        self._invalidate_plan()

    # ---------- 동작 ----------

    def _browse(self):
        path = filedialog.askdirectory(title="대상 폴더 선택")
        if path:
            self.folder.set(os.path.normpath(path))
            self._invalidate_plan()

    def _browse_dest(self):
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if path:
            self.dest_folder.set(os.path.normpath(path))
            self._invalidate_plan()

    def _invalidate_plan(self):
        """폴더·작업·입력이 바뀌면 이전 미리보기는 무효."""
        self.plan = []
        self.apply_button.config(state="disabled")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status.config(text="미리보기를 눌러 변경 내용을 확인하세요.")

    def _validate_inputs(self):
        folder = self.folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("폴더 없음", "먼저 대상 폴더를 선택하세요.")
            return None, None
        op = OPERATIONS[self.operation.get()]
        values = {key: var.get() for key, var in self.field_vars.items()}
        for label, key, required in op["fields"]:
            if required and not values[key]:
                messagebox.showwarning("입력 필요", f"'{label}' 값을 입력하세요.")
                return None, None
        if op.get("needs_dest"):
            dest = self.dest_folder.get()
            if not dest or not os.path.isdir(dest):
                messagebox.showwarning("폴더 없음", "출력 폴더를 선택하세요.")
                return None, None
            values["dest"] = dest
        return folder, values

    def _preview(self):
        folder, values = self._validate_inputs()
        if folder is None:
            return

        op = OPERATIONS[self.operation.get()]
        self.plan = op["plan"](folder, values)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for change in self.plan:
            src = self._display_path(change["src"], folder)
            dst = self._display_path(change["dst"], folder) if "dst" in change else ""
            self.tree.insert(
                "", "end", values=(ACTION_LABELS[change["type"]], src, dst)
            )

        count = len(self.plan)
        if count:
            self.status.config(text=f"변경 예정 {count}건")
            self.apply_button.config(state="normal")
        else:
            self.status.config(text="변경할 항목이 없습니다.")
            self.apply_button.config(state="disabled")

    def _apply(self):
        if not self.plan:
            return

        op = OPERATIONS[self.operation.get()]
        count = len(self.plan)
        if op["destructive"]:
            ok = messagebox.askyesno(
                "삭제 확인",
                f"{count}건의 파일이 영구 삭제됩니다.\n휴지통으로 가지 않습니다. 계속할까요?",
                icon="warning",
            )
        else:
            ok = messagebox.askyesno("적용 확인", f"{count}건의 변경을 적용할까요?")
        if not ok:
            return

        done, errors = FilenameManager.apply(self.plan)
        self._invalidate_plan()

        if errors:
            detail = "\n".join(errors[:10])
            if len(errors) > 10:
                detail += f"\n… 외 {len(errors) - 10}건"
            messagebox.showwarning(
                "일부 실패", f"성공 {done}건, 실패 {len(errors)}건\n\n{detail}"
            )
        else:
            messagebox.showinfo("완료", f"{done}건 적용 완료")
        self.status.config(text=f"적용 완료: 성공 {done}건, 실패 {len(errors)}건")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
