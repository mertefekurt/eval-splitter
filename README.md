![Eval Splitter cover](assets/readme-cover.svg)

# Eval Splitter

Create deterministic stratified splits for LLM evaluation JSONL datasets.

## Working shape

The repo is meant to be opened, understood, and run quickly. The command surface is deliberately narrow: `eval-splitter`.

## Fresh clone

```bash
git clone https://github.com/mertefekurt/eval-splitter.git
cd eval-splitter
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## First command

```bash
eval-splitter examples/eval.jsonl
```

## Local confidence

```bash
ruff check .
pytest
python -m eval_splitter --help
```
