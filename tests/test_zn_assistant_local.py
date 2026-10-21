"""Pruebas de regresión sin conexión a Internet y sin claves API."""
import sys
import unittest
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

    def test_vacio(self):
        self.assertIn("Escribe", reply("   "))


if __name__ == "__main__":
    unittest.main()
