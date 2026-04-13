#!/usr/bin/env python3
"""
本地手动运行：python3 build.py
生成 Grok.list（合并 blackmatrix7/Twitter.list + xAI 独有域名）
"""
import urllib.request

TWITTER_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/"
    "ios_rule_script/master/rule/QuantumultX/Twitter/Twitter.list"
)

# xAI 独有域名（Twitter.list 里没有的）
GROK_EXTRA = [
    "HOST-SUFFIX,grok.com",
    "HOST-SUFFIX,x.ai",
]

def strip_policy(line):
    """去掉条目末尾的策略名，如 HOST-SUFFIX,foo.com,Twitter → HOST-SUFFIX,foo.com"""
    parts = line.split(",")
    if len(parts) >= 3:
        return ",".join(parts[:2])
    return line

def build():
    with urllib.request.urlopen(TWITTER_URL) as r:
        twitter_lines = r.read().decode().splitlines()

    seen = set()
    output = [
        "# Grok.list — Auto-generated, do not edit manually",
        "# Source: blackmatrix7/Twitter + xAI domains",
        "# Updated by GitHub Actions",
        "",
        "# xAI / Grok specific",
    ]

    for line in GROK_EXTRA:
        key = line.upper()
        if key not in seen:
            seen.add(key)
            output.append(line)

    output += ["", "# Twitter / X (blackmatrix7)"]

    for raw_line in twitter_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line = strip_policy(stripped)
        key = line.upper()
        if key not in seen:
            seen.add(key)
            output.append(line)

    with open("Grok.list", "w") as f:
        f.write("\n".join(output) + "\n")

    print(f"Done. Total rules: {len(seen)}")

if __name__ == "__main__":
    build()
