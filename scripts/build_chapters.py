#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「章节结构」写进数学二 / 408 的计划 JSON，并把正文里的教材指向改对。

教材口径：
    数学二  高数：武忠祥《高等数学辅导讲义》6 章
            线代：李永乐《线性代数辅导讲义》6 章
    408     王道考研四本单科书：数据结构 8 章 / 计组 7 章 / 操作系统 5 章 / 计网 6 章

写入字段：plan["course"] = {"title": ..., "books": [{"id","name","book","chapters":[{id,name}]}]}
网页「单科今日」右侧和「进度统计」按这个结构勾选章节；笔记库总览也列同一份表。

同时把数学二正文里的「同济《高等数学》…」改成「武忠祥讲义 第 N 章（同济 x.y）」，
章节号按原书章节对应，节号保留同济教材的，方便对照。

运行：python3 scripts/build_chapters.py  然后 python3 build_v2.py / build_obsidian_vault.py
幂等：重复跑结果一致。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

MATH2_COURSE = {
    "title": "武忠祥《高等数学辅导讲义》+ 李永乐《线性代数辅导讲义》",
    "books": [
        {"id": "gaoshu", "name": "高等数学", "short": "高数", "book": "武忠祥 高等数学辅导讲义", "chapters": [
            {"id": "m1", "name": "第 1 章 函数、极限、连续"},
            {"id": "m2", "name": "第 2 章 一元函数微分学"},
            {"id": "m3", "name": "第 3 章 一元函数积分学"},
            {"id": "m4", "name": "第 4 章 多元函数微分学"},
            {"id": "m5", "name": "第 5 章 二重积分"},
            {"id": "m6", "name": "第 6 章 常微分方程"},
        ]},
        {"id": "xiandai", "name": "线性代数", "short": "线代", "book": "李永乐 线性代数辅导讲义", "chapters": [
            {"id": "l1", "name": "第 1 章 行列式"},
            {"id": "l2", "name": "第 2 章 矩阵"},
            {"id": "l3", "name": "第 3 章 向量"},
            {"id": "l4", "name": "第 4 章 线性方程组"},
            {"id": "l5", "name": "第 5 章 特征值与特征向量"},
            {"id": "l6", "name": "第 6 章 二次型"},
        ]},
    ],
}

CS408_COURSE = {
    "title": "王道考研 四本单科书（数据结构 / 计组 / 操作系统 / 计网）",
    "books": [
        {"id": "ds", "name": "数据结构", "short": "数据结构", "book": "王道《数据结构》", "chapters": [
            {"id": "ds1", "name": "第 1 章 绪论"},
            {"id": "ds2", "name": "第 2 章 线性表"},
            {"id": "ds3", "name": "第 3 章 栈、队列和数组"},
            {"id": "ds4", "name": "第 4 章 串"},
            {"id": "ds5", "name": "第 5 章 树与二叉树"},
            {"id": "ds6", "name": "第 6 章 图"},
            {"id": "ds7", "name": "第 7 章 查找"},
            {"id": "ds8", "name": "第 8 章 排序"},
        ]},
        {"id": "co", "name": "计算机组成原理", "short": "计组", "book": "王道《计算机组成原理》", "chapters": [
            {"id": "co1", "name": "第 1 章 计算机系统概述"},
            {"id": "co2", "name": "第 2 章 数据的表示和运算"},
            {"id": "co3", "name": "第 3 章 存储系统"},
            {"id": "co4", "name": "第 4 章 指令系统"},
            {"id": "co5", "name": "第 5 章 中央处理器"},
            {"id": "co6", "name": "第 6 章 总线"},
            {"id": "co7", "name": "第 7 章 输入/输出系统"},
        ]},
        {"id": "os", "name": "操作系统", "short": "OS", "book": "王道《计算机操作系统》", "chapters": [
            {"id": "os1", "name": "第 1 章 操作系统概述"},
            {"id": "os2", "name": "第 2 章 进程与线程"},
            {"id": "os3", "name": "第 3 章 内存管理"},
            {"id": "os4", "name": "第 4 章 文件管理"},
            {"id": "os5", "name": "第 5 章 输入/输出管理"},
        ]},
        {"id": "net", "name": "计算机网络", "short": "计网", "book": "王道《计算机网络》", "chapters": [
            {"id": "net1", "name": "第 1 章 计算机网络体系结构"},
            {"id": "net2", "name": "第 2 章 物理层"},
            {"id": "net3", "name": "第 3 章 数据链路层"},
            {"id": "net4", "name": "第 4 章 网络层"},
            {"id": "net5", "name": "第 5 章 传输层"},
            {"id": "net6", "name": "第 6 章 应用层"},
        ]},
    ],
}


TONGJI_TO_WU = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 6, 9: 4, 10: 5}


def rewrite_reading(text: str, short: str, is_gaoshu: bool) -> str:
    """把正文里的教材指向改成 武忠祥 / 李永乐 讲义，节号仍标同济，便于对照。

    兼容两种输入：原始「同济《高等数学》第 1 章 1.1–1.2」和已改写过的
    「武忠祥讲义 第 1 章（同济 1.1–1.2）」，重复跑结果一致。
    """
    if not text:
        return text
    m = re.match(r"^(武忠祥讲义|李永乐线代讲义)\s+第\s*(\d+)\s*章(?:（同济\s*(.+)）)?$", text)
    if m:
        book, _old, section = m.group(1), m.group(2), m.group(3) or ""
        short = book
    else:
        if "同济" not in text:
            return text
        section = text.replace("同济《高等数学》", "").replace("同济《线性代数》", "").replace("同济", "").strip()
        section = re.sub(r"^第\s*\d+\s*章\s*", "", section).strip()
    tongji_ch = None
    m2 = re.search(r"第\s*(\d+)\s*章", text)
    if m2:
        tongji_ch = int(m2.group(1))
    else:
        m3 = re.search(r"(?<![\d.])(\d+)\.(\d+)", section or text)
        if m3:
            tongji_ch = int(m3.group(1))
    ch = TONGJI_TO_WU.get(tongji_ch, tongji_ch) if (is_gaoshu and tongji_ch) else tongji_ch
    if ch is None:
        return f"{short} · {section}" if section else short
    if not section:
        return f"{short} 第 {ch} 章"
    return f"{short} 第 {ch} 章（同济 {section}）"


def apply_course(path: Path, course: dict, subject: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["course"] = course
    if subject == "math":
        for w in data["weeks"]:
            weeks = w["week"]
            short = "武忠祥讲义" if weeks <= 7 else ("李永乐线代讲义" if weeks <= 10 else "讲义")
            for d in w["days"]:
                d["reading"] = rewrite_reading(d.get("reading") or "", short, weeks <= 7)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = sum(len(b["chapters"]) for b in course["books"])
    print(f"  + {path.name}：{len(course['books'])} 本 / {n} 章")


def main() -> int:
    for name, course, subject in (
        ("math2-2028.json", MATH2_COURSE, "math"),
        ("cs408-2028.json", CS408_COURSE, "cs408"),
    ):
        p = DATA / name
        if not p.exists():
            print(f"[x] 缺少 {name}", file=sys.stderr)
            return 1
        apply_course(p, course, subject)
    return 0


if __name__ == "__main__":
    sys.exit(main())
