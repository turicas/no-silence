import csv
import shlex
import subprocess
from decimal import Decimal


ZERO = Decimal("0")


def execute(cmd):
    # TODO: check return code
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()  # must be used instead of wait


def save_intervals(intervals, filename):
    with open(filename, encoding="utf8", mode="w") as fobj:
        writer = csv.writer(fobj)
        writer.writerow(["start", "end"])
        for interval in intervals:
            writer.writerow([interval["start"], interval["end"]])


def load_intervals(filename):
    with open(filename, encoding="utf8") as fobj:
        intervals = [{"start": Decimal(row["start"]), "end": Decimal(row["end"])} for row in csv.DictReader(fobj)]
    return intervals


def print_intervals(intervals):
    print("  start,end")
    for interval in intervals:
        start = interval["start"]
        end = interval["end"]
        print(f"  {start:10.5f},{end:10.5f}")


def video_length(filename):
    cmd = f'ffprobe -v quiet -of csv=p=0 -show_entries format=duration "{filename}"'
    stdout, stderr = execute(cmd)
    return Decimal(stdout.decode("utf8").strip())


def detect_silence_intervals(filename, noise_level, minimum_duration):
    command = (
        f'ffmpeg -i "{filename}" '
        f"-af silencedetect=noise={noise_level}dB:d={minimum_duration} "
        f"-f null -"
    )
    stdout, stderr = execute(command)
    result = stderr.decode("utf8")
    intervals = []
    start = None
    end = None
    for line in result.splitlines():
        if "silence_" not in line:
            continue
        data = line.split("silence_")[1].split(": ")
        if data[0] == "start":
            start = Decimal(data[1].strip())
        elif data[0] == "end":
            end = Decimal(data[1].split()[0].strip())
            this_duration = Decimal(line.split("silence_duration:")[1].strip())
            if start < 0:  # TODO: should really force this?
                start = ZERO
                this_duration = end
            row = {"start": start, "end": end, "duration": this_duration}
            intervals.append(row)
            start, end, this_duration = None, None, None

    return intervals


def extract_non_silence_from_silence(silence_intervals, threshold=ZERO):
    extract = []
    pairs = zip(silence_intervals, silence_intervals[1:])
    for index, (silence_1, silence_2) in enumerate(pairs, start=1):
        start = silence_1["end"] - threshold
        if start < 0:
            start = ZERO
        end = silence_2["start"] + threshold
        extract.append({"start": start, "end": end})

    return extract


def optimize_intervals(intervals, minimum_gap):
    finished = False
    while not finished:
        finished = True
        result = []
        last = len(intervals) - 1
        index = 0
        while index <= last:
            interval = intervals[index]
            if index < last:
                next_interval = intervals[index + 1]
                if next_interval["start"] - interval["end"] <= minimum_gap:
                    # merge these two intervals
                    finished = False
                    result.append({"start": interval["start"], "end": next_interval["end"]})
                    index += 1  # jump the next one
                else:
                    result.append(interval)

            else:  # last interval, just append
                result.append(interval)

            index += 1
        intervals = result

    return result
