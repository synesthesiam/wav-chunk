#!/usr/bin/env python3
"""Tests for wavchunk"""
import io
import os
import unittest
import wave

import wavchunk


class WavChunkTestCase(unittest.TestCase):
    """Test cases for wavchunk"""

    def test_add_remove_chunk(self):
        """Test adding and removing INFO chunk"""
        # Generate random WAV file with 100 samples
        audio_data = os.urandom(2 * 100)

        with io.BytesIO() as wav_buffer:
            wav_file: wave.Wave_write = wave.open(wav_buffer, mode="wb")
            with wav_file:
                wav_file.setframerate(16000)
                wav_file.setsampwidth(2)
                wav_file.setnchannels(1)
                wav_file.writeframes(audio_data)

            wav_bytes = wav_buffer.getvalue()

        # Random data for INFO
        chunk_data = os.urandom(50)

        with io.BytesIO(wav_bytes) as in_file:
            with io.BytesIO() as out_file:
                wavchunk.add_chunk(in_file, chunk_data, out_file=out_file)
                out_bytes = out_file.getvalue()

        # Verify chunk data
        with io.BytesIO(out_bytes) as chunked_file:
            actual_data = wavchunk.get_chunk(chunked_file)
            self.assertEqual(chunk_data, actual_data)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
