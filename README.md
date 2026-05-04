# Blink Artifact - OSDI '26
This repository bundles the necessary dependencies and experiment scripts
to reproduce results from the paper


**Rethinking Process Snapshots for Near-Warm Serverless Cold Starts**

Ben Holmes, Baltasar Dinis, Lana Honcharuk, Joshua Fried, Adam Belay

# Overview
This repository evaluates the cold-start performance of Blink, a system
for restoring process snapshots with a highly optimized snapshot format and
kernel-space loader to minimize CPU cost during restore. 

## Directory Structure

```
blink-ae/
├-- criu/                   # Fork of CRIU with added timestamps for benchmarking and support for restoring an address space via mmap() only
├-- faasnap/                # Fork of the FaaSnap artifact with modifications to support multiple functions and simplify the invocation path. Also used for REAP experiments.
├-- faasnap-kernel/         # Linux 4.14 kernel used as the guest in the FaaSnap evaluation
├-- firecracker/            # FaaSnap's modified firecracker with added support for detailed tracing of the guest kernel
├-- functions               # Serverless Function Examples
|   ├-- data                # Input data for function examples
|   ├-- java                # Java functions
|   ├-- node                # Node functions
|   └── python              # Python functions
├-- jifpager                # Kernel module for loading snapshots
├-- jiftools                # Userspace tool for generating/editing/reading snapshots
├-- junction                # LibOS-based container system for executing functions
├-- node                    # Modified Node.js runtime to support freezing the GC
└── scripts                 # Experiment and util scripts
```

Blink's implementation is split between the `junction` and `jifpager` submodules. Junction [1] is
a libOS container system responsible for generating snapshots and invoking 
functions from a snapshot image. `jifpager` is a Linux 6.5.0 kernel module 
containing the implementation of the the kernel-space snapshot loader.

The paper compares Blink to CRIU [2], REAP [3] and FaaSnap [4] which are contained in
this repo as submodules.

# Artifact Evaluation Guide

We have provisioned hardware through CloudLab with a disk image containing
a 6.5.0 Linux kernel that automatically mounts a partition on an NVMe SSD
used for storing snapshots. We ask artifact reviewers to please email bencw12@mit.edu so we can provide access to the hardware. We currently have
a c6620 node reserved which has a Micron 7450 MAX NVMe SSD rated for 
sequential 128KB reads of up to 6800 MB/s (1M IOPS 4K random read). The SSD used in the paper
was a Crucial T705 rated at 13600 MB/s (1.4M IOPS 4K random read). 


# Getting Started Instructions
The following builds all systems/dependencies and runs a simple helloworld function as a minimal starting example.
```
./scripts/build_all.sh
# run only the helloworld python function, result plot placed in ./results/e2e.recent/latency.py
./scripts/run_all.py --name-filter helloworld
```

# Detailed Instructions
Assuming everything was built from the previous step, run `./scripts/run_all.py` to run latency experiments with all functions. 

To run tests for invididual systems, run

```
# Run a set of functions with Blink (results in results/blink.recent)
./scripts/blink_bench.py --name-filter <function name regex> --lang-filter <function language regex>

# Run a set of functions with FaaSnap (results in results/faasnap.recent)
./scripts/faasnap_bench.py --name-filter <function name regex>
 --lang-filter <function language regex> --do-faasnap
 
# Run a set of functions with REAP (results in results/faasnap.recent)
./scripts/faasnap_bench.py --name-filter <function name regex>
 --lang-filter <function language regex> --do-reap
 
# Run a set of functions with CRIU (results in results/criu.recent)
./scripts/criu_bench.py --name-filter <function name regex>
 --lang-filter <function language regex> --criu-mmap-only

# plot_e2e.py will plot results for whichever systems/functions are available in <result dir>
 ./scripts/plot_e2e.py <result dir>
 ```

# Claims 
The data produced from `./scripts/run_all.py` re-creates the results presented in Figure 10 of the paper comparing end-to-end latency of the systems evaluated. The expectation is that Blink has significantly lower latency than FaaSnap, REAP, and CRIU and is close to the latency of a warm invocation. Because the SSD on the CloudLab node is slower than the one used in the paper, results will vary slightly but in our testing on the slower drive Blink's latencies are within 1-2ms of the numbers presented in the paper.
