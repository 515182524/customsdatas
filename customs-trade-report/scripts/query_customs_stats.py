#!/usr/bin/env python3
"""Fill a China Customs statistics query in a headed Playwright CLI browser."""

from __future__ import annotations

import argparse
import atexit
import json
import os
from pathlib import Path
import re
import subprocess
import sys


PARTNER_CODES = (
    "101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,"
    "118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,"
    "135,136,137,138,139,141,142,143,144,145,146,147,148,149,199,201,202,"
    "203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,"
    "220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,"
    "237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,"
    "254,255,256,257,258,259,260,299,301,302,303,304,305,306,307,308,309,"
    "310,311,312,313,314,315,316,318,320,321,322,323,324,325,326,327,328,"
    "329,330,331,334,335,336,337,338,339,340,343,344,347,349,350,351,352,"
    "353,354,355,356,357,358,359,399,401,402,403,404,405,406,408,409,410,"
    "411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,"
    "428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,"
    "445,446,447,448,449,499,501,502,503,504,599,601,602,603,604,605,606,"
    "607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,"
    "625,699,701,702,999,150,151,152,261,262,263,360,361,362,363,364,450,"
    "451,452,453,454,455,456,505,626,627,628,629,630,631,632,633,634,635,700"
)
TRADE_MODE_CODES = "10,11,12,13,14,15,16,19,20,22,23,25,27,30,31,33,34,35,39,41"
REGION_CODES = "11,12,13,14,15,21,22,23,31,32,33,34,35,36,37,41,42,43,44,45,46,50,51,52,53,54,61,62,63,64,65"

FLOW_VALUES = {"import": "1", "进口": "1", "export": "0", "出口": "0", "both": "10", "进出口": "10"}
CURRENCY_VALUES = {"rmb": "rmb", "人民币": "rmb", "usd": "usd", "美元": "usd"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow", default="export", choices=FLOW_VALUES)
    parser.add_argument("--currency", default="usd", choices=CURRENCY_VALUES)
    parser.add_argument("--year", default=2026, type=int)
    parser.add_argument("--start-month", default=1, type=int)
    parser.add_argument("--end-month", default=12, type=int)
    parser.add_argument("--hs-code", required=True)
    parser.add_argument("--session", default="cstats")
    parser.add_argument("--fill-only", action="store_true")
    parser.add_argument("--download", action="store_true", help="结果页已直接出现时自动下载")
    parser.add_argument("--download-dir", default="output/customs-stats")
    return parser.parse_args()


def validate(args: argparse.Namespace) -> None:
    if not re.fullmatch(r"\d{8}", args.hs_code):
        raise SystemExit("--hs-code 必须是 8 位数字")
    if not 1 <= args.start_month <= 12 or not 1 <= args.end_month <= 12:
        raise SystemExit("月份必须在 1 到 12 之间")
    if args.start_month > args.end_month:
        raise SystemExit("起始月份不能大于结束月份")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.session):
        raise SystemExit("--session 只能包含字母、数字、下划线和连字符")
    if len(args.session) > 8:
        raise SystemExit("--session 最多 8 个字符，避免 Playwright CLI 套接字路径过长")
    if args.fill_only and args.download:
        raise SystemExit("--fill-only 与 --download 不能同时使用")


def run(command: list[str], *, check: bool = True, quiet: bool = False) -> None:
    kwargs = {"check": check, "text": True}
    if quiet:
        kwargs.update({"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL})
    subprocess.run(command, **kwargs)


def main() -> None:
    args = parse_args()
    validate(args)

    default_pwcli = Path.home() / ".codex/skills/playwright/scripts/playwright_cli.sh"
    pwcli = Path(os.environ.get("PWCLI", default_pwcli)).expanduser()
    if not pwcli.exists():
        raise SystemExit(f"找不到 Playwright CLI 包装脚本: {pwcli}")

    payload = {
        "flow": FLOW_VALUES[args.flow],
        "currency": CURRENCY_VALUES[args.currency],
        "year": str(args.year),
        "startMonth": str(args.start_month),
        "endMonth": str(args.end_month),
        "hsCode": args.hs_code,
        "submit": not args.fill_only,
        "partners": PARTNER_CODES,
        "tradeModes": TRADE_MODE_CODES,
        "regions": REGION_CODES,
    }

    script = f"""async page => {{
  const params = {json.dumps(payload, ensure_ascii=False)};
  await page.waitForTimeout(2500);
  const frame = page.frames().find(f => f.url().includes("/queryData/queryDataByWhere"));
  if (!frame) throw new Error("未找到海关查询表单 iframe");

  await frame.locator(`input[name="iEType"][value="${{params.flow}}"]`).check();
  await frame.locator(`input[name="currencyType"][value="${{params.currency}}"]`).check();

  const monthResponse = page.waitForResponse(
    response => response.url().includes("/queryData/getMonth"),
    {{ timeout: 10000 }}
  ).catch(() => null);
  await frame.locator("#year").selectOption(params.year);
  await monthResponse;
  const availableMonths = await frame.locator("#endMonth option").evaluateAll(
    options => options.map(option => Number(option.value)).filter(Number.isFinite)
  );
  const actualEndMonth = String(Math.min(Number(params.endMonth), Math.max(...availableMonths)));
  await frame.locator("#startMonth").selectOption(params.startMonth);
  await frame.locator("#endMonth").selectOption(actualEndMonth);
  await frame.locator('input[name="monthFlag"]').check();

  const fields = [
    ["CODE_TS", params.hsCode],
    ["ORIGIN_COUNTRY", params.partners],
    ["TRADE_MODE", params.tradeModes],
    ["TRADE_CO_PORT", params.regions],
  ];
  for (let index = 0; index < fields.length; index++) {{
    await frame.locator(`#outerField${{index + 1}}`).selectOption(fields[index][0]);
    await frame.locator(`#outerValue${{index + 1}}`).fill(fields[index][1]);
  }}

  const state = await frame.evaluate(() => ({{
    flow: document.querySelector('input[name="iEType"]:checked').value,
    currency: document.querySelector('input[name="currencyType"]:checked').value,
    year: document.querySelector("#year").value,
    start_month: document.querySelector("#startMonth").value,
    end_month: document.querySelector("#endMonth").value,
    month_flag: document.querySelector('input[name="monthFlag"]').checked,
    hs_code: document.querySelector("#outerValue1").value,
  }}));
  let captcha = false;
  let result = false;
  if (params.submit) {{
    await frame.locator("#doSearch").click();
    await page.waitForTimeout(800);
    const confirm = frame.locator(".layui-layer-btn0").last();
    if (await confirm.isVisible().catch(() => false)) await confirm.click();
    await page.waitForTimeout(5000);
    captcha = page.frames().some(f => f.url().includes("/queryData/toCaptchaView"));
    result = page.frames().some(f => f.url().includes("/queryData/queryDataList"));
  }}
  return {{ ...state, submitted: params.submit, captcha, result }};
}}"""

    session_arg = f"-s={args.session}"
    if args.download:
        atexit.register(
            subprocess.run,
            [str(pwcli), session_arg, "close"],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    run([str(pwcli), session_arg, "close"], check=False, quiet=True)
    run([str(pwcli), session_arg, "open", "http://stats.customs.gov.cn/", "--headed"])
    run([str(pwcli), session_arg, "run-code", script])

    if args.fill_only:
        print(f"已填写查询参数，浏览器会话: {args.session}")
    elif args.download:
        downloader = Path(__file__).with_name("download_customs_results.py")
        command = [
            sys.executable,
            str(downloader),
            "--session",
            args.session,
            "--output-dir",
            args.download_dir,
            "--wait-seconds",
            "180",
            "--flow",
            args.flow,
            "--currency",
            args.currency,
            "--year",
            str(args.year),
            "--start-month",
            str(args.start_month),
            "--end-month",
            str(args.end_month),
            "--hs-code",
            args.hs_code,
        ]
        completed = subprocess.run(command, text=True)
        if completed.returncode:
            print(
                "尚未进入结果页。请手动完成拼图验证码后运行：\n"
                f"{sys.executable} {downloader} --session {args.session} "
                f"--output-dir {args.download_dir} --flow {args.flow} "
                f"--currency {args.currency} --year {args.year} "
                f"--start-month {args.start_month} --end-month {args.end_month} "
                f"--hs-code {args.hs_code}"
            )
            sys.exit(completed.returncode)
    else:
        print(f"已提交查询，浏览器会话: {args.session}。如出现拼图验证码，请在浏览器中手动完成。")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
