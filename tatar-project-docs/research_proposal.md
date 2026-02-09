# Research Proposal: Advancing LLM-Based CTF Solving with D-CIPHER

**Date:** January 27, 2026  
**Focus:** Improving the D-CIPHER Multi-Agent Framework for Automated CTF Challenge Solving  
**Benchmark:** [NYU CTF Bench](https://nyu-llm-ctf.github.io) - 200 challenges across 6 categories

---

## Executive Summary

This research proposal outlines a systematic study to improve and evaluate the D-CIPHER framework for automated CTF challenge solving. We propose testing multiple LLM configurations, environment improvements, and architectural variations to identify optimal approaches for AI-based cybersecurity competitions.

---

## Background

### D-CIPHER Framework

D-CIPHER is a multi-agent system consisting of:

- **Planner Agent:** Devises step-by-step plans to solve CTF challenges
- **Executor Agent:** Executes specific tasks delegated by the Planner
- **Auto-Prompter Agent (Optional):** Generates tailored prompts based on challenge exploration

### Current Environment

- **Base Image:** Ubuntu 22.04
- **Tools Available:** gdb, radare2, Ghidra, pwntools, angr, sqlmap, nikto, etc.
- **Limitations:** No Kali Linux toolset, limited penetration testing capabilities

---

## Research Questions & Hypotheses

### RQ1: Infrastructure — Does enhanced security tooling improve results?

**Objective:** Evaluate whether providing LLMs with access to enhanced security tooling and comprehensive tool documentation affects CTF solving capability.

#### Hypothesis 1.1: Enhanced security tooling improves solve rates

> **H1.1:** Providing LLMs with access to a comprehensive set of penetration testing tools will improve solve rates compared to the baseline Ubuntu environment.
>
> **Rationale:** Security-specialized tools (nmap, john, hashcat, burpsuite, etc.) may be necessary for certain challenge types that require specific capabilities not available in the base environment.
>
> - Replace Ubuntu-based Docker environment with Kali Linux, providing pre-installed penetration testing tools
> - Integrate the [MCP-Kali Server](https://www.kali.org/tools/mcp-kali-server/) as an MCP tool, allowing LLMs to execute Kali security tools through the Model Context Protocol without replacing the base environment
>
> **MCP-Kali Server Details:**
>
> - Lightweight API bridge connecting LLMs to Kali Linux tools via MCP
> - Enables execution of nmap, nxc, curl, wget, gobuster, and other security tools
> - Can be installed via `sudo apt install mcp-kali-server` or Docker
> - Supports CTF and bug bounty workflows natively
>
> **Metrics:** Solve rate comparison, tool usage patterns, failed tool invocation counts, successful tool invocations

---

### RQ2: Prompt Engineering — How do prompts affect performance?

**Objective:** Evaluate the impact of system prompt content on LLM performance.

#### Hypothesis 2.1: Prompt customization improves performance

> **H2.1:** Customized prompts (including category-specific tips and guidance) will improve solve rates compared to minimal generic prompts.
>
> **Rationale:** LLMs benefit from domain-specific guidance. Category-specialized prompts can direct agents toward appropriate techniques for each challenge type.
>
> **Current State:** Framework has category-specific prompts (e.g., `crypto_planner_prompt.yaml`) with tips like "Write python scripts with pwntools" and "Use hexdump to parse binary data"
>
> **Experiment:**
>
> - **Condition A:** Category-specific prompts with tips (SPECIALIZED)
> - **Condition B:** Minimal generic prompts without tips (GENERIC)
>
> **Metrics:** Solve rate comparison by category, error rates, category-wise solve rates

---

### RQ3: Model Selection — Which LLMs perform best on CTF challenges?

**Objective:** Benchmark models across different providers and sizes to identify top performers, with emphasis on comparing general-purpose models against security-specialized models.

#### Hypothesis 3.1: Larger frontier models outperform smaller models

> **H3.1:** Larger frontier models (GPT-5.2, Claude 4.5 Sonnet, Gemini 3 Pro) will significantly outperform smaller models (Llama 3.1 8B, Qwen 30B) on complex CTF challenges.
>
> **Rationale:** Larger models have more reasoning capacity and broader knowledge of security techniques.
>
> **Metrics:** Challenge solve rate, rounds to solution, token usage

#### Hypothesis 3.2: Pentest-specialized models outperform general-purpose models

> **H3.2:** Security-focused or pentest-specialized LLMs will outperform general-purpose models on CTF challenges, particularly in categories requiring specialized security knowledge.
>
> **Rationale:** Models fine-tuned on security content may have better knowledge of exploitation techniques, vulnerability patterns, and security tool usage.
>
> **Metrics:** Category-wise solve rates, comparison with CyBench leaderboard results

---

### RQ4: Multi-Agent Architecture — What is the optimal model combination?

**Objective:** Investigate whether different model combinations for Planner and Executor roles affect performance.

> **Note:** Model combinations will be determined based on findings from RQ3 (Model Selection). Top-performing models from RQ3 will be used to test architectural variations.

#### Hypothesis 4.1: Large Planner + Small Executor is cost-optimal

> **H4.1:** Using a larger, more capable model as Planner and a smaller, faster model as Executor will achieve better cost-performance balance than uniform model assignment.
>
> **Rationale:** Planning requires more strategic reasoning, while execution is more mechanical.
>
> **Combinations to Test (based on RQ3 findings):**
>
> - Large Planner (GPT-5.2) + Small Executor (GPT-5.2-Mini)
> - Large Planner (Gemini 3 Pro) + Small Executor (Gemini 3 Flash)
> - Large Planner (Claude 4.5 Sonnet) + Small Executor (Claude 4.5 Haiku)
> - Equal models: Both use same model
>
> **Metrics:** Solve rate, cost per challenge, token efficiency

#### Hypothesis 4.2: Specialized executor models improve performance

> **H4.2:** Using a code-specialized or pentest-specialized model as Executor will outperform general-purpose models in execution tasks.
>
> **Rationale:** Execution often involves code analysis, exploit writing, and tool usage that specialized models may handle better.
>
> **Metrics:** Solve rate, token efficiency, execution success rate

---

### RQ5: Reproducibility — How consistent are LLM CTF solvers?

**Objective:** Quantify the variance in LLM performance across multiple runs of the same challenge.

#### Hypothesis 5.1: Significant run-to-run variance exists

> **H5.1:** Running the same challenge with identical configuration multiple times will yield different success outcomes due to LLM non-determinism.
>
> **Rationale:** LLMs have inherent randomness that affects decision-making. Understanding variance is essential for statistical validity.
>
> **Configuration:** Temperature = 1.0 (D-CIPHER paper found this provides optimal performance)
>
> **Experiment:**
>
> - Run each challenge 5 times with identical settings
> - Calculate success rate variance and standard deviation
>
> **Metrics:** Success rate variance, standard deviation of rounds used, confidence intervals

---

## Experimental Design

### Independent Variables

1. **Model Selection:** 15+ different LLMs (including leaderboard models)
2. **Environment:** Ubuntu vs. Kali Linux Docker vs. MCP-Kali Server
3. **Model Combination:** Various Planner-Executor pairings
4. **System Prompts:** Specialized vs. Generic prompts

### Dependent Variables

1. **Solve Rate:** Percentage of challenges solved
2. **Rounds Used:** Number of planner/executor rounds
3. **Token Usage:** Input/output tokens consumed
4. **Time:** Total runtime per challenge
5. **Cost:** API cost per challenge
6. **Error Rate:** Failed tool invocations, parsing errors

### Control Variables

1. **Challenge Set:** Consistent subset of NYU CTF Bench
2. **Docker Environment:** Same base configuration per condition
3. **Network Conditions:** Same containerized setup
4. **Timeout:** Consistent max rounds/time limits

---

## Analysis Metrics

### Cost-Performance Analysis

Cost-performance tradeoffs are analyzed as part of the results rather than as a separate research question. Key metrics include:

| Metric | Description |
| ------ | ----------- |
| **Cost per Solved Challenge** | Total API cost / number of challenges solved |
| **Cost per Point Gained** | Total API cost / total CTF points earned |
| **Solve Rate per Dollar** | Challenges solved / total cost |
| **Token Efficiency** | Challenges solved / total tokens used |

This analysis will inform future work on orchestrator agents that dynamically allocate resources based on challenge difficulty.

### Statistical Validity

- Minimum 5 runs per configuration for variance estimation
- Report confidence intervals for all solve rates
- Use appropriate statistical tests for comparisons

---


## Data Collection Template

For each experimental run, record:

| Field             | Description           | Example                               |
| ----------------- | --------------------- | ------------------------------------- |
| Run ID            | Unique identifier     | `run_001_gpt4o_crypto_001`            |
| Timestamp         | ISO timestamp         | `2026-01-20T14:30:00Z`                |
| Challenge         | Challenge name        | `2016q-for-kill`                      |
| Category          | CTF category          | `forensics`                           |
| Model (Planner)   | Planner model         | `gpt-5.2`                             |
| Model (Executor)  | Executor model        | `gemini-3-flash`                      |
| Config            | Configuration file    | `vertexai_config.yaml`                |
| Auto-Prompter     | On/Off                | `False`                               |
| Environment       | Docker/MCP setup      | `kali` / `ubuntu`        |
| Prompt Type       | Specialized/Generic   | `specialized`                         |
| Solved            | Success/Failure       | `True`                                |
| Points            | Challenge points      | `50`                                  |
| Rounds (Planner)  | Planner rounds used   | `12`                                  |
| Rounds (Executor) | Total executor rounds | `45`                                  |
| Time (seconds)    | Total runtime         | `324`                                 |
| Tokens (input)    | Total input tokens    | `15234`                               |
| Tokens (output)   | Total output tokens   | `8432`                                |
| Cost ($)          | API cost              | `0.23`                                |
| Failure Reason    | If failed, why        | `timeout/giveup/error`                |
| Notes             | Observations          | `Used wrong tool for binary analysis` |

---

## Expected Contributions

1. **Comprehensive Model Benchmark:** Systematic comparison of frontier and security-specialized LLMs on CTF challenges, aligned with CyBench leaderboard
2. **Infrastructure Comparison:** Evidence-based comparison of Ubuntu vs. MCP-Kali Server approaches
3. **Architecture Guidelines:** Best practices for multi-agent model combinations
4. **Prompt Engineering Insights:** Impact analysis of specialized vs. generic prompts
5. **Cost-Performance Analysis:** Practical guidance including cost-per-point metrics

---

## Resources Required

### Compute

- [x] Vertex AI access for Gemini and partner models
- [x] OpenRouter credits for proprietary model access
- [x] Local GPU for Ollama (optional)
- [x] Docker environment with sufficient compute

### Data

- [x] NYU CTF Bench dataset (200 challenges)
- [-] Additional challenges from CyBench (optional)

### Tools

- [x] Kali Linux Docker image
- [x] MCP-Kali Server installation
- [-] Logging and analysis scripts
