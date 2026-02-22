"""
D-CIPHER Experiment Results Visualizer
======================================
Generates presentation-ready plots from parsed RQ1+RQ2 and RQ3 results.
Works with any subset of available conditions/models (no mock data required).

Usage:
    uv run parse_results.py          # parse real results first
    uv run visualize_results.py      # generate plots
"""

import json
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.colors import Normalize

# ── Styling ──────────────────────────────────────────────────────────
CATEGORY_ORDER = ["crypto", "forensics", "misc", "pwn", "reverse", "web"]

CONDITION_COLORS = {
    "ubuntu_generic":            "#F4A460",
    "ubuntu_generic_autoprompt": "#E95420",
    "ubuntu_tips":               "#87CEEB",
    "ubuntu_tips_autoprompt":    "#4169E1",
    "kali_generic":              "#90EE90",
    "kali_generic_autoprompt":   "#2ECC71",
    "kali_tips":                 "#DA70D6",
    "kali_tips_autoprompt":      "#8B008B",
}

PROVIDER_COLORS = {
    "OpenAI": "#10A37F", "Anthropic": "#D97706", "Google": "#4285F4",
    "DeepSeek": "#6366F1", "xAI": "#1D1D1F", "Meta": "#0668E1",
    "Alibaba": "#FF6A00", "Mistral": "#F24E1E", "Cisco": "#049FD9",
}

PALETTE = {
    "frontier": "#3498DB", "small": "#E67E22", "open-source": "#9B59B6",
    "reasoning": "#1ABC9C", "code-specialized": "#E74C3C",
    "security-specialized": "#2ECC71",
}


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


# =====================================================================
# RQ1+RQ2 CHART 1: All available conditions — overall solve rate bar
# =====================================================================
def rq1rq2_all_conditions_bar(data: dict, out: Path):
    """Bar chart comparing all available conditions, sorted by solve rate."""
    conds = data["conditions"]
    if not conds:
        print("  ⚠ No conditions available, skipping all_conditions_bar")
        return

    sorted_keys = sorted(conds.keys(), key=lambda k: conds[k]["overall"]["solve_rate"])
    labels = [conds[k]["label"] for k in sorted_keys]
    rates  = [conds[k]["overall"]["solve_rate"] * 100 for k in sorted_keys]
    colors = [CONDITION_COLORS.get(k, "#888") for k in sorted_keys]

    fig, ax = plt.subplots(figsize=(12, max(4, len(labels) * 0.8)))
    bars = ax.barh(labels, rates, color=colors, edgecolor="white", linewidth=1, height=0.65, zorder=3)

    ax.set_xlabel("Solve Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("RQ1+RQ2: Overall Solve Rates — Available Conditions",
                 fontsize=14, fontweight="bold", pad=12)
    max_rate = max(rates) if rates else 40
    ax.set_xlim(0, max_rate * 1.3)
    ax.grid(axis="x", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2,
                f"{rate:.1f}%", va="center", fontsize=10, fontweight="bold", color="#333")

    fig.tight_layout()
    fig.savefig(out / "rq1rq2_all_conditions.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq1rq2_all_conditions.png'}")


# =====================================================================
# RQ1+RQ2 CHART 2: Grouped bar — by category for available conditions
# =====================================================================
def rq1rq2_category_comparison(data: dict, out: Path):
    """Grouped bar chart: all available conditions by category."""
    conds = data["conditions"]
    if not conds:
        print("  ⚠ No conditions available, skipping category_comparison")
        return

    cats = CATEGORY_ORDER
    keys = sorted(conds.keys())

    x = np.arange(len(cats))
    n = len(keys)
    w = 0.8 / n

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, key in enumerate(keys):
        rates = [conds[key]["by_category"].get(c, {}).get("solve_rate", 0) * 100 for c in cats]
        color = CONDITION_COLORS.get(key, "#888")
        offset = (i - n/2 + 0.5) * w
        bars = ax.bar(x + offset, rates, w, label=conds[key]["label"],
                      color=color, edgecolor="white", linewidth=0.8, zorder=3)

    ax.set_ylabel("Solve Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("RQ1+RQ2: Solve Rates by Category and Condition",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in cats], fontsize=11)
    ax.set_ylim(0, max(45, 10))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(out / "rq1rq2_category_comparison.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq1rq2_category_comparison.png'}")


# =====================================================================
# RQ1+RQ2 CHART 3: Heatmap table (from heatmap_table.py) + Overall col
# =====================================================================
def rq1rq2_heatmap_table(data: dict, out: Path):
    """Heatmap with table-style y-axis showing OS / Tips / AutoPrompt columns,
    plus an Overall accuracy column."""
    conds = data["conditions"]
    if not conds:
        print("  ⚠ No conditions available, skipping heatmap_table")
        return

    cats = CATEGORY_ORDER

    # Order: group by environment, then by prompts, then autoprompt
    env_order = {"ubuntu": 0, "kali": 1}
    prompt_order = {"generic": 0, "tips": 1}

    key_order = sorted(conds.keys(), key=lambda k: (
        env_order.get(conds[k]["environment"], 2),
        prompt_order.get(conds[k]["prompts"], 2),
        0 if not conds[k]["autoprompt"] else 1,
    ))

    n_rows = len(key_order)
    n_cats = len(cats)

    # Build matrix (categories + overall)
    matrix = np.array([
        [conds[k]["by_category"][c]["solve_rate"] * 100 for c in cats]
        for k in key_order
    ])

    overall_rates = [conds[k]["overall"]["solve_rate"] * 100 for k in key_order]

    # Build table rows
    table_rows = []
    for k in key_order:
        c = conds[k]
        table_rows.append({
            "os":   "Kali" if c["environment"] == "kali" else "Ubuntu",
            "tips": "✓" if c["prompts"] == "tips" else "✗",
            "ap":   "✓" if c["autoprompt"] else "✗",
        })

    # ── Layout: 3 table cols + n_cats heatmap cols + 1 overall col ──
    table_cols = 3
    heat_cols = n_cats + 1  # categories + overall
    total_cols = table_cols + heat_cols

    table_col_w = 1.0
    heat_col_w  = 1.8
    total_w = table_cols * table_col_w + heat_cols * heat_col_w
    fig_w = total_w * 0.85 + 0.5
    fig_h = n_rows * 0.7 + 1.8

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(-0.5, n_rows + 0.5)
    ax.axis("off")
    ax.invert_yaxis()

    cmap = plt.cm.Blues
    norm = Normalize(vmin=0, vmax=45)

    def col_x(col_idx):
        """Return (left, center, right) of a logical column."""
        x = 0
        for i in range(col_idx):
            x += table_col_w if i < table_cols else heat_col_w
        w = table_col_w if col_idx < table_cols else heat_col_w
        return x, x + w / 2, x + w

    # ── Header row ──
    header_labels = ["OS", "Tips", "AP"] + [c.capitalize() for c in cats] + ["Overall"]
    for ci in range(total_cols):
        left, cx, right = col_x(ci)
        w = table_col_w if ci < table_cols else heat_col_w

        if ci < table_cols:
            fc, tc = "#1a3a5c", "white"
        elif ci == total_cols - 1:
            fc, tc = "#1a5c3a", "white"  # green tint for Overall
        else:
            fc, tc = "#2c5f8a", "white"

        rect = plt.Rectangle((left, -0.5), w, 1, facecolor=fc, edgecolor="white",
                              linewidth=1.5, clip_on=False)
        ax.add_patch(rect)
        ax.text(cx, 0, header_labels[ci], ha="center", va="center",
                fontsize=12, fontweight="bold", color=tc)

    # Find split point between Ubuntu and Kali rows
    kali_start = None
    for ri, k in enumerate(key_order):
        if conds[k]["environment"] == "kali":
            kali_start = ri
            break

    # ── Data rows ──
    for ri in range(n_rows):
        y_top = ri + 0.5
        is_kali = conds[key_order[ri]]["environment"] == "kali"

        # Table columns
        row = table_rows[ri]
        vals = [row["os"], row["tips"], row["ap"]]
        for ci in range(table_cols):
            left, cx, right = col_x(ci)

            if ri % 2 == 0:
                bg = "#e0ecf8" if not is_kali else "#ddf0e5"
            else:
                bg = "#f0f5fc" if not is_kali else "#edf8f1"

            rect = plt.Rectangle((left, y_top), table_col_w, 1,
                                 facecolor=bg, edgecolor="#ccc", linewidth=0.8, clip_on=False)
            ax.add_patch(rect)

            txt = vals[ci]
            if txt == "✓":
                tc_color, fw = "#1e8449", "bold"
            elif txt == "✗":
                tc_color, fw = "#c0392b", "bold"
            else:
                tc_color, fw = "#1a1a2e", "normal"

            ax.text(cx, ri + 1, txt, ha="center", va="center",
                    fontsize=11, fontweight=fw, color=tc_color)

        # Heatmap columns (categories)
        for cj in range(n_cats):
            ci = table_cols + cj
            left, cx, right = col_x(ci)
            val = matrix[ri, cj]
            fc = cmap(norm(val))

            rect = plt.Rectangle((left, y_top), heat_col_w, 1,
                                 facecolor=fc, edgecolor="white", linewidth=1.5, clip_on=False)
            ax.add_patch(rect)

            text_color = "white" if val > 30 else "#1a1a2e"
            ax.text(cx, ri + 1, f"{val:.1f}%", ha="center", va="center",
                    fontsize=12, fontweight="bold", color=text_color)

        # Overall column
        ci_overall = table_cols + n_cats
        left, cx, right = col_x(ci_overall)
        ov = overall_rates[ri]
        fc = cmap(norm(ov))

        rect = plt.Rectangle((left, y_top), heat_col_w, 1,
                              facecolor=fc, edgecolor="white", linewidth=2, clip_on=False)
        ax.add_patch(rect)

        text_color = "white" if ov > 30 else "#1a1a2e"
        ax.text(cx, ri + 1, f"{ov:.1f}%", ha="center", va="center",
                fontsize=13, fontweight="bold", color=text_color)

    # ── Divider between Ubuntu and Kali groups ──
    if kali_start is not None and kali_start > 0:
        div_y = kali_start + 0.5
        ax.axhline(y=div_y, xmin=0, xmax=1, color="#1a3a5c", linewidth=2.5, clip_on=False)

    fig.suptitle("Solve Rates by Experiment Configuration and Challenge Category",
                 fontsize=15, fontweight="bold", x=0.5, y=0.97, ha="center")

    fig.savefig(out / "rq1rq2_heatmap_table.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq1rq2_heatmap_table.png'}")


# =====================================================================
# RQ3 CHART 1: Horizontal bar chart — models ranked by solve rate
# =====================================================================
def rq3_horizontal_bar(data: dict, out: Path):
    """RQ3 – Horizontal bar chart: models ranked by overall solve rate."""
    models = sorted(data["models"], key=lambda m: m["overall"]["solve_rate"])
    if not models:
        print("  ⚠ No models available, skipping horizontal_bar")
        return

    names = [m["name"] for m in models]
    rates = [m["overall"]["solve_rate"] * 100 for m in models]
    colors = [PROVIDER_COLORS.get(m["provider"], "#888") for m in models]

    fig, ax = plt.subplots(figsize=(10, max(4, len(models) * 0.7)))
    bars = ax.barh(names, rates, color=colors, edgecolor="white", linewidth=0.8, height=0.7, zorder=3)
    ax.set_xlabel("Solve Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Model Benchmark — Overall Solve Rates on NYU CTF Bench",
                 fontsize=14, fontweight="bold", pad=12)
    max_rate = max(rates) if rates else 48
    ax.set_xlim(0, max_rate * 1.3)
    ax.grid(axis="x", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", labelsize=10)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{rate:.1f}%", va="center", fontsize=9, fontweight="bold", color="#333")

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=p) for p, c in PROVIDER_COLORS.items()
                       if p in {m["provider"] for m in models}]
    if legend_elements:
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9,
                  title="Provider", title_fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "rq3_model_ranking.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq3_model_ranking.png'}")


# =====================================================================
# RQ3 CHART 2: Cost vs solve rate scatter
# =====================================================================
def rq3_cost_vs_solve(data: dict, out: Path):
    """RQ3 – Scatter plot: cost per challenge vs solve rate."""
    models = data["models"]
    if not models:
        print("  ⚠ No models available, skipping cost_vs_solve")
        return

    fig, ax = plt.subplots(figsize=(10, 7))
    for m in models:
        x = m["overall"].get("avg_cost", 0)
        y = m["overall"]["solve_rate"] * 100
        s = m["overall"].get("total_cost", 10) * 2.5 + 20
        c = PROVIDER_COLORS.get(m["provider"], "#888")
        ax.scatter(x, y, s=s, c=c, alpha=0.75, edgecolors="white", linewidth=1.2, zorder=3)
        ax.annotate(m["name"], (x, y), fontsize=7.5, ha="left", va="bottom",
                    xytext=(5, 4), textcoords="offset points", color="#333")
    ax.set_xlabel("Avg Cost per Challenge ($)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Solve Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("RQ3: Cost-Performance Tradeoff", fontsize=14, fontweight="bold", pad=12)
    ax.grid(alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.annotate("← Lower cost, higher solve rate is better",
                xy=(0.02, 0.98), xycoords="axes fraction", fontsize=8,
                color="#999", ha="left", va="top", style="italic")

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=p) for p, c in PROVIDER_COLORS.items()
                       if p in {m["provider"] for m in models}]
    if legend_elements:
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9,
                  title="Provider", title_fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "rq3_cost_vs_solve.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq3_cost_vs_solve.png'}")


# =====================================================================
# RQ3 CHART 3: Heatmap table — models × categories + overall
# =====================================================================
def rq3_heatmap_table(data: dict, out: Path):
    """RQ3 – Table-style heatmap: models × categories with overall column."""
    cats = CATEGORY_ORDER
    models_sorted = sorted(data["models"], key=lambda m: m["overall"]["solve_rate"], reverse=True)
    if not models_sorted:
        print("  ⚠ No models available, skipping rq3_heatmap_table")
        return

    names = [m["name"] for m in models_sorted]
    n_rows = len(names)
    n_cats = len(cats)

    # Build matrix
    matrix = np.array([[m["by_category"].get(c, 0) * 100 for c in cats] for m in models_sorted])
    overall_rates = [m["overall"]["solve_rate"] * 100 for m in models_sorted]

    # Layout: 1 model-name col + n_cats heat cols + 1 overall col
    name_col_w = 3.0
    heat_col_w = 1.8
    total_cols = 1 + n_cats + 1
    total_w = name_col_w + (n_cats + 1) * heat_col_w
    fig_w = total_w * 0.85 + 0.5
    fig_h = n_rows * 0.7 + 1.8

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(-0.5, n_rows + 0.5)
    ax.axis("off")
    ax.invert_yaxis()

    cmap = plt.cm.YlGnBu
    norm = Normalize(vmin=0, vmax=50)

    def col_x(col_idx):
        if col_idx == 0:
            return 0, name_col_w / 2, name_col_w
        x = name_col_w + (col_idx - 1) * heat_col_w
        return x, x + heat_col_w / 2, x + heat_col_w

    # ── Header row ──
    header_labels = ["Model"] + [c.capitalize() for c in cats] + ["Overall"]
    for ci in range(total_cols):
        left, cx, right = col_x(ci)
        w = name_col_w if ci == 0 else heat_col_w

        if ci == 0:
            fc, tc = "#1a3a5c", "white"
        elif ci == total_cols - 1:
            fc, tc = "#1a5c3a", "white"
        else:
            fc, tc = "#2c5f8a", "white"

        rect = plt.Rectangle((left, -0.5), w, 1, facecolor=fc, edgecolor="white",
                              linewidth=1.5, clip_on=False)
        ax.add_patch(rect)
        ax.text(cx, 0, header_labels[ci], ha="center", va="center",
                fontsize=11, fontweight="bold", color=tc)

    # ── Data rows ──
    for ri in range(n_rows):
        y_top = ri + 0.5

        # Model name column
        left, cx, right = col_x(0)
        bg = "#e0ecf8" if ri % 2 == 0 else "#f0f5fc"
        rect = plt.Rectangle((left, y_top), name_col_w, 1,
                              facecolor=bg, edgecolor="#ccc", linewidth=0.8, clip_on=False)
        ax.add_patch(rect)
        provider_color = PROVIDER_COLORS.get(models_sorted[ri]["provider"], "#1a1a2e")
        ax.text(cx, ri + 1, names[ri], ha="center", va="center",
                fontsize=10, fontweight="bold", color=provider_color)

        # Category columns
        for cj in range(n_cats):
            ci = 1 + cj
            left, cx, right = col_x(ci)
            val = matrix[ri, cj]
            fc = cmap(norm(val))

            rect = plt.Rectangle((left, y_top), heat_col_w, 1,
                                 facecolor=fc, edgecolor="white", linewidth=1.5, clip_on=False)
            ax.add_patch(rect)

            text_color = "white" if val > 30 else "black"
            ax.text(cx, ri + 1, f"{val:.1f}%", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=text_color)

        # Overall column
        ci_overall = 1 + n_cats
        left, cx, right = col_x(ci_overall)
        ov = overall_rates[ri]
        fc = cmap(norm(ov))

        rect = plt.Rectangle((left, y_top), heat_col_w, 1,
                              facecolor=fc, edgecolor="white", linewidth=2, clip_on=False)
        ax.add_patch(rect)

        text_color = "white" if ov > 30 else "black"
        ax.text(cx, ri + 1, f"{ov:.1f}%", ha="center", va="center",
                fontsize=12, fontweight="bold", color=text_color)

    fig.suptitle("RQ3: Solve Rates by Model × Category",
                 fontsize=15, fontweight="bold", x=0.5, y=0.97, ha="center")

    fig.savefig(out / "rq3_heatmap_table.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq3_heatmap_table.png'}")


# =====================================================================
# RQ3 CHART 4: Model type comparison
# =====================================================================
def rq3_model_type_comparison(data: dict, out: Path):
    """RQ3 – Bar: average solve rate by model type."""
    models = data["models"]
    if not models:
        print("  ⚠ No models available, skipping model_type_comparison")
        return

    type_rates: dict[str, list[float]] = {}
    for m in models:
        type_rates.setdefault(m["type"], []).append(m["overall"]["solve_rate"] * 100)
    types = sorted(type_rates.keys(), key=lambda t: np.mean(type_rates[t]), reverse=True)
    means = [np.mean(type_rates[t]) for t in types]
    stds  = [np.std(type_rates[t]) for t in types]
    colors_list = [PALETTE.get(t, "#888") for t in types]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(range(len(types)), means, yerr=stds, capsize=5,
                  color=colors_list, edgecolor="white", linewidth=1, zorder=3)
    ax.set_ylabel("Avg Solve Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("RQ3: Performance by Model Type", fontsize=14, fontweight="bold", pad=12)
    ax.set_xticks(range(len(types)))
    ax.set_xticklabels([t.replace("-", " ").title() for t in types], fontsize=10, rotation=15, ha="right")
    ax.set_ylim(0, max(means) * 1.4 if means else 45)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for b, m_val, n in zip(bars, means, [len(type_rates[t]) for t in types]):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5,
                f"{m_val:.1f}%\n(n={n})", ha="center", fontsize=9, color="#333")
    fig.tight_layout()
    fig.savefig(out / "rq3_model_types.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out / 'rq3_model_types.png'}")


# =====================================================================
# MAIN
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Visualize D-CIPHER experiment results")
    parser.add_argument("--results-dir", default="tatar-project-results",
                        help="Directory containing JSON result files")
    parser.add_argument("--output-dir", default="tatar-project-results/plots",
                        help="Directory to save plots")
    args = parser.parse_args()

    results = Path(args.results_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Loading experiment data...")
    rq12_path = results / "rq1_rq2_combined.json"
    rq3_path  = results / "rq3_models.json"

    if not rq12_path.exists() or not rq3_path.exists():
        print("⚠ JSON files not found. Run parse_results.py first:")
        print("    uv run tatar-project-results/parse_results.py")
        return

    rq12 = load_json(rq12_path)
    rq3  = load_json(rq3_path)

    print(f"\nGenerating plots → {out}/\n")

    # RQ1+RQ2
    n_conds = len(rq12.get("conditions", {}))
    print(f"RQ1+RQ2: {n_conds} conditions available")
    rq1rq2_all_conditions_bar(rq12, out)
    rq1rq2_category_comparison(rq12, out)
    rq1rq2_heatmap_table(rq12, out)

    # RQ3
    n_models = len(rq3.get("models", []))
    print(f"\nRQ3: {n_models} models available")
    rq3_horizontal_bar(rq3, out)
    rq3_cost_vs_solve(rq3, out)
    rq3_heatmap_table(rq3, out)
    rq3_model_type_comparison(rq3, out)

    print(f"\n✅ Done! {len(list(out.glob('*.png')))} plots saved to {out}/")


if __name__ == "__main__":
    main()
