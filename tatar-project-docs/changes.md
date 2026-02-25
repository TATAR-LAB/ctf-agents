# Changes After Fork

Forked from [NYU-LLM-CTF/ctf-agents](https://github.com/NYU-LLM-CTF/ctf-agents). Below is a summary of what we changed.

## New Backend & Model Support

- Added **Vertex AI** backend (`vertexai_backend.py`) for Google Cloud-hosted models
- Added **OpenRouter** backend (`openrouter_backend.py`) for accessing OpenAI, Anthropic, DeepSeek, xAI, Mistral, and other models via OpenRouter
- Added **Ollama** backend (`ollama_backend.py`) for local model inference
- Rewrote the **Gemini backend** to use the new `google-genai` SDK (replacing the old `google.generativeai`), with Gemini 3 `thought_signature` support
- Created a centralized **`models.yaml`** config file so all model definitions (backend, pricing, context limits) live in one place instead of being hardcoded per backend
- Unified the backend init (`__init__.py`) to dynamically load models from `models.yaml`

## Kali Linux Environment

- Added a full **Kali Linux Docker image** (`docker/kali/`) with pre-installed security tools, Ghidra scripts, and an entrypoint
- Added a `commands_documentation.csv` with documentation for ~100+ Kali security tools
- Added `--use-kali` flag to `run_dcipher.py` and the config system to switch between Ubuntu and Kali environments
- Removed the hardcoded `--platform linux/amd64` flag from Docker run to support ARM (macOS Apple Silicon)

## New Agent Tools

- Added **`LookupCommandTool`** and **`ListCommandsTool`** (`tools/lookup.py`) that let the agent query Kali tool documentation during CTF solving
- Extended `ToolCall` with `thought_signature` field for Gemini 3 compatibility

## Experiment Runner & Automation

- Created **`run_exp_parallel.sh`** — a bash script to run CTF challenges in parallel with resume and cleanup functionality
- Created **`challengeRunner/`** directory with:
  - `autoRun.py` — systematic batch runner for the D-CIPHER framework
  - `autoRunConfig.template.py` — config template for the batch runner
  - `filterFinishedChallenges.py` — filters already-completed challenges from the run list
  - `PythonMetrics.py` — metrics collection script
  - `allChallenges.txt` — full challenge list

## Experiment Configs

- Created **`configs/tatar-project/`** with experiment configs for each research question:
  - **RQ1 & RQ2**: Ubuntu vs Kali, generic vs tips prompts, with/without autoprompt (8 configs + custom prompts)
  - **RQ3**: Per-model configs for 18+ models (Claude, GPT, Gemini, DeepSeek, Grok, Llama, Mistral, Qwen, etc.)
  - **RQ4**: Asymmetric planner/executor architecture configs (large planner + small executor, and vice versa)
  - **RQ5**: Reproducibility configs
- Added D-CIPHER configs for Gemini, Ollama, OpenRouter, and Vertex AI under `configs/dcipher/`

## Results & Visualization

- Added **`tatar-project-results/`** with:
  - `parse_results.py` — parses experiment log files into structured JSON
  - `visualize_results.py` — generates plots for all research questions
  - Result JSON files (`rq1_rq2_combined.json`, `rq3_models.json`, `rq4_architecture.json`)

## Project Documentation

- Added `tatar-project-docs/project_overview.md`, `research_proposal.md`, and `setup_gcp.md`

## Bug Fixes

- Fixed cost calculation for Vertex AI and Gemini models (handling `None` token counts)
- Fixed empty response handling in the agent loop
- Fixed Vertex AI config bug for Gemini 3 models
- Various minor fixes and cleanups in `run_dcipher.py`
