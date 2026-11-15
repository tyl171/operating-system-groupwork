#!/usr/bin/env python3
"""RQ3 (runtime overhead, paper Fig. 7): rebuild every number from the raw logs.

Usage (from the repository root):
    python3 scripts/rq3/analyze_rq3.py                # reads logs/rq3, writes results/rq3
    python3 scripts/rq3/analyze_rq3.py --logs logs/rq3 --out results/rq3

Definitions (also written into docs/claims/C2_overhead_fig7.md):
  * Native time of a program   = mean wall time of runs with exit code 0 (runs with exit code
    139 = crash caused by the bug itself are excluded and counted).
  * Period time per schedule   = (Time total printed by run_PDS.py) / (Round total printed by
    run_PDS.py), i.e. the tool's own numbers for the testing phase. Using the tool's own Round
    total avoids the old counting bug (lines "test NNNN for prefix [...]:" were not counted).
  * Slowdown of one Period run = (time per schedule) / (native mean time).
  * A Period run is EXCLUDED if (a) it has no Round summary (the dry run was cut short, 0
    schedules executed) or (b) it contains a timeout interleaving ("Total Timeouts
    Interleavings" > 0): one hung schedule waiting for the timeout dominates the run time.
    Exclusions are listed in rq3_runs.csv with the reason; no outlier rule based on the
    median is used.
  * The summary reports mean +- std over ALL valid runs (not only the first three).
Sensitivity columns: wall-clock based ratio, ratio with the native MEDIAN, ratio when
timeout runs are kept.
"""
import argparse
import csv
import re
import statistics as st
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def hms(s):
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def last_block(path):
    """Reruns append to the same *_runs.log; only the LAST block belongs to the logs on disk."""
    blocks = [b for b in path.read_text().strip().split("---") if b.strip()]
    return blocks[-1]


def parse_native(d):
    runs = []
    for line in last_block(d / "native_runs.log").splitlines():
        m = re.match(r"run(\d+): exit=(\d+) time=([\d.]+) s", line.strip())
        if m:
            runs.append((int(m.group(1)), int(m.group(2)), float(m.group(3))))
    return runs


def parse_period(d):
    walls = {}
    for m in re.finditer(r"run(\d+): wall=([\d.]+) s", last_block(d / "period_runs.log")):
        walls[int(m.group(1))] = float(m.group(2))
    recs = []
    for k in sorted(walls):
        f = d / f"period_run{k}.log"
        text = ANSI.sub("", f.read_text(errors="replace"))
        rnd = re.search(r"^Round\s+\d+\s+(\d+)", text, re.M)
        tim = re.search(r"^Time\s+\S+\s+(\d+:\d+:[\d.]+)", text, re.M)
        tmo = re.search(r"Total Timeouts Interleavings:\s*(\d+)", text)
        err = re.search(r"Total Error Interleavings:\s*(\d+)", text)
        recs.append({
            "run": k, "log": str(f), "wall": walls[k],
            "rounds": int(rnd.group(1)) if rnd else None,
            "tool_time": hms(tim.group(1)) if tim else None,
            "timeouts": int(tmo.group(1)) if tmo else 0,
            "errors": int(err.group(1)) if err else None,
        })
    return recs


def mean_std(v):
    return (st.mean(v), st.stdev(v) if len(v) > 1 else 0.0) if v else (float("nan"), float("nan"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", default="logs/rq3")
    ap.add_argument("--out", default="results/rq3")
    ap.add_argument("--paper", default=None, help="CSV with paper Fig.7 estimates")
    a = ap.parse_args()
    logs, out = Path(a.logs), Path(a.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    paper_csv = Path(a.paper) if a.paper else out / "paper_fig7_estimates.csv"
    paper = {}
    if paper_csv.exists():
        for r in csv.DictReader(paper_csv.open()):
            paper[r["program"]] = float(r["paper_period_slowdown_est"])

    progs = sorted(p for p in logs.iterdir() if p.is_dir() and p.name.startswith("CVE-"))
    runs_rows, summ = [], []
    for d in progs:
        cve = d.name
        nat = parse_native(d)
        nat_ok = [t for (_, rc, t) in nat if rc == 0]
        nat_bad = [(k, rc, t) for (k, rc, t) in nat if rc != 0]
        nat_mean, nat_std = mean_std(nat_ok)
        nat_med = st.median(nat_ok)
        for (k, rc, t) in nat:
            runs_rows.append([cve, "native", k, f"{t:.6f}", "", "", "", "",
                              "valid" if rc == 0 else f"excluded: exit code {rc} (crash caused by the bug)"])
        per = parse_period(d)
        valid, valid_incl_tmo = [], []
        for r in per:
            if r["rounds"] is None:
                status = "excluded: no Round summary (0 schedules executed)"
            else:
                valid_incl_tmo.append(r)
                if r["timeouts"] > 0:
                    status = f"excluded: contains {r['timeouts']} timeout interleaving(s)"
                else:
                    status = "valid"
                    valid.append(r)
            ps = (r["tool_time"] / r["rounds"]) if r["rounds"] else None
            runs_rows.append([cve, "period", r["run"], f"{r['wall']:.6f}", r["rounds"] or "",
                              f"{ps:.6f}" if ps else "", f"{ps / nat_mean:.2f}" if ps else "",
                              r["log"], status])
        ratios = [r["tool_time"] / r["rounds"] / nat_mean for r in valid]
        rm, rs = mean_std(ratios)
        wall_ratios = [r["wall"] / r["rounds"] / nat_mean for r in valid]
        ratio_med = [r["tool_time"] / r["rounds"] / nat_med for r in valid]
        ratio_tmo = [r["tool_time"] / r["rounds"] / nat_mean for r in valid_incl_tmo]
        rounds_vals = sorted({r["rounds"] for r in valid})
        summ.append({
            "program": cve,
            "native_valid_runs": len(nat_ok), "native_excluded_runs": len(nat_bad),
            "native_mean_ms": nat_mean * 1000, "native_std_ms": nat_std * 1000,
            "native_median_ms": nat_med * 1000,
            "period_total_runs": len(per), "period_valid_runs": len(valid),
            "rounds_min": min(rounds_vals) if rounds_vals else "", "rounds_max": max(rounds_vals) if rounds_vals else "",
            "period_ms_per_schedule": st.mean(r["tool_time"] / r["rounds"] for r in valid) * 1000,
            "slowdown_mean": rm, "slowdown_std": rs,
            "slowdown_wall_based": mean_std(wall_ratios)[0],
            "slowdown_native_median": mean_std(ratio_med)[0],
            "slowdown_keep_timeout_runs": mean_std(ratio_tmo)[0],
            "paper_est": paper.get(cve, ""),
        })

    with (out / "rq3_runs.csv").open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["program", "tool", "run", "wall_s", "schedules_round_total",
                    "period_s_per_schedule", "slowdown_x", "log_file", "status"])
        w.writerows(runs_rows)
    cols = list(summ[0].keys())
    with (out / "rq3_summary.csv").open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for s in summ:
            w.writerow([f"{s[c]:.3f}" if isinstance(s[c], float) else s[c] for c in cols])

    # ---- console report -------------------------------------------------------------
    print(f"{'program':15} {'nat ms':>8} {'valid':>5} {'rounds':>9} {'ms/sched':>9} {'slowdown':>13} {'paper~':>7}")
    for s in summ:
        rr = f"{s['rounds_min']}-{s['rounds_max']}" if s['rounds_min'] != s['rounds_max'] else str(s['rounds_min'])
        print(f"{s['program']:15} {s['native_mean_ms']:8.2f} {s['period_valid_runs']:>2}/{s['period_total_runs']:<2} "
              f"{rr:>9} {s['period_ms_per_schedule']:9.1f} {s['slowdown_mean']:6.1f}+-{s['slowdown_std']:<5.1f} {s['paper_est']!s:>7}")
    ours = [s["slowdown_mean"] for s in summ]
    print(f"\nrange of ours: {min(ours):.1f}x - {max(ours):.1f}x ; median {st.median(ours):.1f}x ; "
          f"within 2-30x: {sum(2 <= x <= 30 for x in ours)}/{len(ours)}")
    pe = [s for s in summ if s["paper_est"] != ""]
    if len(pe) >= 3:
        def ranks(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v)
            for pos, i in enumerate(order):
                r[i] = pos + 1
            return r
        x, y = ranks([s["paper_est"] for s in pe]), ranks([s["slowdown_mean"] for s in pe])
        mx, my = st.mean(x), st.mean(y)
        rho = sum((a_ - mx) * (b_ - my) for a_, b_ in zip(x, y)) / (
            (sum((a_ - mx) ** 2 for a_ in x) * sum((b_ - my) ** 2 for b_ in y)) ** 0.5)
        print(f"Spearman rank correlation (paper estimate vs ours, per program): {rho:.2f}")

    # ---- figure ---------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        names = [s["program"] for s in summ]
        xs = range(len(names))
        fig, ax = plt.subplots(figsize=(11, 4.2))
        wd = 0.38
        if paper:
            ax.bar([i - wd / 2 for i in xs], [s["paper_est"] if s["paper_est"] != "" else 0 for s in summ],
                   wd, label="Paper (Fig. 7, estimated)", color="#1f6a8f")
        ax.bar([i + wd / 2 for i in xs], [s["slowdown_mean"] for s in summ], wd,
               yerr=[s["slowdown_std"] for s in summ], capsize=3, label="Ours (mean ± std)", color="#e08a1e")
        ax.axhspan(2, 30, color="grey", alpha=0.12, label="paper's claimed range 2-30x")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(names, rotation=35, ha="right")
        ax.set_ylabel("slowdown over native (x)")
        ax.set_title("PERIOD runtime overhead on the CVE benchmark")
        ax.set_ylim(0, 38)
        ax.legend(loc="upper center", ncol=3, frameon=False)
        fig.tight_layout()
        fig.savefig(out / "figures" / "rq3_slowdown.png", dpi=160)
        print("figure written:", out / "figures" / "rq3_slowdown.png")
    except Exception as e:  # keep the CSVs even if plotting fails
        print("plotting skipped:", e)


if __name__ == "__main__":
    main()
