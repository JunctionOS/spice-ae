#!/usr/bin/env python3
"""Run blink, faasnap/reap, and CRIU benches and consolidate the artifacts
into a single result dir that scripts/plot_e2e.py can read.

Two modes:
  ./run_all.py                  run benches, then consolidate from RESULT_DIR
  ./run_all.py <results-dir>    skip benches, consolidate from <results-dir>'s
                                {blink,faasnap,criu}.recent symlinks
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime

from dirs import RESULT_DIR, SCRIPT_DIR


def run_bench(cmd, env=None):
    print("\n>>>", " ".join(shlex.quote(c) for c in cmd))
    sys.stdout.flush()
    subprocess.run(cmd, check=True, env=env)


def latest(name, base=RESULT_DIR):
    """Return absolute path the {base}/{name}.recent symlink points at, or None."""
    link = os.path.join(base, f"{name}.recent")
    if not os.path.islink(link):
        return None
    target = os.readlink(link)
    if not os.path.isabs(target):
        target = os.path.join(base, target)
    return target


def copy(src, dst):
    """Copy file or directory tree to dst, replacing any existing entry."""
    if os.path.lexists(dst):
        if os.path.islink(dst) or not os.path.isdir(dst):
            os.remove(dst)
        else:
            shutil.rmtree(dst)
    if os.path.isdir(src):
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def consolidate(e2e_dir, blink_dir, criu_dir, faasnap_dir):
    os.makedirs(e2e_dir, exist_ok=True)

    if blink_dir and os.path.isdir(blink_dir):
        for fn in os.listdir(blink_dir):
            if fn.startswith("restore_images_"):
                copy(os.path.join(blink_dir, fn), os.path.join(e2e_dir, fn))

    if criu_dir and os.path.isdir(criu_dir):
        out = os.path.join(criu_dir, "output")
        if os.path.isdir(out):
            copy(out, os.path.join(e2e_dir, "output"))

    if faasnap_dir and os.path.isdir(faasnap_dir):
        for entry in sorted(os.listdir(faasnap_dir)):
            if entry.startswith("faasnap_") or entry.startswith("reap_"):
                copy(
                    os.path.join(faasnap_dir, entry),
                    os.path.join(e2e_dir, entry),
                )


def main():
    ap = argparse.ArgumentParser(
        description="Run all systems and bundle results for plot_e2e.py"
    )
    ap.add_argument(
        "source_dir",
        nargs="?",
        help="Existing results dir holding {blink,faasnap,criu}.recent symlinks. "
        "If given, skip benches and only consolidate.",
    )
    ap.add_argument("--skip-blink", action="store_true")
    ap.add_argument("--skip-faasnap", action="store_true")
    ap.add_argument("--skip-criu", action="store_true")
    ap.add_argument(
        "--name-filter", help="regex passed to each bench's --name-filter"
    )
    ap.add_argument(
        "--lang-filter", help="regex passed to each bench's --lang-filter"
    )
    ap.add_argument(
        "--criu-args",
        default="--criu-mmap-only",
        help="extra args forwarded to criu_bench.py (mode flags)",
    )
    ap.add_argument(
        "--no-plot", action="store_true", help="skip running plot_e2e.py at the end"
    )
    args = ap.parse_args()

    if args.source_dir:
        base = os.path.abspath(args.source_dir)
        if not os.path.isdir(base):
            print(f"source_dir {base} does not exist")
            sys.exit(1)
    else:
        base = RESULT_DIR
        py = sys.executable
        common = []
        if args.name_filter:
            common += ["--name-filter", args.name_filter]
        if args.lang_filter:
            common += ["--lang-filter", args.lang_filter]

        if not args.skip_blink:
            run_bench([py, f"{SCRIPT_DIR}/blink_bench.py"] + common)
        if not args.skip_faasnap:
            run_bench(
                [py, f"{SCRIPT_DIR}/faasnap_bench.py", "--do-faasnap", "--do-reap"]
                + common
            )
        if not args.skip_criu:
            run_bench(
                [py, f"{SCRIPT_DIR}/criu_bench.py", *shlex.split(args.criu_args)]
                + common
            )

    blink_dir = None if (not args.source_dir and args.skip_blink) else latest("blink", base)
    faasnap_dir = None if (not args.source_dir and args.skip_faasnap) else latest("faasnap", base)
    criu_dir = None if (not args.source_dir and args.skip_criu) else latest("criu", base)

    ts = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    e2e_name = f"e2e.{ts}"
    e2e_dir = os.path.join(base, e2e_name)

    consolidate(e2e_dir, blink_dir, criu_dir, faasnap_dir)

    recent = os.path.join(base, "e2e.recent")
    if os.path.lexists(recent):
        os.remove(recent)
    os.symlink(e2e_name, recent)

    print(f"\nconsolidated artifacts at {e2e_dir}")
    print("contents:")
    for fn in sorted(os.listdir(e2e_dir)):
        print(f"  {fn}")

    if not args.no_plot:
        run_bench([sys.executable, f"{SCRIPT_DIR}/plot_e2e.py", e2e_dir])


if __name__ == "__main__":
    main()
