# Eval Splitter

![Eval Splitter cover](assets/readme-cover.svg)

![stack](https://img.shields.io/badge/stack-Python-b45309?style=flat-square) ![python](https://img.shields.io/badge/python-3.11-be185d?style=flat-square) ![license](https://img.shields.io/badge/license-MIT-4b5563?style=flat-square) ![ci](https://img.shields.io/badge/ci-GitHub%20Actions-2563eb?style=flat-square)

> Create deterministic stratified splits for LLM evaluation JSONL datasets

## How I use it

The project stays focused on one job: take a small input, produce a clear result, and avoid adding a heavy service around a problem that fits in a command line.

## Quick start

```bash
python -m pip install -e ".[dev]"
eval-splitter examples/eval.jsonl
```

## What is inside

```text
.github/        CI workflow
examples/       sample inputs
src/            package source
tests/          test coverage
.gitignore      project file
pyproject.toml  package metadata
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
python -m eval_splitter --help
```
