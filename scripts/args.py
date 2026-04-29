import argparse

parser = argparse.ArgumentParser(
    prog="faasnap_bench", description="FaaSnap/REAP benchmark script"
)

parser.add_argument(
    "--do-reap", action="store_true", default=False, help="run REAP experiments"
)
parser.add_argument(
    "--do-faasnap", action="store_true", default=False, help="run FaaSnap experiments"
)
parser.add_argument(
    "--name-filter", help="regex to positively filter tests by their name"
)
parser.add_argument(
    "--lang-filter", help="regex to positively filter tests by their language"
)
parser.add_argument(
    "--snapshot-only",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="only take a snapshot for REAP/FaaSnap experiments",
)
parser.add_argument(
    "--restore-only",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="only restore a snapshot for REAP/FaaSnap experiments",
)
parser.add_argument(
    "--use-chroot",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="use the chroot'ed filesystem",
)
parser.add_argument(
    "--redo-snapshot",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="regenerate the snapshots",
)
parser.add_argument(
    "--cold-uarch",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="flush cpu caches when measuring warm invocation times",
)
parser.add_argument(
    "--criu-eager",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="run CRIU eager mode (optionally with lazy pages)",
)
parser.add_argument(
    "--no-lazy-pages",
    action="store_true",
    default=False,
    help="disable CRIU lazy pages when --criu-eager",
)
parser.add_argument(
    "--criu-mmap-only",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="restore memory with mmap only, disabling preadv in CRIU",
)
parser.add_argument(
    "--criu-no-cow",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="disable CoW by mapping the snapshot file shared in CRIU",
)
parser.add_argument(
    "--criu-strace",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="run CRIU restore under strace",
)

ARGS = parser.parse_args()
