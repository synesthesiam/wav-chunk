#!/usr/bin/env python3
"""Command-line interface to wavchunk"""
import argparse
import io
import os
import sys

import wavchunk

# -----------------------------------------------------------------------------


def main():
    """Main entry point"""
    args = get_args()

    # Dispatch to sub-command
    args.func(args)


# -----------------------------------------------------------------------------


def do_add(args):
    """Add chunk to WAV file"""
    in_file = sys.stdin.buffer
    out_file = sys.stdout.buffer
    data_file = None

    if args.data_file:
        # --data is a file path
        if args.data == "-":
            # Read data from stdin
            assert args.input, "Must specify --input if --data is stdin"
            data_file = sys.stdin.buffer

            if os.isatty(sys.stdin.fileno()):
                print("Reading data from stdin...", file=sys.stderr)
        else:
            # Read data from a file
            data_file = open(args.data, "rb")
    else:
        # Read data from argument
        data_file = io.BytesIO(args.data.encode())

    # Load chunk data
    chunk_data = data_file.read()

    if args.input:
        # Read WAV from file
        in_file = open(args.input, "rb")
    else:
        # Read WAV from stdin
        if os.isatty(sys.stdin.fileno()):
            print("Reading WAV from stdin...", file=sys.stderr)

    wavchunk.add_chunk(in_file, chunk_data, chunk_name=args.name, out_file=out_file)


# -----------------------------------------------------------------------------


def do_get(args):
    """Get chunk from WAV file"""
    in_file = sys.stdin.buffer
    out_file = sys.stdout.buffer
    data_file = None
    keep_chunk = True

    if args.delete:
        keep_chunk = False

    if args.data == "-":
        # Write data to stdout
        data_file = sys.stdout.buffer

        if not args.output:
            # No WAV output
            out_file = None
    elif args.data:
        # Write data to file
        data_file = open(args.data, "wb")

    if args.input:
        # Read WAV from stdin
        in_file = open(args.input, "rb")
    else:
        # Read WAV from a file
        if os.isatty(sys.stdin.fileno()):
            print("Reading WAV from stdin...", file=sys.stderr)

    if args.output:
        # Write WAV to stdout
        out_file = open(args.output, "wb")

    chunk_data = wavchunk.get_chunk(
        in_file, chunk_name=args.name, out_file=out_file, keep_chunk=keep_chunk
    )

    if chunk_data and data_file:
        data_file.write(chunk_data)


# -----------------------------------------------------------------------------


def get_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(prog="wavchunk")

    # Create subparsers for each sub-command
    sub_parsers = parser.add_subparsers()
    sub_parsers.required = True
    sub_parsers.dest = "command"

    # ---
    # add
    # ---
    add_parser = sub_parsers.add_parser("add", help="Add chunk to WAV file")
    add_parser.add_argument(
        "-d", "--data", required=True, help="Chunk data to add ('-' for stdin)"
    )
    add_parser.add_argument(
        "-i", "--input", help="Path to input WAV file (default: stdin)"
    )
    add_parser.add_argument(
        "--data-file", action="store_true", help="Argument to --data is a file"
    )
    add_parser.add_argument(
        "--name", default="INFO", help="Name of chunk to add (default: INFO)"
    )
    add_parser.set_defaults(func=do_add)

    # ---
    # get
    # ---
    get_parser = sub_parsers.add_parser("get", help="Get chunk data from WAV file")
    get_parser.add_argument(
        "-i", "--input", help="Path to input WAV file (default: stdin)"
    )
    get_parser.add_argument(
        "-d", "--data", help="Path to write chunk data ('-' for stdout)"
    )
    get_parser.add_argument(
        "-o", "--output", help="Path to write WAV data (default: stdout)"
    )
    get_parser.add_argument(
        "--delete", action="store_true", help="Remove chunk from WAV data"
    )
    get_parser.add_argument(
        "--name", default="INFO", help="Name of chunk to get (default: INFO)"
    )
    get_parser.set_defaults(func=do_get)

    return parser.parse_args()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
