# Tatar Project Experiment Configurations

Experiment configurations for the D-CIPHER CTF research project.

## Research Questions

| RQ | Directory | Description | Configs |
|----|-----------|-------------|---------|
| RQ1 | `RQ1/` | Infrastructure (Ubuntu vs Kali) | 2 configs |
| RQ2 | `RQ2/` | Prompt Engineering (Specialized vs Generic) | 2 configs |
| RQ3 | `RQ3/` | Model Selection (17 models) | 17 configs |
| RQ4 | `RQ4/` | Multi-Agent Architecture | 5 configs |
| RQ5 | `RQ5/` | Reproducibility (variance) | 1 config (run 5x) |

## Quick Start

```bash
# Navigate to ctf-agents directory
cd ctf-agents

# Run an experiment
uv run run_dcipher.py \
  --split development \
  --challenge "2016q-for-kill" \
  --config configs/tatar-project/RQ3/gemini3_pro.yaml \
  --keys ./keys.cfg
```

## Directory Structure

```
configs/tatar-project/
├── README.md
├── RQ1/                    # Infrastructure
│   ├── README.md
│   ├── ubuntu_baseline.yaml
│   └── kali_docker.yaml
├── RQ2/                    # Prompts
│   ├── README.md
│   ├── specialized_prompts.yaml
│   ├── generic_prompts.yaml
│   └── prompts/
│       ├── generic_planner_prompt.yaml
│       └── generic_executor_prompt.yaml
├── RQ3/                    # Models
│   ├── README.md
│   └── [17 model configs]
├── RQ4/                    # Architecture
│   ├── README.md
│   └── [5 architecture configs]
└── RQ5/                    # Reproducibility
    ├── README.md
    └── reproducibility_gemini3_pro.yaml
```

## Experiment Execution Order

2. **RQ1** - Test infrastructure improvements with top models
3. **RQ2** - Test prompt variations with top models
1. **RQ3** - Identify top-performing models
4. **RQ4** - Test architecture combinations using RQ3 findings
5. **RQ5** - Run reproducibility analysis on final configurations

## Notes

- All configs use dcipher prompts by default for consistency
- RQ2 has separate generic prompts for the minimal prompt condition
- RQ1 uses same prompts for both Ubuntu and Kali (fair infrastructure comparison)
