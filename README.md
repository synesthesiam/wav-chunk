# wav-chunk

Read or write INFO chunks from a [RIFF WAV](https://en.wikipedia.org/wiki/WAV) file.

## Dependencies

* Python 3.6 or higher

## Usage

By default, `wavchunk` adds or gets INFO chunk bytes after the WAV `data` chunk.

### Add INFO chunk

```python
import wavchunk

with open("infile.wav", "rb") as in_file:
    with open("outfile.wav", "wb") as out_file:
        wavchunk.add_chunk(in_file, "my data".encode(), out_file=out_file)
```

### Get INFO chunk

```python
import wavchunk

with open("infile.wav", "rb") as in_file:
    my_data = wavchunk.get_chunk(in_file).decode()
    print(my_data)
```

## Command-Line Interface

The `wavchunk` module can also be used from the command-line.
By default, WAV data is expected on stdin and is written to stdout so that commands can be chained together in a pipe.

### Add INFO chunk

```sh
$ python3 -m wavchunk add --data 'my data' < infile.wav > outfile.wav
```

### Get INFO chunk

```sh
$ python3 -m wavchunk get --data - < infile.wav
<data from chunk>
```

### Delete INFO chunk

```sh
$ python3 -m wavchunk get --delete --data mydata.bin < infile.wav > outfile.wav
```
