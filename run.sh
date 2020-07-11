#!/bin/bash

VIDEO_FILENAME=$1
SILENCE_FILENAME="$VIDEO_FILENAME-silence.csv"
NON_SILENCE_FILENAME="$VIDEO_FILENAME-non-silence.csv"
NON_SILENCE_OPTIMIZED_FILENAME="$VIDEO_FILENAME-non-silence-optimized.csv"
SILENCE_THRESHOLD=-35
MIN_SILENCE_DURATION=0.5
EXCESS_DURATION=0.0
MIN_INTERVAL_GAP=0.25
BATCH_SIZE=20

if [ ! -e "$VIDEO_FILENAME" ]; then
	echo 'ERROR: must provide a video filename.'
	exit 1
fi

time ./detect.py \
	--silence-threshold=$SILENCE_THRESHOLD \
	--minimum-silence-duration=$MIN_SILENCE_DURATION \
	"$VIDEO_FILENAME" "$SILENCE_FILENAME"

time ./extract.py \
	--excess-duration=$EXCESS_DURATION \
	--minimum-interval-gap=$MIN_INTERVAL_GAP \
	--non-silence-filename="$NON_SILENCE_FILENAME" \
	--non-silence-optimized-filename="$NON_SILENCE_OPTIMIZED_FILENAME" \
	--batch-size=$BATCH_SIZE \
	"$VIDEO_FILENAME" "$SILENCE_FILENAME"
