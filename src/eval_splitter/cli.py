from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eval_splitter import __version__
from eval_splitter.io import read_jsonl, write_jsonl
from eval_splitter.splitter import split_records, summary_to_json, summary_to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eval-splitter",
        description="Create deterministic stratified splits for LLM eval JSONL datasets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", nargs="?", type=Path, help="input JSONL eval dataset")
    parser.add_argument("--out-dir", type=Path, default=Path("splits"))
    parser.add_argument("--strata-field", default="category")
    parser.add_argument("--text-field", default="input")
    parser.add_argument("--ratios", default="80,10,10", help="train,validation,test percentages")
    parser.add_argument("--seed", default="eval-splitter")
    parser.add_argument("--report-format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--fail-on-leakage", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input is None:
        parser.print_help()
        return 0
    try:
        ratios = _parse_ratios(args.ratios)
        records = read_jsonl(args.input)
        result = split_records(
            records,
            ratios=ratios,
            strata_field=args.strata_field,
            text_field=args.text_field,
            seed=args.seed,
        )
        for split_name, split_records_ in result.splits.items():
            write_jsonl(args.out_dir / f"{split_name}.jsonl", split_records_)
    except (OSError, ValueError) as exc:
        print(f"eval-splitter: error: {exc}", file=sys.stderr)
        return 1

    if args.report_format == "json":
        print(summary_to_json(result), end="")
    else:
        print(summary_to_markdown(result), end="")
    return 2 if args.fail_on_leakage and result.leakage else 0


def _parse_ratios(raw: str) -> tuple[int, int, int]:
    parts = raw.split(",")
    if len(parts) != 3:
        raise ValueError("--ratios must look like 80,10,10")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]

