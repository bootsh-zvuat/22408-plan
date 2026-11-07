# -*- coding: utf-8 -*-
"""把 web/ 模板 + data/ 四份计划注入，打包成单文件网页。

输出两份（内容相同）：
    22408每日计划.html      ← 双击直接用
    deploy/index.html       ← 直接推 GitHub Pages / Netlify

运行：python3 scripts/build_v2.py
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
TPL = BASE / "web" / "plan-app-v2.template.html"


def payload(path: Path) -> str:
    d = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main() -> int:
    html = TPL.read_text(encoding="utf-8")
    for slot, name in (
        ("__PLAN_MATH2__", "math2-2028.json"),
        ("__PLAN_CS408__", "cs408-2028.json"),
        ("__PLAN_ENGLISH__", "english-2028.json"),
        ("__PLAN_POLITICS__", "politics-2028.json"),
    ):
        html = html.replace(slot, payload(DATA / name))

    out_root = BASE / "22408每日计划.html"
    out_deploy = BASE / "deploy" / "index.html"
    out_root.write_text(html, encoding="utf-8")
    out_deploy.parent.mkdir(exist_ok=True)
    out_deploy.write_text(html, encoding="utf-8")
    print(f"  + {out_root.relative_to(BASE)}（{len(html)} 字符）")
    print(f"  + {out_deploy.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
