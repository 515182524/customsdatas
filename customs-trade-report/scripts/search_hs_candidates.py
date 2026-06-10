#!/usr/bin/env python3
"""Search official China Customs product parameters for 8-digit HS candidates."""

from __future__ import annotations

import argparse
import atexit
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keyword", help="商品名称关键词或已知编码")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--session", default="hscode")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    if not args.keyword.strip():
        raise SystemExit("关键词不能为空")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,8}", args.session):
        raise SystemExit("--session 必须为 1 到 8 位字母、数字、下划线或连字符")

    pwcli = Path(
        os.environ.get(
            "PWCLI",
            Path.home() / ".codex/skills/playwright/scripts/playwright_cli.sh",
        )
    ).expanduser()
    if not pwcli.exists():
        raise SystemExit(f"找不到 Playwright CLI 包装脚本: {pwcli}")

    script = f"""async page => {{
  await page.locator("#search").fill({json.dumps(args.keyword, ensure_ascii=False)});
  await page.locator("#codeLength").selectOption("8");
  await page.locator("#yearId").selectOption({json.dumps(str(args.year))});
  await Promise.all([
    page.waitForLoadState("domcontentloaded"),
    page.getByText("查询", {{ exact: true }}).click()
  ]);
  await page.waitForTimeout(2500);
  const rows = await page.locator("table").nth(1).locator("tbody tr").evaluateAll(rows =>
    rows.map(row => [...row.querySelectorAll("td")].map(cell =>
      (cell.querySelector("[title]")?.getAttribute("title") || cell.innerText || "").trim()
    )).filter(values => /^\\d{{8}}$/.test(values[0] || ""))
  );
  return rows.map(values => ({{
    hs_code: values[0],
    product_name: values[1],
    year: values[2],
    unit_1: values[4],
    unit_2: values[6]
  }}));
}}"""

    session_arg = f"-s={args.session}"
    atexit.register(
        subprocess.run,
        [str(pwcli), session_arg, "close"],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run([str(pwcli), session_arg, "close"], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        [str(pwcli), session_arg, "open", "http://stats.customs.gov.cn/paramManager/selComplexList", "--headed"],
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
    )
    completed = subprocess.run(
        [str(pwcli), session_arg, "run-code", script],
        check=True,
        text=True,
        capture_output=True,
    )
    match = re.search(r"### Result\n(.+?)\n### Ran", completed.stdout, re.S)
    if not match:
        print(completed.stdout)
        raise SystemExit("未能解析海关商品参数查询结果")
    candidates = json.loads(match.group(1))
    result = {
        "keyword": args.keyword,
        "year": args.year,
        "source": "http://stats.customs.gov.cn/paramManager/selComplexList",
        "candidates": candidates,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(output)
    else:
        print(text, end="")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
