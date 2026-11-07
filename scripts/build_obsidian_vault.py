#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 math2-2028.json / cs408-2028.json 里的真实排课生成成 Obsidian 笔记库骨架。

用法：
    python3 build_obsidian_vault.py          # 生成/覆盖笔记，不动已有笔记内容以外的东西
    python3 build_obsidian_vault.py --force  # 同义（本脚本默认覆盖自己生成的文件）

只写这些路径，不动 html / xlsx / py / json 原件：
    .obsidian/            库配置
    _templates/           模板
    00-入口/ 01-数学二/ 02-408/ 03-错题本/ 04-每日/ 99-附件/
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE  # 笔记库根目录 = 项目根
DATA = BASE / "data"

WEEKDAY_OFFSET = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6}

KIND_META = {
    "learn":    ("学习", "abstract", "📘"),
    "practice": ("练习", "example",  "✏️"),
    "review":   ("复盘", "success",  "🔁"),
    "rest":     ("休息", "info",     "☕"),
}


# ---------------------------------------------------------------- 工具

def sanitize(name: str) -> str:
    """去掉文件名里 macOS / Obsidian 不接受的字符。"""
    return re.sub(r'[/\\:*?"<>|]', "-", name).strip()


def esc(text: str) -> str:
    """转义内容里的 [[ ，避免矩阵写法 [[1,2],[3,4]] 被 Obsidian 当成 wikilink。"""
    return str(text).replace("[[", "\\[\\[")


def bq(text: str) -> str:
    """把任意文本变成引用块（每行加 > ）。"""
    if not text:
        return ">"
    out = []
    for line in esc(text).splitlines():
        out.append(("> " + line).rstrip() if line.strip() else ">")
    return "\n".join(out)


def hardbreak(text: str) -> str:
    """单行内的换行转成 markdown 硬换行，避免被并成一段。"""
    return esc(text).replace("\r\n", "\n").replace("\n", "  \n").strip()


def stars(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    return " " + "★" * max(0, min(n, 5))


def human_minutes(total: int) -> str:
    h, m = divmod(int(total), 60)
    if h and m:
        return f"{h} 小时 {m} 分"
    if h:
        return f"{h} 小时"
    return f"{m} 分钟"


def week_dates(start: date, days):
    """返回 {day_id: date}，按 weekday 字段落位到本周对应的那天。"""
    out = {}
    for day in days:
        off = WEEKDAY_OFFSET.get(day.get("weekday", ""), 0)
        out[day["id"]] = start + timedelta(days=off)
    return out


# ---------------------------------------------------------------- 单个学习日

def render_day(day: dict, the_date: date | None) -> str:
    kind = day.get("kind", "learn")
    kind_name, callout, emoji = KIND_META.get(kind, ("学习", "note", "•"))
    minutes = day.get("minutes") or 0

    head = f"## {day.get('weekday', '')}"
    if the_date:
        head += f" · {the_date.isoformat()}"
    head += f" · {esc(day.get('title', '')).strip()}"
    lines = [head, ""]

    meta = [f"`{kind_name}`"]
    if minutes:
        meta.append(f"`{human_minutes(minutes)}`")
    if day.get("reading"):
        meta.append(f"阅读：{day['reading']}")
    lines += [" · ".join(meta), ""]

    learn = [x for x in (day.get("learn") or []) if str(x).strip()]
    if learn:
        lines += [f"> [!{callout}] 今天学什么", bq("\n".join(f"- {x}" for x in learn)), ""]

    practice = [x for x in (day.get("practice") or []) if str(x).strip()]
    if practice:
        lines += [bq("**动手**：\n" + "\n".join(f"- {x}" for x in practice)), ""]

    exercises = day.get("exercises") or []
    for i, ex in enumerate(exercises, 1):
        lines += [f"### 课后题 {i} · {ex.get('title', '')}{stars(ex.get('difficulty'))}", ""]
        if ex.get("prompt"):
            lines += [hardbreak(ex["prompt"]), ""]
        if ex.get("hint"):
            lines += [f"> [!tip]- 提示（先自己卡 3 分钟）", bq(ex["hint"]), ""]
        if ex.get("answer"):
            lines += [f"> [!success]- 参考答案（做完再对）", bq(ex["answer"]), ""]
        lines += [f"- 状态：`未做` → 做完改成 `已独立完成` / `看答案`", ""]

    checklist = [x for x in (day.get("checklist") or []) if str(x).strip()]
    if checklist:
        lines += ["**完成标准**", ""]
        lines += [f"- [ ] {esc(x)}" for x in checklist]
        lines += [""]

    return "\n".join(lines)


# ---------------------------------------------------------------- 周笔记

def render_week(meta: dict, subj_dir: str, start: date, prev_w, next_w, sibling_dir_name) -> str:
    week = meta["week"]
    days = meta.get("days") or []
    dates = week_dates(start, days)
    end = start + timedelta(days=6)

    kinds = {}
    for d in days:
        kinds[d.get("kind", "learn")] = kinds.get(d.get("kind", "learn"), 0) + 1
    rhythm = "、".join(f"{KIND_META[k][0]} {v} 天" for k, v in kinds.items() if k in KIND_META)
    total_min = sum(int(d.get("minutes") or 0) for d in days)
    n_ex = sum(len(d.get("exercises") or []) for d in days)

    fm = [
        "---",
        f"week: {week}",
        f"subject: {sibling_dir_name}",
        f"range: {start.isoformat()} ~ {end.isoformat()}",
        f"start: {start.isoformat()}",
        "tags:",
        f"  - {sibling_dir_name}",
        f"  - 第{week:02d}周",
        "---",
        "",
    ]

    body = [f"# 第 {week} 周 · {esc(meta.get('title', '')).strip()}", ""]

    nav = ["[[00-入口/首页|← 首页]]", f"[[{subj_dir}/{sibling_dir_name}总览|{sibling_dir_name}总览]]"]
    if prev_w:
        nav.append(f"[[{subj_dir}/第{prev_w['week']:02d}周 {sanitize(prev_w['title'])}|← 第 {prev_w['week']} 周]]")
    if next_w:
        nav.append(f"[[{subj_dir}/第{next_w['week']:02d}周 {sanitize(next_w['title'])}|第 {next_w['week']} 周 →]]")
    body += [" · ".join(nav), ""]

    body += [f"`{start.isoformat()} ~ {end.isoformat()}` · `{rhythm}` · `{human_minutes(total_min)}` · `{n_ex} 道课后题`", ""]

    if meta.get("goal"):
        body += ["> [!goal] 本周目标", bq(meta["goal"]), ""]

    rows = []
    if meta.get("target"):
        rows.append(("进度要求", meta["target"]))
    if meta.get("check"):
        rows.append(("验收", meta["check"]))
    rows.append(("学习日", f"{len(days)} 天，共 {human_minutes(total_min)}"))
    rows.append(("课后题", f"{n_ex} 道"))
    if rows:
        body += ["| 项 | 内容 |", "|---|---|"]
        for k, v in rows:
            cell = str(v).strip().replace("|", "\\|")
            body.append(f"| {k} | {cell} |")
        body += [""]

    body += ["---", ""]
    for d in days:
        body += [render_day(d, dates.get(d["id"])), ""]
        body += ["---", ""]

    body += ["> [!note] 怎么用这页", bq(
        "- 每天学完把对应那天的 `- [ ]` 勾掉，课后题状态从 `未做` 改掉。\n"
        "- 做错的题不要就地抄答案，记进 [[03-错题本/错题本总表|错题本]]，写错因。\n"
        "- 周日复盘：翻这一周的错题，只留 3 条下周动作。"
    ), ""]
    return "\n".join(fm + body)


# ---------------------------------------------------------------- 总览 / 首页

def render_overview(data: dict, subj_dir: str, name: str) -> str:
    weeks = data["weeks"]
    start = date.fromisoformat(data["startDate"])
    total_days = sum(len(w.get("days") or []) for w in weeks)
    total_ex = sum(len(d.get("exercises") or []) for w in weeks for d in w.get("days") or [])
    total_min = sum(int(d.get("minutes") or 0) for w in weeks for d in w.get("days") or [])

    out = [
        "---",
        f"subject: {name}",
        "tags:",
        f"  - {name}",
        "  - 总览",
        "---",
        "",
        f"# {name}总览",
        "",
        "[[00-入口/首页|← 首页]]",
        "",
        f"> [!info] {data.get('title', '')}",
        bq(
            f"- 起点：{data.get('level', '')}\n"
            f"- 全年目标：{data.get('yearGoal', '')}\n"
            f"- 本阶段目标：{data.get('goal', '')}\n"
            f"- 阶段：{(str(len(data.get('phases') or [])) + ' 段 / ' + str(sum(p['weeks'] for p in data.get('phases') or [])) + ' 周（详见「00-入口/阶段路线」）') if data.get('phases') else '—'}\n"
            f"- 资料：{data.get('tools', '')}\n"
            f"- 每天：{human_minutes(data.get('dailyMinutes') or 0)}\n"
            f"- 开始日期：{data.get('startDate', '')}\n"
            f"- 已细化：{len(weeks)} 周 / {total_days} 个日条目 / {total_ex} 道课后题 / {human_minutes(total_min)}"
        ),
        "",
    ]
    course = data.get("course")
    if course:
        out += ["## 章节进度（按教材勾）", "", f"{course.get('title', '')}", ""]
        for b in course.get("books") or []:
            out += [f"**{b['name']}**（{b['book']}）", ""]
            out += [f"- [ ] {ch['name']}" for ch in b.get("chapters") or []]
            out.append("")
    out += [
        "## 周计划",
        "",
        "| 周 | 章节 | 日期 | 日数 | 题数 | 时长 |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for w in weeks:
        wk = w["week"]
        s = start + timedelta(days=7 * (wk - 1))
        e = s + timedelta(days=6)
        days = w.get("days") or []
        ex = sum(len(d.get("exercises") or []) for d in days)
        mn = sum(int(d.get("minutes") or 0) for d in days)
        title = sanitize(w["title"])
        out.append(
            f"| {wk} | [[{subj_dir}/第{wk:02d}周 {title}\\|{w['title'].strip()}]] | "
            f"{s.strftime('%m-%d')}~{e.strftime('%m-%d')} | {len(days)} | {ex} | {human_minutes(mn)} |"
        )
    out += ["", "---", "", "> [!tip] 改计划", bq(
        "笔记是从 `math2-2028.json` / `cs408-2028.json` 生成的。要改内容改 JSON，"
        "然后重跑 `python3 build_obsidian_vault.py`；手写在周笔记里的批注会被覆盖，"
        "自己的总结请新建笔记或用 `_templates/学习笔记.md`。"
    ), ""]
    return "\n".join(out)


def render_phase_note(data, ph, subj_dir, name, prev_ph, next_ph) -> str:
    """单阶段笔记：英语 / 政治这类周数多的科目按阶段建笔记，不按周。"""
    out = [
        "---",
        f"subject: {name}",
        f"phase: {ph['id']}",
        f"range: {ph['start']} ~ {ph['end']}",
        "tags:",
        "  - " + name,
        "  - 阶段",
        "---",
        "",
        f"# 第 {ph['seq']} 阶段 · {ph['short']}",
        "",
        f"[[00-入口/首页|← 首页]] · [[{subj_dir}/{name}总览|{name}总览]]" +
        (f" · [[{subj_dir}/第{prev_ph['seq']:02d}阶段 {sanitize(prev_ph['short'])}|← 上一段]]" if prev_ph else "") +
        (f" · [[{subj_dir}/第{next_ph['seq']:02d}阶段 {sanitize(next_ph['short'])}|下一段 →]]" if next_ph else ""),
        "",
        f"`{ph['start']} ~ {ph['end']}` · `{ph['weeks']} 周` · 每周 {ph.get('hoursPerWeek', '')}",
        "",
        "> [!goal] 阶段目标",
        bq(ph.get("goal", "")),
        "",
    ]
    mainline = ph.get("mainline") or []
    if mainline:
        out += ["## 主线", "", "| 模块 | 周数 | 内容 |", "|---|---:|---|"]
        for m in mainline:
            m_name = str(m["name"]).replace("|", "\\|")
            m_body = str(m["content"]).replace("|", "\\|")
            out.append(f"| {m_name} | {m['weeks']} | {m_body} |")
        out.append("")
    if ph.get("outputs"):
        out += ["## 阶段产出", ""] + [f"- {x}" for x in ph["outputs"]] + [""]
    if ph.get("checkpoints"):
        out += ["## 检查点", "", "| 日期 | 检查点 | 达标线 |", "|---|---|---|"]
        for c in ph["checkpoints"]:
            out.append(f"| {c['date']} | {c['what']} | {c['pass']} |")
        out.append("")
    if ph.get("exit"):
        out += ["## 进入下一阶段的门槛", ""] + [f"- [ ] {x}" for x in ph["exit"]] + [""]
    if ph.get("blocks"):
        out += ["## 周骨架", "", "| 周次块 | 周数 | 要做什么 |", "|---|---:|---|"]
        for b in ph["blocks"]:
            out.append(f"| {b['name']} | {b['weeks']} | {b['content']} |")
        out.append("")
    out += ["---", "", "> [!tip] 每天练什么", bq(
        "- 逐日任务在网页 `22408每日计划.html` 的「今日」里，勾完成标准算打卡。\n"
        "- 这一页只放阶段级的判断：目标、产出、检查点、门槛。\n"
        "- 复盘写在 `04-每日/`，错题/生词记在 `03-错题本/`。"
    ), ""]
    return "\n".join(out)


def render_overview_phased(data, subj_dir, name) -> str:
    weeks = data.get("weeks") or []
    phases = data.get("phases") or []
    total_days = sum(len(w.get("days") or []) for w in weeks)
    total_min = sum(int(d.get("minutes") or 0) for w in weeks for d in w.get("days") or [])
    out = [
        "---",
        f"subject: {name}",
        "tags:",
        f"  - {name}",
        "  - 总览",
        "---",
        "",
        f"# {name}总览",
        "",
        "[[00-入口/首页|← 首页]]",
        "",
        f"> [!info] {data.get('title', '')}",
        bq(
            f"- 起点：{data.get('level', '')}\n"
            f"- 全年目标：{data.get('yearGoal', '')}\n"
            f"- 资料：{data.get('tools', '')}\n"
            f"- 每天：{human_minutes(data.get('dailyMinutes') or 0)}\n"
            f"- 开始日期：{data.get('startDate', '')}\n"
            f"- 总计：{len(weeks)} 周 / {total_days} 个日条目 / {human_minutes(total_min)}"
        ),
        "",
        "## 阶段",
        "",
        "| 阶段 | 时间 | 周数 | 目标 | 笔记 |",
        "|---|---|---:|---|---|",
    ]
    for ph in phases:
        out.append(
            f"| 第 {ph['seq']} 阶段 · {ph['short']} | {ph['start']} ~ {ph['end']} | {ph['weeks']} | "
            f"{(ph.get('goal') or '')[:34]}… | [[{subj_dir}/第{ph['seq']:02d}阶段 {sanitize(ph['short'])}\\|阶段笔记]] |"
        )
    out += ["", "---", "", "> [!tip] 怎么用", bq(
        "这一科的周数多、每天内容重复（单词 / 背诵），所以笔记按**阶段**建，不按周建。\n"
        "每天的清单在网页里勾，阶段结束后回这一页对照「检查点」和「门槛」。"
    ), ""]
    return "\n".join(out)


def render_phases(datasets) -> str:
    """00-入口/阶段路线.md：四科阶段的总览页。"""
    out = [
        "---",
        "tags:",
        "  - 首页",
        "  - 阶段",
        "---",
        "",
        "# 全年阶段路线",
        "",
        "[[00-入口/首页|← 首页]]",
        "",
        "> [!info] 阶段 = 时间 + 目标 + 主线 + 门槛",
        bq(
            "数学二 / 408 / 英语 共用一条四段时间线（2026-11-09 → 2027-12-26，初试 2027-12-25）；"
            "政治单独一条：11 月启动，跟着肖八 → 肖四。\n"
            "细到天的排期只做当前阶段，后面阶段先锁周数与主线，等前一阶段实测成绩出来再细化。"
        ),
        "",
        "## 四科的总览",
        "",
        "| 科目 | 阶段数 | 时间 | 周数 |",
        "|---|---:|---|---:|",
    ]
    for name, data, subj_dir in datasets:
        phs = data.get("phases") or []
        if not phs:
            continue
        out.append(f"| [[{subj_dir}/{name}总览\\|{name}]] | {len(phs)} | {phs[0]['start']} ~ {phs[-1]['end']} | "
                   f"{sum(p['weeks'] for p in phs)} |")
    for name, data, subj_dir in datasets:
        phs = data.get("phases") or []
        if not phs:
            continue
        out += ["", "---", "", f"## {name}", "",
                "| 阶段 | 时间 | 周数 | 阶段目标 |", "|---|---|---:|---|"]
        for ph in phs:
            goal = (ph.get('goal') or '').replace('|', '\\|')
            out.append(f"| 第 {ph['seq']} 阶段 · {ph['short']} | {ph['start']} ~ {ph['end']} | {ph['weeks']} | "
                       f"{goal} |")
        out += ["", "**进入下一阶段的门槛**", ""]
        for ph in phs:
            for e in ph.get("exit") or []:
                out.append(f"- [ ] （{ph['short']}）{e}")
        out += ["", f"看细节：[[{subj_dir}/{name}总览|{name}总览]]"]
    out += ["", "---", "", "> [!tip] 怎么推进", bq(
        "- 门槛制：上一阶段门槛没过，先补 1–2 周再进下一段，别两段平行推进。\n"
        "- 网页顶部有「当前阶段」，阶段按固定日期自动切换，历史勾选不会丢。\n"
        "- 要改阶段时间或目标：改 `build_phases.py` → `python3 build_phases.py` → 再重建网页和笔记。"
    ), ""]
    return "\n".join(out)


def render_index(datasets) -> str:
    rows = []
    for name, data, subj_dir in datasets:
        weeks = data["weeks"]
        n_days = sum(len(w.get("days") or []) for w in weeks)
        n_ex = sum(len(d.get("exercises") or []) for w in weeks for d in w.get("days") or [])
        n_min = sum(int(d.get("minutes") or 0) for w in weeks for d in w.get("days") or [])
        rows.append((name, subj_dir, len(weeks), n_days, n_ex, n_min))

    out = [
        "---",
        "tags:",
        "  - 首页",
        "---",
        "",
        "# 22408 复习 · 笔记库首页",
        "",
        "2028 考研：数学二 + 408。全年 4 个阶段 / 59 周，2026-11-09 开始，初试 2027-12-25。",
        "",
        "> [!question] 现在走到哪一段",
        "> 打开 [[00-入口/阶段路线|阶段路线]]：一轮基础 → 二轮基础 → 强化 → 真题，每段都有目标和进入门槛。",
        "> 细到天的排期只做当前阶段，后面的阶段先锁周数。",
        "",
        "> [!abstract] 两个入口",
        "> - **要打卡 / 看今天该学什么** → 双击工作区里的 `22408每日计划.html`（带进度、错题、导出）。",
        "> - **要整理 / 手写推导 / 复盘** → 就在这个库里，用下面的周笔记。",
        "> 两边的章节地图是同一张，别各记一份。",
        "",
        "## 各科总览",
        "",
        "| 科目 | 细化周数 | 日条目 | 课后题 | 总时长 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, subj_dir, nw, nd, ne, nm in rows:
        out.append(f"| [[{subj_dir}/{name}总览\\|{name}]] | {nw} | {nd} | {ne} | {human_minutes(nm)} |")
    out += ["", "## 常用入口", ""]
    out += [
        f"- [[{d[1]}/{d[0]}总览|{d[0]}总览]]" for d in rows
    ]
    out += [
        "- [[00-入口/阶段路线|阶段路线（四科 + 门槛）]]",
        "- [[03-错题本/错题本总表|错题本总表]]",
        "- [[04-每日/每日说明|每日笔记怎么用]]",
        "- [[00-入口/项目说明|项目说明（文件、脚本、部署）]]",
        "- [[00-入口/库设置说明|库设置说明]]",
        "",
        "## 节奏",
        "",
        "| | 内容 | 时间段 |",
        "|---|---|---|",
        "| 全年 | 四段：一轮基础 18 周 → 二轮基础 15 周 → 强化 13 周 → 真题 13 周 | 2026-11-09 ~ 2027-12-26 |",
        "| 数学二 | 高数 1–7 周，线代 8–10 周，错题 11 周，总测 12 周 | 2026-11-09 ~ 2027-01-31 |",
        "| 408 | 数据结构 1–5 周，计组 6–9 周，操作系统 10–11 周，计网 12 周 | 同期 |",
        "| 英语 | 单词 11 月起不停；3 月开阅读、7 月开题型、10 月开作文 | 2026-11-09 ~ 2027-12-26 |",
        "| 政治 | 11 月启动：核心考点 + 肖八 → 12 月肖四背诵 | 2027-11-01 ~ 2027-12-26 |",
        "| 每日 | 新课约 2 小时 + 当天课后题 | 周一至周六 |",
        "| 周日 | 复盘 + 章节测（检查点周为 100 分限时测） | 周日 |",
        "",
        "> [!warning] 手写批注会被覆盖",
        "> `01-数学二/`、`02-408/` 下的周笔记由脚本生成，重跑会覆盖。"
        "自己的总结请用 `_templates/学习笔记.md` 新建，或者直接写在 `03-错题本/`。",
        "",
    ]
    return "\n".join(out)


# ---------------------------------------------------------------- 静态笔记

def tpl(text: str) -> str:
    """模板：去掉行尾多余空格（frontmatter 里 `week: ` 这类会变 null）。"""
    return "\n".join(line.rstrip() for line in text.splitlines())


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path.relative_to(ROOT)}")


TEMPLATE_DAILY = """---
date: {{date:YYYY-MM-DD}}
weekday: {{date:dddd}}
tags:
  - 每日
---

# {{date:YYYY-MM-DD}} · {{date:dddd}}

[[00-入口/首页|首页]]

## 今日任务
- [ ] 数学二：
- [ ] 408：

## 学习记录

### 数学二
| 项 | 内容 |
|---|---|
| 章节 |  |
| 用时 |  min |
| 卡在哪 |  |

### 408
| 项 | 内容 |
|---|---|
| 章节 |  |
| 用时 |  min |
| 卡在哪 |  |

## 课后题
| 题号 | 独立完成 | 错因 |
|---|---|---|
|  |  |  |

## 记进错题本
- 

## 明天要先处理
- 
"""

TEMPLATE_MISTAKE = """---
date: {{date:YYYY-MM-DD}}
subject: 
chapter: 
source: 
status: 未掌握
tags:
  - 错题
---

# 错题 · {{title}}

## 题目

```

```

## 我当时的做法

```

```

## 错因归类
- [ ] 概念不清
- [ ] 计算失误
- [ ] 思路卡壳
- [ ] 时间不够
- [ ] 审题偏差

## 正确解法

```

```

## 一句话教训


## 复盘
- {{date:YYYY-MM-DD}} 首次记录
- 
"""

TEMPLATE_NOTE = """---
topic: {{title}}
subject: 
chapter: 
created: {{date:YYYY-MM-DD}}
tags:
  - 学习笔记
---

# {{title}}

[[00-入口/首页|首页]]

## 这节要解决什么


## 定义 / 定理（用自己的话）

| 概念 | 我的表述 | 条件 | 反例 |
|---|---|---|---|
|  |  |  |  |

## 推导（手写拍照放 99-附件）


## 典型题
| 题 | 关键一步 | 结论 | 是否独立做出 |
|---|---|---|---|
|  |  |  |  |

## 易错点
- 

## 自测（合上书能不能写出来）
- [ ] 复述定义
- [ ] 独立推一遍
- [ ] 举一个反例
"""

TEMPLATE_WEEKLY = """---
week: 
range: {{date:YYYY-MM-DD}}
tags:
  - 周复盘
---

# 第 N 周复盘

[[00-入口/首页|首页]]

## 完成度
| 科目 | 计划 | 实际 | 差 |
|---|---|---|---|
| 数学二 |  |  |  |
| 408 |  |  |  |

## 错题统计
| 科目 | 新增 | 已掌握 | 仍未掌握 |
|---|---:|---:|---:|
| 数学二 |  |  |  |
| 408 |  |  |  |

## 卡住的地方
1. 

## 这周测了没
| 项 | 分数 | 用时 | 失分类型 |
|---|---|---|---|
| 章节测 |  |  |  |

## 下周只做 3 件事
1. 
2. 
3. 
"""


def build_static() -> None:
    write(ROOT / "_templates" / "每日笔记.md", tpl(TEMPLATE_DAILY))
    write(ROOT / "_templates" / "错题卡.md", tpl(TEMPLATE_MISTAKE))
    write(ROOT / "_templates" / "学习笔记.md", tpl(TEMPLATE_NOTE))
    write(ROOT / "_templates" / "周复盘.md", tpl(TEMPLATE_WEEKLY))

    write(ROOT / "00-入口" / "项目说明.md", """---
tags:
  - 首页
  - 项目
---

# 项目说明

[[00-入口/首页|← 首页]]

这个目录同时是**Obsidian 笔记库**和**计划工程目录**，两种东西混在一起，认一下：

## 该看的（笔记）

| 路径 | 作用 |
|---|---|
| `00-入口/` | 首页、说明 |
| `01-数学二/` | 数学二总览 + 12 周周笔记 |
| `02-408/` | 408 总览 + 12 周周笔记 |
| `03-错题本/` | 错题总表 |
| `04-每日/` | 每日笔记（按日期自动生成） |
| `_templates/` | 每日 / 错题 / 学习 / 周复盘 四个模板 |
| `99-附件/` | 图片、手写拍照、PDF |

## 不用管的（工程文件）

| 路径 | 作用 |
|---|---|
| `22408每日计划.html` | 主程序，双击就能用，带打卡进度、错题本、单词 / 章节进度 |
| `data/` | 四份计划 JSON + 两份 Excel，笔记和网页都从这儿来 |
| `scripts/` | 所有构建脚本（见下） |
| `web/plan-app-v2.template.html` | 网页模板，改界面改这里 |
| `deploy/` | GitHub Pages 静态包（`index.html` 由脚本生成） |
| `scripts/_archive/` | 第 1 版排课脚本、旧补丁，仅留档 |
| `screenshots/` | 界面截图 |
| `.obsidian/` | Obsidian 配置（已排除 `scripts/` `data/` `web/` `deploy/` `screenshots/`） |

## scripts/ 里都是什么

| 脚本 | 作用 |
|---|---|
| `build.py` | **一键重建**：数据 → 阶段 → 章节 → 网页 → 笔记 → Excel |
| `gen_english_plan.py` `gen_politics_plan.py` | 英语 / 政治的每日内容生成器 |
| `build_phases.py` | **阶段配置**：四段时间、目标、主线、门槛，写回四份 JSON |
| `build_chapters.py` | **章节表**：武忠祥高数 / 李永乐线代 / 王道四本书的章目录 |
| `build_v2.py` | 打包网页，同时更新 `deploy/index.html` |
| `build_obsidian_vault.py` | **生成笔记库**（就是它生成了这些 md） |
| `build_plan_v2.py` | 重建 Excel（需要 openpyxl） |

## 改计划的顺序

```bash
python3 scripts/build.py            # 全部重建（最省事）
python3 scripts/build.py --only web # 只重打包网页
```

手工分步：

```bash
python3 scripts/build_phases.py     # 改阶段后
python3 scripts/build_chapters.py   # 改章节 / 重排周次后
python3 scripts/build_v2.py         # 重打包网页（含 deploy）
python3 scripts/build_plan_v2.py    # 重建 Excel
python3 scripts/build_obsidian_vault.py  # 重建笔记库
```

走完，网页 / Excel / 笔记三边才对得上。
""")

    write(ROOT / "00-入口" / "库设置说明.md", """---
tags:
  - 首页
  - 设置
---

# 库设置说明

[[00-入口/首页|← 首页]]

## 已经配好的

| 设置 | 值 |
|---|---|
| 附件目录 | `99-附件/` |
| 新建笔记位置 | `04-每日/` |
| 模板目录 | `_templates/` |
| 日记格式 | `YYYY-MM-DD`，建在 `04-每日/` |
| 日记模板 | `_templates/每日笔记.md` |
| 自动更新内部链接 | 开 |

## 建议手动开的

- **设置 → 文件与链接 → 附件默认存放路径**：已设为 `99-附件`，粘图会自己放对地方。
- **设置 → 核心插件 → 模板**：已开，热键建议设 `⌘T`。
- **设置 → 外观**：想要护眼看 `Calm` 之类主题就行，不用装插件。
- **设置 → 编辑器**：建议开「严格换行」关闭状态，笔记里的软换行才不会乱。

## 关于工程文件

工程文件已经收进 `scripts/`、`data/`、`web/` 三个子目录，Obsidian 会在文件列表里显示这几个目录。
已经用 `userIgnoreFilters` 把它们从**搜索和关系图**里排除了，文件列表里还看得见——不影响笔记使用，别删就行。
""")

    write(ROOT / "04-每日" / "每日说明.md", """---
tags:
  - 首页
  - 每日
---

# 每日笔记怎么用

[[00-入口/首页|← 首页]]

1. 点左侧丝带图标的**打开今天的日记**（或 `⌘P` → `打开今天的日记`）。
2. 笔记会按 `2026-11-09` 这种格式建在 `04-每日/`，自动套用 `_templates/每日笔记.md`。
3. 一天只写三样：**学了什么、错在哪、明天先干嘛**。别抄书。

## 跟周笔记的分工

- 周笔记（`01-数学二/第NN周`）是**骨架**：这周该学什么、有哪些课后题、完成标准。脚本生成，别手改。
- 每日笔记是**当天的手账**：实际用了多久、卡在哪、哪道题没做出来。

## 错题怎么记

错题**不要**写在每日笔记里，用 `_templates/错题卡.md` 建独立笔记，再在
[[03-错题本/错题本总表|错题本总表]] 里登记一行。原因：错题会被翻很多遍，散在日记里就再也找不到了。
""")

    write(ROOT / "03-错题本" / "错题本总表.md", """---
tags:
  - 错题本
---

# 错题本总表

[[00-入口/首页|← 首页]]

> [!tip] 用法
> 每道错题用 `_templates/错题卡.md` 建独立笔记，再在下面登记一行。
> 只在「已掌握」那一列打勾的时候，才算真的会了——标准是**一周后不看答案能独立做对**。

## 待复盘

| 日期 | 科目 | 章节 | 题号 | 来源 | 错因 | 状态 | 笔记 |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  | 未掌握 |  |

## 已掌握

| 日期 | 科目 | 章节 | 题号 | 错因 | 掌握日期 |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 错因统计

| 错因 | 数量 |
|---|---:|
| 概念不清 | 0 |
| 计算失误 | 0 |
| 思路卡壳 | 0 |
| 时间不够 | 0 |
| 审题偏差 | 0 |
""")

    write(ROOT / "99-附件" / "附件说明.md", """---
tags:
  - 附件
---

# 附件说明

[[00-入口/首页|← 首页]]

手写推导拍照、错题截图、教材页扫描都丢这里，Obsidian 粘图会自动落到这个目录。

命名建议：`2026-11-09-数学二-极限定义.png`，日期在前，以后按时间找得到。
""")


# ---------------------------------------------------------------- 库配置

OBSIDIAN_CONFIG = {
    "app.json": {
        "attachmentFolderPath": "99-附件",
        "newFileLocation": "folder",
        "newFileFolderPath": "04-每日",
        "alwaysUpdateLinks": True,
        "useMarkdownLinks": False,
        "newLinkFormat": "shortest",
        "showLineNumber": True,
        "readableLineLength": True,
        "promptDelete": True,
        "trashOption": "local",
        "showUnsupportedFiles": True,
        "userIgnoreFilters": [
            "*.py", "*.xlsx", "*.json", "*.html", "scripts/", "data/", "web/", "deploy/", "screenshots/",
        ],
    },
    "core-plugins.json": [
        "file-explorer", "global-search", "switcher", "graph", "backlink",
        "outgoing-link", "tag-pane", "page-preview", "daily-notes", "templates",
        "note-composer", "command-palette", "editor-status", "bookmarks",
        "outline", "word-count", "file-recovery", "canvas",
    ],
    "daily-notes.json": {
        "folder": "04-每日",
        "format": "YYYY-MM-DD",
        "template": "_templates/每日笔记.md",
    },
    "templates.json": {
        "folder": "_templates",
        "dateFormat": "YYYY-MM-DD",
        "timeFormat": "HH:mm",
    },
    "appearance.json": {"theme": "system", "baseFontSize": 16},
    "community-plugins.json": [],
    "hotkeys.json": {},
    "bookmarks.json": {
        "items": [
            {"type": "file", "ctime": 1, "path": "00-入口/首页.md", "title": "首页"},
            {"type": "file", "ctime": 2, "path": "03-错题本/错题本总表.md", "title": "错题本"},
        ]
    },
}


def build_config() -> None:
    cfg_dir = ROOT / ".obsidian"
    for name, payload in OBSIDIAN_CONFIG.items():
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        write(cfg_dir / name, text + "\n")


# ---------------------------------------------------------------- 主流程

def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    missing = [n for n in ("math2-2028.json", "cs408-2028.json", "english-2028.json", "politics-2028.json")
               if not (DATA / n).exists()]
    if missing:
        print(f"[x] 缺少数据文件：{', '.join(missing)}", file=sys.stderr)
        return 1

    math2 = load("math2-2028.json")
    cs408 = load("cs408-2028.json")
    english = load("english-2028.json")
    politics = load("politics-2028.json")

    print("[1/5] 静态说明与模板")
    build_static()

    print("[2/5] 库配置 .obsidian/")
    build_config()

    print("[3/5] 周笔记 / 阶段笔记 + 总览")
    datasets = []
    plans = (("数学二", math2, "01-数学二"), ("408", cs408, "02-408"),
             ("英语", english, "05-英语"), ("政治", politics, "06-政治"))
    for name, data, subj_dir in plans:
        start0 = date.fromisoformat(data["startDate"])
        weeks = data["weeks"]
        phs = data.get("phases") or []
        if len(weeks) > 20:
            # 周数多的科目（英语）：只建阶段笔记，周内容在网页里看
            write(ROOT / subj_dir / f"{name}总览.md", render_overview_phased(data, subj_dir, name))
            for i, ph in enumerate(phs):
                prev_ph = phs[i - 1] if i > 0 else None
                next_ph = phs[i + 1] if i + 1 < len(phs) else None
                write(ROOT / subj_dir / f"第{ph['seq']:02d}阶段 {sanitize(ph['short'])}.md",
                      render_phase_note(data, ph, subj_dir, name, prev_ph, next_ph))
        else:
            for i, w in enumerate(weeks):
                wk_start = start0 + timedelta(days=7 * (w["week"] - 1))
                prev_w = weeks[i - 1] if i > 0 else None
                next_w = weeks[i + 1] if i + 1 < len(weeks) else None
                content = render_week(w, subj_dir, wk_start, prev_w, next_w, name)
                write(ROOT / subj_dir / f"第{w['week']:02d}周 {sanitize(w['title'])}.md", content)
            write(ROOT / subj_dir / f"{name}总览.md", render_overview(data, subj_dir, name))
        datasets.append((name, data, subj_dir))

    print("[4/5] 首页 + 阶段路线")
    write(ROOT / "00-入口" / "首页.md", render_index(datasets))
    write(ROOT / "00-入口" / "阶段路线.md", render_phases(datasets))

    total = sum(1 for _ in ROOT.rglob("*.md"))
    print(f"\n完成：库根目录 {ROOT}")
    print(f"     markdown 文件 {total} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
