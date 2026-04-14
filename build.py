#!/usr/bin/env python3
"""
本地手动运行：python3 build.py
同时生成：
  Grok.list  / Grok.yaml   — blackmatrix7/Twitter QX 列表 + xAI 独有域名
  OpenAI.yaml              — blackmatrix7/OpenAI Clash 列表，去除 IP-ASN 行
  Anthropic.list / Anthropic.yaml — blackmatrix7/Claude QX 列表 + claude.com
"""
import urllib.request

# ── 源地址 ────────────────────────────────────────────────────────────────────
TWITTER_QX_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/"
    "ios_rule_script/master/rule/QuantumultX/Twitter/Twitter.list"
)
OPENAI_CLASH_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/"
    "ios_rule_script/master/rule/Clash/OpenAI/OpenAI.yaml"
)
CLAUDE_QX_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/"
    "ios_rule_script/master/rule/QuantumultX/Claude/Claude.list"
)

# ── xAI 独有域名（Twitter.list 里没有的）─────────────────────────────────────
GROK_EXTRA_QX = [
    "HOST-SUFFIX,grok.com",
    "HOST-SUFFIX,x.ai",
]

# ── Anthropic 独有域名（blackmatrix7/Claude.list 里缺失的）───────────────────
ANTHROPIC_EXTRA_QX = [
    "HOST-SUFFIX,claude.com",
]

# ── 工具函数 ──────────────────────────────────────────────────────────────────
def qx_to_clash(line):
    """QX 规则格式 → Clash 规则格式"""
    if line.startswith("HOST-SUFFIX,"):
        return "DOMAIN-SUFFIX," + line[len("HOST-SUFFIX,"):]
    if line.startswith("HOST,"):
        return "DOMAIN," + line[len("HOST,"):]
    if line.startswith("HOST-KEYWORD,"):
        return "DOMAIN-KEYWORD," + line[len("HOST-KEYWORD,"):]
    if line.startswith(("IP-CIDR,", "IP-CIDR6,")):
        return line + ",no-resolve"
    return line

def strip_policy(line):
    """去掉 QX 条目末尾的策略名：HOST-SUFFIX,foo,Twitter → HOST-SUFFIX,foo"""
    parts = line.split(",")
    return ",".join(parts[:2]) if len(parts) >= 3 else line

def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode().splitlines()

# ── 生成 Grok.list（QX）和 Grok.yaml（Clash）────────────────────────────────
def build_grok():
    twitter_lines = fetch(TWITTER_QX_URL)

    seen = set()
    qx_output = [
        "# Grok.list — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Twitter + xAI domains",
        "# Updated by GitHub Actions",
        "",
        "# xAI / Grok specific",
    ]

    for line in GROK_EXTRA_QX:
        key = line.upper()
        if key not in seen:
            seen.add(key)
            qx_output.append(line)

    qx_output += ["", "# Twitter / X (blackmatrix7)"]

    for raw in twitter_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line = strip_policy(stripped)
        key = line.upper()
        if key not in seen:
            seen.add(key)
            qx_output.append(line)

    with open("Grok.list", "w") as f:
        f.write("\n".join(qx_output) + "\n")

    clash_rules = [
        "  - " + qx_to_clash(l)
        for l in qx_output
        if l and not l.startswith("#")
    ]
    clash_output = [
        "# Grok.yaml — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Twitter + xAI domains",
        "# Updated by GitHub Actions",
        "payload:",
    ] + clash_rules

    with open("Grok.yaml", "w") as f:
        f.write("\n".join(clash_output) + "\n")

    print(f"Grok  — QX: {len(seen)} rules, Clash: {len(clash_rules)} rules")

# ── 生成 OpenAI.yaml（Clash，去除 IP-ASN）───────────────────────────────────
def build_openai():
    lines = fetch(OPENAI_CLASH_URL)

    output = [
        "# OpenAI.yaml — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/OpenAI (IP-ASN lines removed for CFW compatibility)",
        "# Updated by GitHub Actions",
        "payload:",
    ]

    skipped = 0
    kept = 0
    in_payload = False

    for line in lines:
        stripped = line.strip()
        if stripped == "payload:":
            in_payload = True
            continue
        if not in_payload:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        # 去掉 "  - " 前缀后判断
        rule = stripped.lstrip("- ").strip()
        if rule.startswith("IP-ASN,"):
            skipped += 1
            continue
        output.append("  - " + rule)
        kept += 1

    with open("OpenAI.yaml", "w") as f:
        f.write("\n".join(output) + "\n")

    print(f"OpenAI — kept: {kept} rules, removed IP-ASN: {skipped}")

# ── 生成 Anthropic.list（QX）和 Anthropic.yaml（Clash）──────────────────────
def build_anthropic():
    claude_lines = fetch(CLAUDE_QX_URL)

    seen = set()
    qx_output = [
        "# Anthropic.list — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Claude + claude.com",
        "# Updated by GitHub Actions",
        "",
        "# Anthropic extra domains (not in blackmatrix7/Claude.list)",
    ]

    for line in ANTHROPIC_EXTRA_QX:
        key = line.upper()
        if key not in seen:
            seen.add(key)
            qx_output.append(line)

    qx_output += ["", "# Anthropic / Claude (blackmatrix7)"]

    for raw in claude_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line = strip_policy(stripped)
        key = line.upper()
        if key not in seen:
            seen.add(key)
            qx_output.append(line)

    with open("Anthropic.list", "w") as f:
        f.write("\n".join(qx_output) + "\n")

    clash_rules = [
        "  - " + qx_to_clash(l)
        for l in qx_output
        if l and not l.startswith("#")
    ]
    clash_output = [
        "# Anthropic.yaml — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Claude + claude.com",
        "# Updated by GitHub Actions",
        "payload:",
    ] + clash_rules

    with open("Anthropic.yaml", "w") as f:
        f.write("\n".join(clash_output) + "\n")

    print(f"Anthropic — QX: {len(seen)} rules, Clash: {len(clash_rules)} rules")


# ── 主入口 ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_grok()
    build_openai()
    build_anthropic()
