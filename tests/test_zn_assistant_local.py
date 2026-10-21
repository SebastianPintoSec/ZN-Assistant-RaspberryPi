"""Pruebas de regresión sin conexión a Internet y sin claves API."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from zn_assistant_local import normalize, reply


class LocalAssistantTests(unittest.TestCase):
    def test_normalizacion(self):
        self.assertEqual(normalize("¡QUÉ HORA es?"), "que hora es")

    def test_saludo(self):
        self.assertIn("Hola", reply("¡Hola, ZN!"))

    def test_ayuda(self):
        self.assertIn("estado", reply("ayuda"))

    def test_estado(self):
        self.assertIn("modo local", reply("¿Cuál es el estado?"))

    def test_no_ejecuta_acciones(self):
        self.assertIn("Todavía no sé", reply("enciende las luces"))

    @patch("zn_assistant_local.weather_santiago", return_value="Clima simulado")
    def test_clima_despacha_sin_red(self, fake_weather):
        self.assertEqual(reply("¿y cómo está el tiempo?"), "Clima simulado")
        fake_weather.assert_called_once()

    @patch("zn_assistant_local.urlopen", side_effect=TimeoutError)
    def test_clima_falla_con_gracia(self, fake_urlopen):
        from zn_assistant_local import weather_santiago
        self.assertIn("No pude consultar", weather_santiago())
        fake_urlopen.assert_called_once()

    def test_vacio(self):
        self.assertIn("Escribe", reply("   "))


if __name__ == "__main__":
    unittest.main()
