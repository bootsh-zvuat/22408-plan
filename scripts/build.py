#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一条命令重建全部产物。

顺序：英语 / 政治计划 → 阶段 → 章节 → 网页（含 deploy）→ 笔记库 → Excel。

    python3 scripts/build.py              # 全部重建（Excel 缺 openpyxl 时自动跳过）
    python3 scripts/build.py --skip-excel # 不重建 Excel
    python3 scripts/build.py --only web   # 只重打包网页（改了模板 / JSON 后最快）

Excel 需要 openpyxl：系统 python3 没装时用带 openpyxl 的解释器跑，
或者单独执行 `python3 scripts/build_plan_v2.py`。
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
BASE = SCRIPTS.parent

STEPS = [
    ("英语计划", "gen_english_plan.py"),
    ("政治计划", "gen_politics_plan.py"),
    ("阶段配置", "build_phases.py"),
    ("章节表", "build_chapters.py"),
    ("网页 + 部署包", "build_v2.py"),
    ("Obsidian 笔记库", "build_obsidian_vault.py"),
    ("Excel", "build_plan_v2.py"),
]

ONLY = {
    "web": [("网页 + 部署包", "build_v2.py")],
    "data": [("英语计划", "gen_english_plan.py"), ("政治计划", "gen_politics_plan.py"),
             ("阶段配置", "build_phases.py"), ("章节表", "build_chapters.py")],
    "vault": [("Obsidian 笔记库", "build_obsidian_vault.py")],
    "excel": [("Excel", "build_plan_v2.py")],
}


def run(label: str, script: str) -> bool:
    print(f"\n[{label}] {script}")
    r = subprocess.run([sys.executable, str(SCRIPTS / script)], cwd=BASE)
    if r.returncode != 0:
        print(f"\n[x] {script} 失败（exit {r.returncode}）", file=sys.stderr)
        return False
    return True


def main(argv: list[str]) -> int:
    skip_excel = "--skip-excel" in argv
    only = None
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 >= len(argv) or argv[i + 1] not in ONLY:
            print(f"[x] --only 可选：{', '.join(ONLY)}", file=sys.stderr)
            return 2
        only = argv[i + 1]

    steps = ONLY[only] if only else STEPS
    have_openpyxl = importlib.util.find_spec("openpyxl") is not None

    for label, script in steps:
        if script == "build_plan_v2.py" and (skip_excel or not have_openpyxl):
            reason = "--skip-excel" if skip_excel else "当前解释器没有 openpyxl"
            print(f"\n[跳过] {label}（{reason}）")
            if not skip_excel and not have_openpyxl:
                print("        需要时用装了 openpyxl 的 python3 单独跑 scripts/build_plan_v2.py")
            continue
        if not run(label, script):
            return 1

    print("\n完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
