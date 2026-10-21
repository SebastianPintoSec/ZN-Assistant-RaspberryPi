#!/usr/bin/env python3
"""ZN Assistant: prototipo local de texto sin servicios externos ni costos de API.

No utiliza modelos de lenguaje: reconoce un conjunto acotado de intenciones.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime


def normalize(message: str) -> str:
    text = unicodedata.normalize("NFKD", message.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def reply(message: str) -> str:
    """Resuelve intenciones permitidas; no ejecuta comandos ni controla equipos."""
    normalized = normalize(message)
    if not normalized:
        return "Escribe una consulta o 'ayuda' para conocer los comandos."
    words = set(normalized.split())
    if "ayuda" in words or "comandos" in words:
        return ("Puedo saludar, decir la hora local, indicar el estado del "
                "prototipo y cerrar la sesión. Prueba: 'hola', 'qué hora es', "
                "'estado', 'salir'.")
    if "hora" in words:
        return f"La hora local del sistema es {datetime.now().strftime('%H:%M')}."
    if "estado" in words or "diagnostico" in words:
        return ("ZN Assistant está ejecutándose en modo local por texto, "
                "sin IA generativa, micrófono ni control domótico.")
    if "gracias" in words:
        return "De nada. ¿Necesitas algo más?"
    if words.intersection({"hola", "buenas", "saludos"}):
        return "Hola. Soy ZN Assistant en modo local. Escribe 'ayuda' para comenzar."
    return ("Todavía no sé responder esa consulta en modo local. "
            "Escribe 'ayuda' para ver lo que sí puedo hacer.")


def main() -> None:
    print("ZN Assistant | MODO LOCAL | sin uso de API")
    print("Escribe 'ayuda' o 'salir'.")
    while True:
        try:
            user_input = input("\nTú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nZN Assistant > Sesión cerrada.")
            return
        if normalize(user_input) in {"salir", "exit", "quit"}:
            print("ZN Assistant > Hasta luego.")
            return
        if len(user_input) > 1200:
            print("ZN Assistant > Consulta demasiado larga (máximo 1200 caracteres).")
            continue
        print(f"ZN Assistant > {reply(user_input)}")


if __name__ == "__main__":
    main()
