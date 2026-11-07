# -*- coding: utf-8 -*-
"""生成英语二计划 english-2028.json（只生成周与天，阶段由 build_phases.py 注入）。

口径（和数学二 / 408 同一时间轴）：
    一阶段 2026-11-09 ~ 2027-03-14  18 周  单词打底：红宝书 50 List 两遍 + 错词本
    二阶段 2027-03-15 ~ 2027-06-27  15 周  单词第三轮 + 阅读方法论 + 英语一真题精读
    三阶段 2027-06-28 ~ 2027-09-26  13 周  阅读提速 + 完型 / 新题型 / 翻译
    四阶段 2027-09-27 ~ 2027-12-26  13 周  大小作文 + 英语二真题按套

每周 6 个学习日 + 1 个复盘日（周日）。
运行：python3 gen_english_plan.py  然后 python3 build_phases.py && python3 build_v2.py
"""
import json
from pathlib import Path

START = "2026-11-09"
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def study_day(theme, title, learn, practice, checklist, minutes=55, reading="", kind="learn"):
    return dict(theme=theme, kind=kind, minutes=minutes, reading=reading, title=title,
                learn=learn, practice=practice, checklist=checklist)


def review_day(week, label):
    return dict(
        theme="review", kind="review", minutes=40,
        title=f"第 {week} 周复盘：{label}",
        learn=[
            "把本周错词本里的 1 级词过一遍（只看英文想中文）",
            f"自测 50 词：本周新词随机抽（限时 8 分钟）",
            "写 3 条下周动作：哪类词总记不住、哪一步最费时间",
        ],
        practice=["把这周阅读/题型的错题按错因归一次类（定位错 / 理解错 / 生词卡住）"],
        checklist=["本周错词过完", "50 词自测 ≥40", "下周 3 条动作写下来"],
    )


# ---------------------------------------------------------------- 一阶段：单词打底（18 周 / 108 学习日）
VOCAB_FOCUS = [
    "先英文后中文：遮住中文能想起意思才算过",
    "复习昨天标出来的生词（15 分钟）",
    "词根词缀：把同根词串起来记，一次记一串",
    "真题例句：在句子里记搭配，不背孤立的词",
    "拼写自测：听写 20 个易混词（形近 / 音近）",
    "熟词僻义 + 高频搭配：考研最爱考第二义",
]


def phase1_days():
    out = []
    for i in range(50):                         # d1–50：一轮，按每日单词量推进
        out.append(study_day(
            "list1", f"单词 · 今日新词（{i+1}/50）",
            ["新词：按「每日单词量」背（默认 100 词），先读英文圈生词再查中文",
             VOCAB_FOCUS[i % 6],
             "生词进错词本，标 1/2/3 级：1 = 眼熟、3 = 完全不认识"],
            ["遮中文自测 30 个词，说不出的回标 1 级",
             "挑 5 个动词 + 5 个形容词各造 1 句（造不出就只读例句）"],
            ["今日新词背完（≥40 分钟）", "昨天的生词复习完", "错词本新增 ≤30 个，分级标好"],
            reading="红宝书（按今日单词量推进）",
        ))
    for g in range(5):                          # d51–55：一轮复盘
        out.append(study_day(
            "review1", f"单词 · 一轮复盘 {g+1}/5",
            ["只看错词本里的 1 级词，按词根 / 主题重新分组",
             "能串起来的放一起记，别按字母顺序硬背"],
            ["遮中文过一遍，仍不会的标成重点词，抄到错词本第一页"],
            ["这一段的 1 级词过完", "重点词表更新完"],
        ))
    for i in range(10):                         # d56–65：自测
        out.append(study_day(
            "self1", f"单词 · 自测 {i+1}/10（100 词）",
            ["随机抽 100 词：只看英文写中文，限时 15 分钟",
             "对答案，错词回错词本，标 3 级"],
            ["错词抄 2 遍（只抄英文 + 中文首字）"],
            ["自测 ≥80 分（错 ≤20 个）", "错词当天过一遍"],
            kind="practice",
        ))
    for k in range(25):                         # d66–90：二轮，只查不认识的
        out.append(study_day(
            "list2", f"单词 · 二轮（{k+1}/25）",
            ["二轮：按每日单词量过第二遍，会的直接过，只查不认识的",
             "遮中文快速过，1 分钟 10 个词算正常速度"],
            ["二轮结束仍不认识的标 3 级，单独抄一页"],
            ["二轮今日量过完（≤40 分钟）", "3 级词抄到「顽固词」页"],
        ))
    for g in range(8):                          # d91–98：二轮复盘
        out.append(study_day(
            "review2", f"单词 · 二轮复盘 {g+1}/8",
            ["顽固词页 + 二轮标出来的 3 级词过一遍",
             "把仍记不住的 20 个词编成 3 个小故事（能记住就行）"],
            ["遮中文再测一次，仍错的单独列出来"],
            ["今天的顽固词过完", "顽固词 ≤60 个"],
        ))
    for k in range(10):                         # d99–108：真题高频词 + 熟词僻义
        out.append(study_day(
            "kaoyan_words", f"真题高频词 {k+1}/10 + 熟词僻义",
            ["真题高频词：这些词在真题里反复出现，优先认",
             "熟词僻义 10 个（如 address 处理、figure 认为）记到错词本"],
            ["拿 2 个高频词套进真题例句读 2 遍", "把熟词僻义遮住中文说一遍"],
            ["高频词过完", "熟词僻义 10 个抄进错词本", "能说出 5 个词的真题常见搭配"],
        ))
    assert len(out) == 108, len(out)
    return out


# ---------------------------------------------------------------- 二阶段：单词 + 阅读（15 周 / 90 学习日）
METHODS = [
    "长难句第一步：先找主干——谁、做了什么、结果如何",
    "从句全用括号括起来，先读括号外，再读括号里",
    "题型分类：细节题 / 主旨题 / 态度题 / 词义题 / 推理题",
    "定位三步：题干关键词 → 回原文找同义替换 → 对比选项",
    "干扰项长什么样：绝对化、偷换概念、以偏概全、无中生有",
    "干扰项进阶：把原文换个说法，但程度变了（most → some）",
    "正确选项：同义替换，不是原文照抄",
    "细节题：定位句的上下文各看 1 句",
    "主旨题：看首末段 + 每段首句，不选细节",
    "态度题：找评价性形容词 / 副词，中立态度一般不是答案",
    "推理题：只推一步，推两步的一定错",
    "词义题：回原文找上下文线索，不靠背单词",
    "时间分配：每篇 18 分钟，先看题再读文（也可先读文，固定一种）",
    "做题顺序：会做的先做，一题卡 2 分钟就跳过",
    "生词处理：不查词也能做，靠逻辑和上下文猜",
    "复盘标准：错题必须写错因，不写等于没复盘",
    "翻译练习：每篇挑 2 个长难句手写中文",
    "整篇复述：合上书用 3 句话说出文章讲了什么",
]


def phase2_days():
    out = []
    for i in range(18):                         # d1–18：方法论
        out.append(study_day(
            "reading_method", f"阅读方法论 {i+1}/18 + 单词",
            [f"方法论：{METHODS[i]}",
             "拿 1 篇旧真题只练这一个动作（不掐时间、不对答案也行）",
             "单词：今日量 + 错词本（30 分钟）"],
            ["把这条方法记到阅读笔记本第 1 页"],
            ["方法论这条能用自己的话讲一遍", "用旧真题走一遍流程", "单词 2 List 过完"],
            reading="阅读笔记本 + 英语一 2005 真题",
        ))
    # d19–66：英语一真题精读，8 周，每周 2 篇精读 + 1 次限时
    years = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]
    for w, year in enumerate(years):
        for t in (1, 2):
            out.append(study_day(
                "reading_real", f"精读 {year} Text {t}（做题）",
                [f"先做题：{year} 英语一 Text {t}，18 分钟，不查词不暂停",
                 "对答案只看错因，不看解析",
                 "单词：今日量（30 分钟）"],
                ["逐句翻译，长难句用括号标从句", "生词入错词本，标真题出处"],
                ["18 分钟内做完 4 题", "逐句翻译完", "错题写错因（定位 / 理解 / 选项陷阱）"],
                reading=f"英语一 {year} Text {t}", kind="practice",
            ))
            out.append(study_day(
                "reading_real", f"精读 {year} Text {t}（复盘）",
                [f"重新读 {year} Text {t}，把每道题的定位句标出来",
                 "对照解析，只改自己错的那 1–2 题",
                 "单词：今日量 + 错词本（30 分钟）"],
                ["手写 2 个长难句的中文", "把这篇文章的 10 个生词做成小卡片"],
                ["定位句标完", "2 个长难句翻译完", "10 个生词进错词本"],
                reading=f"英语一 {year} Text {t}",
            ))
        out.append(study_day(
            "reading_test", f"{year} 阅读限时 2 篇",
            [f"{year} 英语一 Text 3 + 4：两篇 36 分钟连做",
             "做完只对答案，记录正确率和用时"],
            ["错题写错因", "单词：今日量 + 错词本（30 分钟）"],
            ["两篇 36 分钟内做完", "正确率记到成绩表", "错题错因写完"],
            kind="practice",
        ))
    # d67–82：阶段测
    for i in range(16):
        out.append(study_day(
            "reading_test", f"阅读阶段测 {i+1}/16",
            [f"限时 4 篇（72 分钟），从做过的年份里随机抽",
             "对答案，统计细节题 / 主旨题 / 推理题各自错几个"],
            ["错题按题型归类，找出现次数最多的错因", "单词：今日量 + 错词本（30 分钟）"],
            ["4 篇 ≤72 分钟", "正确率 ≥60%（错 ≤6 个）", "错因统计表更新"],
            kind="practice",
        ))
    # d83–98：阅读二刷 + 单词
    for i in range(16):
        out.append(study_day(
            "reading_2nd", f"阅读二刷 {i+1}/16 + 单词",
            ["二刷之前错得最多的 2 篇：先不看答案，再做一遍",
             "对比两次做法，看是哪一步改了",
             "单词：今日量 + 错词本（30 分钟）"],
            ["把这篇的定位句 + 干扰项陷阱写成一页笔记"],
            ["二刷 2 篇", "两次做法差异写下来", "单词 3 List 过完"],
            kind="practice",
        ))
    assert len(out) == 90, len(out)
    return out


# ---------------------------------------------------------------- 三阶段：阅读 + 题型（13 周 / 78 学习日）
CLOZE_TIPS = [
    "逻辑衔接词：however / therefore / moreover 决定前后句关系",
    "固定搭配：动词 + 介词，先把搭配背熟再看选项",
    "上下文复现：空格答案常在上下句原词复现",
    "词义辨析：先判断词性，再看感情色彩",
    "排除法：明显不搭的先划掉，剩下的按语境选",
    "时间：15 分钟做完 20 题，不会的标记后补",
]
NEWTYPE_TIPS = [
    "七选五：先看选项首尾句，再找代词和逻辑词",
    "七选五：段落首句一般是主题句，空格前后要能接上",
    "排序题：先定首段，再找时间 / 逻辑顺序",
    "小标题：每段概括成 5 个字再匹配",
    "复核：填完通读一遍，看逻辑是否顺",
    "时间：15 分钟，别在一题上死磕",
]
WRITING_SMALL = [
    "书信格式：称呼 / 开头 / 主体 / 结尾 / 署名，五件套",
    "建议信：先肯定，再给 2 条建议，最后期待回复",
    "道歉信：说明原因 + 补救方案 + 再次致歉",
    "推荐信：推荐什么 + 2 个理由 + 期待采纳",
    "感谢信：具体感谢 + 影响 + 回馈意愿",
    "通知：标题 + 时间地点 + 内容 + 联系方式",
    "辞职 / 请求信：一句话说明目的，不要铺垫太长",
    "小作文高频套句 10 句，背到能默",
    "小作文 100 词：3 段，别写超（超了扣分）",
    "默写一篇完整的建议信",
]
WRITING_BIG = [
    "图表描述：先总趋势，再极值，再对比，最后原因",
    "数据表达：increase / decline / remain stable + 幅度词",
    "三段式：描述图表 → 分析原因 → 总结建议",
    "开头段模板 3 套，按图表类型（柱 / 线 / 饼）选",
    "原因段：经济、社会、个人三个角度各写一句",
    "结尾段：预测趋势 / 提出建议，不要空喊口号",
    "词汇升级：把 important 换成 crucial / vital",
    "句型升级：定语从句 + 状语从句各 1 个就够",
    "大作文 160 词，写完检查时态和主谓一致",
    "默写一篇完整的大作文",
]


def phase3_days():
    out = []
    for w in range(4):                          # 4 周：阅读提速 + 单词
        for i in range(6):
            out.append(study_day(
                "reading_speed", f"阅读提速 {w+1}/4 · 第 {i+1} 天 + 单词",
                [f"限时阅读 1 篇（18 分钟）：英语二 {2012 + w} 真题",
                 "做完立刻对答案，统计题型错因",
                 "单词：今日量 + 错词本（30 分钟）"],
                ["把这篇的定位句标出来", "生词入错词本"],
                ["18 分钟内做完", "正确率记到成绩表", "单词 3 List 过完"],
                reading=f"英语二 {2012+w} 真题阅读", kind="practice",
            ))
    for w in range(3):                          # 3 周：完型
        for i in range(6):
            out.append(study_day(
                "cloze", f"完型 {w*6+i+1}/18 + 单词",
                [f"完型技巧：{CLOZE_TIPS[(w*6+i) % len(CLOZE_TIPS)]}",
                 f"做题：{2013+w} 英语一完型 20 题，15 分钟，做完只对答案",
                 "单词：今日量 + 错词本（30 分钟）"],
                ["把 10 个固定搭配抄到搭配本", "错题写错因（搭配 / 逻辑 / 词义）"],
                ["完型 15 分钟内做完", "正确率 ≥50%", "10 个搭配抄完"],
                reading=f"英语一 {2013+w} 完型", kind="practice",
            ))
    for w in range(3):                          # 3 周：新题型
        for i in range(6):
            out.append(study_day(
                "newtype", f"新题型 {w*6+i+1}/18 + 单词",
                [f"新题型技巧：{NEWTYPE_TIPS[(w*6+i) % len(NEWTYPE_TIPS)]}",
                 f"做题：{2013+w} 英语一新题型，15 分钟",
                 "单词：今日量 + 错词本（30 分钟）"],
                ["把选项首尾句标出来，看代词指代", "错题写错因"],
                ["新题型 15 分钟内做完", "错 ≤2 个", "代词指代标完"],
                reading=f"英语一 {2013+w} 新题型", kind="practice",
            ))
    for w in range(3):                          # 3 周：翻译
        for i in range(6):
            out.append(study_day(
                "translation", f"翻译 {w*6+i+1}/18 + 单词",
                [f"翻译：{2013+w} 英语一翻译第 {i+1} 句，先拆句子再译",
                 "译完对照参考译文，看是结构错还是词义错",
                 "单词：今日量 + 错词本（30 分钟）"],
                ["把这句话的主干和从句分别写出来", "积累 5 个翻译常用表达"],
                ["1 句翻译完（≤8 分钟）", "对照参考译文改一遍", "5 个表达记下"],
                reading=f"英语一 {2013+w} 翻译", kind="practice",
            ))
    assert len(out) == 78, len(out)
    return out


# ---------------------------------------------------------------- 四阶段：作文 + 真题（13 周 / 78 学习日）
def phase4_days():
    out = []
    for i, tip in enumerate(WRITING_SMALL):      # 10 天：小作文模板
        out.append(study_day(
            "writing_small", f"小作文 {i+1}/10 · 模板",
            [f"模板：{tip}", "把这段模板抄一遍，再默写一遍", "单词：今日量 + 错词本（20 分钟）"],
            ["用这个模板写 1 篇（100 词，25 分钟）"],
            ["模板能默写", "写 1 篇并自查格式", "单词 1 List 过完"],
            reading="小作文模板", kind="learn",
        ))
    for i in range(14):                          # 14 天：小作文默写 / 改写
        out.append(study_day(
            "writing_small", f"小作文 默写 {i+1}/14",
            ["默写一篇完整小作文（15 分钟）", "对照范文改：格式、时态、拼写", "单词：今日量 + 错词本（20 分钟）"],
            ["把改出来的错句重写一遍"],
            ["默写 1 篇", "改完 3 处以上错误", "单词 1 List"],
            kind="practice",
        ))
    for i, tip in enumerate(WRITING_BIG):        # 10 天：大作文模板
        out.append(study_day(
            "writing_big", f"大作文 {i+1}/10 · 模板",
            [f"模板：{tip}", "抄一遍，再默写一遍", "单词：今日量 + 错词本（20 分钟）"],
            ["按这个模板写 1 篇（160 词，35 分钟）"],
            ["模板能默写", "写 1 篇", "单词 1 List"],
            reading="大作文模板",
        ))
    for i in range(14):                          # 14 天：大作文默写
        out.append(study_day(
            "writing_big", f"大作文 默写 {i+1}/14",
            ["默写一篇大作文（20 分钟）", "对照范文改：图表描述、连接词、时态", "单词：今日量 + 错词本（20 分钟）"],
            ["把改出来的错句重写一遍"],
            ["默写 1 篇", "改完错误", "单词 1 List"],
            kind="practice",
        ))
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    for y in years:                              # 6 套真题，每套 2 天（做 + 复盘）
        out.append(study_day(
            "zhenti", f"英语二 {y} 真题（套卷）",
            [f"{y} 英语二整卷：180 分钟，按考试时间做（14:00–17:00）",
             "作文也要写，不许跳过"],
            ["对答案，记录各题型得分"],
            ["3 小时内做完", "作文写完", "各题型得分记到成绩表"],
            reading=f"英语二 {y} 真题", kind="practice",
        ))
        out.append(study_day(
            "zhenti", f"英语二 {y} 真题（复盘）",
            ["重做错题，只看错的那几题", "统计：阅读错几个、完型错几个、翻译扣几分", "单词：今日量 + 错词本（20 分钟）"],
            ["把这篇卷子的 10 个高频生词抄下来"],
            ["错题重做", "数据记到成绩表", "10 个生词"],
            kind="practice",
        ))
    # 2024–2027 四套：限时 + 复盘
    for y in (2024, 2025, 2026, 2027):
        out.append(study_day(
            "zhenti", f"英语二 {y} 真题（限时）",
            [f"{y} 英语二整卷：180 分钟，完全按考试流程",
             "做完只对答案，不马上复盘，留到第二天"],
            ["第二天看错题，只看错的题"],
            ["3 小时内做完", "作文写完", "得分记表"],
            kind="practice",
        ))
        out.append(study_day(
            "zhenti", f"英语二 {y} 真题（复盘）",
            ["只看错题，重做一遍", "统计四篇阅读分别错几个", "作文对照范文改"],
            ["把这套卷子的高频生词抄下来"],
            ["错题重做", "数据记表", "高频生词 10 个"],
            kind="practice",
        ))
    # 考前滚动 10 天
    for i in range(10):
        out.append(study_day(
            "final", f"考前滚动 {i+1}/10",
            ["默写小作文 1 篇 + 大作文 1 篇", "真题错题回看：只做错过的题", "单词：错词本 1–2 级词过一遍"],
            ["把两篇作文的模板再默一遍"],
            ["作文默写 2 篇", "错题回看 20 题", "错词本过完"],
            kind="practice",
        ))
    assert len(out) == 78, len(out)
    return out


THEME_LABEL = {
    "list1": "单词一轮", "review1": "一轮复盘", "self1": "单词自测", "list2": "单词二轮",
    "review2": "二轮复盘", "kaoyan_words": "真题高频词",
    "reading_method": "阅读方法论", "reading_real": "真题精读", "reading_test": "阅读限时测",
    "reading_2nd": "阅读二刷", "reading_speed": "阅读提速",
    "cloze": "完型", "newtype": "新题型", "translation": "翻译",
    "writing_small": "小作文", "writing_big": "大作文", "zhenti": "真题套卷", "final": "考前冲刺",
    "review": "周复盘",
}

WEEK_GOAL = {
    "单词一轮": "6 个 List 新词全部过一遍，错词本按 1/2/3 级标好",
    "一轮复盘": "这一段的 1 级词过完，顽固词收敛到 60 个以内",
    "单词自测": "自测 100 词 ≥80 分",
    "单词二轮": "每天 2 List，只查不认识的，顽固词单独记",
    "二轮复盘": "顽固词页过一遍，仍不会的编成小故事",
    "真题高频词": "高频词 100 个 + 熟词僻义 10 个，能套进真题例句",
    "阅读方法论": "每天一条方法，能用旧真题走一遍流程",
    "真题精读": "每周 2 篇精读 + 1 次限时，错题全部写错因",
    "阅读限时测": "限时 4 篇，正确率 ≥60%",
    "阅读二刷": "二刷错得最多的篇目，找出改在哪一步",
    "阅读提速": "每篇 18 分钟，正确率不低于二阶段的水平",
    "完型": "15 分钟做完 20 题，固定搭配抄满一页",
    "新题型": "15 分钟做完，错 ≤2 个",
    "翻译": "每天 1 句，对照参考译文改结构",
    "小作文": "模板能默写，10 类书信各写过 1 篇",
    "大作文": "三段式模板能默写，10 篇图表各写过 1 篇",
    "真题套卷": "3 小时内整卷做完，作文不许空",
    "考前冲刺": "作文默写 + 错题回看，不碰新题",
}


def build():
    days = phase1_days() + phase2_days() + phase3_days() + phase4_days()
    assert len(days) == 354, len(days)
    weeks = []
    idx = 0
    for w in range(1, 60):
        chunk = days[idx: idx + 6]
        idx += 6
        # 本周标题 = 周一那天的主题（具体到 List / 篇目），太长就退回主题名
        themes = [d["theme"] for d in chunk]
        main = max(set(themes), key=themes.count)
        label = THEME_LABEL[main]
        title = chunk[0]["title"]
        for suf in (" + 单词", "（做题）", "（复盘）", "（套卷）"):
            title = title.replace(suf, "")
        title = title.strip()
        if w <= 9:
            title = f"单词一轮 · 第 {w} 周"
        elif w <= 11:
            title = "单词一轮复盘 + 自测"
        elif w <= 15:
            title = f"单词二轮 · 第 {w - 11} 周"
        elif w <= 18:
            title = "真题高频词 + 熟词僻义"
        if len(title) > 42 or not title:
            title = f"{label} · 第 {w} 周"
        week_days = []
        for i, d in enumerate(chunk):
            day_id = f"e{w}d{i+1}"
            week_days.append(dict(
                id=day_id, weekday=WEEKDAYS[i], title=d["title"], minutes=d["minutes"],
                kind=d["kind"], reading=d["reading"], learn=d["learn"],
                practice=d["practice"], checklist=d["checklist"],
            ))
        week_days.append(dict(
            id=f"e{w}d7", weekday="周日", title=f"第 {w} 周复盘：{label}",
            minutes=40, kind="review", reading="",
            learn=review_day(w, label)["learn"],
            practice=review_day(w, label)["practice"],
            checklist=review_day(w, label)["checklist"],
        ))
        weeks.append(dict(
            week=w, title=title,
            goal=WEEK_GOAL.get(label, "完成本周任务，错题当天消化"),
            target=f"6 个学习日 · 1 次周复盘（{label}）",
            check="",
            days=week_days,
        ))
    plan = {
        "id": "english-2028",
        "title": "英语 全年计划 · 单词贯穿 + 阅读 / 题型 / 作文",
        "subject": "英语二",
        "level": "单词起步（红宝书 6000 词）",
        "goal": "一阶段：红宝书两遍，错词本建起来，100 词自测 ≥80",
        "tools": "红宝书《考研英语词汇》、英语一 2005–2014 真题、英语二 2010–2023 真题",
        "dailyMinutes": 55,
        "startDate": START,
        "wordBook": {"name": "红宝书", "total": 6590, "lists": 50,
                     "startDone": 949, "startCycle": 1, "defaultPerDay": 100},
        "source": {"note": "由 gen_english_plan.py 生成；阶段由 build_phases.py 按四段时间线注入"},
        "weeks": weeks,
    }
    out = DATA / "english-2028.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{out.name}: {len(weeks)} 周 / {sum(len(w['days']) for w in weeks)} 天 / "
          f"{sum(1 for w in weeks for d in w['days'] if d['kind'] in ('learn','practice'))} 学习日")


if __name__ == "__main__":
    build()
