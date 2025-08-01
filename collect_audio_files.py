#!/usr/bin/env python

import argparse
import json
import subprocess
import logging
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "playlist",
    type=str,
    help="Path to playlist file",
)
parser.add_argument(
    "dir",
    type=str,
    nargs="+",
    help="Paths to directories containing audio files",
)
parser.add_argument(
    "--output-dir",
    type=str,
    default="output",
    help="Path to output directory",
)


def ensure_ffmpeg_present():
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            logging.error("ffmpeg version check failed")
            sys.exit(1)
    except FileNotFoundError:
        logging.error("ffmpeg not found")
        sys.exit(1)


def get_output_name(item):
    output_name_components = [f"{index + 1:02}"]

    if (title := item["content"]["title"]) != "":
        output_name_components.append(title)

    if (artist := item["content"]["artist"]) != "":
        output_name_components.append(artist)

    name = " - ".join(output_name_components)
    return f"{name}.mp3"


def process_file(index, item, input_path, output_dir):
    args = ["ffmpeg"]

    args += ["-i", input_path]

    # set bitrate to 256 kbps
    args += ["-b:a", "256k"]

    # add metadata
    if (title := item["content"]["title"]) != "":
        args += ["-metadata", f"title={title}"]

    if (artist := item["content"]["artist"]) != "":
        args += ["-metadata", f"artist={artist}"]

    output_name = get_output_name(item)
    output_path = os.path.join(output_dir, output_name)
    args.append(output_path)

    result = subprocess.run(args)
    if result.returncode != 0:
        logging.error(f"ffmpeg failed on file '{input_path}'")
        sys.exit(1)


if __name__ == "__main__":
    args = parser.parse_args()

    ensure_ffmpeg_present()

    # parse playlist
    with open(args.playlist) as f:
        playlist = json.load(f)

    if "items" not in playlist:
        logging.error("Invalid playlist format")
        sys.exit(1)

    # scan directories
    dir_contents = {}
    for dir_path in args.dir:
        dir_contents[dir_path] = os.listdir(dir_path)

    # find audio files in directories
    items = []
    for item in playlist["items"]:
        if not "content" in item:
            continue # air break

        content = item["content"]
        if not "file" in content["attributes"]:
            continue # no audio file linked

        file_name = content["attributes"]["file"]

        for dir_path, contents in dir_contents.items():
            if file_name in contents:
                input_path = os.path.join(dir_path, file_name)
                break
        else:
            logging.error(f"Could not find file '{file_name}' in any directory")
            sys.exit(1)

        items.append((item, input_path))

    # process
    os.makedirs(args.output_dir, exist_ok=True)
    for index, (item, input_path) in enumerate(items):
        process_file(index, item, input_path, args.output_dir)
