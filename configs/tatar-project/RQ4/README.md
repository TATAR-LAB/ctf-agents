# RQ4: Multi-Agent Architecture — What is the optimal model combination?

## Hypotheses
- H4.1: Large Planner + Small Executor is cost-optimal

## Experiment Conditions

| Config | Planner | Executor | Purpose |
|--------|---------|----------|---------|
| `large_planner_small_executor_gemini.yaml` | Gemini 3 Pro | Gemini 3 Flash | H4.1: Cost optimization |
| `small_planner_large_executor_gemini.yaml` | Gemini 3 Flash | Gemini 3 Pro | H4.1: Cost optimization |


## Usage

```bash
# Large Planner + Small Executor (Gemini)
uv run run_dcipher.py --config configs/tatar-project/RQ4/large_planner_small_executor_gemini.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg

# Same model baseline
uv run run_dcipher.py --config configs/tatar-project/RQ4/same_model_gemini_pro.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg
```
