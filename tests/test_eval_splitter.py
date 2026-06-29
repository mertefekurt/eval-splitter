import json

from eval_splitter.cli import main
from eval_splitter.io import read_jsonl
from eval_splitter.splitter import detect_leakage, split_records


def _records() -> list[dict[str, str]]:
    return [
        {"id": f"a-{index}", "category": "auth", "input": f"login problem {index}"}
        for index in range(5)
    ] + [
        {"id": f"b-{index}", "category": "billing", "input": f"invoice problem {index}"}
        for index in range(5)
    ]


def test_split_counts_are_deterministic() -> None:
    first = split_records(_records(), ratios=(60, 20, 20), seed="same")
    second = split_records(_records(), ratios=(60, 20, 20), seed="same")

    assert first.summary == {"train": 6, "validation": 2, "test": 2}
    assert first.splits == second.splits


def test_preserves_small_strata_across_splits() -> None:
    records = [
        {"id": "a", "category": "x", "input": "one"},
        {"id": "b", "category": "x", "input": "two"},
        {"id": "c", "category": "x", "input": "three"},
    ]

    result = split_records(records, ratios=(80, 10, 10))

    assert result.summary == {"train": 1, "validation": 1, "test": 1}


def test_detects_text_leakage_across_splits() -> None:
    leakage = detect_leakage(
        {
            "train": [{"id": "a", "input": "Reset  password"}],
            "validation": [{"id": "b", "input": "reset password"}],
            "test": [],
        },
        "input",
    )

    assert leakage == ["b in validation duplicates a in train"]


def test_reads_jsonl(tmp_path) -> None:
    path = tmp_path / "eval.jsonl"
    path.write_text('{"id":"1","input":"hello"}\n', encoding="utf-8")

    assert read_jsonl(path) == [{"id": "1", "input": "hello"}]


def test_cli_writes_splits_and_json_report(tmp_path, capsys) -> None:
    input_path = tmp_path / "eval.jsonl"
    out_dir = tmp_path / "splits"
    input_path.write_text(
        "\n".join(json.dumps(record) for record in _records()) + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            str(input_path),
            "--out-dir",
            str(out_dir),
            "--ratios",
            "60,20,20",
            "--report-format",
            "json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert (out_dir / "train.jsonl").exists()
    assert json.loads(captured.out)["summary"]["test"] == 2

