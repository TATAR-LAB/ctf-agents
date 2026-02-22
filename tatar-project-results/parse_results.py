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
RQ3_MODELS = {
    "gpt52":      {"name": "GPT-5.2",              "provider": "OpenAI",    "type": "frontier"},
    "gpt52_pro":  {"name": "GPT-5.2-Pro",          "provider": "OpenAI",    "type": "frontier"},
    "gpt52_codex":{"name": "GPT-5.2-Codex",        "provider": "OpenAI",    "type": "code-specialized"},
    "opus":       {"name": "Claude 4.5 Opus",       "provider": "Anthropic", "type": "frontier"},
    "sonnet":     {"name": "Claude 4.5 Sonnet",     "provider": "Anthropic", "type": "frontier"},
    "haiku":      {"name": "Claude 4.5 Haiku",      "provider": "Anthropic", "type": "small"},
    "gemini3_pro":{"name": "Gemini 3 Pro",          "provider": "Google",    "type": "frontier"},
    "gemini3_flash":{"name": "Gemini 3 Flash",      "provider": "Google",    "type": "small"},
    "deepseek_r1":{"name": "DeepSeek-R1",           "provider": "DeepSeek",  "type": "reasoning"},
    "deepseek_v3":{"name": "DeepSeek-V3",           "provider": "DeepSeek",  "type": "frontier"},
    "grok4":      {"name": "Grok-4",                "provider": "xAI",       "type": "frontier"},
    "grok41_fast":{"name": "Grok-4.1 Fast",         "provider": "xAI",       "type": "small"},
    "llama33_70b":{"name": "Llama 3.3 70B",         "provider": "Meta",      "type": "open-source"},
    "llama31_8b": {"name": "Llama 3.1 8B",          "provider": "Meta",      "type": "open-source"},
    "qwen3_30b":  {"name": "Qwen3-30B",             "provider": "Alibaba",   "type": "open-source"},
    "mistral_large":{"name": "Mistral Large",       "provider": "Mistral",   "type": "frontier"},
    "foundation_sec_8b":{"name": "Foundation-Sec 8B","provider": "Cisco",     "type": "security-specialized"},
}


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

def read_jupyter_jsons(logs_dir: Path) -> dict[str, dict]:
    """Read per-challenge jupyter JSON files.

    Returns dict of challenge_name → {success, total_cost, time_taken}.
    Handles both flat layout and default/ subdirectory.
    """
    result = {}
    jupyter_dir = logs_dir / "jupyter"
    if not jupyter_dir.exists():
        return result

    # Check for default/ subdirectory first, then flat
    search_dirs = []
    default_dir = jupyter_dir / "default"
    if default_dir.exists():
        search_dirs.append(default_dir)
    else:
        search_dirs.append(jupyter_dir)

    for search_dir in search_dirs:
        for json_file in search_dir.glob("*.json"):
            # Filename format: challenge-name-TIMESTAMP.json
            # e.g. 2018f-msc-leaked_flag-260216181333.json
            stem = json_file.stem
            # The timestamp is the last segment after the last dash that is all digits
            parts = stem.rsplit("-", 1)
            if len(parts) == 2 and parts[1].isdigit():
                challenge_name = parts[0]
            else:
                challenge_name = stem

            try:
                with open(json_file) as f:
                    data = json.load(f)
                info = {
                    "success": data.get("success", False),
                    "total_cost": data.get("total_cost", 0.0),
                    "time_taken": data.get("time_taken", 0.0),
                    "exit_reason": data.get("exit_reason", ""),
                }
                # If there are duplicate entries for a challenge, keep the one
                # marked as successful (or the last one if none succeeded)
                if challenge_name not in result or info["success"]:
                    result[challenge_name] = info
            except (json.JSONDecodeError, OSError):
                pass

    return result


def read_finished_challenges(logs_dir: Path) -> dict[str, dict]:
    """Parse finishedChallenges.txt if present.

    Format per line:
        challenge_name - SOLVED/FAILED/NOT_SOLVED - [details] - exit: ... cost: $X.XX ...

    Returns dict of challenge_name → {success, total_cost}.
    Deduplicates: if a challenge appears multiple times, SOLVED wins.
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

        # Split on first " - " to get challenge name
        parts = line.split(" - ", 2)
        if len(parts) < 2:
            continue

        challenge_name = parts[0].strip()
        status = parts[1].strip().upper()
        rest = parts[2] if len(parts) > 2 else ""

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

def build_master_challenge_list(results_dir: Path) -> list[str]:
    """Build the canonical list of 200 challenges.

    Primary source: finishedChallenges.txt from exp-logs-kt (has all 200).
    Fallback: aggregate from ALL exp-logs-* directories.
    """
    # Try the canonical source first (kt has all 200 challenges)
    canonical = results_dir / "RQ1_RQ2" / "exp-logs-kt" / "finishedChallenges.txt"
    if canonical.exists():
        names: set[str] = set()
        for line in canonical.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            name = line.split(" - ")[0].strip()
            if name and "-" in name:
                names.add(name)
        if len(names) >= 200:
            return sorted(names)

    # Fallback: aggregate from all experiment directories
    all_challenges: set[str] = set()
    for rq_subdir in ["RQ1_RQ2", "RQ3"]:
        rq_path = results_dir / rq_subdir
        if not rq_path.exists():
            continue
        for logs_dir in rq_path.glob("exp-logs-*"):
            jupyter_data = read_jupyter_jsons(logs_dir)
            all_challenges.update(jupyter_data.keys())
            fc_data = read_finished_challenges(logs_dir)
            all_challenges.update(fc_data.keys())
            batch_data = read_batch_logs(logs_dir)
            all_challenges.update(batch_data.keys())

    all_challenges = {ch for ch in all_challenges if ch and "-" in ch}
    return sorted(all_challenges)


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

    Any challenge in master_challenges not found in logs is treated as failed.

    Returns:
        completed: list of solved challenge names
        failed: list of failed/unsolved challenge names
        costs: dict of challenge_name → total_cost (for solved challenges)
    """
    completed = []
    failed = []
    costs = {}
    seen = set()

    # ── Source 1: Jupyter JSONs ──
    jupyter_data = read_jupyter_jsons(logs_dir)
    for ch, info in jupyter_data.items():
        if ch in seen:
            continue
        seen.add(ch)
        if info["success"]:
            completed.append(ch)
            costs[ch] = info["total_cost"]
        else:
            failed.append(ch)

    # ── Source 2: finishedChallenges.txt ──
    fc_data = read_finished_challenges(logs_dir)
    for ch, info in fc_data.items():
        if ch in seen:
            # If jupyter said failed but FC says solved, upgrade
            if info["success"] and ch not in completed:
                failed.remove(ch) if ch in failed else None
                completed.append(ch)
                costs[ch] = info["total_cost"]
            continue
        seen.add(ch)
        if info["success"]:
            completed.append(ch)
            costs[ch] = info["total_cost"]
        else:
            failed.append(ch)

    # ── Source 3: batch_*.log ──
    batch_data = read_batch_logs(logs_dir)
    for ch, info in batch_data.items():
        if ch in seen:
            if info["success"] and ch not in completed:
                failed.remove(ch) if ch in failed else None
                completed.append(ch)
                costs[ch] = info["total_cost"]
            continue
        seen.add(ch)
        if info["success"]:
            completed.append(ch)
            costs[ch] = info["total_cost"]
        else:
            failed.append(ch)

    # ── Pad missing challenges as failed ──
    completed_set = set(completed)
    failed_set = set(failed)
    for ch in master_challenges:
        if ch not in completed_set and ch not in failed_set:
            failed.append(ch)

    return completed, failed, costs


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
        key = meta["key"]
        conditions[key] = {
            "label": meta["label"],
            "config": f"{key}.yaml",
            "environment": meta["environment"],
            "prompts": meta["prompts"],
            "autoprompt": meta["autoprompt"],
            "overall": stats["overall"],
            "by_category": stats["by_category"],
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
    """Parse all RQ3 experiment results from exp-logs-* directories."""
    rq_dir = results_dir / "RQ3"
    models = []

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

        # Convert by_category to the RQ3 flat format (just solve_rate values)
        by_cat_flat = {cat: stats["by_category"][cat]["solve_rate"]
                       for cat in CATEGORY_ORDER}

        models.append({
            "name": meta["name"],
            "provider": meta["provider"],
            "type": meta["type"],
            "config": f"{suffix}.yaml",
            "overall": stats["overall"],
            "by_category": by_cat_flat,
        })
        print(f"  ✓ {meta['name']}: {stats['overall']['solved']}/{stats['overall']['total']} solved ({stats['overall']['solve_rate']*100:.1f}%)")

    return {
        "rq": "RQ3",
        "title": "Model Selection — Which LLMs perform best on CTF challenges?",
        "description": "Benchmark of models using Kali + specialized prompts on NYU CTF Bench (200 challenges)",
        "environment": "kali",
        "prompt_type": "specialized",
        "total_challenges": len(master_challenges),
        "categories": CATEGORY_ORDER,
        "models": models,
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
    master_challenges = build_master_challenge_list(results_dir)
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

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
