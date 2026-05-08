# Spice Artifact - OSDI '26
This repository bundles the necessary dependencies and experiment scripts
to reproduce results from the paper


**Rethinking Process Snapshots for Near-Warm Serverless Cold Starts**

Ben Holmes, Baltasar Dinis, Lana Honcharuk, Joshua Fried, Adam Belay

# Overview
This repository evaluates the cold-start performance of Spice, a system
for restoring process snapshots with a highly optimized snapshot format and
kernel-space loader to minimize CPU cost during restore. 

## Directory Structure

```
spice-ae/
├-- criu/                   # Fork of CRIU with added timestamps for benchmarking and support for restoring an address space via mmap() only
├-- faasnap/                # Fork of the FaaSnap artifact with modifications to support multiple functions and simplify the invocation path. Also used for REAP experiments.
├-- faasnap-kernel/         # Linux 4.14 kernel used as the guest in the FaaSnap evaluation
├-- firecracker/            # FaaSnap's modified firecracker with added support for detailed tracing of the guest kernel
├-- functions               # Serverless Function Examples
|   ├-- data                # Input data for function examples
|   ├-- java                # Java functions
|   ├-- node                # Node functions
|   └── python              # Python functions
├-- reexec                  # Kernel module for loading snapshots
├-- jiftools                # Userspace tool for generating/editing/reading snapshots
├-- junction                # LibOS-based container system for executing functions
├-- node                    # Modified Node.js runtime to support freezing the GC
└── scripts                 # Experiment and util scripts
```

Spice's implementation is split between the `junction` and `reexec` submodules. Junction [^1] is
a libOS container system responsible for generating snapshots and invoking 
functions from a snapshot image. `reexec` is a Linux 6.5.0 kernel module 
containing the implementation of the the kernel-space snapshot loader.

The paper compares Spice to CRIU [^2], REAP [^3] and FaaSnap [^4] which are contained in
this repo as submodules.

# Artifact Evaluation Guide

We provide a [CloudLab disk image](https://www.cloudlab.us/p/Shenango/Blink) running Linux 6.5.0 and Ubuntu 24.04 for reviewers to instantiate
for artifact evaluation. We have tested the artifact on a c6620 node with a 
Micron 7450 MAX NVMe SSD rated for 
sequential 128KB reads of up to 6800 MB/s (1M IOPS 4K random read). The SSD used in the paper
was a Crucial T705 rated at 13600 MB/s (1.4M IOPS 4K random read).
CloudLab partitions default to 64GB so the profile will format/mount any available SSD
capacity for snapshot storage. The filesystems are mounted at, for example `/mnt/unused-nvme1n1` for
the remaining capacity of the first available NVMe SSD. Reviewers should create a directory for
storing snapshots at one of these locations, e.g.

```
sudo mkdir /mnt/unused-nvme1n1/snapshots; sudo chown $USER /mnt/unused-nvme1n1/snapshots
```

# Getting Started Instructions

Building and running the artifact requires root privileges. The first
step is to add yourself to the `docker` group and start a new session.

```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

The following builds all systems/dependencies and runs a simple helloworld function as a minimal starting example. These instructions assume
a snapshot directory has been created at `/mnt/unused-nvme1n1/snapshots`. The build takes ~30 minutes and requires ~70GB of disk space (not including snapshot files).

> [!NOTE]
> CloudLab rootfs partitions default to 64GB. To avoid running out of space, either run `sudo RESIZEROOT=128 /opt/setup-grow-rootfs.sh` to resize to 128GB, or
> run `FAASNAP_ROOTFS=/mnt/unused-nvme1n1/ ./scripts/build_all.sh` to build the rootfs for FaaSnap/REAP guest VMs on the larger unused partition.

```
# setting FAASNAP_ROOTFS is optional, default location is ./faasnap/rootfs/debian-rootfs.ext4
FAASNAP_ROOTFS=/mnt/unused-nvme1n1 ./scripts/build_all.sh

# run only the helloworld python function, result plot placed in ./results/e2e.recent/latency.py
SNAPSHOT_DIR=/mnt/unused-nvme1n1/snapshots ./scripts/run_all.py --name-filter helloworld
```

# Detailed Instructions
Assuming everything was built from the previous step, run `./scripts/run_all.py` to run latency experiments with all functions. 

To run tests for invididual systems, run

```
# Run a set of functions with Spice (results in results/spice.recent)
SNAPSHOT_DIR=/mnt/unused-nvme1n1/snapshots ./scripts/spice_bench.py --name-filter <function name regex> --lang-filter <function language regex>

# Run a set of functions with FaaSnap (results in results/faasnap.recent)
SNAPSHOT_DIR=/mnt/unused-nvme1n1/snapshots ./scripts/faasnap_bench.py --name-filter <function name regex> --lang-filter <function language regex> --do-faasnap
 
# Run a set of functions with REAP (results in results/faasnap.recent)
SNAPSHOT_DIR=/mnt/unused-nvme1n1/snapshots ./scripts/faasnap_bench.py --name-filter <function name regex> --lang-filter <function language regex> --do-reap
 
# Run a set of functions with CRIU (results in results/criu.recent)
SNAPSHOT_DIR=/mnt/unused-nvme1n1/snapshots ./scripts/criu_bench.py --name-filter <function name regex> --lang-filter <function language regex> --criu-mmap-only

# plot_e2e.py will plot results for whichever systems/functions are available in <result dir>
 ./scripts/plot_e2e.py <result dir>
 ```

# Claims 
The data produced from `./scripts/run_all.py` re-creates the results presented in Figure 10 of the paper comparing end-to-end latency of the systems evaluated. The expectation is that Spice has significantly lower latency than FaaSnap, REAP, and CRIU and is close to the latency of a warm invocation. Because the SSD on the CloudLab node is slower than the one used in the paper, results will vary slightly but in our testing on the slower drive Spice's latencies are within 1-2ms of the numbers presented in the paper.

# References

[^1]: https://www.usenix.org/conference/nsdi24/presentation/fried
[^2]: https://www.criu.org/Main_Page
[^3]: https://dl.acm.org/doi/10.1145/3445814.3446714
[^4]: https://dl.acm.org/doi/10.1145/3492321.3524270
