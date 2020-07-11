#!/usr/bin/env python
import argparse
from decimal import Decimal

from nosilence import detect_silence_intervals, execute, save_intervals, video_length, ZERO


# TODO: configure better logging


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video-filename")
    parser.add_argument("csv-filename")
    parser.add_argument(
        "--silence-threshold",
        type=Decimal,
        default=Decimal("-30"),
        help="minimum volume level to accept as non-silence, in dB",
    )
    parser.add_argument(
        "--minimum-silence-duration",
        type=Decimal,
        default=Decimal("0.3"),
        help="Minimum duration for each silence interval detection, in seconds",
    )
    args = parser.parse_args()
    video_filename = getattr(args, "video-filename")
    csv_filename = getattr(args, "csv-filename")

    total_length = video_length(video_filename)
    print(f"Total video length: {total_length}")

    print("Detecting silence intervals...", end="", flush=True)
    silence_intervals = detect_silence_intervals(
        filename=video_filename, noise_level=args.silence_threshold, minimum_duration=args.minimum_silence_duration
    )
    print(" done.", flush=True)
    # Add borders to silence intervals so non-silence algorithm will not miss
    # first and last intervals.
    if silence_intervals[0]["start"] > 0:
        data = {"start": ZERO, "end": ZERO, "duration": ZERO}
        silence_intervals.insert(0, data)
    if silence_intervals[-1]["end"] < total_length:
        data = {"start": total_length, "end": total_length, "duration": ZERO}
        silence_intervals.append(data)
    save_intervals(silence_intervals, csv_filename)


if __name__ == "__main__":
    main()
