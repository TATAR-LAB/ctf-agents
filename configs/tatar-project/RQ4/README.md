# RQ4: Multi-Agent Architecture — What is the optimal model combination?

## Hypotheses
- H4.1: Large Planner + Small Executor is cost-optimal
- H4.2: Specialized executor models improve performance

## Experiment Conditions

| Config | Planner | Executor | Purpose |
|--------|---------|----------|---------|
| `large_planner_small_executor_gemini.yaml` | Gemini 3 Pro | Gemini 3 Flash | H4.1: Cost optimization |
| `large_planner_small_executor_claude.yaml` | Claude Sonnet | Claude Haiku | H4.1: Cost optimization |
| `same_model_gemini_pro.yaml` | Gemini 3 Pro | Gemini 3 Pro | Baseline: Same model |
| `same_model_claude_sonnet.yaml` | Claude Sonnet | Claude Sonnet | Baseline: Same model |
| `specialized_executor_codex.yaml` | GPT-5.2 | GPT-5.2 Codex | H4.2: Code-specialized |

## Notes
- All configs use dcipher prompts
- Model combinations based on RQ3 findings (top performers)
- Compare solve rate, cost, and token efficiency

## Usage

```bash
# Large Planner + Small Executor (Gemini)
uv run run_dcipher.py --config configs/tatar-project/RQ4/large_planner_small_executor_gemini.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg

# Same model baseline
uv run run_dcipher.py --config configs/tatar-project/RQ4/same_model_gemini_pro.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg
```
