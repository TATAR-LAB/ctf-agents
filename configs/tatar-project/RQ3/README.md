# RQ3: Model Selection — Which LLMs perform best on CTF challenges?

## Hypotheses
- H3.1: Larger frontier models outperform smaller models
- H3.2: Pentest-specialized models outperform general-purpose models

## Models to Test (17 total)

| Model | Provider | Size | Reasoning | Access | Config File |
|-------|----------|------|-----------|--------|-------------|
| gemini-3-pro | Google | - | Yes | Vertex AI | `gemini3_pro.yaml` |
| gemini-3-flash | Google | - | Yes | Vertex AI | `gemini3_flash.yaml` |
| gpt-5.2 | OpenAI | - | Yes | OpenRouter | `gpt52.yaml` |
| gpt-5.2-pro | OpenAI | - | Yes | OpenRouter | `gpt52_pro.yaml` |
| gpt-5.2-codex | OpenAI | - | Yes | OpenRouter | `gpt52_codex.yaml` |
| claude-4.5-haiku | Anthropic | - | Yes | OpenRouter | `claude_haiku.yaml` |
| claude-4.5-sonnet | Anthropic | - | Yes | OpenRouter | `claude_sonnet.yaml` |
| claude-4.5-opus | Anthropic | - | Yes | OpenRouter | `claude_opus.yaml` |
| deepseek-r1 | DeepSeek | 671B | Yes | OpenRouter | `deepseek_r1.yaml` |
| deepseek-v3 | DeepSeek | 671B | Yes | OpenRouter | `deepseek_v3.yaml` |
| grok-4 | xAI | - | Yes | OpenRouter | `grok4.yaml` |
| grok-4.1-fast | xAI | - | Yes | OpenRouter | `grok41_fast.yaml` |
| llama-3.3-70b-instruct | Meta | 70B | No | Vertex AI | `llama33_70b.yaml` |
| llama-3.1-8b-instruct | Meta | 8B | No | Vertex AI | `llama31_8b.yaml` |
| Qwen3-30B-A3B-Instruct | Alibaba | 30B | No | Vertex AI | `qwen3_30b.yaml` |
| mistral-large | Mistral | - | No | OpenRouter | `mistral_large.yaml` |
| Foundation-Sec-1.1-8B | Cisco | 8B | No | Vertex AI | `foundation_sec_8b.yaml` |

## Notes
- All configs use **dcipher prompts** for consistency
- Both planner and executor use the same model per config
- Run on same challenge set across all models

## Usage

```bash
# Run with a specific model
uv run run_dcipher.py --config configs/tatar-project/RQ3/gemini3_pro.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg

# Run benchmark script across all models
for config in configs/tatar-project/RQ3/*.yaml; do
  echo "Testing: $config"
  uv run run_dcipher.py --config "$config" --challenge "2016q-for-kill" --keys ./keys.cfg
done
```
