#!/usr/bin/env python3
import argparse
import json
import os

import numpy as np
from matplotlib import pyplot as plt
from parsing import (
    BLINK_TAG,
    CRIU_CONFIGS,
    parse_blink_logs,
    parse_criu_logs,
    parse_faasnap_logs,
)

FUNC_LABEL_MAP = {
    "python_helloworld": "hello",
    "python_pyaes": "pyaes",
    "java_matmul": "mtml",
    "python_chameleon": "html",
    "python_image_rotate_s3": "img",
    "python_json_serdes_s3": "json",
    "node_json_serdes_s3": "json",
    "python_lr_serving": "lr",
    "python_rnn_serving": "rnn",
    "python_cnn_serving": "cnn",
    "node_image_rotate_s3": "img",
    "python_video_processing_s3": "video",
    "java_image_rotate_s3": "img",
}


def get_label(f):
    return FUNC_LABEL_MAP.get(f)


annotations = []
seen = set()


def get_lbl(label):
    if label in seen:
        return None
    seen.add(label)
    return {
        "function": "Function",
        "metadata": "Cereal restore",
        "fs": "MemFS restore",
        "data": "VMA restore",
        "restore": "Restore time",
        "vmm": "Load VMM",
    }.get(label, label)


COLORS = {
    "function": "tab:blue",
    "restore": "tab:red",
    "Spice": "darkorange",
    "REAP*": "crimson",
    "FaaSnap*": "tab:brown",
    "CRIU*": "violet",
    "Warm": "dodgerblue",
}

HATCHES = {
    "REAP*": "//",
    "FaaSnap*": "\\\\",
    "Spice": "xx",
    "CRIU*": "oo",
    "Warm": "",
}


def plot_one_system(ax, x, d, title, split=None):
    width = 0.2
    b = 0
    for v, _ in d:
        b += v

    val = b / 1000
    target_axes = [ax]
    if split is not None:
        target_axes.append(split)

    for a in target_axes:
        a.bar(
            x,
            val,
            width=width,
            color=COLORS.get(title),
            label=get_lbl(title),
            hatch=HATCHES[title],
            edgecolor="black",
        )
        if title != "Warm":
            a.bar(
                x,
                d[1][0] / 1000,
                width=width,
                color=COLORS.get(title),
                hatch=None,
                edgecolor="black",
            )

    if title in ("Spice", "Warm"):
        text_str = str(int(val)) if int(val) > 1 else f"{val:.1f}"
        target = split if split is not None else ax
        text = target.text(
            x * 1.01,
            val,
            text_str,
            ha="center",
            va="bottom",
            fontsize=10,
            rotation=50,
        )
        annotations.append(text)

    return val


FUNCTIONS = [
    "python_helloworld",
    "python_pyaes",
    "python_chameleon",
    "python_image_rotate_s3",
    "python_json_serdes_s3",
    "python_lr_serving",
    "python_rnn_serving",
    "python_cnn_serving",
    "python_video_processing_s3",
    "node_json_serdes_s3",
    "node_image_rotate_s3",
    "java_matmul",
    "java_image_rotate_s3",
]

# Functions plotted on the secondary (right) axis
SECONDARY = {
    "python_video_processing_s3",
    "python_lr_training_s3",
    "java_image_rotate_s3",
}


def build_stack(key, blink_data, faasnap_data, criu_data):
    fdata = faasnap_data.get("faasnap", {}).get(key)
    rdata = faasnap_data.get("reap", {}).get(key)
    bdata = blink_data.get(key, {}).get(BLINK_TAG)

    def faasnap_stack(s):
        if not s:
            return [(0, "function"), (0, "restore")]
        vmm = s["vm_dial"] + s["request_load_snapshot"] + s["vm_resume"]
        return [(s["invoke"], "function"), (vmm, "restore")]

    def criu_stack(configs):
        if not configs:
            return [(0, "function"), (0, "restore")]
        for c in CRIU_CONFIGS:
            entry = configs.get(c)
            if not entry:
                continue
            iter_us = entry.get("post_resume_iter_us") or 0
            restore = entry.get("restore_us") or 0
            if iter_us or restore:
                return [(iter_us, "function"), (restore, "restore")]
        return [(0, "function"), (0, "restore")]

    if bdata:
        blink = [
            (bdata["cold_first_iter"], "function"),
            (
                bdata["metadata_restore"] + bdata["fs_restore"] + bdata["data_restore"],
                "restore",
            ),
        ]
        warm = [(bdata["uncached_iter"], "function")]
    else:
        blink = [(0, "function"), (0, "restore")]
        warm = [(0, "function")]

    return (
        key,
        faasnap_stack(fdata),
        faasnap_stack(rdata),
        criu_stack(criu_data.get(key)),
        blink,
        warm,
    )


def merge_lang_groups(spans):
    """Merge consecutive (lang, lo, hi) spans into one entry per language run."""
    out = []
    for lang, lo, hi in spans:
        if out and out[-1][0] == lang:
            out[-1] = (lang, out[-1][1], hi)
        else:
            out.append([lang, lo, hi])
    return [tuple(x) for x in out]


def draw_lang_brackets(ax, spans, line_y, label_y, width, lw=1):
    """Draw a horizontal bracket below `ax` for each language group with its label."""
    for lang, lo, hi in merge_lang_groups(spans):
        ax.plot(
            [lo - width / 2, hi + width / 2],
            [line_y, line_y],
            transform=ax.get_xaxis_transform(),
            color="black",
            clip_on=False,
            lw=lw,
        )
        ax.text(
            (lo + hi) / 2,
            label_y,
            lang.capitalize(),
            transform=ax.get_xaxis_transform(),
            fontsize=9,
            ha="center",
        )


def plot_comparison(result_dir, data):
    fig = plt.figure(figsize=(12, 3))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], width_ratios=[11, 2], hspace=0.1)

    ax1 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[:, 1])

    ax3.spines.bottom.set_visible(False)
    ax1.spines.top.set_visible(False)
    ax3.xaxis.tick_top()
    ax3.tick_params(labeltop=False)
    ax1.xaxis.tick_bottom()
    ax2.xaxis.tick_bottom()

    fig.subplots_adjust(left=0.05, right=1.0)

    blink_data = data.get("spice", {})
    faasnap_data = data.get("faasnap", {})
    criu_data = data.get("criu", {})

    stacks = [build_stack(k, blink_data, faasnap_data, criu_data) for k in FUNCTIONS]

    width = 0.2
    primary_heights = []
    secondary_heights = []
    primary_lang_spans = []
    secondary_lang_spans = []
    data_copy = {}

    for is_secondary, ax, split in [(False, ax1, ax3), (True, ax2, None)]:
        x_coords = []
        x_labels = []
        lang_spans = secondary_lang_spans if is_secondary else primary_lang_spans
        x = 0

        for workload, faasnap, reap, criu, blink, warm in stacks:
            in_secondary = workload in SECONDARY
            if is_secondary != in_secondary:
                continue

            label = get_label(workload) or workload
            data_copy[label] = {
                "faasnap": int(sum(v for v, _ in faasnap)),
                "reap": int(sum(v for v, _ in reap)),
                "criu": int(sum(v for v, _ in criu)),
                "spice": int(sum(v for v, _ in blink)),
                "warm": int(sum(v for v, _ in warm)),
            }

            systems = [
                ("FaaSnap*", faasnap),
                ("REAP*", reap),
                ("CRIU*", criu),
                ("Spice", blink),
                ("Warm", warm),
            ]
            first_bar_x = x
            for sys_label, stack in systems:
                bottom = plot_one_system(ax, x, stack, sys_label, split=split)
                if is_secondary:
                    secondary_heights.append(bottom)
                else:
                    primary_heights.append(bottom)
                x += width + width / 6
            last_bar_x = x - (width + width / 6)

            x_coords.append(x - len(systems) * (width + width / 6) + 1.5 * width)
            x_labels.append(label)
            lang_spans.append((workload.split("_")[0], first_bar_x, last_bar_x))
            x += width * 2

        x_labels = [x.replace("_", " ").replace("s3", "") for x in x_labels]
        ax.set_xticks(x_coords, x_labels, rotation=0, ha="center")

    ax3.legend(loc="upper left", ncol=7, bbox_to_anchor=(0, 1), frameon=False)
    split_y = 60
    primary_top = max(primary_heights, default=1) * 1.25
    ax3.set_ylim((split_y, primary_top))
    ax1.set_ylim((0, split_y))
    if secondary_heights:
        ax2.set_ylim((0, max(secondary_heights) * 1.15))
    ax1.set_ylabel("Time (ms)")
    ax1.tick_params(axis="x", which="both", length=0)
    ax2.tick_params(axis="x", which="both", length=0)
    ax3.tick_params(axis="x", which="both", length=0)

    for a in annotations:
        if a.get_position()[1] < split_y:
            ax1.text(
                a._x,
                a._y,
                a.get_text(),
                ha="center",
                va="bottom",
                fontsize=10,
                rotation=45,
            )
            a.remove()

    d_marker = 0.5
    kwargs = dict(
        marker=[(-1, -d_marker), (1, d_marker)],
        markersize=12,
        linestyle="none",
        color="k",
        mec="k",
        mew=1,
        clip_on=False,
    )
    ax3.plot([0, 1], [0, 0], transform=ax3.transAxes, **kwargs)
    ax1.plot([0, 1], [1, 1], transform=ax1.transAxes, **kwargs)

    draw_lang_brackets(
        ax1, primary_lang_spans, line_y=-0.18, label_y=-0.29, width=width
    )
    draw_lang_brackets(
        ax2, secondary_lang_spans, line_y=-0.11, label_y=-0.17, width=width, lw=1.2
    )

    fig.subplots_adjust(hspace=0.05, wspace=0.1, bottom=0.22, right=0.99, top=0.99)

    out_path = os.path.join(result_dir, "latency.pdf")
    plt.savefig(out_path, transparent=True)
    print(f"wrote {out_path}")

    with open(os.path.join(result_dir, "e2e.json"), "w") as f:
        json.dump(data_copy, f, indent=4)

    for fn, vals in data_copy.items():
        if vals["faasnap"] and vals["spice"]:
            speedup = 100.0 * (vals["faasnap"] - vals["spice"]) / vals["faasnap"]
            print(f"{fn}: spice {speedup:.1f}% faster than faasnap")


def main():
    parser = argparse.ArgumentParser(description="Plot e2e latency")
    parser.add_argument("dirs", nargs="+", help="result directories to plot")
    parser.add_argument(
        "--spice-log",
        default="restore_images",
        help="prefix of spice restore log files inside each result dir",
    )
    parser.add_argument(
        "--faasnap-subdir",
        default=".",
        help="subdirectory under each result dir holding faasnap/reap runs",
    )
    parser.add_argument(
        "--criu-subdir",
        default=".",
        help="subdirectory under each result dir holding CRIU runs",
    )
    args = parser.parse_args()

    for d in args.dirs:
        data = {
            "spice": parse_blink_logs(d, log_name=args.spice_log),
            "faasnap": parse_faasnap_logs(os.path.join(d, args.faasnap_subdir)),
            "criu": parse_criu_logs(os.path.join(d, args.criu_subdir)),
        }
        plot_comparison(d, data)


if __name__ == "__main__":
    main()
