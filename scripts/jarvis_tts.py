"""Síntesis de voz local con eSpeak NG y reproducción ALSA.

Sin comandos de shell interpolados y sin exponer puertos de red.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class AudioError(RuntimeError):
    """Error recuperable de síntesis o reproducción."""


def speak(text: str, device: str = "plughw:0,0") -> None:
    """Genera un WAV temporal, lo reproduce y elimina el archivo."""
    if not text or not text.strip():
        return
    if len(text) > 1000:
        raise AudioError("Respuesta demasiado larga para sintetizar.")
    if not shutil.which("espeak-ng") or not shutil.which("aplay"):
        raise AudioError("Falta espeak-ng o aplay (alsa-utils).")

    with tempfile.TemporaryDirectory(prefix="jarvis-tts-") as directory:
        wav_path = str(Path(directory) / "respuesta.wav")
        try:
            subprocess.run(
                ["espeak-ng", "-v", "es", "-s", "145", "-w", wav_path, text],
                check=True, capture_output=True, timeout=20,
            )
            subprocess.run(
                ["aplay", "-q", "-D", device, wav_path],
                check=True, capture_output=True, timeout=45,
            )
        except subprocess.TimeoutExpired as exc:
            raise AudioError("Se agotó el tiempo de espera del audio.") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.decode("utf-8", errors="replace").strip() if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
            raise AudioError(f"Falló el audio ({exc.returncode}): {detail[:160]}") from exc
        except OSError as exc:
            raise AudioError(f"No se pudo iniciar el programa de audio: {exc}") from exc
