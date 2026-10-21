#!/usr/bin/env python3
"""Jarvis: prototipo local de texto sin servicios externos ni costos de API.

No utiliza modelos de lenguaje: reconoce un conjunto acotado de intenciones.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from datetime import datetime
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from jarvis_tts import speak, AudioError
from jarvis_piper import PiperSpeaker


def normalize(message: str) -> str:
    text = unicodedata.normalize("NFKD", message.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


# Coordenadas aproximadas del centro de Santiago; no representan la ubicación del usuario.
CITY = "Santiago"
WEATHER_LAT = -33.45
WEATHER_LON = -70.66
WEATHER_CODES = {
    0: "despejado", 1: "principalmente despejado",
    2: "parcialmente nublado", 3: "nublado",
    45: "con niebla", 48: "con niebla escarchada",
    51: "con llovizna ligera", 53: "con llovizna",
    55: "con llovizna intensa", 61: "con lluvia ligera",
    63: "con lluvia", 65: "con lluvia intensa",
    71: "con nieve ligera", 73: "con nieve", 75: "con nieve intensa",
    80: "con chubascos ligeros", 81: "con chubascos",
    82: "con chubascos intensos", 95: "con tormenta",
    96: "con tormenta y granizo", 99: "con tormenta y granizo intenso",
}


def weather_santiago() -> str:
    """Consulta el pronóstico actual (modelo) sin API key; nunca ejecuta órdenes."""
    params = urlencode({
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
        "timezone": "America/Santiago",
        "forecast_days": 1,
    })
    url = "https://api.open-meteo.com/v1/forecast?" + params
    try:
        with urlopen(url, timeout=8) as result:
            payload = json.load(result)
        data = payload["current"]
        temperature = float(data["temperature_2m"])
        humidity = int(data["relative_humidity_2m"])
        precipitation = float(data["precipitation"])
        condition = WEATHER_CODES.get(int(data["weather_code"]), "condiciones variables")
        timestamp = data.get("time", "sin hora")
        return (f"Según Open-Meteo, en {CITY} ({timestamp}, hora local) "
                f"hay {temperature:.1f} °C, cielo {condition}, "
                f"humedad de {humidity}% y precipitación {precipitation:.1f} mm "
                "en el intervalo reciente. Es una estimación meteorológica.")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
        return "No pude consultar el tiempo ahora. Comprueba Internet e inténtalo nuevamente."


def reply(message: str) -> str:
    """Resuelve intenciones permitidas; no ejecuta comandos ni controla equipos."""
    normalized = normalize(message)
    if not normalized:
        return "Escribe una consulta o 'ayuda' para conocer los comandos."
    words = set(normalized.split())
    if "ayuda" in words or "comandos" in words:
        return ("Puedo saludar, decir la hora local, indicar el estado del "
                "prototipo, consultar el clima en Santiago y cerrar la sesión. "
                "Prueba: 'hola', 'qué hora es', 'cómo está el tiempo', 'estado', 'salir'.")
    if words.intersection({"tiempo", "clima", "temperatura", "meteorologico"}):
        return weather_santiago()
    if "hora" in words:
        return f"La hora local del sistema es {datetime.now().strftime('%H:%M')}."
    if "estado" in words or "diagnostico" in words:
        return ("Jarvis está ejecutándose en modo local por texto, "
                "sin IA generativa, micrófono ni control domótico.")
    if "gracias" in words:
        return "De nada. ¿Necesitas algo más?"
    if words.intersection({"hola", "buenas", "saludos"}):
        return "Hola. Soy Jarvis en modo local. Escribe 'ayuda' para comenzar."
    return ("Todavía no sé responder esa consulta en modo local. "
            "Escribe 'ayuda' para ver lo que sí puedo hacer.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis: asistente local por terminal")
    parser.add_argument("--voice", action="store_true",
                        help="Leer las respuestas mediante el motor TTS seleccionado")
    parser.add_argument("--audio-device", default="plughw:0,0",
                        help="Dispositivo ALSA (predeterminado: plughw:0,0)")
    parser.add_argument("--tts", choices=("espeak", "piper"), default="espeak",
                        help="Motor de voz (predeterminado: espeak)")
    parser.add_argument("--piper-model",
                        default="models/piper/es_MX-ald-medium.onnx",
                        help="Ruta al modelo Piper ONNX")
    args = parser.parse_args()
    piper_speaker = None
    if args.voice and args.tts == "piper":
        print("Cargando voz Piper (solo al iniciar)...")
        try:
            piper_speaker = PiperSpeaker(args.piper_model, device=args.audio_device)
        except AudioError as exc:
            print(f"[Piper no disponible: {exc}; se utilizará eSpeak NG.]")
    print("Jarvis | MODO LOCAL | sin API de IA (clima usa Open-Meteo)")
    print(f"Salida hablada: {'activada' if args.voice else 'desactivada'}")
    print("Escribe 'ayuda' o 'salir'.")
    while True:
        try:
            user_input = input("\nTú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJarvis > Sesión cerrada.")
            return
        if normalize(user_input) in {"salir", "exit", "quit"}:
            print("Jarvis > Hasta luego.")
            return
        if len(user_input) > 1200:
            print("Jarvis > Consulta demasiado larga (máximo 1200 caracteres).")
            continue
        response = reply(user_input)
        print(f"Jarvis > {response}")
        if args.voice:
            try:
                if piper_speaker is not None:
                    try:
                        piper_speaker.speak(response)
                    except AudioError as exc:
                        print(f"[Piper falló: {exc}; probando eSpeak NG.]")
                        speak(response, device=args.audio_device)
                else:
                    speak(response, device=args.audio_device)
            except AudioError as exc:
                print(f"[Audio no disponible: {exc}; el modo texto continúa.]")


if __name__ == "__main__":
    main()
