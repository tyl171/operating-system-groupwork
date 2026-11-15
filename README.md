# CS340 Reproduction — Period (ICSE 2022)

Course project: **Research Paper Replication**, CS340 Operating Systems (2026–2027).

---

## 1. Purpose

This repository reproduces the main claims of:

> **Controlled Concurrency Testing via Periodical Scheduling**
> Cheng Wen, Mengda He, Bohao Wu, Zhiwu Xu, Shengchao Qin — ICSE 2022

- Paper: <https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf>
- DOI: 10.1145/3510003.3510178
- Upstream artifact: <https://github.com/wcventure/PERIOD> (MIT License)

PERIOD is a controlled concurrency testing (CCT) tool. It models the execution
of a concurrent program as **periodical execution**: context switches become
period switches, implemented with the Linux `SCHED_DEADLINE` policy, so no
preemption or sleep delay is needed and threads may still run in parallel
within a period.

**Claims tested:**

| ID | Claim | Evidence in paper |
|----|-------|-------------------|
| **C1** | PERIOD detects all 10 buggy programs in the CVE benchmark, whereas existing CCT techniques detect only 7. | Table 1 |
| **C2** | PERIOD incurs a 2–30× runtime slowdown relative to native execution, well below the 10–500× of IPB/IDB/PCT. | Figure 7 |

---

## 2. Environment

### 2.1 Paper's setup (ICSE 2022, §4.1.3)

| Component | Value |
|-----------|-------|
| CPU | Intel Xeon Silver 4214 (12 cores / 24 threads) |
| OS | Ubuntu 18.04 |
| GCC | 7.5 |
| LLVM | 10.0 |
| Schedule depth | 5 (CVE benchmark) / 3 (SCTBench) |
| Schedule budget | 10,000 schedules per invocation |

### 2.2 Our setup

| Component | Value |
|-----------|-------|
| Host | Windows 11 + VMware Workstation 26 |
| Guest OS | Ubuntu 26.04 LTS |
| Kernel | 7.0.0-43-generic |
| CPU | 8 vCPU (1 socket × 8 cores, no SMT) |
| Memory | 16 GB |
| Docker | 29.1.3 (`docker.io` 29.1.3-0ubuntu4.1) |
| PERIOD image | `wcventure/period:stable` |
| Image digest | `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Side-channel mitigations | enabled (host default) |

All differences from the paper are listed in [`docs/deviations.md`](docs/deviations.md).

---

## 3. Installation

Full procedure: **[INSTALL.md](INSTALL.md)** — includes the network workaround
we needed because `registry-1.docker.io` is unreachable from our testbed.

Short version:

```bash
sudo apt install -y docker.io
sudo docker pull wcventure/period:stable
sudo docker tag wcventure/period:stable period:latest
```

---

## 4. Testing

Full procedure: **[TEST.md](TEST.md)**.

Short version:

```bash
sudo docker run --privileged -it period:latest /bin/bash
# inside the container:
source /workdir/PERIOD/tool/init_env.sh
cd $ROOT_DIR/test/doubleFree
./cleanDIR.sh && ./build.sh
$ROOT_DIR/tool/DBDS/run_PDS.py -y -d 3 ./df
```

Expected final lines:

```
Total Error Interleavings: 4
Total Timeouts Interleavings: 0
```

## 5.claim



claim 2

### Build

All ten programs are built with the upstream batch script. This is the exact
sequence recorded in [`logs/claim2log/cve/build_all.log`](logs/claim2log/cve/build_all.log):

```bash
# inside the container, at the repository root
cd /workdir/PERIOD
source tool/init_env.sh

# compile all ten ConVul-CVE-Benchmarks programs
cd $ROOT_DIR/evaluation/ConVul-CVE-Benchmarks
./build_all.sh
```

`build_all.sh` runs `cleanDIR.sh`, the LLVM bitcode step, `staticAnalysis.sh`
and the DBDS instrumentation for each program. It takes about 3 minutes.

### Run

Schedule depth `-d 5` and `-y` (skip the interactive prompt) are the settings
used for this benchmark throughout the paper. The binary name is the directory
name without the `CVE-` prefix:

```bash
cd $ROOT_DIR/evaluation/ConVul-CVE-Benchmarks/CVE-2009-3547
$ROOT_DIR/tool/DBDS/run_PDS.py -y -d 5 ./2009-3547
```

| Program | Binary |
|---|---|
| CVE-2009-3547 | `2009-3547` |
| CVE-2011-2183 | `2011-2183` |
| CVE-2013-1792 | `2013-1792` |
| CVE-2015-7550 | `2015-7550` |
| CVE-2016-1972 | `2016-1972` |
| CVE-2016-1973 | `2016-1973` |
| CVE-2016-7911 | `2016-7911` |
| CVE-2016-9806 | `2016-9806` |
| CVE-2017-6346 | `2017-6346` |
| CVE-2017-15265 | `2017-15265` |

### Expected output

Every program ends with a summary block; `Total Error Interleavings` must be
greater than zero, otherwise PERIOD did not detect the bug:

```
End Testing!

Total Error Interleavings: 3
Total Timeouts Interleavings: 0
```

For CVE-2009-3547 we get 3 error interleavings on every run; the per-program
numbers we measured are in [`claim2cve.md`](claim2cve.md).

### Runtime

- `./build_all.sh`: about 3 minutes.

Measure with `/usr/bin/time -f "%e s" $ROOT_DIR/tool/DBDS/run_PDS.py -y -d 5 ./2009-3547`
if you need to re-measure on another machine.

The process and results of reproducing this experiment are in
[`claim2cve.md`](claim2cve.md).

Upstream per-program instructions:
[CVE-2009-3547](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2009-3547) ·
[CVE-2011-2183](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2011-2183) ·
[CVE-2013-1792](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2013-1792) ·
[CVE-2015-7550](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2015-7550) ·
[CVE-2016-1972](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2016-1972) ·
[CVE-2016-1973](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2016-1973) ·
[CVE-2016-7911](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911) ·
[CVE-2016-9806](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2016-9806) ·
[CVE-2017-6346](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2017-6346) ·
[CVE-2017-15265](https://github.com/wcventure/PERIOD/tree/main/evaluation/ConVul-CVE-Benchmarks/CVE-2017-15265)

These commands are adapted from the upstream
[README](https://github.com/wcventure/PERIOD); the upstream source is used
unmodified.


## Inspect subset (paper Table 2)

### Build

Both programs live under `$ROOT_DIR/evaluation/Inspect_benchmarks/`. Build with
the per-program script:

```bash
cd $ROOT_DIR/evaluation/Inspect_benchmarks/qsort_mt
./cleanDIR.sh && ./build.sh

cd $ROOT_DIR/evaluation/Inspect_benchmarks/boundedBuffer
./cleanDIR.sh && ./build.sh
```

### Run

```bash
cd $ROOT_DIR/evaluation/Inspect_benchmarks/qsort_mt
$ROOT_DIR/tool/DBDS/run_PDS.py -y -d 3 -f 10000 ./qsort_mt -n 32 -f 4 -h 3 -v

cd $ROOT_DIR/evaluation/Inspect_benchmarks/boundedBuffer
$ROOT_DIR/tool/DBDS/run_PDS.py -y -d 3 -f 10000 ./boundedBuffer
```

The process and results of reproducing this experiment are in
[`sctinspect.md`](sctinspect.md).
