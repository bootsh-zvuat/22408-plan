# -*- coding: utf-8 -*-
"""把网页版计划从「22 周 · 两科错峰」重排成「12 周 · 两科每日推进」，与 Excel v2 同图。

保留原有 66 节/科的正文（learn/reading/practice/exercises/checklist 全部沿用），
只改：周次归属、日期、周标题/验收/题量、检查点；操作系统 3 处、计网 6 处做合并。
运行：python3 rebuild_app_plan.py  然后 python3 build_v2.py
"""
import json, copy, re

START = "2026-11-09"


def load(path):
    return json.load(open(path, encoding="utf-8"))


def index_sessions(plan):
    """id -> 完整 day 记录（仅 learn/practice）"""
    out = {}
    for w in plan["weeks"]:
        for d in w["days"]:
            if d["kind"] in ("learn", "practice"):
                out[d["id"]] = d
    return out


def rest(text):
    return ("rest", text)


def merge(idx, ids, title, reading, extra_learn=None, extra_ck=None, ex_n=2):
    """把多个原小节合并成一个新小节：正文取并集（去重），课后题只留前 ex_n 道。"""
    parts = [idx[i] for i in ids]
    learn, practice, ck, exs = [], [], [], []
    for p in parts:
        for x in p.get("learn") or []:
            if x not in learn:
                learn.append(x)
        for x in p.get("practice") or []:
            if x not in practice:
                practice.append(x)
        for x in p.get("checklist") or []:
            if x not in ck:
                ck.append(x)
        for e in p.get("exercises") or []:
            if all(e["title"] != old["title"] for old in exs):
                exs.append(e)
    if extra_learn:
        learn = list(extra_learn) + learn
    if extra_ck:
        ck = ck + list(extra_ck)
    return {
        "id": parts[0]["id"],
        "title": title,
        "minutes": 120,
        "kind": parts[-1]["kind"] if len(parts) > 1 else parts[0]["kind"],
        "learn": learn[:7],
        "reading": reading,
        "practice": practice[:6],
        "exercises": exs[:ex_n],
        "checklist": ck[:6],
    }


def single(idx, sid):
    return copy.deepcopy(idx[sid])


WEEKDAY = ["周一", "周二", "周三", "周四", "周五", "周六"]


def build_week(spec, idx, week_no):
    """spec['days'] 必须给 6 个（周一–周六）；周日统一为复盘/测验。"""
    assert len(spec["days"]) == 6, (spec["week"], len(spec["days"]))
    days = []
    for i, item in enumerate(spec["days"]):
        if isinstance(item, tuple) and item[0] == "rest":
            days.append({"id": "m%d_%d_rest" % (week_no, i), "weekday": WEEKDAY[i],
                         "title": item[1], "minutes": 0, "kind": "rest", "learn": [],
                         "reading": "本周讲义 + 课后题；错题本里还没掌握的题", "practice": [],
                         "exercises": [], "checklist": []})
        elif isinstance(item, dict):
            d = item
            d["weekday"] = WEEKDAY[i]
            days.append(d)
    rv = spec["review"]
    days.append({
        "id": rv.get("id", "w%d_review" % week_no), "weekday": "周日",
        "title": rv["title"], "minutes": rv.get("minutes", 60),
        "kind": "review", "learn": rv.get("learn", []),
        "reading": rv.get("reading", "错题本 + 本周王道/讲义章节"),
        "practice": rv.get("practice", ["重做本周错题", "核对另一科目本周进度"]),
        "exercises": [],
        "checklist": rv["checklist"],
    })
    return {"week": week_no, "title": spec["title"], "goal": spec["goal"],
            "target": spec["target"], "check": spec.get("check", ""),
            "days": days}


# ============================================================ 数学二（66 节 → 12 周）
def math_weeks(idx):
    W = []
    W.append(dict(week=1, title="函数、极限与连续",
                  goal="极限限时 30 题正确率 ≥85%；可导/连续关系辨析 5 题全对；660 题 30 道完成",
                  target="660 题 30 道 + 讲义例题 20 道", check="",
                  days=[single(idx, "w1d1"), single(idx, "w1d3"), single(idx, "w1d5"),
                        single(idx, "w2d1"), single(idx, "w2d3"), single(idx, "w2d5")],
                  review=dict(title="第 1 周复盘：极限与连续的错题重做",
                              checklist=["极限等价替换不再混用加减法", "间断点分类能一次说全", "错题本已登记"])))
    W.append(dict(week=2, title="导数与微分 + 微分中值定理",
                  goal="中值定理证明 8 题独立完成 ≥6；求导法则不查书；660 题 40 道",
                  target="660 题 40 道 + 中值定理证明 8 道", check="",
                  days=[single(idx, "w3d1"), single(idx, "w3d3"), single(idx, "w3d5"),
                        single(idx, "w4d1"), single(idx, "w4d3"), single(idx, "w4d5")],
                  review=dict(title="第 2 周复盘：求导与中值定理",
                              checklist=["罗尔/拉格朗日/柯西的适用条件不混", "构造辅助函数有套路", "错题本已登记"])))
    W.append(dict(week=3, title="导数应用收尾 + 不定积分",
                  goal="不等式证明 5 题全对；积分专项 40 题 ≥85%；660 题 60 道",
                  target="660 题 60 道（积分 40）", check="",
                  days=[single(idx, "w5d1"), single(idx, "w5d3"), single(idx, "w5d5"),
                        single(idx, "w6d1"), single(idx, "w6d3"), single(idx, "w6d5")],
                  review=dict(title="第 3 周复盘：导数应用 + 积分方法",
                              checklist=["凑微分与分部积分选择果断", "有理函数积分步骤完整", "错题本已登记"])))
    W.append(dict(week=4, title="定积分及其应用 + 阶段测一",
                  goal="高数上 100 分卷 ≥75；反常积分敛散判定 10 题全对",
                  target="660 题 30 道 + 阶段测 1 套", check="检查点 1：高数上 100 分卷 ≥75",
                  days=[single(idx, "w7d1"), single(idx, "w7d3"), single(idx, "w7d5"),
                        single(idx, "w8d1"), single(idx, "w8d3"), single(idx, "w8d5")],
                  review=dict(title="阶段测一：高数上 100 分（限时 2 小时）",
                              checklist=["限时完成，不查书不翻笔记", "对答案只记错因不记分数", "错题当天登记进错题本"])))
    W.append(dict(week=5, title="多元函数微分学",
                  goal="条件极值 5 题全对；二阶偏导不出错；660 题 50 道",
                  target="660 题 50 道", check="",
                  days=[single(idx, "w9d1"), single(idx, "w9d3"), single(idx, "w9d5"),
                        single(idx, "w10d1"), single(idx, "w10d3"), single(idx, "w10d5")],
                  review=dict(title="第 5 周复盘：多元微分",
                              checklist=["复合与隐函数求导链条清楚", "拉格朗日乘数法步骤完整", "错题本已登记"])))
    W.append(dict(week=6, title="二重积分",
                  goal="二重积分换序 10 题全对；极坐标与对称性会用；660 题 55 道",
                  target="660 题 55 道", check="",
                  days=[single(idx, "w11d1"), single(idx, "w11d3"), single(idx, "w11d5"),
                        single(idx, "w12d1"), single(idx, "w12d3"), single(idx, "w12d5")],
                  review=dict(title="第 6 周复盘：二重积分",
                              checklist=["换序先画区域再写限", "极坐标雅可比 r 不丢", "错题本已登记"])))
    W.append(dict(week=7, title="常微分方程 + 阶段测二",
                  goal="高数下 100 分卷 ≥75；一阶线性通解不查书；二阶常系数 10 题全对",
                  target="660 题 20 道 + 阶段测 1 套", check="检查点 2：高数下 100 分卷 ≥75",
                  days=[single(idx, "w13d1"), single(idx, "w13d3"), single(idx, "w13d5"),
                        single(idx, "w14d1"), single(idx, "w14d3"), single(idx, "w14d5")],
                  review=dict(title="阶段测二：高数下 100 分（限时 2 小时）",
                              checklist=["限时完成，不查书", "错题按章归类", "高数错题本首轮整理完"])))
    W.append(dict(week=8, title="线性代数：行列式与矩阵",
                  goal="行列式 10 题全对；秩与初等变换关系能说清；660 题 45 道",
                  target="660 题 45 道", check="",
                  days=[single(idx, "w15d1"), single(idx, "w15d3"), single(idx, "w15d5"),
                        single(idx, "w16d1"), single(idx, "w16d3"), single(idx, "w16d5")],
                  review=dict(title="第 8 周复盘：行列式与矩阵",
                              checklist=["范德蒙德与分块行列式会用", "逆矩阵两种求法都会", "错题本已登记"])))
    W.append(dict(week=9, title="线性代数：向量组与线性方程组",
                  goal="线性相关判定 5 题全对；基础解系写得对；660 题 45 道",
                  target="660 题 45 道", check="",
                  days=[single(idx, "w17d1"), single(idx, "w17d3"), single(idx, "w17d5"),
                        single(idx, "w18d1"), single(idx, "w18d3"), single(idx, "w18d5")],
                  review=dict(title="第 9 周复盘：向量组与方程组",
                              checklist=["极大无关组能独立求", "非齐次通解结构写对", "错题本已登记"])))
    W.append(dict(week=10, title="线性代数：特征值与二次型 + 阶段测三",
                  goal="线代 100 分卷 ≥75；能判断矩阵可否相似对角化并说理由",
                  target="660 题 45 道 + 阶段测 1 套", check="检查点 3：线性代数 100 分卷 ≥75",
                  days=[single(idx, "w19d1"), single(idx, "w19d3"), single(idx, "w19d5"),
                        single(idx, "w20d1"), single(idx, "w20d3"), single(idx, "w20d5")],
                  review=dict(title="阶段测三：线性代数 100 分（限时 2 小时）",
                              checklist=["限时完成，不查书", "正定判定 5 题全对", "线代错题本建立"])))
    W.append(dict(week=11, title="高数与线代错题二刷",
                  goal="错题二刷正确率 ≥85%；跨章综合题 10 道能独立完成",
                  target="错题本未掌握题全部重做", check="",
                  days=[single(idx, "w21d1"), single(idx, "w21d3"), single(idx, "w21d5"),
                        single(idx, "w22d1"), single(idx, "w22d3"),
                        rest("机动：只做错题本（不上新资料）")],
                  review=dict(title="第 11 周复盘：错题二刷收口",
                              checklist=["错题本标「已掌握」的比例 ≥85%", "跨章综合题不再卡第一步", "总测范围已确认"])))
    W.append(dict(week=12, title="基础阶段总测",
                  goal="数学 150 分卷 ≥100；寒假 6 周计划成形",
                  target="150 分总测 1 套（限时 3 小时）", check="检查点 4：数学 150 分总测 ≥100",
                  days=[single(idx, "w22d5"), rest("机动：错题本与公式默写"),
                        rest("机动：高数/线代框架图默写"), rest("机动：总测前只回看错题"),
                        rest("机动：调整作息，按考试时间起床"), rest("机动：寒假计划初稿")],
                  review=dict(title="基础阶段总测：数学 150 分（限时 3 小时）",
                              checklist=["限时 3 小时，按考试节奏", "对答案后写 3 条失分原因", "据此定寒假 6 周计划"])))
    return W


# ============================================================ 408（57 节 → 12 周）
def cs_weeks(idx):
    W = []
    W.append(dict(week=1, title="数据结构①：绪论与线性表",
                  goal="手写单链表逆置不查书；复杂度分析 5 题全对；选择 40 题完成",
                  target="选择 40 + 大题 4（逆置/删除/合并）", check="",
                  days=[single(idx, "w1d2"), single(idx, "w1d4"), single(idx, "w1d6"),
                        single(idx, "w2d2"),
                        rest("今日无新课：顺序表/单链表代码各手写一遍"),
                        rest("今日无新课：线性表选择题错题重做")],
                  review=dict(title="第 1 周复盘：线性表与复杂度",
                              checklist=["四类逻辑结构与四类存储结构能对上号", "头结点作用说清楚", "错题本已登记"])))
    W.append(dict(week=2, title="数据结构②：栈、队列、串与数组",
                  goal="循环队列判空判满公式默写；KMP next 手推 3 题全对；选择 40 题",
                  target="选择 40 + 大题 4（循环队列、KMP next）", check="",
                  days=[single(idx, "w2d4"), single(idx, "w2d6"), single(idx, "w3d2"),
                        single(idx, "w3d4"), single(idx, "w3d6"),
                        rest("今日无新课：KMP next 数组手推 5 题")],
                  review=dict(title="第 2 周复盘：栈队列串",
                              checklist=["队列判空判满三件套默写", "next 与 nextval 不混", "错题本已登记"])))
    W.append(dict(week=3, title="数据结构③：树与二叉树",
                  goal="三种遍历手写全对；哈夫曼与并查集能独立算；选择 45 + 大题 6",
                  target="选择 45 + 大题 6（遍历、哈夫曼、并查集）", check="",
                  days=[single(idx, "w4d2"), single(idx, "w4d4"), single(idx, "w4d6"),
                        single(idx, "w5d2"),
                        rest("今日无新课：树与二叉树大题手写 2 道"),
                        rest("今日无新课：并查集路径压缩再过一遍")],
                  review=dict(title="第 3 周复盘：树与二叉树",
                              checklist=["递归与非递归遍历都写得出来", "树森与二叉树转换不乱", "错题本已登记"])))
    W.append(dict(week=4, title="数据结构④：图",
                  goal="Dijkstra 与 Prim 手写正确；关键路径能算；选择 50 + 大题 5",
                  target="选择 50 + 大题 5", check="",
                  days=[single(idx, "w5d4"), single(idx, "w5d6"), single(idx, "w6d2"),
                        single(idx, "w6d4"),
                        rest("今日无新课：最短路径手推 3 个图"),
                        rest("今日无新课：MST 与最短路对比表默写")],
                  review=dict(title="第 4 周复盘：图算法",
                              checklist=["DFS/BFS 复杂度与分析对", "Prim/Kruskal 各自适用场景说清", "错题本已登记"])))
    W.append(dict(week=5, title="数据结构⑤：查找与排序 + 数据结构测",
                  goal="数据结构 100 分卷 ≥75；查找与排序复杂度/稳定性 20 项全对",
                  target="选择 50 + 大题 5 + 100 分测 1 套",
                  check="检查点 1：数据结构 100 分卷 ≥75",
                  days=[single(idx, "w6d6"), single(idx, "w7d2"), single(idx, "w7d4"),
                        single(idx, "w7d6"),
                        rest("今日无新课：排序代码手写（插入/归并/快排）"),
                        rest("今日无新课：测前只过错题与复杂度表")],
                  review=dict(title="数据结构 100 分卷（限时 2 小时）",
                              checklist=["大题步骤写全（不只写结果）", "复杂度表不查书", "错题按章归档"])))
    W.append(dict(week=6, title="计组①：系统概述与数据表示",
                  goal="IEEE754 单精度手算互转 5 题全对；补码运算与溢出判断不错",
                  target="选择 45 + 大题 4（IEEE754、海明码）", check="",
                  days=[single(idx, "w8d2"), single(idx, "w8d4"), single(idx, "w8d6"),
                        single(idx, "w9d2"), single(idx, "w9d4"),
                        rest("今日无新课：补码与浮点计算错题重做")],
                  review=dict(title="第 6 周复盘：数据表示",
                              checklist=["移码与补码关系不混", "IEEE754 分阶码位数记准", "错题本已登记"])))
    W.append(dict(week=7, title="计组②：存储系统与 Cache",
                  goal="Cache 三种映射能画图并算命中率；主存扩展能画；选择 50 + 大题 5",
                  target="选择 50 + 大题 5（Cache 命中率、主存扩展）", check="",
                  days=[single(idx, "w9d6"), single(idx, "w10d2"), single(idx, "w10d4"),
                        single(idx, "w10d6"),
                        rest("今日无新课：Cache 地址划分手算 5 题"),
                        rest("今日无新课：替换算法与写策略对比表默写")],
                  review=dict(title="第 7 周复盘：存储系统",
                              checklist=["地址位划分顺序不写反", "写策略与一致性问题说清", "错题本已登记"])))
    W.append(dict(week=8, title="计组③：虚拟存储、指令系统与 CPU",
                  goal="TLB 与缺页流程说得顺；寻址方式计算不错；选择 50 + 大题 5",
                  target="选择 50 + 大题 5", check="",
                  days=[single(idx, "w11d2"), single(idx, "w11d4"), single(idx, "w11d6"),
                        single(idx, "w12d2"), single(idx, "w12d4"),
                        rest("今日无新课：寻址方式与有效地址计算 10 题")],
                  review=dict(title="第 8 周复盘：虚存与指令系统",
                              checklist=["VA→PA 流程能默写", "CISC 与 RISC 差异 5 条", "错题本已登记"])))
    W.append(dict(week=9, title="计组④：控制器、流水线与总线 IO + 计组测",
                  goal="计组 100 分卷 ≥75；单总线数据通路能画并口述取指周期",
                  target="选择 50 + 大题 5 + 100 分测 1 套",
                  check="检查点 2：计组 100 分卷 ≥75",
                  days=[single(idx, "w12d6"), single(idx, "w13d2"), single(idx, "w13d4"),
                        single(idx, "w13d6"),
                        rest("今日无新课：数据通路微操作序列写 3 遍"),
                        rest("今日无新课：中断与 DMA 5 行对比默写")],
                  review=dict(title="计组 100 分卷（限时 2 小时）",
                              checklist=["数据通路大题步骤齐全", "流水线冒险与解决会说", "错题按章归档"])))
    W.append(dict(week=10, title="操作系统①：概述与进程管理",
                  goal="PV 大题能写信号量定义与初值；调度指标算得对；选择 45 + 大题 4",
                  target="选择 45 + 大题 4（PV、调度计算）", check="",
                  days=[merge(idx, ["w14d2", "w14d4"], "操作系统概述 + 进程的概念与状态",
                              "王道《操作系统》第 1 章 + 2.1",
                              ex_n=2),
                        merge(idx, ["w14d6", "w15d2"], "线程与处理机调度（含调度算法计算）",
                              "王道 2.2–3.1", ex_n=2),
                        single(idx, "w15d4"), single(idx, "w15d6"),
                        single(idx, "w16d2"),
                        merge(idx, ["w16d4", "w16d6"], "死锁与银行家算法",
                              "王道 2.4 死锁", ex_n=2)],
                  review=dict(title="第 10 周复盘：进程与同步",
                              checklist=["进程状态转换图能画", "信号量 P/V 顺序不写反", "银行家算法能算安全序列"])))
    W.append(dict(week=11, title="操作系统②：内存、文件与 IO + OS 测",
                  goal="OS 100 分卷 ≥70；页面置换与磁盘调度计算全对",
                  target="选择 50 + 大题 5 + 100 分测 1 套",
                  check="检查点 3：操作系统 100 分卷 ≥70",
                  days=[single(idx, "w17d2"), single(idx, "w17d4"), single(idx, "w17d6"),
                        single(idx, "w18d2"), single(idx, "w18d4"), single(idx, "w18d6")],
                  review=dict(title="操作系统 100 分卷（限时 2 小时）",
                              checklist=["页表与快表计算不错", "页面置换手算 4 种算法", "I/O 控制方式对比表默写"])))
    W.append(dict(week=12, title="计算机网络一轮 + 408 总测",
                  goal="408 150 分总测 ≥90；四科框架图能默写；计选 55 + 大题 5",
                  target="选择 55 + 大题 5 + 150 分总测 1 套",
                  check="检查点 4：408 150 分总测 ≥90",
                  days=[merge(idx, ["w19d2", "w19d4"], "计网体系结构、性能指标与物理层",
                              "王道《计算机网络》第 1–2 章", ex_n=2),
                        merge(idx, ["w19d6", "w20d2"], "链路层：差错控制、流量控制与介质访问",
                              "王道 3.1–3.4", ex_n=2),
                        merge(idx, ["w20d4", "w20d6"], "以太网与交换机 + 网络层 IPv4 与子网划分",
                              "王道 3.5–4.2", ex_n=2),
                        merge(idx, ["w21d2", "w21d4"], "路由协议 + ARP、ICMP、NAT 与 IPv6",
                              "王道 4.3–4.4", ex_n=2),
                        merge(idx, ["w21d6", "w22d2"], "传输层：UDP、TCP 连接管理与可靠传输",
                              "王道 5.1–5.2", ex_n=2),
                        merge(idx, ["w22d4", "w22d6"], "拥塞控制 + 应用层（DNS/HTTP/邮件/FTP）",
                              "王道 5.3–6.4", ex_n=2)],
                  review=dict(title="408 150 分总测（限时 3 小时）",
                              checklist=["按考试顺序做题，选择先拿满", "大题步骤写全，宁多勿简", "四科失分点写进寒假计划"])))
    return W


def assemble(base, weeks_spec, name):
    for w in weeks_spec:
        w["goal"] = re.sub(r"；选择.*$", "", w["goal"])   # 题量单独展示，避免与 goal 重复
    out = {
        "id": base["id"],
        "title": base["title"].replace("22 周", "12 周").replace(" · 与 408 错峰", "").replace(" · 与数学二错峰", ""),
        "subject": base["subject"],
        "level": base["level"],
        "goal": base["goal"],
        "tools": base["tools"],
        "dailyMinutes": base["dailyMinutes"],
        "startDate": START,
        "source": {"note": "由 rebuild_app_plan.py 按 12 周基础期重排；章节正文沿用第 1 版权威内容，按 Excel v2 的周次地图重新归周"},
        "weeks": [build_week(s, base["_idx"], s["week"]) for s in weeks_spec],
    }
    return out


def main():
    # 源文件必须是 22 周原版（本脚本不可重复运行在原版之上，会找不到源小节 id）
    math = load("math2-2028.json")
    cs = load("cs408-2028.json")
    if len(math["weeks"]) != 22:
        raise SystemExit("math2-2028.json 已是 12 周版本，请先从备份恢复 22 周原版再运行")
    math["_idx"] = index_sessions(math)
    cs["_idx"] = index_sessions(cs)

    new_math = assemble(math, math_weeks(math["_idx"]), "math")
    new_cs = assemble(cs, cs_weeks(cs["_idx"]), "cs")
    new_math["goal"] = ("完成数二基础一轮（12 周）：高数 7 周 + 线代 3 周 + 错题/总测 2 周，"
                        "阶段测一/二/三达标，期末 150 分总测 ≥100")
    new_math["tools"] = "武忠祥《高等数学辅导讲义》、李永乐《线性代数辅导讲义》、660 题（只做基础篇）、错题本"
    new_cs["goal"] = ("完成 408 四科基础一轮（12 周）：数据结构 5 周、计组 4 周、操作系统 2 周、计网 1 周，"
                      "四科各一次 100 分测，期末 150 分总测 ≥90")
    new_cs["tools"] = "王道四本单科书 + 课后选择题；教材：严蔚敏《数据结构》、唐朔飞《计组》、汤小丹《操作系统》、谢希仁《计网》"

    for name, plan in (("math2-2028.json", new_math), ("cs408-2028.json", new_cs)):
        # 校验
        assert len(plan["weeks"]) == 12
        ids = []
        for w in plan["weeks"]:
            assert len(w["days"]) == 7, w["week"]
            for d in w["days"]:
                ids.append(d["id"])
        assert len(ids) == len(set(ids)), "重复 id"
        learn = sum(1 for w in plan["weeks"] for d in w["days"] if d["kind"] in ("learn", "practice"))
        ex = sum(len(d.get("exercises") or []) for w in plan["weeks"] for d in w["days"])
        json.dump(plan, open(name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%s: 12 周 / 学习日 %d / 课后题 %d" % (name, learn, ex))


if __name__ == "__main__":
    main()
