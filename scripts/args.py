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

ARGS = parser.parse_args()
