# LLM CTF Solver Research Project

**Timeline:** 4 weeks (Poster Submission Deadline: February 12, 2026)  
**Focus:** Benchmarking LLM-based CTF Solving Architectures

---

## 📋 Project Overview

This project evaluates different LLM architectures for solving Capture The Flag (CTF) challenges:

| Approach     | Paper    | Architecture                    |
| ------------ | -------- | ------------------------------- |
| **D-CIPHER** | NYU      | Multi-agent (Planner-Executor)  |
| **CRAKEN**   | External | Knowledge-Based Execution (RAG) |
| **EnIGMA**   | External | Interactive Tool Use            |

**Benchmark:** [NYU CTF Bench](https://nyu-llm-ctf.github.io) - 200 challenges across 6 categories

---

## 🗓️ Weekly Timeline

### Week 1 (Jan 12-18): Setup & Familiarization

| Task                                      |
| ----------------------------------------- |
| Read D-CIPHER paper                       |
| Read CRAKEN paper                         |
| Read EnIGMA paper                         |
| Clone & setup repositories locally        |
| Run D-CIPHER on 1 easy challenge (Ollama) |
| Document setup issues/questions           |

**Deliverable:** Everyone can run D-CIPHER locally with Ollama

---

### Week 2 (Jan 19-25): Model Exploration

| Task                                          |
| --------------------------------------------- |
| Connect to Vertex AI endpoints                |
| Test Gemini models (gemini-2.0-flash)         |
| Test open-source models via OpenRouter        |
| Research available pentest-specific LLMs      |
| Run 5+ challenges across different categories |
| Collect success/failure logs                  |

**Deliverable:** Model comparison spreadsheet (model, challenge, solved?, tokens, time)

---

### Week 3 (Jan 26 - Feb 1): Experimentation & Analysis

| Task                                                      | RQ    |
| --------------------------------------------------------- | ----- |
| Run systematic experiments (20+ challenges)               | All   |
| RQ1: Test Kali Linux Docker / MCP-Kali Server integration | RQ1   |
| RQ2: Compare specialized vs generic prompts               | RQ2   |
| RQ3: Benchmark frontier vs smaller models                 | RQ3   |
| RQ5: Run 5 repetitions for variance analysis              | RQ5   |
| Deploy open-source HuggingFace models to Vertex AI        | Setup |
| Find how to use 290 challenges (90 CyBench + HackTheBox)  | Data  |
| Collect Kali tool documentation / man pages               | RQ1   |
| Analyze failure modes                                     | All   |

**Deliverable:** Preliminary results table + key findings

---

### Week 4 (Feb 2-8): Poster Preparation

| Task                                  |
| ------------------------------------- |
| Finalize experiment results           |
| Create visualizations (charts/graphs) |
| Draft poster sections                 |
| Review and iterate on poster          |
| Prepare 2-min presentation            |

**Deliverable:** Final poster PDF

---

## 🛠️ Technical Setup Tasks

### Local Environment Setup

```bash
# 1. Clone repository
git clone <ctf-agents-repo>
cd ctf-agents

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Build Docker image
cd docker/multiagent
# docker build -f Dockerfile.arm -t ctfenv:multiagent .  # For Mac ARM
docker build -f Dockerfile -t ctfenv:multiagent .  # For Linux
docker network create ctfnet
cd ../..

# 4. Configure keys.cfg
echo "OLLAMA=ollama" > keys.cfg

# 5. Run first challenge
uv run run_dcipher.py --split development --challenge "2016q-for-kill" --config configs/dcipher/ollama_config.yaml --keys ./keys.cfg
# OR
uv run run_dcipher.py --split development --challenge "2016q-for-kill" --config configs/dcipher/vertexai_config.yaml --keys ./keys.cfg
# OR
uv run run_dcipher.py --split development --challenge "2016q-for-kill" --config configs/dcipher/openrouter_config.yaml --keys ./keys.cfg
```

### Available Configurations

| Config                   | Backend        | Notes                       |
| ------------------------ | -------------- | --------------------------- |
| `ollama_config.yaml`     | Ollama (local) | Free, requires local Ollama |
| `vertexai_config.yaml`   | Vertex AI      | Requires `gcloud auth`      |
| `openrouter_config.yaml` | OpenRouter     | Access to 200+ models       |

### Models 

https://1drv.ms/x/c/8ff85b3a143d6c03/IQDGBcKO9J0aSaqYDA3gJ-h6AYLZJ_oAdjsKYTNqO5vomzk

---

## 📊 Data Collection Template

For each experiment run, record:

| Field      | Value                             |
| ---------- | --------------------------------- |
| Challenge  | e.g., 2016q-for-kill              |
| Category   | forensics/web/crypto/pwn/rev/misc |
| Model      | e.g., gemini-2.0-flash            |
| Config     | ollama/vertexai/openrouter        |
| Solved?    | ✅ / ❌                           |
| Rounds     | # of planner rounds               |
| Time (min) | Total runtime                     |
| Cost ($)   | API cost if applicable            |
| Notes      | Failure reason, observations      |

---

## 📚 Reading List Priority

1. **Required (Week 1):**

   - [NYU CTF Bench Paper](https://arxiv.org/abs/2406.05590) - Understand the benchmark
   - [D-CIPHER Paper](https://arxiv.org/abs/2412.07880) - Multi-agent architecture

2. **Recommended (Week 2-3):**

   - [CRAKEN Paper](https://arxiv.org/abs/) - Knowledge retrieval approach
   - [EnIGMA Paper](https://arxiv.org/abs/) - Tool use approach

3. **Optional:**
   - NYU CTF Leaderboard analysis
   - Related CTF automation papers

---

## 🎯 Poster Research Questions

Potential angles for the poster:

1. **Model Comparison:** How do different LLMs perform on CTF challenges?
2. **Architecture Comparison:** Multi-agent vs Single-agent effectiveness
3. **Category Analysis:** Which CTF categories are easiest/hardest for LLMs?
4. **Failure Analysis:** Why do LLMs fail on certain challenges?
5. **Cost-Performance Tradeoff:** Local vs Cloud model performance

---

## 🔗 Resources

- **NYU CTF Website:** https://nyu-llm-ctf.github.io
- **Benchmark Repo:** https://github.com/NYU-LLM-CTF/NYU_CTF_Bench
- **Agents Repo:** https://github.com/NYU-LLM-CTF/nyuctf_agents
- **OpenRouter:** https://openrouter.ai/models
