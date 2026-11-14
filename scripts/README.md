# scripts/ (planned)

Driver scripts that wrap the commands documented in [`../TEST.md`](../TEST.md).

| Script | Purpose | Status |
|---|---|---|
| `00_setup.sh` | install Docker, pull the pinned image, verify `SCHED_DEADLINE` | planned |
| `01_smoke_test.sh` | run `test/doubleFree`, assert `Total Error Interleavings: 4` | planned |
| `02_build_cve.sh` | build the 10 CVE programs | planned |
| `03_run_cve.sh` | run the CVE benchmark N times, one log per run | planned |
| `04_overhead.sh` | native vs PERIOD wall-clock timing | planned |
| `collect.py` | parse `logs/*.log` into `results/summary.csv` | planned |

Until these exist, use the raw commands in [`../TEST.md`](../TEST.md); they are
the same commands and have been verified on our testbed.
