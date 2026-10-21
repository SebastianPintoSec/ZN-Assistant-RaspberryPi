"""Pruebas de TTS sin reproducir audio físico."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from jarvis_tts import speak, AudioError


class TTSTests(unittest.TestCase):
    @patch("jarvis_tts.subprocess.run")
    @patch("jarvis_tts.shutil.which", return_value="/usr/bin/fake")
    def test_sintesis_y_reproduccion(self, mock_which, mock_run):
        speak("Hola, soy Jarvis")
        self.assertEqual(mock_run.call_count, 2)
        gen = mock_run.call_args_list[0].args[0]
        play = mock_run.call_args_list[1].args[0]
        self.assertEqual(gen[0], "espeak-ng")
        self.assertEqual(play[0], "aplay")
        self.assertEqual(play[3], "plughw:0,0")
        self.assertEqual(gen[-1], "Hola, soy Jarvis")

    @patch("jarvis_tts.subprocess.run")
    def test_texto_vacio(self, mock_run):
        speak(" ")
        mock_run.assert_not_called()

    def test_texto_excesivo(self):
        with self.assertRaises(AudioError):
            speak("a" * 1001)

    @patch("jarvis_tts.shutil.which", return_value=None)
    def test_dependencia_ausente(self, mock_which):
        with self.assertRaisesRegex(AudioError, "Falta"):
            speak("Hola")


if __name__ == "__main__":
    unittest.main()
