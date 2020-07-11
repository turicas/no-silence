#!/usr/bin/env python

import argparse
import os
import pathlib
import tempfile
from decimal import Decimal

from rows.plugins.utils import ipartition

from nosilence import execute, extract_non_silence_from_silence, load_intervals, optimize_intervals, save_intervals


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video-filename")
    parser.add_argument("silence-filename")
    parser.add_argument(
        "--excess-duration",
        type=Decimal,
        default=Decimal("0.1"),
        help="Time to add before and after each cut interval, in seconds",
    )
    parser.add_argument(
        "--minimum-interval-gap",
        type=Decimal,
        default=Decimal("0.2"),
        help="If less than this, will merge intervals, in seconds",
    )
    parser.add_argument("--batch-size", type=int, default=15, help="Number of slices to generate per ffmpeg run")
    parser.add_argument(
        "--non-silence-filename",
        type=str,
        default="",
        help="If provided save generated silence intervals (non optimized)",
    )
    parser.add_argument(
        "--non-silence-optimized-filename",
        type=str,
        default="",
        help="If provided save generated silence intervals (optimized)",
    )
    args = parser.parse_args()
    video_filename = getattr(args, "video-filename")
    silence_filename = getattr(args, "silence-filename")

    print("Loading silence intervals...", end="", flush=True)
    silence_intervals = load_intervals(silence_filename)
    print(" done.", flush=True)

    print("Calculating non-silence intervals...", end="", flush=True)
    non_silence_intervals = extract_non_silence_from_silence(silence_intervals, threshold=args.excess_duration)
    print(" done.", flush=True)
    if args.non_silence_filename:
        save_intervals(non_silence_intervals, args.non_silence_filename)

    print("Optimizing non-silence intervals...", end="", flush=True)
    old = non_silence_intervals
    new = None
    while new != old:
        new = optimize_intervals(intervals=old, minimum_gap=args.minimum_interval_gap)
        old = new
    non_silence_intervals = [interval for interval in new if interval["end"] - interval["start"] > 0]
    print(" done.", flush=True)
    if args.non_silence_optimized_filename:
        save_intervals(non_silence_intervals, args.non_silence_optimized_filename)

    print("Splitting video...", end="", flush=True)
    parts = []
    temporary_filename = tempfile.NamedTemporaryFile(delete=False).name
    interval_batches = ipartition(non_silence_intervals, args.batch_size)
    splitnames = []
    # TODO: check why some files are empty
    counter = 1
    for intervals in interval_batches:
        commands = []
        for interval in intervals:
            start = interval["start"]
            end = interval["end"]
            splitname = f"{temporary_filename}-{counter:05d}.mp4"
            splitnames.append(splitname)
            cmd = f' -i "{video_filename}" -ss {start} -to {end} "{splitname}"'
            commands.append(cmd)
            counter += 1
        command = f'ffmpeg {" ".join(commands)}'
        execute(command)
    print(" done.")

    print("Merging video parts...", end="", flush=True)
    with open(temporary_filename, mode="w", encoding="utf8") as fobj:
        for splitname in splitnames:
            fobj.write(f"file '{splitname}'\n")
    original = pathlib.Path(video_filename)
    output = original.parent / original.name.replace(".mp4", "-nosilence.mp4")
    cmd = f'ffmpeg -safe 0 -f concat -i "{temporary_filename}" "{output}"'
    stdout, stderr = execute(cmd)
    log_filename = temporary_filename + ".log"
    with open(log_filename, mode="wb") as fobj:
        fobj.write(b"stdout:\n")
        fobj.write(stdout)
        fobj.write(b"\n\n---\n\nstderr:\n")
        fobj.write(stderr)
    print(" done.")
    if b"Input/output error" in stderr:
        print(f"ERROR merging files. See details on {log_filename}")

    # TODO: remove temporary files


if __name__ == "__main__":
    main()
