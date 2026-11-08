# Setup Notes — Network restrictions

This file records the troubleshooting performed while obtaining the PERIOD
Docker image. It is a log, not part of the reproduction procedure.

## Symptom

```
$ sudo docker pull wcventure/period:stable
Error response from daemon: failed to resolve reference
"docker.io/wcventure/period:stable": failed to do request:
Head "https://registry-1.docker.io/v2/...": dial tcp 199.16.158.9:443:
connect: connection refused
```

## Attempts and outcomes

| # | Attempt | Result |
|---|---------|--------|
| 1 | `docker pull` as a normal user | `permission denied ... /var/run/docker.sock` (user not in `docker` group) |
| 2 | `sudo docker pull` | `connect: connection refused` → Docker Hub not reachable |
| 3 | Registry mirrors: `docker.m.daocloud.io` | connection established, then stalled; layers restarted repeatedly |
| 4 | Registry mirrors: `docker.nju.edu.cn`, `docker.1panel.live`, `hub.rat.dev` | reachable (IPv4 `210.28.130.20`), but ≈0.1 MB/s; 8 of 10 layers completed, 2 stalled |
| 5 | Disabled IPv6 on the guest interface | modest improvement (Docker was waiting on IPv6 timeouts) |
| 6 | **dockerd behind a host HTTP proxy** | ✅ completed in ≈5 minutes |

## Root causes identified

1. `registry-1.docker.io` is blocked from this network.
2. The guest's DNS returned an **IPv6-only** record for the mirror host, while
   the NAT network has no IPv6 route — Docker stalled on IPv6 connect attempts.
3. Docker's registry mirrors and a proxy must not be configured at the same
   time: Docker tries the mirror first and waits on it before falling back.

## Final configuration

```
/etc/docker/daemon.json                                        → removed
/etc/systemd/system/docker.service.d/proxy.conf                → present
    [Service]
    Environment="HTTP_PROXY=http://192.168.31.174:7890"
    Environment="HTTPS_PROXY=http://192.168.31.174:7890"
    Environment="NO_PROXY=localhost,127.0.0.1"
```

## Verification

```bash
curl -x http://192.168.31.174:7890 -I https://registry-1.docker.io/v2/
# HTTP/2 401  → reachable (401 is expected for an unauthenticated ping)
```

## Lesson

Public registry mirrors are unreliable for small, rarely-pulled images.
Routing the Docker daemon through the host's existing proxy was both faster and
more reproducible than any mirror configuration.
