# no silence

Automatically detect and delete silence parts in videos.

This script is experimental and a lot of manual adjustments/tests must be done
to have the best possible results. There are a lot of tasks related to
development to make it easier to use, feel free to create a pull request.

## Installation

Tested on Python 3.8.2.

```shell
pip install -r requirements.txt
```

Also requires `ffmpeg` installed on your system.


## Usage

```shell
./run.sh /path/to/input-video-filename.extension
```

> There are a lot of options you can customise by changing variable values
> inside `run.sh`.


## TO DO
- Use ffmpeg's ebur128 filters
