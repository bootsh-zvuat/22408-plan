# -*- coding: utf-8 -*-
"""生成政治计划 politics-2028.json（11 月启动，跟着肖八 → 肖四走）。

口径：
    一阶段 2027-11-01 ~ 2027-12-05（5 周）  启动：马原 / 毛中特 / 史纲核心考点 + 肖八选择题
    二阶段 2027-12-06 ~ 2027-12-26（3 周）  冲刺：肖四选择题 + 大题背诵 + 时政

每周 6 个学习日 + 1 个复盘日。运行：python3 gen_politics_plan.py
"""
import json
from pathlib import Path

START = "2027-11-01"
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def day(title, learn, practice, checklist, minutes=60, kind="learn", reading=""):
    return dict(title=title, learn=learn, practice=practice, checklist=checklist,
                minutes=minutes, kind=kind, reading=reading)


def week_days(n, label, extra=()):
    """第 n 周：考点 2 天 + 套卷 2 天 + 错题/时政 1 天 + 自测 1 天，再补 extra。"""
    base = [
        day(f"{label} · 核心考点",
            [f"{label} 第一块高频考点：先看肖秀荣《精讲精练》对应章节（30 分钟）",
             "只记结论和关键词，不抄书", "选择题常考的原句用荧光笔标出来"],
            ["合上书，用 3 句话复述这块讲了什么", "配套 1000 题做 20 道选择"],
            ["考点看完", "3 句话复述", "选择 20 道 ≥14 对"]),
        day(f"{label} · 考点 + 易混点",
            [f"{label} 第二块：易混概念对比（会议 / 时间 / 人物）", "把易混点在纸上列成对照表"],
            ["对照表默写一遍", "1000 题再做 20 道"],
            ["考点看完", "对照表能默", "选择 20 道 ≥14 对"]),
        day("选择题套卷（限时）",
            ["肖八选择题 33 题，限时 40 分钟，一次做完不看解析",
             "对答案，只记错题，不看长篇解析"],
            ["错题回原文找对应考点"],
            ["40 分钟内做完", "得分记到成绩表", "错题标出对应考点"],
            kind="practice", reading="肖八"),
        day("套卷复盘 + 知识点补漏",
            ["错题二刷：先自己做，再看解析", "把错题涉及的考点在书上折角"],
            ["整理 10 条「我总错的点」"],
            ["错题全搞懂", "10 条易错点写下"]),
        day("时政 + 错题滚动",
            ["时政电台 / 时政小册子 20 分钟，只记时间地点人物",
             "错题本滚动 20 题"],
            ["把本月时政做成 5 条一句话"],
            ["时政 20 分钟", "错题 20 题", "5 条时政写下"]),
        day("周自测",
            ["随机 50 道选择（1000 题 + 肖八错题混合），限时 30 分钟",
             "对答案，记录正确率"],
            ["把错题按马原 / 毛中特 / 史纲 / 思修分类"],
            ["50 题 ≥30 对", "正确率记表", "错题分类完"],
            kind="practice"),
    ]
    out = list(base)
    for e in extra:
        out.append(e)
    return out


def build():
    weeks_spec = [
        # ---- 一阶段：11 月，肖八 + 考点
        (1, "马原①：唯物论与辩证法", 5),
        (2, "马原②：认识论与唯物史观", 5),
        (3, "毛中特：新民主主义与新时代", 5),
        (4, "史纲：近代史时间线", 5),
        (5, "思修法基 + 时政 + 肖八二刷", 5),
        # ---- 二阶段：12 月，肖四
        (6, "肖四①②选择 + 大题", 3),
        (7, "肖四③④选择 + 大题", 3),
        (8, "考前冲刺", 3),
    ]
    weeks = []
    for w, label, _ in weeks_spec:
        ds = week_days(w, label)
        if w >= 6:
            # 12 月：考点天改成大题背诵天
            ds[0] = day("大题背诵 1",
                        ["肖四大题第 1 套：先自己写要点，再对答案", "背结构：是什么 → 为什么 → 怎么做"],
                        ["合上书默写要点（关键词即可）"],
                        ["第 1 套要点能默", "结构能说出来"])
            ds[1] = day("大题背诵 2",
                        ["肖四大题第 2 套（或下一套）", "同一句话换说法背一遍"],
                        ["默写要点 + 关键词"],
                        ["第 2 套要点能默", "换说法能说出"])
            ds[4] = day("时政 + 肖四选择错题",
                        ["时政小册子 20 分钟：只记可能出选择题的点", "肖四选择错题滚动"],
                        ["5 条时政 + 10 道选择错题"],
                        ["时政 20 分钟", "错题 10 道"])
        if w == 8:
            ds[2] = day("肖四选择题（限时）",
                        ["肖四选择题 33 题，限时 40 分钟", "对答案，只记错题"],
                        ["错题回考点"],
                        ["40 分钟做完", "得分记表"],
                        kind="practice", reading="肖四")
            ds[3] = day("大题滚动背",
                        ["四套大题快速过：只看关键词，说出框架", "背不出的做标记，晚上再背一次"],
                        ["睡前再过一遍标记的题"],
                        ["四套大题过完", "标记题二次背"])
            ds[5] = day("考前调整",
                        ["只做错题和关键词默写，不碰新题", "按考试时间做一套选择（8:30–9:00）"],
                        ["把四套大题的关键词写成一页纸"],
                        ["不碰新题", "关键词一页纸写完"],
                        kind="review")
        week_days_final = []
        for i, d in enumerate(ds[:6]):
            week_days_final.append(dict(id=f"g{w}d{i+1}", weekday=WEEKDAYS[i], **d))
        week_days_final.append(dict(
            id=f"g{w}d7", weekday="周日", title=f"第 {w} 周复盘：{label}", minutes=40,
            kind="review", reading="",
            learn=["本周错题按科目归类，找出最弱的一块", "把本周的关键词默写一遍", "写下周 3 条动作"],
            practice=["错题重做 10 道"],
            checklist=["错题分类完", "关键词默写", "下周 3 条动作"],
        ))
        weeks.append(dict(
            week=w, title=f"{label}",
            goal="选择题正确率 ≥60%，易混点能分清" if w <= 5 else "肖四大题能默写关键词，选择 ≥35",
            target="6 个学习日 + 1 次复盘",
            check="",
            days=week_days_final,
        ))
    plan = {
        "id": "politics-2028",
        "title": "政治 计划 · 11 月启动（肖八 → 肖四）",
        "subject": "政治",
        "level": "零基础，11 月才启动",
        "goal": "11 月：核心考点 + 肖八选择题；12 月：肖四选择 + 大题背诵",
        "tools": "肖秀荣《精讲精练》《1000 题》、肖八、肖四、时政小册子",
        "dailyMinutes": 60,
        "startDate": START,
        "startsLater": True,
        "source": {"note": "由 gen_politics_plan.py 生成；阶段由 build_phases.py 注入"},
        "weeks": weeks,
    }
    out = DATA / "politics-2028.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{out.name}: {len(weeks)} 周 / {sum(len(w['days']) for w in weeks)} 天")


if __name__ == "__main__":
    build()
