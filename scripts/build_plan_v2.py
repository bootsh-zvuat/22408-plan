# -*- coding: utf-8 -*-
"""生成 22408 学习计划 v2（改进版）。
基于 22408考研400分学习计划_12周细化.xlsx 的结构问题重做：
  1) 时间预算与作息模板对不上 -> 重排作息，四科预算逐格可算
  2) 408 只排了数据结构+计组  -> 12 周走完四科基础一轮
  3) 数学考点缺口（反常积分/向量组相关性/相似对角化）
  4) 无题量、无缓冲、检查点少、无追踪表
运行：python3 build_plan_v2.py
"""
import datetime as dt
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

FONT = "PingFang SC"
INK = "1F3864"
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
SUB_FILL = PatternFill("solid", fgColor="D9E2F3")
BAND_FILL = PatternFill("solid", fgColor="F2F5FA")
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
OK_FILL = PatternFill("solid", fgColor="E2EFDA")
MID_FILL = PatternFill("solid", fgColor="FFF2CC")
LAX_FILL = PatternFill("solid", fgColor="EDEDED")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

HOURS = "0.00"
PCT = "0.0%"


def title(ws, text, ncol, row=1):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncol)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=15, bold=True, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 30


def note(ws, text, ncol, row):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncol)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=10, color="404040")
    c.fill = BAND_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[row].height = 34


def section(ws, text, ncol, row):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncol)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=11, bold=True, color=INK)
    c.fill = SUB_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22


def header(ws, row, values, height=30):
    for i, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    ws.row_dimensions[row].height = height


def put_row(ws, row, values, height=None, align="left", bold=False, fills=None):
    for i, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(name=FONT, size=10, bold=bold)
        c.alignment = Alignment(horizontal=align if i > 1 else "center",
                                vertical="center" if len(str(v)) < 30 else "top",
                                wrap_text=True)
        c.border = BOX
        if fills and i in fills:
            c.fill = fills[i]
    if height:
        ws.row_dimensions[row].height = height


def widths(ws, mapping):
    for col, w in mapping.items():
        ws.column_dimensions[col].width = w


def page(ws, print_area=None):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


wb = Workbook()

# ============================================================ 1 改进说明
ws = wb.active
ws.title = "改进说明"
ws.sheet_properties.tabColor = "C00000"
N = 6
title(ws, "v2 改进说明：对照原表逐条指出问题与改法", N)
note(ws, "读法：「原表证据」列写的是原 xlsx 里的具体位置和数字，可以逐个点开核对；「v2 改法」列写的改动都已落到后面各表。"
         "本轮保留原表的 12 周区间（2026.11.09–2027.01.31）、每天 10 小时、400 分目标结构，只动排法和颗粒度。", N, 2)
header(ws, 4, ["#", "问题", "原表证据（可核对）", "后果", "v2 改法", "落地表"])

rows = [
    (1, "时间预算和作息模板对不上",
     "「总览」D14–E17 写数学 26 / 408 24 / 英语 15 / 机动 5 = 70h/周；但按「每日作息」的时段逐格相加是每天 10.2h × 6 天 + 周日 7h = 68h/周，实算数学 26.5、408 28.5、英语 10、复盘 3。",
     "英语被系统性压缩 5h/周（12 周共 60h），一个 CET4 底子要 76 分，词汇和长难句的原始积累直接缺一块；同时 408 挤占了数学时间，而数学是唯一「不能断」的科目。",
     "重排作息：工作日 6 天 × 10h + 周日 10h = 70h，四科预算改成数学 25.5 / 408 23.5 / 英语 13.7 / 复盘机动 7.3，合计格用公式校验必须等于 70。",
     "总览、每日作息"),
    (2, "408 只排了两科",
     "「12周计划」C/D 列：W1–W7 全是数据结构、W8–W12 全是计组，操作系统和计算机网络在两列表格里一次都没出现。",
     "408 目标 118 分要求四科都过一轮；把 OS 与计网整体压给强化期，等于强化期要同时做「两科新课 + 四科强化 + 真题」，这是最常见的崩盘点。",
     "408 本轮走完四科基础一轮：数据结构 W1–W5（120h，含查找与排序）、计组 W6–W9（96h）、操作系统 W10–W11（48h）、计网 W12（24h），每科一次 100 分测。",
     "12周计划"),
    (3, "数据结构摊了 7 周",
     "「12周计划」C5–C11：数据结构占 7 周 × 24h = 168h。",
     "王道数据结构基础一轮（讲义 + 课后选择 + 大题手写）60–80h 足够，168h 是 2 倍冗余，等于把操作系统和计网的 72h 花在重复刷同一本书上。",
     "数据结构压到 5 周 120h（含查找与排序，原 v2 草稿漏了这两章），省出的 48h 正好补上操作系统的 48h。",
     "12周计划"),
    (4, "数学考点有缺口",
     "「12周计划」C7「定积分计算与性质」后直接进多元，全表无「反常积分」；C12 停在「初等变换与秩」，W9 直接跳线性方程组，无「向量组线性相关性」；C13 特征值后无「相似对角化」；C6「排序」之后整表再无排序相关周次。",
     "这三块都是数二稳定考点（反常积分敛散判定、向量组表出与极大无关组、相似对角化的判定与实对称正交化），缺口拖到强化期补，代价是 2 倍以上。",
     "W3 补反常积分；W8 补向量组线性相关性（表出、相关、极大无关组）；W10 补相似对角化与实对称矩阵正交相似。",
     "12周计划"),
    (5, "题量只有第 1 周有数字",
     "「12周计划」C5 写「基础题 15 道/天」，C6–C16 全是纯章节描述，一个数字都没有。",
     "没有周题量就分不清「学完」和「做过」，进度表也没法量化偏差；到 W12 总测才发现题感不够，已无时间补救。",
     "每周给死题量：数学 20–60 道（累计 420 道，另 4 套测）；408 选择 40–55 + 大题 4–6（累计选择 570、大题 57），并在「进度追踪」里逐周记实做数。",
     "12周计划、进度追踪"),
    (6, "检查点少且只给一条补救规则",
     "「阶段验收」A6–A9 只有 4 个检查点；D6 只写「<60 分：停新章节 3 天」，60–69 分这一档没有任何处置。",
     "60–69 分（刚好卡线）恰恰是最危险的区间，进强化期会被真题放大；且 408 全程只有 1 次测试，四科里三科没有验收。",
     "检查点扩到 5 个 / 6 场测（数学 3 场 + 408 三科各 1 场 + 双科总测），每场按 <60 / 60–69 / 70–84 / ≥85 四档给动作。",
     "阶段验收"),
    (7, "12 周零缓冲",
     "「12周计划」W1–W12 全满，W12 一周内要同时做「计组结课 + 数学 150 分总测 + 408 150 分总测 + 四科框架默写」。",
     "任何一周塌方（生病、实验、期末）都会整体顺延到寒假；而 W9 期末考撞车是已知的，原表只能靠「保底模式」硬扛，没有可动用的时间。",
     "每周日固定留 3h 机动（补欠账专用，不开新内容）；每个检查点周的周日同时是「清算日」（W4/W5/W7/W9/W10/W11/W12）；另定义 A/B/C 三级运行模式与补丁周触发线。",
     "每日作息、阶段验收"),
    (8, "单词没有复习闭环",
     "「12周计划」E5–E12 是「单词 Unit1–21」一路推，唯一的质量约束是 F 列的「听写 ≥85%」。",
     "12 周 5500 词只靠「学一遍 + 听写一次」，留存率极低；强化期做阅读时会因为词汇回生重新卡住，等于白背。",
     "单词按 D1 / D2 / D4 / D7 四轮滚动（见每日作息早读时段），每周日听写；听写 <75% 当周新词减半（保留原红线）。",
     "每日作息、12周计划"),
    (9, "英语写作完全推后",
     "「资料清单」C7 写「王江涛写作（寒假后开始）」，12 周内写作零投入。",
     "写作 25 分里小作文 10 分是最早能稳定拿分的项（模板 + 6 个句型就够），寒假前完全不动等于白扔 12 周。",
     "W9 起每两周 1 篇小作文（占机动时间，不占新课时间），本轮共 2 篇；大作文仍留到寒假后。",
     "12周计划"),
    (10, "打卡只有「未开始」三个字",
     "「12周计划」G 列下拉，全部是「未开始」。",
     "没有「计划 vs 实际」的数据积累，无法回看哪一周开始塌、无法算完成率，计划也就无法滚动修正。",
     "新增「进度追踪」：计划课时 / 实际课时 / 完成率（公式）/ 题量 / 听写正确率 / 状态（公式自动判达标-偏紧-需补丁）。",
     "进度追踪"),
    (11, "错题本只说「整理」",
     "「总览」E17 与 W11 写「错题本整理 / 二刷」，但没有任何字段定义。",
     "没有错因分类，二刷时只能整本重做一遍，等于把错题再错一遍；W11 的「错题二刷正确率 ≥85%」无法执行。",
     "新增「错题本模板」：错因五分类（概念不清/计算失误/思路没想到/审题错/时间不够）+ 复盘次数 + 掌握日期，二刷只做未掌握的。",
     "错题本模板"),
    (12, "400 分的分段目标没交代",
     "「总览」A6 政治 72 分，但「资料清单」C8 写「本阶段不启动」，没有说 72 分什么时候挣、靠什么挣。",
     "读者不知道 12 周里政治该不该碰，容易在焦虑下提前开政治，反而拖垮数学和 408。",
     "「总览」加「启动时间」列；「后续路线」给出 2027 全年框架：政治 11 月启动，12 周内只跑数学 / 408 / 英语三线。",
     "总览、后续路线"),
]
r = 5
for row in rows:
    put_row(ws, r, list(row), height=96)
    r += 1

r += 1
section(ws, "本轮改动的量化结果（原表 vs v2）", N, r)
r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
for col, val in [(1, "指标"), (3, "原表"), (4, "v2 改动与效果")]:
    c = ws.cell(row=r, column=col, value=val)
    c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for col in range(1, 7):
    cc = ws.cell(row=r, column=col)
    cc.border = BOX
    cc.fill = HEAD_FILL
    cc.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
    cc.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[r].height = 28
r += 1
quant = [
    ("408 基础一轮覆盖科目", "2 科（数据结构、计组）", "4 科（＋操作系统、计网）→ 强化期不再背基础债，400 分路线才成立"),
    ("数据结构投入", "7 周 / 168h", "5 周 / 120h（查找到排序都进来了）→ 省 48h，正好补上操作系统"),
    ("英语有效周时", "实算 10h（表头写 15h）", "13.7h（公式可校验）→ 12 周多 44h，词汇与长难句才有底"),
    ("数学周题量", "无量化（仅 W1 有 15 道/天）", "20–60 道/周，累计 420 道 + 4 套测 → 题感可逐周跟踪"),
    ("验收检查点", "4 个", "7 个检查点 / 8 场测，四档通用处置 → 卡线分数也有明确动作"),
    ("缓冲时间", "0", "每周日 3h 机动 + 4 个清算日 → 塌方不会一次性滚到寒假"),
    ("总时长口径", "表头 70h/周，实算 68h/周", "70h/周，公式校验 → 计划数字与作息表不再两套"),
]
for a, b, c in quant:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
    for col, val in [(1, a), (3, b), (4, c)]:
        cell = ws.cell(row=r, column=col, value=val)
        cell.font = Font(name=FONT, size=10)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    for col in range(1, 7):
        cc = ws.cell(row=r, column=col)
        cc.border = BOX
        cc.font = Font(name=FONT, size=10)
        cc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[r].height = 28
    r += 1

widths(ws, {"A": 6, "B": 24, "C": 44, "D": 40, "E": 46, "F": 14})
ws.freeze_panes = "A5"
page(ws)

# ============================================================ 2 总览
ws = wb.create_sheet("总览")
ws.sheet_properties.tabColor = "1F3864"
N = 6
title(ws, "22408 · 2028 考研 400 分学习计划（v2 基础期 12 周）", N)
note(ws, "周期 2026.11.09 — 2027.01.31（12 周，初试 2027.12.25，距初始还有 328 天）｜每天 10 小时｜70 小时/周｜"
         "总投入约 810 小时（含 W9 期末降载周）｜英语 CET4 底子｜数学二中等水平。", N, 2)

section(ws, "一、目标分数拆解（总分 400）", N, 4)
header(ws, 5, ["科目", "满分", "目标分", "得分结构", "允许失误", "启动时间"])
score = [
    ("政治", 100, 72, "客观 40 + 主观 32", "客观题最多错 5 题（10 分）", "2027.11"),
    ("英语二", 100, 76, "完型 7 + 阅读 34 + 新题型 8 + 翻译 11 + 写作 16", "阅读最多错 3 题", "本轮：单词/长难句/阅读"),
    ("数学二", 150, 134, "选填 75/80 + 解答 59/70", "16 道选填最多错 1 题", "本轮：高数 + 线代基础"),
    ("408", 150, 118, "客观 74/80 + 大题 44/70", "大题最多丢 2 个小问", "本轮：四科基础一轮"),
]
r = 6
for row in score:
    put_row(ws, r, list(row), height=34)
    r += 1
put_row(ws, r, ["合计", "=SUM(B6:B9)", "=SUM(C6:C9)",
                "400 分安全线；建议按 410 训练，留 10 分容错", "—", "—"], height=30, bold=True)
ws.cell(row=r, column=2).number_format = "0"
ws.cell(row=r, column=3).number_format = "0"
for col in (2, 3):
    ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
ws.cell(row=r, column=4).value = '=IF(C10=400,"✔ 目标合计 = 400 分，与总分线一致","✘ 目标合计 ≠ 400，请检查拆解")'
sum_row = r

section(ws, "二、每周时间预算（70 小时 = 工作日 6 天 × 10h + 周日 10h，与「每日作息」逐格对应）", N, 12)
header(ws, 13, ["科目", "每周小时", "占比", "固定时段", "说明", "校验"])
budget = [
    ("数学二", "='每日作息'!B26", "8:00–10:00 新课 + 13:30–14:30 做题 + 周一三五晚 19:00–20:20 补漏 + 周日 3.5h 限时测", "全程第一优先级，一天也不能断", None),
    ("408", "='每日作息'!B27", "10:10–11:40 讲义 + 14:40–16:40 课后题/手写代码 + 周日 2.5h 复盘", "四科顺序推进，偏科一次就还不上", None),
    ("英语二", "='每日作息'!B28", "早读 40min 单词 + 16:50–17:50 长难句与精读 + 周二四晚 1.33h", "每天必做，中断一周等于倒退两周", None),
    ("复盘 / 机动", "='每日作息'!B29", "每晚 20:20–20:50 三行复盘 + 周六错题本 + 周日 3h 机动", "只用来补欠账与错题，不开新内容", None),
]
r = 14
for name, hours, when, why, _ in budget:
    put_row(ws, r, [name, hours, None, when, why, "—"], height=40)
    ws.cell(row=r, column=2).number_format = "0.0"
    ws.cell(row=r, column=3, value=f"=B{r}/70")
    ws.cell(row=r, column=3).number_format = PCT
    ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=3).border = BOX
    r += 1
put_row(ws, r, ["合计", "=ROUND(SUM(B14:B17),2)", "=SUM(C14:C17)", "70 小时/周", "—", None], height=28, bold=True)
ws.cell(row=r, column=2).number_format = "0.0"
ws.cell(row=r, column=3).number_format = PCT
for col in (2, 3):
    ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
ws.cell(row=r, column=6, value='=IF(ABS(B18-70)<0.01,"✔ = 70h","✘ ≠ 70h，检查作息")')
ws.cell(row=r, column=6).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
ws.cell(row=r, column=4, value="与「每日作息」周合计公式联动，不相等就是有一处时段没算对")
ws.cell(row=r, column=4).font = Font(name=FONT, size=10)
ws.cell(row=r, column=4).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

section(ws, "三、这 12 周的定位与产出", N, 20)
ws.merge_cells("A21:F21")
c = ws.cell(row=21, column=1,
            value="阶段定位：基础期第一段。不碰套卷、不碰政治。产出目标：\n"
                  "① 数学二：高数 7 周 + 线代 3 周 + 错题/总测 2 周完成一轮基础（武忠祥/李永乐讲义 + 660 基础篇 420 道），三场阶段测达标。\n"
                  "② 408：四科全部走完基础一轮（数据结构 120h、计组 96h、操作系统 48h、计网 24h），每科一次 100 分测 + 一次 150 分总测。\n"
                  "③ 英语：单词 5500 首轮 + 高频 1500 二轮、长难句体系过完、英语一 2005–2011 真题精读 28 篇、小作文 2 篇。\n"
                  "④ 结束时基线：数学 150 分卷 ≥100、408 150 分卷 ≥90（400 分路线的起点，不是终点）。")
c.font = Font(name=FONT, size=10)
c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
c.border = BOX
ws.row_dimensions[21].height = 96

section(ws, "四、五条不能破的底线", N, 23)
lines = [
    "红线一：数学每天不能断。断 1 天 ≈ 倒退 2 天；其他科目可调，数学不行。",
    "红线二：408 每周必须有手写产出（代码或大题步骤）。只看讲义等于没学，四科里任何一科都不能只过眼睛。",
    "红线三：单词听写 <75% 当天新词量减半，把时间全给复习，别硬冲进度。",
    "红线四：期末考（W9）撞车时按 B 档降载执行，考完当周末集中补 8 小时，不要连续停 5 天以上。",
    "红线五（新增）：每周日必须填「进度追踪」，不填等于这周没验收——没有实际数据的计划只是愿望。",
]
r = 24
for t in lines:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
    c = ws.cell(row=r, column=1, value=t)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    c.border = BOX
    ws.row_dimensions[r].height = 26
    r += 1
widths(ws, {"A": 12, "B": 12, "C": 12, "D": 46, "E": 40, "F": 16})
ws.freeze_panes = "A4"
page(ws)

# ============================================================ 3 12周计划
ws = wb.create_sheet("12周计划")
ws.sheet_properties.tabColor = "2E75B6"
N = 9
title(ws, "12 周逐周任务表（2026.11.09 — 2027.01.31）｜内容 + 题量 + 验收 三件套", N)
note(ws, "读表口径：每周 70h = 数学 25.5 / 408 23.5 / 英语 13.7 / 复盘机动 7.3（与「每日作息」公式联动）。"
         "408 本轮走完四科基础一轮：数据结构 W1–W5、计组 W6–W9、操作系统 W10–W11、计网 W12。"
         "检查点周（W4/W5/W7/W9/W10/W11/W12）先测再进；W9 期末周按 B 档降载。实际执行填在「进度追踪」。", N, 2)
header(ws, 4, ["周次", "日期", "数学二（25.5h/周）", "408（23.5h/周）", "英语二（13.7h/周）",
               "数学题量", "408 题量", "检查点 / 测试", "本周验收标准（不达标走「阶段验收」的补丁规则）"], height=38)

weeks = [
    ("W1", "11.09–11.15",
     "函数极限连续（ε–N、无穷小比较、两个重要极限、间断点分类）+ 660 基础篇起步",
     "数据结构 ①：绪论与线性表（顺序表、单链表、双链表、循环链表、静态链表、复杂度分析）",
     "单词 U1–U3（按 D1/D2/D4/D7 滚动）+ 定语从句 + 2005 T1 精读",
     "660 题 30 道 + 讲义例题 20 道",
     "选择 40 + 大题 4（逆置/删除/合并手写）",
     "—",
     "极限限时 30 题 ≥85%；可导/连续关系辨析 5 题全对；手写单链表逆置不查书；听写 ≥85%"),
    ("W2", "11.16–11.22",
     "导数与微分（定义、法则、复合/隐函数/参数方程）+ 中值定理（罗尔/拉格朗日/柯西）",
     "数据结构 ②：栈、队列、串与数组（循环队列判空判满、KMP、特殊矩阵压缩）",
     "单词 U4–U6 + 状语从句 + 2005 T2、T3 精读",
     "660 题 40 道",
     "选择 40 + 大题 4（循环队列、KMP next 手推）",
     "—",
     "中值定理证明 8 题独立完成 ≥6；循环队列判空判满公式默写；KMP next 手推 3 题全对"),
    ("W3", "11.23–11.29",
     "导数应用收尾（不等式证明、方程根、曲率）+ 不定积分（凑微分、换元、分部、有理函数）",
     "数据结构 ③：树与二叉树（三序遍历递归+非递归、线索树、哈夫曼、并查集、树森转换）",
     "单词 U7–U9 + 名词性从句 + 2006 T1、T2 精读",
     "660 题 60 道（积分 40）",
     "选择 45 + 大题 6（遍历手写、哈夫曼、并查集）",
     "—",
     "积分专项 40 题 ≥85%；三种遍历手写全对；并查集路径压缩能写；单词累计 1900+"),
    ("W4", "11.30–12.06",
     "定积分（性质、变限积分、牛顿–莱布尼茨、对称性、反常积分）+ 定积分应用（面积、体积、弧长、物理）",
     "数据结构 ④：图（存储、DFS/BFS、Prim/Kruskal、Dijkstra/Floyd、拓扑、关键路径）",
     "单词 U10–U12 + 2006 T3、T4 + 单词一轮过半校对",
     "660 题 30 道 + 高数上测 1 套",
     "选择 50 + 大题 5",
     "检查点 1：高数上 100 分卷 ≥75（周日限时）",
     "高数上 ≥75/100；反常积分敛散判定 10 题全对；Dijkstra 与 Prim 手写正确；单词累计 2700+"),
    ("W5", "12.07–12.13",
     "多元函数微分（偏导、全微分、复合/隐函数、极值与条件极值）",
     "数据结构 ⑤：查找（顺序/折半/分块/BST/AVL/B 树/散列）+ 排序（全部 + 外部排序）+ 数据结构 100 分测",
     "单词 U13–U15 + 2007 T1、T2 + 长难句翻译 5 句/周",
     "660 题 50 道",
     "选择 50 + 大题 5 + 测 1 套",
     "检查点 2：数据结构 100 分卷 ≥75",
     "数据结构 ≥75/100（大题步骤齐全）；复杂度与稳定性 20 项全对；哈希冲突处理能画表"),
    ("W6", "12.14–12.20",
     "二重积分（直角/极坐标、换序、对称性）+ 660 综合题",
     "计组 ①：系统概述 + 数据表示（补码、定点/浮点、IEEE754、校验码）",
     "单词 U16–U18 + 2007 T3、T4 + 2008 T1 精读",
     "660 题 55 道",
     "选择 45 + 大题 4（IEEE754、海明码）",
     "—",
     "二重积分换序 10 题全对；IEEE754 单精度手算互转 5 题全对；单词累计 3700+"),
    ("W7", "12.21–12.27",
     "常微分方程（可分离、一阶线性、可降阶、二阶常系数）+ 高数下测 + 高数错题首轮整理",
     "计组 ②：运算方法（ALU/乘除）+ 存储系统（主存扩展、Cache 映射/替换/写策略、虚拟存储）",
     "单词 U19–U21 + 2008 T2、T3 + 阅读错因归类表",
     "660 题 20 道 + 高数下测 1 套",
     "选择 50 + 大题 5（Cache 命中率、主存扩展）",
     "检查点 3：高数下 100 分卷 ≥75",
     "高数下 ≥75/100；一阶线性通解不查书；Cache 三种映射能画图算命中率；单词累计 4200+"),
    ("W8", "12.28–01.03",
     "线代 ①：行列式（性质、范德蒙德、分块）+ 矩阵（运算、逆、分块、初等变换、秩）",
     "计组 ③：虚拟存储与 TLB + 指令系统（格式、寻址、CISC/RISC）+ CPU（数据通路、控制器）",
     "单词一轮收尾（5500 完成）+ 2009 T1、T2 + 高频 1500 二轮启动",
     "660 题 45 道",
     "选择 50 + 大题 5",
     "—",
     "行列式 10 题全对；秩与初等变换关系能说清；VA→PA 流程能默写；单词 5500 首轮完成"),
    ("W9", "01.04–01.10",
     "线代 ②：向量组（表出、相关性、极大无关组、秩）+ 线性方程组（解结构、基础解系）——期末周 B 档，保底 2h/天",
     "计组 ④：流水线（冲突、性能、多发射）+ 总线 + IO（中断、DMA）+ 计组 100 分测",
     "高频词二轮 + 真题阅读保底 1 篇/天 + 长难句 3 句/天 + 小作文 1 篇（首篇）",
     "660 题 45 道（只做错题与选择）",
     "选择 50 + 大题 5 + 测 1 套",
     "检查点 4：计组 100 分卷 ≥75（可顺延到考完当周末）",
     "数学 ≥2h/天 ×6 天；PV 大题能写信号量定义与初值；计组 ≥75/100；考完当周末补 8h 追平"),
    ("W10", "01.11–01.17",
     "线代 ③：特征值与特征向量、相似对角化、实对称正交相似 + 二次型（标准形、惯性定理、正定）",
     "操作系统 ①：概述 + 进程管理（进程/线程、调度、同步互斥、PV、管程、死锁、银行家算法）",
     "高频词 1500 一轮完成 + 2010 T1、T2 精读 + 小作文 1 篇",
     "660 题 45 道 + 线代测 1 套",
     "选择 45 + 大题 4（PV、调度计算）",
     "检查点 5：线性代数 100 分卷 ≥75",
     "线代 ≥75/100；能判断矩阵可否相似对角化并说理由；PV 顺序不写反；高频 1500 正确率 ≥80%"),
    ("W11", "01.18–01.24",
     "高数与线代错题二刷（只做错题本，不上新资料）+ 跨章综合题 10 道",
     "操作系统 ②：内存管理（分页/分段/虚存/置换）+ 文件系统 + IO 管理 + OS 100 分测",
     "高频词二轮推进 + 2010 T3、T4 + 长难句翻译 8 句",
     "错题本未掌握题全部重做",
     "选择 50 + 大题 5 + 测 1 套",
     "检查点 6：操作系统 100 分卷 ≥70",
     "错题二刷正确率 ≥85%；OS ≥70/100；页面置换 4 种算法手算全对"),
    ("W12", "01.25–01.31",
     "数学 150 分总测（周日 3h 限时）+ 寒假 6 周计划",
     "计网一轮（体系结构/物理层/链路层/网络层/传输层/应用层）+ 计网测 + 408 150 分总测",
     "高频词二轮收尾 + 2011 T1、T2 + 小作文 1 篇 + 寒假英语清单",
     "150 分总测 1 套（限时 3h）",
     "选择 55 + 大题 5 + 408 总测 1 套",
     "检查点 7：数学 ≥100 且 408 ≥90 + 四科框架默写",
     "数学 ≥100/150；408 ≥90/150；四科框架图能默写；计网若未走完，寒假第 1 周补完（不影响 2 月强化启动）"),
]
r = 5
for i, w in enumerate(weeks):
    put_row(ws, r, list(w), height=88 if len(w[2]) > 60 else 76)
    for col in (1, 2, 6, 7, 8):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if w[7] != "—":
        for col in (8, 9):
            ws.cell(row=r, column=col).fill = MID_FILL
    if i % 2 == 1:
        for col in (3, 4, 5):
            if ws.cell(row=r, column=col).fill.fgColor.rgb in ("00000000", None):
                ws.cell(row=r, column=col).fill = BAND_FILL
    ws.row_dimensions[r].height = 92 if len(w[3]) > 55 else 80
    r += 1

r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
c = ws.cell(row=r, column=1,
            value="说明：①②③④ 是 408 单科内的章节推进，不等于每周只看这一科；四科按上表顺序走完一轮，任何一科都不允许跨周留尾巴。"
                  "检查点周先测再进，测不完不许开新章。补丁与顺延规则见「阶段验收」；实际完成情况填「进度追踪」。")
c.font = Font(name=FONT, size=10, color="404040")
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
c.fill = BAND_FILL
c.border = BOX
ws.row_dimensions[r].height = 34
widths(ws, {"A": 7, "B": 13, "C": 40, "D": 44, "E": 32, "F": 20, "G": 24, "H": 26, "I": 44})
ws.freeze_panes = "C5"
page(ws)

# ============================================================ 4 每日作息
ws = wb.create_sheet("每日作息")
ws.sheet_properties.tabColor = "268E8E"
N = 6
title(ws, "每日 10 小时模板（工作日 6 天 × 10h + 周日 10h = 70h/周，公式校验）", N)
note(ws, "底线两条：数学 2 小时整块 + 英语 40 分钟单词。被课程/实验挤占时，先保这两条，再补 408。"
         "工作日时段之和必须等于 10.00h，周日也必须等于 10.00h——原表按它的作息算只有 68h/周，v2 把差额补回英语。", N, 2)

section(ws, "一、工作日模板（周一–周六）", N, 4)
header(ws, 5, ["#", "时段", "时长(h)", "科目", "内容", "执行要点"])
weekday = [
    (1, "07:00–07:40", 0.67, "英语", "单词复习：只做 D1/D2/D4/D7 到期的词，不背新词", "复习优先于背新词；晚上新课之后再补 20 个新词"),
    (2, "08:00–10:00", 2.00, "数学", "讲新课 + 例题（讲义）", "全天最清醒的两小时给最难科目；做题捂答案，10 分钟无思路才看提示"),
    (3, "10:10–11:40", 1.50, "408", "讲义单科推进（按周计划顺序，不跳科）", "数学之后大脑仍在运算状态，适合啃抽象概念"),
    (4, "13:30–14:30", 1.00, "数学", "当天内容配套题（660 基础篇）", "学完 4 小时内做题，记忆消退最少"),
    (5, "14:40–16:40", 2.00, "408", "课后题 / 手写代码 / 大题步骤", "408 拉分在大题，必须落笔而不是看懂"),
    (6, "16:50–17:50", 1.00, "英语", "长难句 + 阅读精读（1 篇/天）", "固定时段，避免被数学挤掉；1 篇精读胜过 5 篇潦草"),
    (7, "19:00–20:20", 1.33, "交替", "周一三五数学补漏；周二四英语；周六错题本", "单日换科，避免单科疲劳；只做当周内容，不开新章"),
    (8, "20:20–20:50", 0.50, "复盘", "3 行总结 + 明日第一道题 + 错题登记", "计划滚动修正，防止跑偏一周才发现"),
]
r = 6
for row in weekday:
    put_row(ws, r, list(row), height=38)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=3).number_format = HOURS
    ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=4).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
put_row(ws, r, ["合计", "每天", "=SUM(C6:C13)", "—", "工作日每天必须 = 10.00h", None], height=26, bold=True)
ws.cell(row=r, column=3).number_format = HOURS
ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
ws.cell(row=r, column=6, value='=IF(ABS(C14-10)<0.01,"✔ = 10h","✘ ≠ 10h")')
ws.cell(row=r, column=6).alignment = Alignment(horizontal="center", vertical="center")
wd_total_row = r

section(ws, "二、周日模板（复盘 + 测验 + 机动）", N, 16)
header(ws, 17, ["#", "时段", "时长(h)", "科目", "内容", "执行要点"])
sunday = [
    (1, "08:00–11:30", 3.50, "数学", "限时整章测 / 阶段测 + 对答案 + 错题登记", "必须按考试时间限时，不查书；对答案只看错因不看分数"),
    (2, "13:30–16:00", 2.50, "408", "周复盘：选择错题重做 + 本周大题手写一遍", "大题重做要写完整步骤，包括数据结构代码"),
    (3, "16:10–17:10", 1.00, "英语", "单词听写 + 阅读复盘 + 阅读错因归类表", "听写 <75% → 下周新词减半（红线三）"),
    (4, "19:00–22:00", 3.00, "机动", "补欠账 / 错题二刷 / 下周计划 + 填「进度追踪」", "只用来补缺口，永远不用来追新进度"),
]
r = 18
for row in sunday:
    put_row(ws, r, list(row), height=38)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=3).number_format = HOURS
    ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=4).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
put_row(ws, r, ["合计", "周日", "=SUM(C18:C21)", "—", "周日也必须 = 10.00h", None], height=26, bold=True)
ws.cell(row=r, column=3).number_format = HOURS
ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
ws.cell(row=r, column=6, value='=IF(ABS(C22-10)<0.01,"✔ = 10h","✘ ≠ 10h")')
ws.cell(row=r, column=6).alignment = Alignment(horizontal="center", vertical="center")

section(ws, "三、周合计（用上面的时段单元格直接算，与「总览」预算表互为校验）", N, 24)
header(ws, 25, ["科目", "周合计(h)", "占比", "推导（引用的就是上面的时段单元格）", "", ""])
ws.merge_cells(start_row=25, start_column=4, end_row=25, end_column=6)
totals = [
    ("数学", "=(C7+C9)*6+C12*3+C18", "(C7 新课 2.00h + C9 做题 1.00h) × 6 天 + C12 周一三五晚 1.33h × 3 次 + C18 周日 3.50h"),
    ("408", "=(C8+C10)*6+C19", "(C8 讲义 1.50h + C10 课后题 2.00h) × 6 天 + C19 周日复盘 2.50h"),
    ("英语", "=(C6+C11)*6+C12*2+C20", "(C6 单词 0.67h + C11 精读 1.00h) × 6 天 + C12 周二四晚 1.33h × 2 次 + C20 周日 1.00h"),
    ("复盘机动", "=C13*6+C12*1+C21", "C13 每晚复盘 0.50h × 6 天 + C12 周六晚错题 1.33h × 1 次 + C21 周日机动 3.00h"),
]
r = 26
for name, formula, why in totals:
    put_row(ws, r, [name, formula, None, why, None, None], height=30)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=2).number_format = "0.0"
    ws.cell(row=r, column=2).alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
    c = ws.cell(row=r, column=4)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.cell(row=r, column=3, value=f"=B{r}/B30")
    ws.cell(row=r, column=3).number_format = PCT
    ws.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=3).border = BOX
    r += 1

put_row(ws, 30, ["合计", "=ROUND(SUM(B26:B29),2)", "=SUM(C26:C29)", None, None, None], height=30, bold=True)
ws.cell(row=30, column=2).number_format = "0.0"
ws.cell(row=30, column=3).number_format = PCT
for col in (2, 3):
    ws.cell(row=30, column=col).alignment = Alignment(horizontal="center", vertical="center")
ws.merge_cells(start_row=30, start_column=4, end_row=30, end_column=6)
c = ws.cell(row=30, column=4, value='=IF(ABS(B30-70)<0.01,"✔ 周合计 = 70 小时 / 每天 10 小时，与「总览」预算一致","✘ 周合计 ≠ 70，检查上面的时段或次数")')
c.font = Font(name=FONT, size=10, bold=True)
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

widths(ws, {"A": 10, "B": 13, "C": 9, "D": 10, "E": 46, "F": 40})
ws.freeze_panes = "A6"
page(ws)

# ============================================================ 5 阶段验收
ws = wb.create_sheet("阶段验收")
ws.sheet_properties.tabColor = "C55A11"
N = 8
title(ws, "阶段验收、四级处置与降载规则", N)
note(ws, "原则：不达标就追加「补丁」，把后续任务顺延，而不是跳过——跳过会在真题阶段集中暴露为断崖式失分。"
         "每个检查点按四档给动作，60–69 分（卡线）这一档必须动手，不许直接进下一阶段。", N, 2)

section(ws, "一、八个检查点（先测再进下一周，测不完不许开新章）", N, 4)
header(ws, 5, ["检查点", "时间", "卷子", "达标线", "不达标动作（当天执行，不讨论）", "", "", ""])
for col in (5, 6, 7, 8):
    ws.merge_cells(start_row=5, start_column=5, end_row=5, end_column=8)
ws.merge_cells(start_row=5, start_column=5, end_row=5, end_column=8)
cps = [
    ("CP1", "W4 结束 12.06", "高数上 100 分卷（极限→定积分应用）", "≥75",
     "停新章 3 天，回炉极限到定积分，题量减半；W5 不进多元"),
    ("CP2", "W5 结束 12.13", "数据结构 100 分卷", "≥75",
     "停计组 3 天，重做图与排序大题；计组整体顺延 2 天"),
    ("CP3", "W7 结束 12.27", "高数下 100 分卷（多元→微分方程）", "≥75",
     "线代起步降到每天 2h，其余时间补高数错题"),
    ("CP4", "W9 结束 01.10", "计组 100 分卷", "≥75",
     "回炉存储系统 5 天，OS 顺延到 W10 中；期末周允许顺延到考完当周末"),
    ("CP5", "W10 结束 01.17", "线性代数 100 分卷", "≥75",
     "3 天只做题方程组与特征值；二次型压到 W11"),
    ("CP6", "W11 结束 01.24", "操作系统 100 分卷", "≥70",
     "回炉进程同步与页面置换；计网只保留讲义 + 选择，大题放弃"),
    ("CP7", "W12 结束 01.31", "数学 150 分卷 + 408 150 分卷 + 四科框架默写", "≥100 / ≥90",
     "不进强化期，寒假前 2 周做补丁周（只补基础，不上强化资料）"),
]
r = 6
for row in cps:
    put_row(ws, r, [row[0], row[1], row[2], row[3], row[4], None, None, None], height=44)
    ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=8)
    for col in (1, 2, 4):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.cell(row=r, column=5).fill = WARN_FILL
    r += 1

header(ws, 14, ["分数区间", "通用处置（任何一场测都按这个走）", "", "限时", "", "", "", ""])
ws.merge_cells(start_row=14, start_column=2, end_row=14, end_column=3)
ws.merge_cells(start_row=14, start_column=4, end_row=14, end_column=8)
tiers = [
    ("<60 分", "停掉当前科目新内容，回炉讲义例题 + 全部错题，题量减半", "最少 3 天"),
    ("60–69 分", "不加新内容，用周日机动 3h 只补错题；7 天内重测同类 20 题", "1 周内"),
    ("70–84 分", "按计划推进，本周题量 +10%，该批错题进二刷", "正常"),
    ("≥85 分", "提前 1–2 天开下一模块，省出的时间存进补丁池（不奖励提前学新科）", "正常"),
]
r = 15
for a1, a2, a3 in tiers:
    put_row(ws, r, [a1, a2, None, a3, None, None, None, None], height=34)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
    for col in (1,):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=4).fill = MID_FILL if a1 in ("60–69 分", "70–84 分") else (WARN_FILL if a1 == "<60 分" else OK_FILL)
    r += 1

section(ws, "二、三级运行模式（按周切换，不按心情切换）", N, 21)
header(ws, 22, ["等级", "触发条件", "", "每天时长", "数学", "408", "英语", "复盘 / 机动"])
modes = [
    ("A 标准", "默认状态", "10h / 天", "3.0h（含交替补漏）", "3.5h", "1.67h（含周二四晚）", "0.83h"),
    ("B 降载", "期末周、实验周、连续 2 天未完成当日任务", "6h / 天", "2.0h（只做题）", "3.0h（只讲义+选择）", "0.7h（单词）", "0.3h"),
    ("C 保底", "生病、出差、家庭事务", "3h / 天", "2.0h（只做错题）", "暂停（≤3 天）", "0.7h（单词）", "0.3h"),
]
r = 23
for m in modes:
    put_row(ws, r, [m[0], m[1], None, m[2], m[3], m[4], m[5], m[6]], height=50)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=4).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
ws.merge_cells("A26:H26")
c = ws.cell(row=26, column=1, value="退出条件：B 档连续 3 天能完成当日任务的 80% 即回 A 档；C 档恢复到能坐满 3h 且数学不断线即回 B 档。"
                                    "任何一档都不允许「数学断线」和「单词断线」同时发生——那是重启成本最高的情况。")
c.font = Font(name=FONT, size=10)
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
c.border = BOX
ws.row_dimensions[26].height = 34

section(ws, "三、补丁与顺延规则（触发即执行，不讨论）", N, 28)
header(ws, 29, ["#", "触发条件", "", "动作", "", "", "代价 / 注意", ""])
ws.merge_cells(start_row=29, start_column=2, end_row=29, end_column=3)
ws.merge_cells(start_row=29, start_column=4, end_row=29, end_column=6)
ws.merge_cells(start_row=29, start_column=7, end_row=29, end_column=8)
patch = [
    ("1", "某周「进度追踪」完成率 <70%", "下周日不作新内容，整天转为补丁日（机动 3h 全部用于欠账）", "只损失半天，不动整体节奏"),
    ("2", "连续 2 周完成率 <70%", "整周转补丁周，408 四科顺序整体后移；数学检查点优先", "总时长会长 1 周，但比带债进强化期便宜"),
    ("3", "数学缺口 >2 章", "停 408 新章 2 天，优先补数学（数学第一优先级）", "408 用周末 2.5h 复盘时间追"),
    ("4", "408 某一科测 <60", "该科回炉 5 天，后续科顺延；但不允许把 OS / 计网推到强化期", "宁可压计网到 1.5 周，也不留两科到强化"),
    ("5", "单词听写 <75%", "当周新词减半，复习翻倍（红线三）", "单词掉队会在 9 月真题期双倍反噬"),
]
r = 30
for p in patch:
    put_row(ws, r, [p[0], p[1], None, p[2], None, None, p[3], None], height=36)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
    ws.merge_cells(start_row=r, start_column=7, end_row=r, end_column=8)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    r += 1

section(ws, "四、五条红线", N, 36)
redlines = [
    "红线一：数学每天不能断。断 1 天 ≈ 倒退 2 天；其他科目可调，数学不行。",
    "红线二：408 每周必须有手写产出（代码或大题步骤），四科里任何一科都不能只过眼睛。",
    "红线三：单词听写 <75% 当天新词量减半，把时间全给复习。",
    "红线四：期末考撞车按 B 档降载，考完当周末集中补 8 小时，不停 5 天以上。",
    "红线五：每周日填「进度追踪」。没有实际数据的计划，三周内一定会跑偏。",
]
r = 37
for t in redlines:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
    c = ws.cell(row=r, column=1, value=t)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    c.border = BOX
    ws.row_dimensions[r].height = 26
    r += 1
widths(ws, {"A": 10, "B": 16, "C": 30, "D": 13, "E": 24, "F": 26, "G": 22, "H": 22})
ws.freeze_panes = "A6"
page(ws)

# ============================================================ 6 进度追踪
ws = wb.create_sheet("进度追踪")
ws.sheet_properties.tabColor = "548235"
N = 15
title(ws, "进度追踪（每周日晚上填一次，填完再排下周）", N)
note(ws, "填法：只需填「实际」列（粗体留空的那些），完成率与状态是公式自动算的。"
         "状态口径：≥90% 达标｜70–89% 偏紧｜<70% 需补丁（触发「阶段验收」第三条规则）。W9 为期末降载周，计划课时按 42h 记。", N, 2)
header(ws, 4, ["周次", "日期", "计划课时", "实际课时", "完成率", "数学题量目标", "数学实做",
               "408 选择目标", "408 选择实做", "408 大题目标", "408 大题实做", "听写正确率", "本周最大缺口", "状态", "下周调整"], height=40)

plan = [
    ("W1", "11.09–11.15", 70, 30, 40, 4), ("W2", "11.16–11.22", 70, 40, 40, 4),
    ("W3", "11.23–11.29", 70, 60, 45, 6), ("W4", "11.30–12.06", 70, 30, 50, 5),
    ("W5", "12.07–12.13", 70, 50, 50, 5), ("W6", "12.14–12.20", 70, 55, 45, 4),
    ("W7", "12.21–12.27", 70, 20, 50, 5), ("W8", "12.28–01.03", 70, 45, 50, 5),
    ("W9", "01.04–01.10", 42, 45, 50, 5), ("W10", "01.11–01.17", 70, 45, 45, 4),
    ("W11", "01.18–01.24", 70, None, 50, 5), ("W12", "01.25–01.31", 70, None, 55, 5),
]
r = 5
for w in plan:
    put_row(ws, r, [w[0], w[1], w[2], None, None, w[3], None, w[4], None, w[5], None, None, None, None, None], height=28)
    for col in (1, 2, 3, 6, 8, 10):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
    for col in (4, 7, 9, 11, 12):
        cell = ws.cell(row=r, column=col)
        cell.fill = LAX_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(name=FONT, size=10, bold=True, color="7F7F7F")
    ws.cell(row=r, column=12).number_format = PCT
    ws.cell(row=r, column=5, value=f'=IF(N(D{r})=0,"",D{r}/C{r})')
    ws.cell(row=r, column=5).number_format = PCT
    ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=5).border = BOX
    ws.cell(row=r, column=14, value=f'=IF(E{r}="","—",IF(E{r}>=0.9,"达标",IF(E{r}>=0.7,"偏紧","需补丁")))')
    ws.cell(row=r, column=14).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=14).border = BOX
    r += 1
last_data = r - 1
put_row(ws, r, ["合计", "12 周", f"=SUM(C5:C{last_data})",
                f'=IF(COUNT(D5:D{last_data})=0,"",SUM(D5:D{last_data}))', None,
                f"=SUM(F5:F{last_data})", f'=IF(COUNT(G5:G{last_data})=0,"",SUM(G5:G{last_data}))',
                f"=SUM(H5:H{last_data})", f'=IF(COUNT(I5:I{last_data})=0,"",SUM(I5:I{last_data}))',
                f"=SUM(J5:J{last_data})", f'=IF(COUNT(K5:K{last_data})=0,"",SUM(K5:K{last_data}))',
                None, None, None, None], height=28, bold=True)
ws.cell(row=r, column=5, value=f'=IF(N(D{r})=0,"",D{r}/C{r})')
ws.cell(row=r, column=5).number_format = PCT
for col in (1, 2, 3, 4, 6, 7, 8, 9, 10, 11):
    ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="center")

ws.conditional_formatting.add(f"N5:N{last_data}",
    CellIsRule(operator="equal", formula=['"达标"'], fill=OK_FILL))
ws.conditional_formatting.add(f"N5:N{last_data}",
    CellIsRule(operator="equal", formula=['"偏紧"'], fill=MID_FILL))
ws.conditional_formatting.add(f"N5:N{last_data}",
    CellIsRule(operator="equal", formula=['"需补丁"'], fill=WARN_FILL))

r += 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
c = ws.cell(row=r, column=1, value="周复盘三问（写在「本周最大缺口」里，每问一行）：① 这周哪一天塌了、为什么？② 哪个指标没达标、是量不够还是方法不对？"
                                    "③ 下周要不要切 B 档，或者动用一个补丁日？")
c.font = Font(name=FONT, size=10)
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
c.fill = BAND_FILL
c.border = BOX
ws.row_dimensions[r].height = 34
widths(ws, {"A": 7, "B": 13, "C": 9, "D": 9, "E": 9, "F": 12, "G": 9, "H": 12, "I": 11,
            "J": 11, "K": 11, "L": 10, "M": 34, "N": 10, "O": 26})
ws.freeze_panes = "C5"
page(ws)

# ============================================================ 7 错题本模板
ws = wb.create_sheet("错题本模板")
ws.sheet_properties.tabColor = "7030A0"
N = 11
title(ws, "错题本模板（字段固定，二刷只做「未掌握」）", N)
note(ws, "下面标了「示例数据」的两行只是格式示范，填自己的错题时直接覆盖。错因必须选五类之一，模糊的「粗心」不算错因。", N, 2)
note(ws, "示例数据 · 第 5–6 行：概念不清 / 计算失误各一条，用来示范「正确思路」应该写多短（不超过 3 行，二刷时能一眼看懂）。", N, 3)
header(ws, 4, ["编号", "日期", "科目", "章节", "题目来源", "错在哪（我的做法）", "错因分类",
               "正确思路（≤3 行）", "复盘次数", "最近复盘", "已掌握"], height=36)
samples = [
    (1, "2026-11-12", "数学", "极限", "660 第 12 题", "直接等价替换 tanx−sinx，忽略加减法不能随意替换", "概念不清",
     "tanx−sinx = sinx(1−cosx)/cosx ~ x³/2；等价替换只在乘除中用", 2, "2026-11-19", "是"),
    (2, "2026-11-14", "408", "线性表", "王道 2.3 综合 5", "单链表逆置时先断开 next 再保存，导致后半段丢失", "计算失误",
     "先存 p->next，再改 p->next=pre，最后 pre=p, p=q", 1, "2026-11-21", "否"),
]
r = 5
for s in samples:
    put_row(ws, r, list(s), height=40)
    for col in (1, 3, 7, 9, 11):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
for i in range(3, 31):
    put_row(ws, r, [i, None, None, None, None, None, None, None, None, None, None], height=30)
    for col in (1, 3, 7, 9, 11):
        ws.cell(row=r, column=col).alignment = Alignment(horizontal="center", vertical="center")
    r += 1

dv_reason = DataValidation(type="list",
                           formula1='"概念不清,计算失误,思路没想到,审题错,时间不够"',
                           allow_blank=True, showDropDown=False)
dv_reason.error = "只能选五类之一"
dv_reason.prompt = "选五类错因之一"
dv_subject = DataValidation(type="list", formula1='"数学,408,英语,政治"', allow_blank=True)
dv_ok = DataValidation(type="list", formula1='"是,否"', allow_blank=True)
ws.add_data_validation(dv_reason)
ws.add_data_validation(dv_subject)
ws.add_data_validation(dv_ok)
dv_reason.add(f"G5:G34")
dv_subject.add("C5:C34")
dv_ok.add("K5:K34")

r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
c = ws.cell(row=r, column=1,
            value="用法：① 当天做错的题当场登记（不抄题，只写页码/题号 + 错的思路）；② 每天 20:20 复盘时把到期错题过一遍，复盘次数 +1；"
                  "③ 每两周日把「复盘次数 ≥2 且最近一次能独立做对」的标「已掌握」；④ W11 错题二刷只做 K 列 = 否 的题，"
                  "目标是二刷正确率 ≥85%。")
c.font = Font(name=FONT, size=10, color="404040")
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
c.fill = BAND_FILL
c.border = BOX
ws.row_dimensions[r].height = 44
widths(ws, {"A": 6, "B": 12, "C": 8, "D": 12, "E": 16, "F": 34, "G": 12, "H": 38,
            "I": 9, "J": 12, "K": 9})
ws.freeze_panes = "C5"
page(ws)

# ============================================================ 8 资料清单
ws = wb.create_sheet("资料清单")
ws.sheet_properties.tabColor = "7F7F7F"
N = 5
title(ws, "资料清单（够用即可，不追新书）", N)
note(ws, "原则：主线资料一本做完再做下一本。同一科同时开两本书，是 12 周跑不完计划的最常见原因。"
         "「使用口径」列写的是本轮要做到什么程度——不写清楚，就容易变成「翻过」。", N, 2)
header(ws, 4, ["科目", "主线资料", "配套 / 备选", "使用口径（本轮做到什么程度）", "启动时间"])
mats = [
    ("数学二", "武忠祥《高等数学辅导讲义》+ 李永乐《线性代数辅导讲义》",
     "660 题（只做基础篇）、历年真题（1997 起）", "讲义例题先做后看解析；660 本轮做 420 道；真题推迟到 2027.03 之后", "本轮"),
    ("408", "王道四本单科书 + 王道历年真题解析",
     "教材：严蔚敏《数据结构》、唐朔飞《计算机组成原理》、汤小丹《操作系统》、谢希仁《计算机网络》",
     "每章课后选择题全做（本轮 570 道）、大题手写 4–6 道/周（本轮 57 道）", "本轮：四科一轮"),
    ("英语二", "红宝书 / 恋练有词 + 田静《句句真研》",
     "英语一真题 2005–2011（练阅读，本轮 28 篇精读）", "单词走完 5500 一轮 + 高频 1500 二轮；长难句按 D1/D2/D4/D7 滚动", "本轮"),
    ("政治", "徐涛《核心考案》+ 肖秀荣 1000 题",
     "肖八肖四必买；腿姐技巧班 / 背诵手册任选其一", "12 周内一本都不开，2027.11 启动（肖八 + 肖四，见「后续路线」）", "2027.11"),
]
r = 5
for m in mats:
    put_row(ws, r, list(m), height=56)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
widths(ws, {"A": 10, "B": 44, "C": 44, "D": 46, "E": 14})
ws.freeze_panes = "A5"
page(ws)

# ============================================================ 9 后续路线
ws = wb.create_sheet("后续路线")
ws.sheet_properties.tabColor = "A6A6A6"
N = 7
title(ws, "全年阶段路线（4 段 / 59 周，2026.11.09 — 2027.12.25 初试）", N)
note(ws, "口径与网页「阶段」页、Obsidian「阶段路线」一致：只有当前阶段排到周（本表前 12 周），"
         "后面阶段锁周数、主线与「必进门槛」，细节等前一阶段实测成绩出来再排——提前排死没有意义，只会让人照着跑。", N, 2)
header(ws, 4, ["阶段", "时间", "数学二主线", "408 主线", "英语二", "政治", "进入下一阶段的门槛"], height=38)
road = [
    ("一、一轮基础", "2026.11.09–2027.03.14（18 周）",
     "高数 7 周 + 线代 3 周 + 错题/总测 2 周；寒假 6 周 660 二刷 + 3 套 150 分卷",
     "数据结构 5 周 + 计组 4 周 + OS 2 周 + 计网 1 周；寒假四科二刷 + 2 套 150 分卷",
     "单词：红宝书 50 List 两遍 + 错词本（每天 55 分钟，一直滚到考前）",
     "不启动（2027.11 才开）",
     "数学 150 分卷 ≥100；408 150 分卷 ≥90；随机 100 道 408 选择 ≥65"),
    ("二、二轮基础", "2027.03.15–2027.06.27（15 周）",
     "复习全书高数 6 周 + 线代 3 周 + 880 基础篇 3 周 + 阶段测 3 周；660 二刷完",
     "四科二刷 + 大题模板（算法 / Cache / PV / 子网）+ 真题分类选择 2010–2018 + 2 套全真卷",
     "单词第三轮 + 阅读方法论 + 英语一 2005–2012 精读 16 篇",
     "不启动（2027.11 才开）",
     "数学 150 分卷 ≥110；408 随机 100 题选择 ≥80；四科大题模板能默写"),
    ("三、强化", "2027.06.28–2027.09.26（13 周）",
     "880 强化篇 5 周 + 线代强化 2 周 + 真题按章（2008–2015）4 周 + 阶段测 2 周",
     "四个高频专题（存储与流水线 / OS 内核 / 数据结构算法 / 网络协议栈）+ 真题按套 2010–2015",
     "阅读提速（英语二 2012–2015）+ 完型 / 新题型 / 翻译",
     "不启动（2027.11 才开）",
     "数学 150 分卷 ≥120；408 真题套卷 ≥105，选择错 ≤10"),
    ("四、真题", "2027.09.27–2027.12.26（13 周）",
     "真题 2016–2019、2020–2023 各 4 周（每周 2 套限时）+ 2024–2027 与模拟卷 3 周 + 错题三刷 2 周",
     "真题 2016–2019、2020–2023 各 4 周（每周 1 套 3h 限时）+ 2024–2027 与模拟卷 3 周 + 模板默写 2 周",
     "单词滚动 + 小作文 10 类 / 大作文三段式 + 英语二真题 2018–2027 按套",
     "11 月：核心考点 + 肖八选择；12 月：肖四选择 + 4 套大题背关键词",
     "12.20 前数学 ≥130、408 ≥115；真题选择错 ≤8、数学选择填空错 ≤2"),
]
r = 5
for row in road:
    put_row(ws, r, list(row), height=64)
    ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=r, column=2).alignment = Alignment(horizontal="center", vertical="center")
    r += 1
r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
c = ws.cell(row=r, column=1, value="提醒：400 分 = 政治 72 + 英语 76 + 数学 134 + 408 118。这条线里最难的不是单科分数，"
                                    "而是「四科同时不掉队」——所以每一段都写了具体门槛，达标再往下走；没过门槛先补 1–2 周，不要两段平行推进。")
c.font = Font(name=FONT, size=10)
c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
c.fill = BAND_FILL
c.border = BOX
ws.row_dimensions[r].height = 34
widths(ws, {"A": 12, "B": 22, "C": 36, "D": 36, "E": 32, "F": 26, "G": 36})
ws.freeze_panes = "A5"
page(ws)

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(exist_ok=True)
wb.save(DATA / "22408考研400分学习计划_v2改进版.xlsx")
print("saved")
