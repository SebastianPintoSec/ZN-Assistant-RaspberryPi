"""Piper TTS persistente: carga una vez y reproduce respuestas mediante ALSA.

Sin acceso de red, sin shell ni nuevas conexiones entrantes.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from jarvis_tts import AudioError


class PiperSpeaker:
    def __init__(self, model: str, device: str = "plughw:0,0"):
        if not shutil.which("aplay"):
            raise AudioError("No se encuentra aplay (alsa-utils).")
        path = Path(model).expanduser()
        if not path.is_file() or not Path(str(path) + ".json").is_file():
            raise AudioError(f"Falta el modelo ONNX o su configuración: {path}")
        try:
            from piper import PiperVoice
            self.voice = PiperVoice.load(str(path))
        except (ImportError, OSError, ValueError, RuntimeError) as exc:
            raise AudioError(f"No se pudo cargar Piper: {exc}") from exc
        self.device = device

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        if len(text) > 1000:
            raise AudioError("Respuesta demasiado larga para sintetizar.")
        with tempfile.TemporaryDirectory(prefix="jarvis-piper-") as directory:
            wav_file = str(Path(directory) / "respuesta.wav")
            try:
                with wave.open(wav_file, "wb") as output:
                    self.voice.synthesize_wav(text, output)
                subprocess.run(
                    ["aplay", "-q", "-D", self.device, wav_file],
                    check=True, capture_output=True, timeout=60,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                    OSError, RuntimeError, ValueError, wave.Error) as exc:
                raise AudioError(f"Error de síntesis/reproducción Piper: {exc}") from exc
