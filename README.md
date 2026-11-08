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
cd /workdir/PERIOD/test/doubleFree
./cleanDIR.sh && ./build.sh
$ROOT_DIR/tool/DBDS/run_PDS.py -y -d 3 ./df
```

Expected final lines:

```
Total Error Interleavings: 4
Total Timeouts Interleavings: 0
```

> `[Error Found]` lines are the expected result, not failures — PERIOD is a
> bug-finding tool and `test/doubleFree` intentionally contains a double-free bug.

---

