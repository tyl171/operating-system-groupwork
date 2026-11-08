Environment setup:
This article records the complete steps used to set up the experimental environment.
On the basis of following the original author's environment setup, 
a testing section has been added, and the deviations we had to make have been documented

reference：<https://github.com/wcventure/PERIOD/blob/main/INSTALL.md>
0. Preconditions

To run smoothly, the environment must meet the following requirements: For the OS, use Ubuntu 18.04 or later (we currently use 26.04 LTS), with kernel version ≥ 4.x (the upstream notes this is due to the scheduling policy) and support for SCHED_DEADLINE, because PERIOD's periodic execution relies on this feature; for software, Docker version ≥ 18.09.7 (upstream requirement); for hardware, since PERIOD is a concurrency testing tool, a multi-core CPU is required, along with at least 20 GB of free disk space (because the extracted image takes up about 6 GB).

Verify if 'SCHED-DEADLINE' is available

```bash
cat /proc/sys/kernel/sched_rt_runtime_us
# expect a number, e.g. 950000

sudo chrt -d --sched-runtime 1000000 --sched-period 5000000 --sched-deadline 5000000 0 true
# silent success = supported
```

If `chrt` returns `Invalid argument`, the kernel lacks `SCHED_DEADLINE` and
PERIOD cannot run — use a different kernel/OS.

1. install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker

# optional: run docker without sudo
sudo usermod -aG docker "$USER"
# log out and back in for the group change to take effect
```

Check:

```bash
docker --version
```
## 2. Obtain the PERIOD image

```bash
sudo docker pull wcventure/period:stable
sudo docker tag wcventure/period:stable period:latest
```

**Pinned identity** (record this in the report / README):

```
wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
```

3. Network workaround (our testbed only)

Due to firewall restrictions, ` registray-1. docker. io ` is * * unreachable * * in our network. 

The attempts and results are as follows:

Because registry:1.docker.io is unreachable in our network, we tested several alternative methods: a direct sudo docker pull failed with a "connection refused" error; using image accelerators (such as daocloud, docker.nju.edu.cn, 1panel, and rat.dev) made the registry reachable, but the speed was severely limited to about 0.1 MB/s, causing 8 out of 10 layers to get stuck; ultimately, configuring dockerd to use a local HTTP proxy succeeded, completing the download in approximately 5 minutes.

Final configuration

Create the systemd drop-in:

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/proxy.conf > /dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://your onw ip address：7890"
Environment="HTTPS_PROXY=http://your onw ip addres：7890"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF
```
Apply:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl show docker --property=Environment    # verify
```

attention：
The upstream **from-source** installation path was not used: it depends on
  Python 2 packages (`python`, `python-pip`) and `libncurses5`, none of which
  are available on Ubuntu 24.04 and later. The Docker image already bundles the
  identical toolchain (LLVM 10, SVF, static-analysis scripts, wllvm).
The guest was configured with NAT networking; the host proxy address was
  therefore a LAN address reachable through the NAT gateway.
