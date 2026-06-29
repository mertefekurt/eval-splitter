from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SplitResult:
    splits: dict[str, list[dict[str, Any]]]
    leakage: list[str]
    summary: dict[str, int]


def split_records(
    records: list[dict[str, Any]],
    *,
    ratios: tuple[int, int, int] = (80, 10, 10),
    strata_field: str = "category",
    text_field: str = "input",
    seed: str = "eval-splitter",
) -> SplitResult:
    _validate_ratios(ratios)
    grouped = _group_by_strata(records, strata_field)
    splits = {"train": [], "validation": [], "test": []}

    for stratum_records in grouped.values():
        ordered = sorted(stratum_records, key=lambda record: _stable_key(record, seed))
        train_cut, validation_cut = _cuts(len(ordered), ratios)
        splits["train"].extend(ordered[:train_cut])
        splits["validation"].extend(ordered[train_cut:validation_cut])
        splits["test"].extend(ordered[validation_cut:])

    leakage = detect_leakage(splits, text_field)
    summary = {name: len(items) for name, items in splits.items()}
    return SplitResult(splits=splits, leakage=leakage, summary=summary)


def detect_leakage(splits: dict[str, list[dict[str, Any]]], text_field: str) -> list[str]:
    seen: dict[str, tuple[str, str]] = {}
    leakage: list[str] = []
    for split_name, records in splits.items():
        for index, record in enumerate(records):
            text = _normalize_text(str(record.get(text_field, "")))
            if not text:
                continue
            record_id = str(record.get("id") or f"{split_name}:{index}")
            if text in seen and seen[text][0] != split_name:
                leakage.append(
                    f"{record_id} in {split_name} duplicates {seen[text][1]} in {seen[text][0]}"
                )
            else:
                seen[text] = (split_name, record_id)
    return leakage


def summary_to_markdown(result: SplitResult) -> str:
    lines = ["# eval-splitter report", "", "## Counts", ""]
    for split_name, count in result.summary.items():
        lines.append(f"- {split_name}: {count}")
    lines.extend(["", "## Leakage", ""])
    if result.leakage:
        lines.extend(f"- {item}" for item in result.leakage)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def summary_to_json(result: SplitResult) -> str:
    return json.dumps({"summary": result.summary, "leakage": result.leakage}, indent=2) + "\n"


def _group_by_strata(
    records: list[dict[str, Any]],
    strata_field: str,
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get(strata_field, "__missing__"))].append(record)
    return grouped


def _stable_key(record: dict[str, Any], seed: str) -> str:
    payload = json.dumps(record, sort_keys=True, default=str)
    return hashlib.sha256(f"{seed}:{payload}".encode()).hexdigest()


def _cuts(count: int, ratios: tuple[int, int, int]) -> tuple[int, int]:
    train = round(count * ratios[0] / 100)
    validation = round(count * ratios[1] / 100)
    test = count - train - validation
    if count >= 3 and validation == 0:
        validation = 1
        train = max(train - 1, 1)
    if count >= 3 and test == 0:
        test = 1
        train = max(train - 1, 1)
    while train + validation + test > count:
        train = max(train - 1, 0)
    if count >= 2 and train + validation >= count:
        validation = max(count - train - 1, 0)
    return train, train + validation


def _validate_ratios(ratios: tuple[int, int, int]) -> None:
    if len(ratios) != 3 or any(value < 0 for value in ratios) or sum(ratios) != 100:
        raise ValueError("--ratios must contain three non-negative integers that sum to 100")


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()
