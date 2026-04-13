#!/usr/bin/env python3
"""
本地手动运行：python3 build.py
同时生成：
  - Grok.list   QuantumultX 格式（HOST-SUFFIX / HOST-KEYWORD / IP-CIDR）
  - Grok.yaml   Clash 格式（classical behavior）
源：blackmatrix7/Twitter QX 列表 + xAI 独有域名
"""
import urllib.request

TWITTER_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/"
    "ios_rule_script/master/rule/QuantumultX/Twitter/Twitter.list"
)

# xAI 独有域名（Twitter.list 里没有的）
GROK_EXTRA_QX = [
    "HOST-SUFFIX,grok.com",
    "HOST-SUFFIX,x.ai",
]

# QX → Clash 规则类型映射
def qx_to_clash(line):
    """HOST-SUFFIX,foo → DOMAIN-SUFFIX,foo  /  IP-CIDR,x/y → IP-CIDR,x/y,no-resolve"""
    if line.startswith("HOST-SUFFIX,"):
        return "DOMAIN-SUFFIX," + line[len("HOST-SUFFIX,"):]
    if line.startswith("HOST,"):
        return "DOMAIN," + line[len("HOST,"):]
    if line.startswith("HOST-KEYWORD,"):
        return "DOMAIN-KEYWORD," + line[len("HOST-KEYWORD,"):]
    if line.startswith("IP-CIDR,"):
        return line + ",no-resolve"
    if line.startswith("IP-CIDR6,"):
        return line + ",no-resolve"
    return line

def strip_policy(line):
    """去掉条目末尾的策略名，如 HOST-SUFFIX,foo.com,Twitter → HOST-SUFFIX,foo.com"""
    parts = line.split(",")
    return ",".join(parts[:2]) if len(parts) >= 3 else line

def build():
    with urllib.request.urlopen(TWITTER_URL) as r:
        twitter_lines = r.read().decode().splitlines()

    seen_qx = set()
    qx_output = [
        "# Grok.list — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Twitter + xAI domains",
        "# Updated by GitHub Actions",
        "",
        "# xAI / Grok specific",
    ]

    for line in GROK_EXTRA_QX:
        key = line.upper()
        if key not in seen_qx:
            seen_qx.add(key)
            qx_output.append(line)

    qx_output += ["", "# Twitter / X (blackmatrix7)"]

    for raw_line in twitter_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line = strip_policy(stripped)
        key = line.upper()
        if key not in seen_qx:
            seen_qx.add(key)
            qx_output.append(line)

    with open("Grok.list", "w") as f:
        f.write("\n".join(qx_output) + "\n")

    # 生成 Clash YAML
    clash_rules = []
    for qx_line in qx_output:
        if not qx_line or qx_line.startswith("#"):
            continue
        clash_rules.append("  - " + qx_to_clash(qx_line))

    clash_output = [
        "# Grok.yaml — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Twitter + xAI domains",
        "# Updated by GitHub Actions",
        "payload:",
    ] + clash_rules

    with open("Grok.yaml", "w") as f:
        f.write("\n".join(clash_output) + "\n")

    print(f"Done. QX rules: {len(seen_qx)}, Clash rules: {len(clash_rules)}")

if __name__ == "__main__":
    build()
