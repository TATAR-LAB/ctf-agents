# D-CIPHER Experiment Results

Parse and visualize results from CTF challenge experiments.

## Usage

Run from the `ctf-agents/` directory:

```bash
# 1. Parse real results into JSON
uv run tatar-project-results/parse_results.py

# 2. Generate plots
uv run --with matplotlib --with numpy tatar-project-results/visualize_results.py
```

## Scripts

| Script                 | Description                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `parse_results.py`     | Reads `results/` directory (completed/failed challenges + per-challenge JSONs) and outputs `rq1_rq2_combined.json` and `rq3_models.json` |
| `visualize_results.py` | Generates plots from the parsed JSON into `plots/`                                                                                       |

## Directory Structure

```
results/
├── RQ1_RQ2/
│   ├── exp-results-{suffix}/   # completed_challenges.txt, failed_challenges.txt
│   └── exp-logs-{suffix}/      # per-challenge logs + jupyter/ JSONs
└── RQ3/
    ├── exp-results-{suffix}/
    └── exp-logs-{suffix}/
```

New experiment runs are auto-discovered — just add `exp-results-*` / `exp-logs-*` directories and re-run the parser.
