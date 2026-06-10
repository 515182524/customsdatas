#!/usr/bin/env python3
"""Download China Customs data and generate the Markdown analysis report."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import sys


def query_segment(args, script_dir: Path, staging: Path, start_month: int) -> dict:
    latest_path = staging / "latest-download.json"
    latest_path.unlink(missing_ok=True)
    query_command = [
        sys.executable,
        str(script_dir / "query_customs_stats.py"),
        "--flow", args.flow,
        "--currency", args.currency,
        "--year", str(args.year),
        "--start-month", str(start_month),
        "--end-month", str(args.end_month),
        "--hs-code", args.hs_code,
        "--session", args.session,
        "--download",
        "--download-dir", str(staging),
    ]
    subprocess.run(query_command, check=True)
    if not latest_path.exists():
        raise SystemExit("查询结束后未生成最新下载记录")
    return json.loads(latest_path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="gb18030", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader.fieldnames or []), list(reader)


def period_of(row: dict) -> str:
    return re.sub(r"\D", "", str(row.get("数据年月", "")))[:6]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hs-code", required=True)
    parser.add_argument("--flow", default="出口", choices=("进口", "出口", "进出口"))
    parser.add_argument("--currency", default="美元", choices=("人民币", "美元"))
    parser.add_argument("--year", default=2026, type=int)
    parser.add_argument("--start-month", default=1, type=int)
    parser.add_argument("--end-month", default=12, type=int)
    parser.add_argument("--session", default="cstats")
    parser.add_argument("--output-root", default="00- 草稿/海关数据报告")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{8}", args.hs_code):
        raise SystemExit("--hs-code 必须是 8 位数字")

    script_dir = Path(__file__).resolve().parent
    staging = Path(args.output_root).expanduser().resolve() / ".downloads"
    accepted_rows = []
    headers = []
    current_start = args.start_month
    segment_records = []

    while current_start <= args.end_month:
        latest = query_segment(args, script_dir, staging, current_start)
        source = Path(latest["path"])
        segment_headers, rows = read_rows(source)
        headers = headers or segment_headers
        total = latest.get("result_total")
        truncated = total is not None and total > len(rows)
        record = {
            "query_start_month": current_start,
            "query_end_month": args.end_month,
            "result_total": total,
            "downloaded_rows": len(rows),
            "source": str(source),
            "truncated": truncated,
        }
        segment_records.append(record)
        if not truncated:
            accepted_rows.extend(rows)
            break

        periods = sorted({period_of(row) for row in rows if len(period_of(row)) == 6})
        if not periods:
            raise SystemExit("截断文件中未识别到数据年月，无法自动补段")
        boundary_period = periods[-1]
        boundary_month = int(boundary_period[-2:])
        if boundary_month <= current_start:
            raise SystemExit(f"{boundary_period} 单月结果超过导出上限，无法按月份继续拆分")
        kept = [row for row in rows if period_of(row) < boundary_period]
        accepted_rows.extend(kept)
        record["discarded_boundary_period"] = boundary_period
        record["accepted_rows"] = len(kept)
        current_start = boundary_month

    if not accepted_rows:
        raise SystemExit("未获得可合并的海关数据")

    periods = sorted({period_of(row) for row in accepted_rows if len(period_of(row)) == 6})
    period_part = "{}-{}".format(periods[0], periods[-1])
    filename = f"{args.hs_code}_{period_part}_{args.flow}.csv"
    result_dir = Path(args.output_root).expanduser().resolve() / Path(filename).stem
    result_dir.mkdir(parents=True, exist_ok=True)
    destination = result_dir / filename
    if destination.exists():
        destination.unlink()
    with destination.open("w", encoding="gb18030", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(accepted_rows)

    report_command = [
        sys.executable,
        str(script_dir / "analyze_customs.py"),
        str(destination),
        "--output", str(result_dir),
        "--title", f"{args.hs_code} {args.flow}海关贸易数据分析报告",
        "--flow-label", args.flow,
    ]
    subprocess.run(report_command, check=True)
    result = {
        "source_table": str(destination),
        "report": str(result_dir / "report.md"),
        "result_dir": str(result_dir),
        "row_count": len(accepted_rows),
        "download_segments": segment_records,
    }
    (result_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
