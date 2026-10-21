#!/usr/bin/env python3
"""Jarvis: prototipo conversacional de texto (sin control físico)."""

import os
import sys
import time

from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    APIStatusError,
)

MODEL = os.getenv("ZN_MODEL", "gpt-4.1-mini")
MAX_OUTPUT_TOKENS = 250
MAX_INPUT_CHARS = 1200
MAX_HISTORY_ITEMS = 6  # tres intercambios previos
SYSTEM_INSTRUCTIONS = (
    "Eres Jarvis, un asistente doméstico conversacional. "
    "Responde en español de Chile, de forma precisa y breve. "
    "No afirmes haber encendido equipos, consultado sensores ni realizado "
    "acciones físicas: este prototipo es únicamente de texto. "
    "Si una consulta depende de información actual, aclara que no tienes "
    "acceso a datos en tiempo real."
)


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: falta OPENAI_API_KEY en el entorno.", file=sys.stderr)
        return 2

    client = OpenAI(timeout=25.0, max_retries=1)
    history: list[dict[str, str]] = []
    total_input = 0
    total_output = 0

    print(f"Jarvis (texto) | modelo: {MODEL}")
    print("Escribe 'salir' para terminar. No introduzcas secretos.")
    while True:
        try:
            user_text = input("\nTú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSesión cerrada.")
            break

        if user_text.lower() in {"salir", "exit", "quit"}:
            break
        if not user_text:
            continue
        if len(user_text) > MAX_INPUT_CHARS:
            print(f"Entrada demasiado larga (máximo {MAX_INPUT_CHARS} caracteres).")
            continue

        messages = history + [{"role": "user", "content": user_text}]
        started = time.monotonic()
        try:
            response = client.responses.create(
                model=MODEL,
                instructions=SYSTEM_INSTRUCTIONS,
                input=messages,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                store=False,
            )
            answer = (response.output_text or "").strip()
            if not answer:
                print("La API respondió sin texto. Intenta otra consulta.")
                continue
        except AuthenticationError:
            print("Autenticación rechazada: revisa la clave API.")
            continue
        except RateLimitError:
            print("Límite de solicitudes o cuota alcanzada; revisa tu cuenta.")
            continue
        except (APIConnectionError, APITimeoutError):
            print("Error de conexión o tiempo de espera.")
            continue
        except BadRequestError as exc:
            print(f"Solicitud rechazada (HTTP {exc.status_code}). Revisa modelo y parámetros.")
            continue
        except APIStatusError as exc:
            print(f"Error de la API (HTTP {exc.status_code}).")
            continue

        usage = response.usage
        if usage:
            total_input += usage.input_tokens
            total_output += usage.output_tokens
        print(f"Jarvis > {answer}")
        print(f"[{time.monotonic()-started:.1f}s | tokens acumulados: {total_input} entrada, {total_output} salida]")
        history = (messages + [{"role": "assistant", "content": answer}])[-MAX_HISTORY_ITEMS:]

    print(f"Totales: {total_input} tokens entrada y {total_output} salida (estimación de consumo por sesión; consulta Usage para facturación).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
