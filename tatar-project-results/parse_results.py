"""
D-CIPHER Real Results Parser
=============================
Reads experiment data from exp-logs-* directories (jupyter JSONs, batch logs,
finishedChallenges.txt) and produces JSON files compatible with visualize_results.py.

Data source priority per experiment:
  1. Jupyter JSON files  (most universal — contain success, total_cost, time_taken)
  2. finishedChallenges.txt  (structured log with SOLVED/FAILED per challenge)
  3. batch_*.log files   (contain "Challenge Solved!" / "Challenge Not Solved!" markers)

Usage:
    uv run parse_results.py [--results-dir results] [--output-dir .]
"""

import json
import re
import argparse
from pathlib import Path

from nyuctf.dataset import CTFDataset

# ── Category mapping from challenge-name abbreviation ────────────────
CAT_MAP = {
    "cry": "crypto",
    "for": "forensics",
    "msc": "misc",
    "pwn": "pwn",
    "rev": "reverse",
    "web": "web",
}

CATEGORY_ORDER = ["crypto", "forensics", "misc", "pwn", "reverse", "web"]

# ── Metadata for each experiment directory suffix ────────────────────
# RQ1_RQ2: suffix → (environment, prompts, autoprompt, label)
RQ1_RQ2_SETUPS = {
    "kt":  {"environment": "kali",   "prompts": "tips",    "autoprompt": False, "label": "Kali + Tips",           "key": "kali_tips"},
    "kta": {"environment": "kali",   "prompts": "tips",    "autoprompt": True,  "label": "Kali + Tips + AP",      "key": "kali_tips_autoprompt"},
    "kg":  {"environment": "kali",   "prompts": "generic", "autoprompt": False, "label": "Kali + Generic",        "key": "kali_generic"},
    "kga": {"environment": "kali",   "prompts": "generic", "autoprompt": True,  "label": "Kali + Generic + AP",   "key": "kali_generic_autoprompt"},
    "ut":  {"environment": "ubuntu", "prompts": "tips",    "autoprompt": False, "label": "Ubuntu + Tips",          "key": "ubuntu_tips"},
    "uta": {"environment": "ubuntu", "prompts": "tips",    "autoprompt": True,  "label": "Ubuntu + Tips + AP",     "key": "ubuntu_tips_autoprompt"},
    "ug":  {"environment": "ubuntu", "prompts": "generic", "autoprompt": False, "label": "Ubuntu + Generic",       "key": "ubuntu_generic"},
    "uga": {"environment": "ubuntu", "prompts": "generic", "autoprompt": True,  "label": "Ubuntu + Generic + AP",  "key": "ubuntu_generic_autoprompt"},
}

# RQ3: suffix → (model name, provider, model type)
# Multiple suffixes may map to the same model (different dir naming conventions).
RQ3_MODELS = {
    "gpt52":            {"name": "GPT-5.2",              "provider": "OpenAI",    "type": "frontier"},
    "gpt52_pro":        {"name": "GPT-5.2-Pro",          "provider": "OpenAI",    "type": "frontier"},
    "gpt52_codex":      {"name": "GPT-5.2-Codex",        "provider": "OpenAI",    "type": "code-specialized"},
    "opus":             {"name": "Claude 4.5 Opus",       "provider": "Anthropic", "type": "frontier"},
    "claude_opus":      {"name": "Claude 4.5 Opus",       "provider": "Anthropic", "type": "frontier"},
    "sonnet":           {"name": "Claude 4.5 Sonnet",     "provider": "Anthropic", "type": "frontier"},
    "claude_sonnet":    {"name": "Claude 4.5 Sonnet",     "provider": "Anthropic", "type": "frontier"},
    "haiku":            {"name": "Claude 4.5 Haiku",      "provider": "Anthropic", "type": "small"},
    "claude_haiku":     {"name": "Claude 4.5 Haiku",      "provider": "Anthropic", "type": "small"},
    "gemini3_pro":      {"name": "Gemini 3 Pro",          "provider": "Google",    "type": "frontier"},
    "gemini3_flash":    {"name": "Gemini 3 Flash",        "provider": "Google",    "type": "small"},
    "deepseek_r1":      {"name": "DeepSeek-R1",           "provider": "DeepSeek",  "type": "reasoning"},
    "deepseek_v3":      {"name": "DeepSeek-V3",           "provider": "DeepSeek",  "type": "frontier"},
    "grok4":            {"name": "Grok-4",                "provider": "xAI",       "type": "frontier"},
    "grok41_fast":      {"name": "Grok-4.1 Fast",         "provider": "xAI",       "type": "small"},
    "llama33_70b":      {"name": "Llama 3.3 70B",         "provider": "Meta",      "type": "open-source"},
    "llama31_8b":       {"name": "Llama 3.1 8B",          "provider": "Meta",      "type": "open-source"},
    "qwen35":        {"name": "Qwen 3.5 397B-A17B",             "provider": "Alibaba",   "type": "open-source"},
    "glm5":             {"name": "GLM-5",                 "provider": "Z-AI",      "type": "frontier"},
    "kimik25":          {"name": "Kimi K2.5",             "provider": "Moonshot",  "type": "frontier"},
    "mistral_large":    {"name": "Mistral Large",         "provider": "Mistral",   "type": "frontier"},
    "foundation_sec_8b":{"name": "Foundation-Sec 8B",     "provider": "Cisco",     "type": "security-specialized"},
}

# RQ4: suffix → (planner model, executor model, label)
RQ4_SETUPS = {
    "large_planner_small_executor": {
        "planner": "Gemini 3 Pro",
        "executor": "Gemini 3 Flash",
        "label": "Pro Planner + Flash Executor",
        "key": "pro_plan_flash_exec",
    },
    "small_planner_large_executor": {
        "planner": "Gemini 3 Flash",
        "executor": "Gemini 3 Pro",
        "label": "Flash Planner + Pro Executor",
        "key": "flash_plan_pro_exec",
    },
}

# RQ5: suffix → run metadata
# Multiple exp-logs dirs map to the same config run at different times.
RQ5_CONFIG = {
    "base_suffix": "reproducibility_gemini",
    "model": "Gemini 3 Pro",
    "label": "Reproducibility (Gemini 3 Pro)",
}


VALID_CAT_ABBREVS = set(CAT_MAP.keys())


def is_valid_challenge_name(name: str) -> bool:
    """Validate that a challenge name follows the YYYY[fq]-CAT-name pattern.

    Also checks year range (benchmark is 2017–2023) and that the name portion
    after the category is non-empty.
    """
    parts = name.split("-")
    if len(parts) < 3:
        return False
    year_part = parts[0]
    if len(year_part) != 5 or not year_part[:4].isdigit() or year_part[4] not in "fq":
        return False
    year = int(year_part[:4])
    if year < 2017 or year > 2023:
        return False
    if parts[1] not in VALID_CAT_ABBREVS:
        return False
    # The challenge name part (everything after YYYY[fq]-CAT-) must be non-empty
    challenge_part = "-".join(parts[2:])
    return len(challenge_part) > 0


def extract_category(challenge_name: str) -> str:
    """Extract category from challenge name like '2017f-cry-ecxor' → 'crypto'."""
    parts = challenge_name.split("-")
    if len(parts) >= 2:
        abbrev = parts[1]
        return CAT_MAP.get(abbrev, "unknown")
    return "unknown"


# ─────────────────────────────────────────────────────────────────────
# Data-source readers
# ─────────────────────────────────────────────────────────────────────

def _parse_filename_timestamp(stem: str) -> int:
    """Extract numeric timestamp from filename stem for recency comparison.

    Filename: 'challenge-name-260216181333' → timestamp 260216181333.
    Returns 0 if no valid timestamp found.
    """
    parts = stem.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return int(parts[1])
    return 0


def read_jupyter_jsons(logs_dir: Path) -> dict[str, dict]:
    """Read per-challenge jupyter JSON files.

    Returns dict of challenge_name → {success, total_cost, time_taken}.
    Handles both flat layout and default/ subdirectory.

    Duplicate handling: when multiple log files exist for the same challenge,
    prefer the successfully-solved run. Among ties (both solved or both failed),
    prefer the most recent run (highest filename timestamp).
    """
    result: dict[str, dict] = {}
    jupyter_dir = logs_dir / "jupyter"
    if not jupyter_dir.exists():
        return result

    default_dir = jupyter_dir / "default"
    search_dir = default_dir if default_dir.exists() else jupyter_dir

    for json_file in search_dir.glob("*.json"):
        stem = json_file.stem
        parts = stem.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            challenge_name = parts[0]
            timestamp = int(parts[1])
        else:
            challenge_name = stem
            timestamp = 0

        if not is_valid_challenge_name(challenge_name):
            continue

        try:
            with open(json_file) as f:
                data = json.load(f)
            info = {
                "success": data.get("success", False),
                "total_cost": data.get("total_cost", 0.0),
                "time_taken": data.get("time_taken", 0.0),
                "exit_reason": data.get("exit_reason", ""),
                "_timestamp": timestamp,
            }
        except (json.JSONDecodeError, OSError):
            continue

        existing = result.get(challenge_name)
        if existing is None:
            result[challenge_name] = info
        elif info["success"] and not existing["success"]:
            result[challenge_name] = info
        elif info["success"] == existing["success"] and timestamp > existing["_timestamp"]:
            result[challenge_name] = info

    # Strip internal metadata before returning
    for info in result.values():
        info.pop("_timestamp", None)

    return result


def read_finished_challenges(logs_dir: Path) -> dict[str, dict]:
    """Parse finishedChallenges.txt if present.

    Format per line:
        challenge_name - SOLVED/FAILED/NOT_SOLVED - [details] - exit: ... cost: $X.XX ...

    Returns dict of challenge_name → {success, total_cost}.
    Deduplicates: if a challenge appears multiple times, SOLVED wins.
    Skips entries with FAILED TO RUN / KEY_ERROR (infrastructure errors).
    """
    result = {}
    fc_path = logs_dir / "finishedChallenges.txt"
    if not fc_path.exists():
        return result

    cost_re = re.compile(r"cost:\s*\$?([\d.]+)")

    for line in fc_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(" - ", 2)
        if len(parts) < 2:
            continue

        challenge_name = parts[0].strip()
        if not is_valid_challenge_name(challenge_name):
            continue

        status = parts[1].strip().upper()
        rest = parts[2] if len(parts) > 2 else ""

        # Skip infrastructure failures — these aren't real attempts
        if status == "FAILED" and ("FAILED TO RUN" in rest.upper() or "KEY_ERROR" in rest.upper()):
            continue

        success = status == "SOLVED"

        cost = 0.0
        m = cost_re.search(rest)
        if m:
            try:
                cost = float(m.group(1))
            except ValueError:
                pass

        # Keep solved over failed for duplicates
        if challenge_name not in result or success:
            result[challenge_name] = {
                "success": success,
                "total_cost": cost,
            }

    return result


def read_batch_logs(logs_dir: Path) -> dict[str, dict]:
    """Parse per-challenge batch_*.log files.

    Looks for lines: "Challenge Solved!" / "Challenge Not Solved!"
    and "exit: ... cost: $X.XX ..."

    Returns dict of challenge_name → {success, total_cost}.
    """
    result = {}
    cost_re = re.compile(r"cost:\s*\$?([\d.]+)")

    for log_file in logs_dir.glob("batch_*.log"):
        # Filename: batch_2017f-cry-ecxor.log → challenge_name: 2017f-cry-ecxor
        stem = log_file.stem
        if not stem.startswith("batch_"):
            continue
        challenge_name = stem[len("batch_"):]
        if not challenge_name:
            continue

        # Read last 2KB to find outcome markers (avoid reading huge files)
        try:
            size = log_file.stat().st_size
            with open(log_file, "r", errors="replace") as f:
                if size > 4096:
                    f.seek(size - 4096)
                tail = f.read()
        except OSError:
            continue

        success = "Challenge Solved!" in tail
        # Also check for NOT_SOLVED marker if no solved marker found
        failed = "Challenge Not Solved!" in tail

        cost = 0.0
        # Find the last "exit:" line in the tail
        for line in reversed(tail.splitlines()):
            if "exit:" in line and "cost:" in line:
                m = cost_re.search(line)
                if m:
                    try:
                        cost = float(m.group(1))
                    except ValueError:
                        pass
                break

        if success or failed:
            result[challenge_name] = {
                "success": success,
                "total_cost": cost,
            }

    return result


# ─────────────────────────────────────────────────────────────────────
# Master challenge list
# ─────────────────────────────────────────────────────────────────────

def build_master_challenge_list() -> list[str]:
    """Load the canonical list of 200 benchmark challenges from the NYU CTF dataset."""
    ds = CTFDataset(split="test")
    return sorted(ds.dataset.keys())


# ─────────────────────────────────────────────────────────────────────
# Unified challenge data extraction
# ─────────────────────────────────────────────────────────────────────

def extract_challenge_data(logs_dir: Path, master_challenges: list[str]
                           ) -> tuple[list[str], list[str], dict[str, float]]:
    """Extract completed/failed challenge lists and costs from an exp-logs dir.

    Tries data sources in priority order:
        1. Jupyter JSONs (most complete data: success, cost, time)
        2. finishedChallenges.txt  (structured log)
        3. batch_*.log  (outcome markers at end of files)

    Only challenges in master_challenges are included.
    Any challenge in master_challenges not found in logs is treated as failed.

    Returns:
        completed: list of solved challenge names
        failed: list of failed/unsolved challenge names
        costs: dict of challenge_name → total_cost (for solved challenges)
    """
    master_set = set(master_challenges)
    completed_set: set[str] = set()
    failed_set: set[str] = set()
    costs: dict[str, float] = {}

    def _mark_solved(ch: str, cost: float) -> None:
        failed_set.discard(ch)
        completed_set.add(ch)
        costs[ch] = cost

    def _mark_failed(ch: str) -> None:
        if ch not in completed_set:
            failed_set.add(ch)

    def _apply_source(data: dict[str, dict]) -> None:
        for ch, info in data.items():
            if ch not in master_set:
                continue
            if info["success"]:
                _mark_solved(ch, info.get("total_cost", 0.0))
            elif ch not in completed_set and ch not in failed_set:
                _mark_failed(ch)

    # Sources in priority order — solved in any source wins
    _apply_source(read_jupyter_jsons(logs_dir))
    _apply_source(read_finished_challenges(logs_dir))
    _apply_source(read_batch_logs(logs_dir))

    # Pad missing benchmark challenges as failed
    for ch in master_challenges:
        if ch not in completed_set and ch not in failed_set:
            failed_set.add(ch)

    return sorted(completed_set), sorted(failed_set), costs


EXIT_REASON_MAP = {
    "solved":          "Solved",
    "cost":            "MaxCost",
    "planner_rounds":  "MaxRound",
    "giveup":          "Gave Up",
    "error":           "Error/Bug",
}
EXIT_REASON_ORDER = ["Solved", "MaxCost", "MaxRound", "Timeout", "Gave Up", "Error/Bug", "Not Attempted"]


BATCH_EXIT_RE = re.compile(r"exit:\s*(\S+)\s+cost:")
FAILED_CHALLENGE_RE = re.compile(r"^([^:]+):(\S+)$")

FAILED_TXT_MAP = {
    "TIMEOUT": "Timeout",
    "EXIT_1":  "Error/Bug",
}


def extract_exit_reasons(logs_dir: Path, master_challenges: list[str]) -> dict[str, int]:
    """Count exit reasons for an experiment, mapped to display categories.

    Aggregates from multiple sources in priority order:
      1. Jupyter JSONs (exit_reason field)
      2. Batch log exit lines (exit: <reason> cost: ...)
      3. failed_challenges.txt (challenge:TIMEOUT / challenge:EXIT_1)
      4. completed_challenges.txt (solved, no detailed reason)
    Challenges not found in any source → 'Not Attempted'.
    """
    master_set = set(master_challenges)
    per_challenge: dict[str, str] = {}

    # Source 1: jupyter JSONs (most authoritative)
    jupyter_data = read_jupyter_jsons(logs_dir)
    for ch, info in jupyter_data.items():
        if ch not in master_set:
            continue
        raw = info.get("exit_reason", "")
        per_challenge[ch] = EXIT_REASON_MAP.get(raw, "Error/Bug")

    # Source 2: batch log exit lines
    cost_re = re.compile(r"cost:\s*\$?([\d.]+)")
    for log_file in logs_dir.glob("batch_*.log"):
        ch = log_file.stem[len("batch_"):]
        if ch not in master_set or ch in per_challenge:
            continue
        try:
            size = log_file.stat().st_size
            with open(log_file, "r", errors="replace") as f:
                if size > 4096:
                    f.seek(size - 4096)
                tail = f.read()
        except OSError:
            continue

        for line in reversed(tail.splitlines()):
            m = BATCH_EXIT_RE.search(line)
            if m:
                raw = m.group(1)
                per_challenge[ch] = EXIT_REASON_MAP.get(raw, "Error/Bug")
                break
        else:
            if "Challenge Solved!" in tail:
                per_challenge[ch] = "Solved"

    # Source 3: failed_challenges.txt
    failed_path = logs_dir / "failed_challenges.txt"
    if failed_path.exists():
        for line in failed_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            m = FAILED_CHALLENGE_RE.match(line)
            if m:
                ch, code = m.group(1), m.group(2)
                if ch in master_set and ch not in per_challenge:
                    per_challenge[ch] = FAILED_TXT_MAP.get(code, "Error/Bug")

    # Source 4: completed_challenges.txt
    completed_path = logs_dir / "completed_challenges.txt"
    if completed_path.exists():
        for line in completed_path.read_text().splitlines():
            ch = line.strip()
            if ch in master_set and ch not in per_challenge:
                per_challenge[ch] = "Solved"

    counts: dict[str, int] = {r: 0 for r in EXIT_REASON_ORDER}
    for ch in master_challenges:
        reason = per_challenge.get(ch, "Not Attempted")
        counts[reason] += 1
    return counts


def compute_stats(completed: list[str], failed: list[str],
                  costs: dict[str, float],
                  master_challenges: list[str]) -> dict:
    """Compute solve stats for one experiment setup.

    Uses master_challenges for per-category totals so that the
    denominator is always the full 200 challenges.
    """
    total = len(master_challenges)
    solved = len(completed)

    # Per-category totals from master list
    cat_total = {c: 0 for c in CATEGORY_ORDER}
    for ch in master_challenges:
        cat = extract_category(ch)
        if cat in cat_total:
            cat_total[cat] += 1

    # Per-category solved from actual results
    cat_solved = {c: 0 for c in CATEGORY_ORDER}
    for ch in completed:
        cat = extract_category(ch)
        if cat in cat_solved:
            cat_solved[cat] += 1

    by_category = {}
    for cat in CATEGORY_ORDER:
        t = cat_total[cat]
        s = cat_solved[cat]
        by_category[cat] = {
            "solved": s,
            "total": t,
            "solve_rate": round(s / t, 4) if t > 0 else 0.0,
        }

    # Cost stats
    cost_values = [costs[ch] for ch in completed if ch in costs]
    avg_cost = round(sum(cost_values) / len(cost_values), 4) if cost_values else 0.0
    total_cost = round(sum(cost_values), 2)

    overall = {
        "solved": solved,
        "total": total,
        "solve_rate": round(solved / total, 4) if total > 0 else 0.0,
        "avg_cost": avg_cost,
        "total_cost": total_cost,
    }

    return {"overall": overall, "by_category": by_category}


def parse_rq1_rq2(results_dir: Path, master_challenges: list[str]) -> dict:
    """Parse all RQ1_RQ2 experiment results from exp-logs-* directories."""
    rq_dir = results_dir / "RQ1_RQ2"
    conditions = {}

    for logs_subdir in sorted(rq_dir.glob("exp-logs-*")):
        suffix = logs_subdir.name.replace("exp-logs-", "")
        if suffix not in RQ1_RQ2_SETUPS:
            print(f"  ⚠ Unknown RQ1_RQ2 suffix: {suffix}, skipping")
            continue

        meta = RQ1_RQ2_SETUPS[suffix]
        completed, failed, costs = extract_challenge_data(logs_subdir, master_challenges)

        if not completed and not failed:
            print(f"  ⚠ {meta['label']}: no challenge data found, skipping")
            continue

        stats = compute_stats(completed, failed, costs, master_challenges)
        exit_reasons = extract_exit_reasons(logs_subdir, master_challenges)
        key = meta["key"]
        conditions[key] = {
            "label": meta["label"],
            "config": f"{key}.yaml",
            "environment": meta["environment"],
            "prompts": meta["prompts"],
            "autoprompt": meta["autoprompt"],
            "overall": stats["overall"],
            "by_category": stats["by_category"],
            "exit_reasons": exit_reasons,
        }
        print(f"  ✓ {meta['label']}: {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    return {
        "title": "RQ1 + RQ2: Infrastructure × Prompt Engineering × AutoPrompt",
        "description": "2×2×2 factorial design: Environment (Ubuntu/Kali) × Prompts (Generic/Tips) × AutoPrompt (Off/On)",
        "total_challenges": len(master_challenges),
        "categories": CATEGORY_ORDER,
        "conditions": conditions,
    }


def parse_rq3(results_dir: Path, master_challenges: list[str]) -> dict:
    """Parse all RQ3 experiment results from exp-logs-* directories.

    Deduplicates by model name: if multiple dir suffixes map to the same
    model (e.g. 'opus' and 'claude_opus'), the one with more solves wins.
    """
    rq_dir = results_dir / "RQ3"
    models_by_name: dict[str, dict] = {}

    for logs_subdir in sorted(rq_dir.glob("exp-logs-*")):
        suffix = logs_subdir.name.replace("exp-logs-", "")
        if suffix not in RQ3_MODELS:
            print(f"  ⚠ Unknown RQ3 suffix: {suffix}, skipping")
            continue

        meta = RQ3_MODELS[suffix]
        completed, failed, costs = extract_challenge_data(logs_subdir, master_challenges)

        if not completed and not failed:
            print(f"  ⚠ {meta['name']}: no challenge data found, skipping")
            continue

        stats = compute_stats(completed, failed, costs, master_challenges)
        exit_reasons = extract_exit_reasons(logs_subdir, master_challenges)
        by_cat_flat = {cat: stats["by_category"][cat]["solve_rate"]
                       for cat in CATEGORY_ORDER}

        entry = {
            "name": meta["name"],
            "provider": meta["provider"],
            "type": meta["type"],
            "config": f"{suffix}.yaml",
            "overall": stats["overall"],
            "by_category": by_cat_flat,
            "exit_reasons": exit_reasons,
        }

        existing = models_by_name.get(meta["name"])
        if existing is None or entry["overall"]["solved"] > existing["overall"]["solved"]:
            models_by_name[meta["name"]] = entry

        print(f"  ✓ {meta['name']}: {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    return {
        "rq": "RQ3",
        "title": "Model Selection — Which LLMs perform best on CTF challenges?",
        "description": "Benchmark of models using Kali + generic prompts on NYU CTF Bench (200 challenges)",
        "environment": "kali",
        "prompt_type": "generic",
        "total_challenges": len(master_challenges),
        "categories": CATEGORY_ORDER,
        "models": list(models_by_name.values()),
    }


def parse_rq4(results_dir: Path, master_challenges: list[str]) -> dict:
    """Parse RQ4 experiment results: multi-agent architecture combos.

    Also pulls the same-model baselines from RQ3 (gemini3_pro, gemini3_flash)
    for comparison.
    """
    rq_dir = results_dir / "RQ4"
    conditions: dict[str, dict] = {}

    # Parse actual RQ4 experiment directories
    if rq_dir.exists():
        for logs_subdir in sorted(rq_dir.glob("exp-logs-*")):
            suffix = logs_subdir.name.replace("exp-logs-", "")
            if suffix not in RQ4_SETUPS:
                print(f"  ⚠ Unknown RQ4 suffix: {suffix}, skipping")
                continue

            meta = RQ4_SETUPS[suffix]
            completed, failed, costs = extract_challenge_data(logs_subdir, master_challenges)

            if not completed and not failed:
                print(f"  ⚠ {meta['label']}: no challenge data found, skipping")
                continue

            stats = compute_stats(completed, failed, costs, master_challenges)
            key = meta["key"]
            conditions[key] = {
                "label": meta["label"],
                "planner": meta["planner"],
                "executor": meta["executor"],
                "overall": stats["overall"],
                "by_category": stats["by_category"],
            }
            print(f"  ✓ {meta['label']}: {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    # Pull same-model baselines from RQ3 for comparison
    rq3_dir = results_dir / "RQ3"
    baselines = {"gemini3_pro": "Gemini 3 Pro (both)", "gemini3_flash": "Gemini 3 Flash (both)"}
    for suffix, label in baselines.items():
        baseline_dir = rq3_dir / f"exp-logs-{suffix}"
        if not baseline_dir.exists():
            continue
        completed, failed, costs = extract_challenge_data(baseline_dir, master_challenges)
        if not completed:
            continue
        stats = compute_stats(completed, failed, costs, master_challenges)
        conditions[f"baseline_{suffix}"] = {
            "label": label,
            "planner": RQ3_MODELS[suffix]["name"],
            "executor": RQ3_MODELS[suffix]["name"],
            "overall": stats["overall"],
            "by_category": stats["by_category"],
        }
        print(f"  ✓ {label} (baseline): {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    return {
        "rq": "RQ4",
        "title": "Multi-Agent Architecture — Optimal Planner/Executor Combination",
        "description": "Compare large-planner+small-executor vs small-planner+large-executor vs same-model baselines",
        "total_challenges": len(master_challenges),
        "categories": CATEGORY_ORDER,
        "conditions": conditions,
    }


def parse_rq5(results_dir: Path, master_challenges: list[str]) -> dict:
    """Parse RQ5 reproducibility results: multiple runs of the same config.

    Expects either:
      - A single dir with duplicate JSON logs per challenge (different timestamps)
      - Multiple dirs like exp-logs-reproducibility_gemini_run1, _run2, etc.
    """
    rq_dir = results_dir / "RQ5"
    base_suffix = RQ5_CONFIG["base_suffix"]
    runs: list[dict] = []

    if not rq_dir.exists():
        return {"rq": "RQ5", "title": "Reproducibility", "runs": runs,
                "total_challenges": len(master_challenges), "categories": CATEGORY_ORDER}

    # Strategy 1: multiple directories (run1, run2, ...)
    run_dirs = sorted(rq_dir.glob(f"exp-logs-{base_suffix}*"))
    if not run_dirs:
        run_dirs = sorted(rq_dir.glob("exp-logs-*"))

    for i, logs_subdir in enumerate(run_dirs, 1):
        completed, failed, costs = extract_challenge_data(logs_subdir, master_challenges)
        if not completed and not failed:
            continue

        stats = compute_stats(completed, failed, costs, master_challenges)
        by_cat_flat = {cat: stats["by_category"][cat]["solve_rate"]
                       for cat in CATEGORY_ORDER}
        runs.append({
            "run": i,
            "dir": logs_subdir.name,
            "overall": stats["overall"],
            "by_category": by_cat_flat,
        })
        print(f"  ✓ Run {i} ({logs_subdir.name}): {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    # Strategy 2: if only one dir, look for per-challenge variance from duplicate logs
    if len(runs) <= 1 and run_dirs:
        single_dir = run_dirs[0]
        jupyter_dir = single_dir / "jupyter"
        search_dir = (jupyter_dir / "default") if (jupyter_dir / "default").exists() else jupyter_dir
        if search_dir.exists():
            from collections import defaultdict
            per_challenge: dict[str, list[bool]] = defaultdict(list)
            for json_file in sorted(search_dir.glob("*.json")):
                stem = json_file.stem
                parts = stem.rsplit("-", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    ch = parts[0]
                else:
                    ch = stem
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    per_challenge[ch].append(data.get("success", False))
                except (json.JSONDecodeError, OSError):
                    pass

            multi_run = {ch: outcomes for ch, outcomes in per_challenge.items() if len(outcomes) > 1}
            if multi_run:
                n_runs = max(len(v) for v in multi_run.values())
                print(f"  Found {len(multi_run)} challenges with {n_runs} runs each (in-dir duplicates)")

    return {
        "rq": "RQ5",
        "title": "Reproducibility — How consistent are LLM CTF solvers?",
        "description": f"Multiple runs of {RQ5_CONFIG['model']} to measure variance",
        "model": RQ5_CONFIG["model"],
        "total_challenges": len(master_challenges),
        "categories": CATEGORY_ORDER,
        "runs": runs,
    }


def main():
    parser = argparse.ArgumentParser(description="Parse D-CIPHER experiment results from logs")
    parser.add_argument("--results-dir", default="tatar-project-results/results",
                        help="Directory containing RQ1_RQ2 and RQ3 subdirectories")
    parser.add_argument("--output-dir", default="tatar-project-results",
                        help="Directory to write output JSON files")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("D-CIPHER Results Parser (log-based)")
    print("=" * 60)

    # ── Build master challenge list ──
    print("\n🔍 Building master challenge list...")
    master_challenges = build_master_challenge_list()
    print(f"  Found {len(master_challenges)} unique challenges")

    # ── RQ1+RQ2 ──
    rq_dir = results_dir / "RQ1_RQ2"
    if rq_dir.exists():
        print("\n📊 Parsing RQ1+RQ2 results from logs...")
        rq12 = parse_rq1_rq2(results_dir, master_challenges)
        out_path = output_dir / "rq1_rq2_combined.json"
        with open(out_path, "w") as f:
            json.dump(rq12, f, indent=2)
        print(f"\n  → Wrote {out_path} ({len(rq12['conditions'])} conditions)")
    else:
        print(f"\n⚠ RQ1_RQ2 directory not found at {rq_dir}")

    # ── RQ3 ──
    rq_dir = results_dir / "RQ3"
    if rq_dir.exists():
        print("\n📊 Parsing RQ3 results from logs...")
        rq3 = parse_rq3(results_dir, master_challenges)
        out_path = output_dir / "rq3_models.json"
        with open(out_path, "w") as f:
            json.dump(rq3, f, indent=2)
        print(f"\n  → Wrote {out_path} ({len(rq3['models'])} models)")
    else:
        print(f"\n⚠ RQ3 directory not found at {rq_dir}")

    # ── RQ4 ──
    rq4_dir = results_dir / "RQ4"
    rq3_dir = results_dir / "RQ3"
    if rq4_dir.exists() or rq3_dir.exists():
        print("\n📊 Parsing RQ4 results (multi-agent architecture)...")
        rq4 = parse_rq4(results_dir, master_challenges)
        if rq4["conditions"]:
            out_path = output_dir / "rq4_architecture.json"
            with open(out_path, "w") as f:
                json.dump(rq4, f, indent=2)
            print(f"\n  → Wrote {out_path} ({len(rq4['conditions'])} conditions)")
        else:
            print("\n  ⚠ No RQ4 results yet (waiting for experiment data)")

    # ── RQ5 ──
    rq5_dir = results_dir / "RQ5"
    if rq5_dir.exists():
        print("\n📊 Parsing RQ5 results (reproducibility)...")
        rq5 = parse_rq5(results_dir, master_challenges)
        if rq5["runs"]:
            out_path = output_dir / "rq5_reproducibility.json"
            with open(out_path, "w") as f:
                json.dump(rq5, f, indent=2)
            print(f"\n  → Wrote {out_path} ({len(rq5['runs'])} runs)")
        else:
            print("\n  ⚠ No RQ5 results yet (waiting for experiment data)")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
