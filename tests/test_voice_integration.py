#!/usr/bin/env python
"""Simple integration test for voice providers."""

import asyncio
import sys
from pathlib import Path


async def test_tts():
    """Test TTS synthesis."""
    print("=" * 60)
    print("Testing TTS (Text-to-Speech)...")
    print("=" * 60)

    from nanobot.voice.tts.qwen import QwenTTSProvider

    provider = QwenTTSProvider(
        python_path="/home/ceke233/miniconda3/envs/qwen3-asr-tts/bin/python",
        device="cpu"
    )

    print(f"✓ Provider initialized")
    print(f"  Model: {provider.model_path}")
    print(f"  Device: {provider.device}")

    print("\nSynthesizing speech...")
    test_text = "你好世界"
    audio_bytes, sample_rate = await provider.synthesize(
        text=test_text,
        language="Chinese"
    )

    print(f"✓ Synthesis complete")
    print(f"  Audio size: {len(audio_bytes)} bytes")
    print(f"  Sample rate: {sample_rate} Hz")

    # Save to file
    output_file = Path("test_tts_output.wav")
    output_file.write_bytes(audio_bytes)
    print(f"✓ Saved to: {output_file}")

    return output_file


async def test_asr(audio_file: Path):
    """Test ASR transcription."""
    print("\n" + "=" * 60)
    print("Testing ASR (Speech-to-Text)...")
    print("=" * 60)

    from nanobot.voice.asr.qwen import QwenASRProvider

    provider = QwenASRProvider(
        python_path="/home/ceke233/miniconda3/envs/qwen3-asr-tts/bin/python",
        device="cpu"
    )

    print(f"✓ Provider initialized")
    print(f"  Model: {provider.model_path}")
    print(f"  Device: {provider.device}")

    print(f"\nTranscribing audio: {audio_file}")
    transcribed_text = await provider.transcribe(
        audio=str(audio_file),
        language="Chinese"
    )

    print(f"✓ Transcription complete")
    print(f"  Result: {transcribed_text}")

    return transcribed_text


async def main():
    """Run integration tests."""
    try:
        # Test TTS
        audio_file = await test_tts()

        # Test ASR
        transcribed = await test_asr(audio_file)

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
