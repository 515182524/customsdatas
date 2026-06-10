#!/usr/bin/env python3
"""Download China Customs query results from an existing Playwright CLI session."""

from __future__ import annotations

import argparse
import atexit
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="cstats")
    parser.add_argument("--output-dir", default="output/customs-stats")
    parser.add_argument("--wait-seconds", type=int, default=300)
    parser.add_argument("--loading-timeout", type=int, default=45)
    parser.add_argument("--flow")
    parser.add_argument("--currency")
    parser.add_argument("--year", type=int)
    parser.add_argument("--start-month", type=int)
    parser.add_argument("--end-month", type=int)
    parser.add_argument("--hs-code")
    return parser.parse_args()


def validate(args: argparse.Namespace) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,8}", args.session):
        raise SystemExit("--session 必须为 1 到 8 位字母、数字、下划线或连字符")
    if args.wait_seconds < 0:
        raise SystemExit("--wait-seconds 不能小于 0")
    if args.loading_timeout < 1:
        raise SystemExit("--loading-timeout 必须大于 0")
    if args.hs_code and not re.fullmatch(r"\d{8}", args.hs_code):
        raise SystemExit("--hs-code 必须是 8 位数字")


def parse_browser_result(output: str) -> dict:
    matches = re.findall(r"### Result\n(\{.*?\})\n### Ran", output, re.S)
    for match in reversed(matches):
        try:
            result = json.loads(match)
        except json.JSONDecodeError:
            continue
        if "total" in result:
            return result
    return {}


def main() -> None:
    args = parse_args()
    validate(args)

    pwcli = Path(
        os.environ.get(
            "PWCLI",
            Path.home() / ".codex/skills/playwright/scripts/playwright_cli.sh",
        )
    ).expanduser()
    if not pwcli.exists():
        raise SystemExit(f"找不到 Playwright CLI 包装脚本: {pwcli}")
    atexit.register(
        subprocess.run,
        [str(pwcli), f"-s={args.session}", "close"],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone()
    temporary = output_dir / f".customs-download-{timestamp:%Y%m%d%H%M%S}.csv"

    script = f"""async page => {{
  const deadline = Date.now() + {args.wait_seconds * 1000};
  const waitForResultFrame = async () => {{
    let resultFrame = page.frames().find(f => f.url().includes("/queryData/queryDataList"));
    while (!resultFrame && Date.now() <= deadline) {{
      const captchaFrame = page.frames().find(f => f.url().includes("/queryData/toCaptchaView"));
      if (captchaFrame) {{
        const success = await captchaFrame.locator("body").innerText().catch(() => "");
        if (/验证成功|校验成功|通过/.test(success)) {{
          const confirm = captchaFrame.getByText("确定", {{ exact: true }});
          if (await confirm.isVisible().catch(() => false)) await confirm.click();
        }}
      }}
      await page.waitForTimeout(1000);
      resultFrame = page.frames().find(f => f.url().includes("/queryData/queryDataList"));
    }}
    return resultFrame;
  }};

  let resultFrame = await waitForResultFrame();
  if (!resultFrame) throw new Error("等待结果页超时，请先手动完成拼图验证码");

  const waitForTotal = async (frame, timeoutMs) => {{
    const loadingDeadline = Date.now() + timeoutMs;
    let total = null;
    while (total === null && Date.now() <= loadingDeadline && Date.now() <= deadline) {{
      total = await frame.locator("#totalSize").inputValue().catch(() => null);
      if (total === null) await page.waitForTimeout(1000);
    }}
    return total;
  }};

  let retried = false;
  let total = await waitForTotal(resultFrame, {args.loading_timeout * 1000});
  if (total === null) {{
    retried = true;
    const returnButton = resultFrame.getByText("返回设置", {{ exact: true }});
    if (!await returnButton.isVisible().catch(() => false)) {{
      throw new Error("数据持续加载且未找到返回设置按钮");
    }}
    await returnButton.click();
    await page.waitForTimeout(1500);
    const settingsFrame = page.frames().find(f => f.url().includes("/queryData/queryDataByWhere"));
    if (!settingsFrame) throw new Error("点击返回设置后未找到查询设置页");
    await settingsFrame.locator("#doSearch").click();
    await page.waitForTimeout(800);
    const historyConfirm = settingsFrame.locator(".layui-layer-btn0").last();
    if (await historyConfirm.isVisible().catch(() => false)) await historyConfirm.click();
    resultFrame = await waitForResultFrame();
    if (!resultFrame) throw new Error("重新查询后等待结果页超时，请手动完成拼图验证码");
    total = await waitForTotal(resultFrame, {args.loading_timeout * 1000});
  }}
  if (total === null) throw new Error("重新查询后数据仍持续加载，请稍后再试");
  if (total === "0") throw new Error("查询结果为空，无法导出");

  const downloadPromise = page.waitForEvent("download", {{ timeout: 60000 }});
  await resultFrame.locator("#downLoad").click();
  const confirm = resultFrame.locator(".layui-layer-btn0").last();
  if (await confirm.isVisible().catch(() => false)) await confirm.click();
  const download = await downloadPromise;
  await download.saveAs({json.dumps(str(temporary), ensure_ascii=False)});
  return {{
    total,
    retried_after_loading_timeout: retried,
    suggested_filename: download.suggestedFilename(),
    saved_path: {json.dumps(str(temporary), ensure_ascii=False)}
  }};
}}"""

    command = [str(pwcli), f"-s={args.session}", "run-code", script]
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode or "### Error" in completed.stdout:
        sys.exit(completed.returncode or 1)
    browser_result = parse_browser_result(completed.stdout)
    if not temporary.exists():
        raise SystemExit(f"浏览器报告下载完成，但未找到文件: {temporary}")

    periods = set()
    hs_codes = set()
    row_count = 0
    with temporary.open("r", encoding="gb18030", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row_count += 1
            period = re.sub(r"\D", "", str(row.get("数据年月", "")))[:6]
            hs_code = re.sub(r"\D", "", str(row.get("商品编码", "")))[:8]
            if len(period) == 6:
                periods.add(period)
            if len(hs_code) == 8:
                hs_codes.add(hs_code)
    if not periods:
        raise SystemExit("下载文件中未识别到数据年月")
    hs_part = args.hs_code or (sorted(hs_codes)[0] if len(hs_codes) == 1 else "多个商品")
    period_part = "{}-{}".format(min(periods), max(periods))
    flow_part = args.flow or "未注明方向"
    destination = output_dir / f"{hs_part}_{period_part}_{flow_part}.csv"
    if destination.exists():
        destination.unlink()
    temporary.rename(destination)

    record = {
        "downloaded_at": timestamp.isoformat(),
        "path": str(destination),
        "size_bytes": destination.stat().st_size,
        "row_count": row_count,
        "result_total": int(browser_result["total"]) if str(browser_result.get("total", "")).isdigit() else None,
        "periods": sorted(periods),
        "retried_after_loading_timeout": bool(browser_result.get("retried_after_loading_timeout")),
        "session": args.session,
        "query": {
            "flow": args.flow,
            "currency": args.currency,
            "year": args.year,
            "start_month": args.start_month,
            "end_month": args.end_month,
            "hs_code": args.hs_code,
        },
    }
    latest = output_dir / "latest-download.json"
    history = output_dir / "download-history.jsonl"
    latest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with history.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"下载完成: {destination}")
    print(f"最新下载记录: {latest}")


if __name__ == "__main__":
    main()
