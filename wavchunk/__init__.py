"""Utility methods for interacting with RIFF WAVE file chunks"""
import io
import shutil
import struct
import typing
from enum import Enum

# -----------------------------------------------------------------------------


class Names(str, Enum):
    """Chunk names in RIFF WAVE"""

    RIFF = "RIFF"
    WAVE = "WAVE"
    FMT = "fmt "
    INFO = "INFO"


# -----------------------------------------------------------------------------


def read_name(file: typing.IO[bytes]) -> str:
    """Read a 4 byte name from a RIFF file"""
    return file.read(4).decode()


def write_name(file: typing.IO[bytes], name: str):
    """Write a 4 byte name from a RIFF file"""
    while len(name) < 4:
        name += " "

    if len(name) > 4:
        raise ValueError(f"'{name}' must be exactly 4 characters long")

    file.write(name.encode())


def read_size(file: typing.IO[bytes]) -> int:
    """Read a 4 byte size from a RIFF file"""
    return struct.unpack_from("<L", file.read(4))[0]


def write_size(file: typing.IO[bytes], size: int):
    """Write a 4 byte size to a RIFF file"""
    file.write(struct.pack("<L", size))


def read_after_format(
    file: typing.IO[bytes], out_file: typing.Optional[typing.IO[bytes]] = None
):
    """
    Read until file is right after data chunk.

    Optionally copy data to output file.
    """
    # Copy RIFF header
    riff = read_name(file)
    assert riff == Names.RIFF, f"Expected {Names.RIFF}, got {riff}"
    riff_size = read_size(file)

    if out_file:
        write_name(out_file, riff)
        write_size(out_file, riff_size)

    # Copy WAVE header
    wave = read_name(file)
    assert wave == Names.WAVE, f"Expected {Names.WAVE}, got {wave}"

    if out_file:
        write_name(out_file, wave)

    # Format chunk
    fmt = read_name(file)
    assert fmt == Names.FMT, f"Expected '{Names.FMT}', got {fmt}"
    fmt_size = read_size(file)

    # Skip format chunk
    fmt_bytes = file.read(fmt_size)

    if out_file:
        write_name(out_file, fmt)
        write_size(out_file, fmt_size)
        out_file.write(fmt_bytes)


def read_after_data(
    file: typing.IO[bytes], out_file: typing.Optional[typing.IO[bytes]] = None
):
    """
    Read until file is right after data chunk.

    Optionally copy data to an output file.
    """
    # Skip until after format chunk
    read_after_format(file, out_file=out_file)

    # Skip chunks until after data
    last_name = ""

    while last_name != "data":
        chunk_name = read_name(file)
        chunk_size = read_size(file)
        chunk_bytes = file.read(chunk_size)

        if out_file:
            write_name(out_file, chunk_name)
            write_size(out_file, chunk_size)
            out_file.write(chunk_bytes)

        last_name = chunk_name


def add_chunk(
    wav_file: typing.IO[bytes],
    chunk_data: bytes,
    chunk_name: str = Names.INFO,
    out_file: typing.Optional[typing.IO[bytes]] = None,
) -> typing.Optional[bytes]:
    """
    Add new chunk after data (INFO by default).

    Optionally copy data to an output file.
    """
    if out_file:
        return_value = False
    else:
        out_file = io.BytesIO()
        return_value = True

    # Skip until after data
    read_after_data(wav_file, out_file=out_file)

    # Add new chunk
    write_name(out_file, chunk_name)
    write_size(out_file, len(chunk_data))
    out_file.write(chunk_data)

    # Copy remainder of input file
    shutil.copyfileobj(wav_file, out_file)

    if return_value:
        assert isinstance(out_file, io.BytesIO)
        return out_file.getvalue()

    return None


def get_chunk(
    wav_file: typing.IO[bytes],
    out_file: typing.Optional[typing.IO[bytes]] = None,
    chunk_name: str = Names.INFO,
    keep_chunk: bool = True,
) -> typing.Optional[bytes]:
    """
    Find a chunk and return data from it (default: INFO).


    Optionally copy data to an output file.
    Set keep_chunk = False to delete chunk.
    """
    return_data = None

    # Skip until after format chunk
    read_after_format(wav_file, out_file=out_file)

    # Read chunks until INFO is found
    current_name = read_name(wav_file)
    while current_name:
        chunk_size = read_size(wav_file)
        chunk_bytes = wav_file.read(chunk_size)

        if current_name == chunk_name:
            return_data = chunk_bytes
            if out_file and keep_chunk:
                # Copy chunk to output
                write_name(out_file, current_name)
                write_size(out_file, chunk_size)
                out_file.write(chunk_bytes)
                break
        elif out_file:
            # Copy chunk to output
            write_name(out_file, current_name)
            write_size(out_file, chunk_size)
            out_file.write(chunk_bytes)

        # Next chunk
        current_name = read_name(wav_file)

    if out_file:
        # Copy remainder of input file
        shutil.copyfileobj(wav_file, out_file)

    return return_data
