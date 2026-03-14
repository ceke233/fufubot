"""Bridge script for isolated TTS/ASR execution in separate conda environment."""

import json
import sys


def tts_synthesize():
    """TTS synthesis in isolated environment."""
    from qwen_tts.inference.qwen3_tts_model import Qwen3TTSModel
    import soundfile as sf
    import io

    # Read params from stdin
    params = json.loads(sys.stdin.read())

    # Load model
    model = Qwen3TTSModel.from_pretrained(
        params["model_path"],
        device_map=params.get("device", "cuda")
    )

    # Generate - auto-detect model type
    model_type = getattr(model.model, 'tts_model_type', 'base')
    language = params.get("language") if params.get("language") != "Auto" else None

    if model_type == "custom_voice":
        wavs, sr = model.generate_custom_voice(
            text=params["text"],
            language=language,
            speaker=params.get("voice", "Vivian"),
            instruct=params.get("instruct", "温柔甜美的女声")
        )
    elif model_type == "voice_design":
        wavs, sr = model.generate_voice_design(
            text=params["text"],
            language=language,
            instruct=params.get("instruct", "温柔甜美的女声")
        )
    else:
        # base model - requires ref_audio
        wavs, sr = model.generate_voice_clone(
            text=params["text"],
            language=language
        )

    # Convert to bytes
    buffer = io.BytesIO()
    sf.write(buffer, wavs[0], sr, format="WAV")

    # Output result
    result = {
        "audio_base64": buffer.getvalue().hex(),
        "sample_rate": sr
    }
    print(json.dumps(result))


def asr_transcribe():
    """ASR transcription in isolated environment."""
    from qwen_asr.inference.qwen3_asr import Qwen3ASRModel

    # Read params from stdin
    params = json.loads(sys.stdin.read())

    # Load model
    model = Qwen3ASRModel.from_pretrained(
        params["model_path"],
        device_map=params.get("device", "cuda")
    )

    # Transcribe
    results = model.transcribe(
        audio=params["audio"],
        language=params.get("language")
    )

    # Output result
    result = {
        "text": results[0].text if results else ""
    }
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bridge.py [tts|asr]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "tts":
        tts_synthesize()
    elif mode == "asr":
        asr_transcribe()
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
