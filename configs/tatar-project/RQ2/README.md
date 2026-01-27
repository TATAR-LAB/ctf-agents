# RQ2: Prompt Engineering — Do the "IMPORTANT TIPS" help?

## Hypothesis
H2.1: The "IMPORTANT TIPS" section in the prompts improves solve rates by providing 
actionable guidance (use pwntools, hexdump, disassemble tools, avoid interactive interfaces).

## What's Being Tested

The **only difference** between conditions is the "IMPORTANT TIPS" section in the `initial` prompt:

### Executor Tips (removed in generic)
```
IMPORTANT TIPS:

  - You are an autonomous agent and you should complete the task by yourself...
  - Write python scripts with `pwntools` to pass inputs to local programs...
  - Use `hexdump` to parse binary data instead of dumping it raw.
  - Try to use the provided `disassemble` and `decompile` tools...
  - Write scripts to run commands like `gdb` or `r2`...
  - REMEMBER! You can finish the task and solve the challenge by yourself...
```

### Planner Tips (removed in generic)
```
IMPORTANT TIPS:

  - You are an autonomous agent and you should complete the challenge...
  - Provide specific information in the task description like file names...
  - REMEMBER! You can plan and solve the challenge without my help...
```

## Experiment Conditions

| Condition | Prompts | Config File |
|-----------|---------|-------------|
| A (Treatment) | With IMPORTANT TIPS | `specialized_prompts.yaml` |
| B (Control) | Without IMPORTANT TIPS | `generic_prompts.yaml` |

## Notes
- Both use identical system prompts, initial prompts, continue prompts, etc.
- Only the "IMPORTANT TIPS" section is removed in the generic condition
- Same model (Gemini 3 Pro/Flash) for fair comparison

## Usage

```bash
# With tips (dcipher defaults)
uv run run_dcipher.py --config configs/tatar-project/RQ2/specialized_prompts.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg

# Without tips
uv run run_dcipher.py --config configs/tatar-project/RQ2/generic_prompts.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg
```
