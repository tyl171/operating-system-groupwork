# Deviations from the Paper's Setup

Every change from the paper's environment is listed here (report requirement:
*item, original setting, setting used, reason*).

| # | Item | Paper (ICSE 2022) | Ours | Reason |
|---|------|-------------------|------|--------|
| 1 | CPU model | Intel Xeon Silver 4214 (server) | Intel Core Ultra 9 275HX (consumer), 8 vCPU assigned | Host hardware available to us |
| 2 | CPU cores / SMT | 12 cores / 24 threads (SMT on) | 8 vCPU, no SMT exposed by the hypervisor | VMware does not expose hyperthreading to the guest |
| 3 | CPU topology | homogeneous | heterogeneous (P-cores + E-cores) | Consumer hybrid CPU; timing noise analysed separately |
| 4 | OS | Ubuntu 18.04 | Ubuntu 26.04 LTS | 18.04 is end-of-life |
| 5 | Kernel | 4.15 series | 7.0.0-43-generic | Ships with 26.04 |
| 6 | GCC on host | 7.5 | 11.4 | Ships with 26.04 (irrelevant: builds run in the container) |
| 7 | Runs per program | 10 | 3 | Course minimum is 3; time budget |
| 8 | Docker image retrieval | direct pull from Docker Hub | via a host HTTP proxy | `registry-1.docker.io` unreachable from our network (see `setup-notes.md`) |
| 9 | Virtualisation | bare metal | VMware Workstation guest | Only available hardware |

## Not changed (deliberately)

| Item | Value | Why it matters |
|---|---|---|
| Benchmark set | `evaluation/ConVul-CVE-Benchmarks` (10 programs) | Same subjects as Table 1 |
| Schedule depth | `-d 5` (CVE) / `-d 3` (SCTBench) | Same as §4.1.3 |
| Schedule budget | 10,000 schedules per invocation | Same as §4.1.3 |
| PERIOD version | starting commit `cb8deb9a` + image digest `sha256:8f47d8b9148f2db5…` | Same tool as the paper |
| Metric definitions | `#schedules`, `#buggy schedules`, `schedules to bug (1st)` | Same metric as Tables 1–2 |

## Expected impact

| Measured quantity | Affected by the deviations above? |
|---|---|
| Number of schedules explored | **No** — PERIOD's exploration is deterministic and bounded by a schedule *count*, not by wall-clock time |
| Number of buggy schedules found | **No** (same reason) |
| Whether a bug is detected | Only via schedule truncation; we therefore did **not** set `-t` timeouts |
| Runtime and runtime slowdown | **Yes** — fewer cores, different CPU, virtualisation overhead |
