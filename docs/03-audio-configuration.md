# LAB-03 — Audio y pruebas sin periféricos

**Estado:** inventario validado el 21 de octubre de 2026; prueba física de captura pendiente de hardware.

## Evidencia de la Raspberry Pi 4

El operador ejecutó `lsusb`, `arecord -l` y `aplay -l`.

| Prueba | Resultado |
|---|---|
| USB | Concentradores USB 2.0/3.0 detectados; sin periféricos de audio USB conectados |
| ALSA captura | Ningún dispositivo de captura encontrado |
| ALSA reproducción | `bcm2835 Headphones` (salida analógica), `vc4-hdmi-0` y `vc4-hdmi-1` |
| Speakerphone USB | No comprado todavía |

**Conclusión:** no es posible captar voz directamente en la Raspberry sin agregar micrófono o un dispositivo externo que transporte audio. La presencia de una salida ALSA no garantiza que haya parlantes conectados.

## Rutas de prueba sin compras

1. **Pipeline conversacional por texto (recomendado):** ejecutar el cliente/servicio desde la Raspberry, introducir consultas por terminal y validar procesamiento, permisos, registro y gestión de errores sin entrada ni salida de voz. La API de OpenAI requiere clave y facturación independiente.
2. **Salida de audio:** conectar parlante al jack 3,5 mm o monitor/TV con audio por HDMI; probar `speaker-test` / `aplay` por el dispositivo correcto, ajustando volumen. No confirma captura.
3. **Micrófono temporal:** si hay webcam USB con micrófono, headset USB o dongle de audio USB con entrada, conectar y repetir `lsusb`, `arecord -l`. Un micrófono integrado del Mac no aparece automáticamente como periférico ALSA de la Raspberry; para usarlo se necesitaría un puente de audio por red y controles de seguridad.
4. **Audio sintético:** utilizar archivos WAV de prueba para verificar conversión de formatos o componentes STT, pero no medir palabra de activación ni captación real.

## Criterios de aceptación diferidos
- Micrófono USB detectado por ALSA.
- Captura y reproducción simultáneas.
- Activación por voz local, cancelación de eco y pruebas a distintas distancias.
- Medición de latencia y estabilidad tras reinicio.

No declarar validado el módulo de voz hasta instalar y probar el hardware real.


## Validación de salida analógica — 21 octubre 2026

El operador conectó **audífonos mediante jack de 3,5 mm** a la Raspberry Pi 4 y confirmó haber escuchado el tono generado por:

```bash
speaker-test -D hw:0,0 -c 2 -t sine -f 440 -l 1
```

**Resultado:** salida ALSA analógica `hw:0,0` y reproducción física **validadas**. La prueba no valida captura de micrófono; el jack analógico integrado en la Raspberry Pi 4 es de salida y ALSA no enumera dispositivos de captura.

### Siguiente prueba propuesta: síntesis de voz local (sin costo de API)

```bash
sudo apt update
sudo apt install -y espeak-ng
espeak-ng -v es -s 145 -w /tmp/zn-assistant-test.wav "Hola, soy ZN Assistant. Mi sistema de audio funciona correctamente."
aplay -D plughw:0,0 /tmp/zn-assistant-test.wav
```

`espeak-ng` es un TTS local ligero y su voz puede sonar robótica; se utiliza únicamente para validar el recorrido texto → síntesis → reproducción. **Pendiente de evidencia de reproducción de voz real.**

Para el asistente final se evaluará motor de voz más natural y hardware de captura USB; la elección dependerá de recursos, latencia y costo.


## Síntesis local con eSpeak NG — prueba satisfactoria (21 octubre 2026)

El operador instaló y probó `espeak-ng` con salida WAV y reproducción ALSA mediante:

```bash
espeak-ng -v es -s 145 -w /tmp/zn-assistant-test.wav "Hola, soy ZN Assistant. Mi sistema de audio funciona correctamente."
aplay -D plughw:0,0 /tmp/zn-assistant-test.wav
```

**Evidencia funcional:** el usuario confirmó que escuchó la frase completa por sus audífonos jack; percibió la voz como muy robótica, comparable a un sintetizador clásico. Se valida el recorrido texto → WAV → ALSA → salida analógica. No se midieron todavía latencia, CPU ni RAM.

**Decisión técnica:** conservar eSpeak NG como TTS de referencia/respaldo; evaluar Piper con modelo de voz en español para salida más natural. La viabilidad y calidad en Raspberry Pi 4 de 2 GB deben medirse, no darse por probadas. Integración de TTS con el motor conversacional y audio de entrada siguen pendientes.


## Jarvis — integración TTS al motor local (código publicado, pruebas en Raspberry pendientes)

Archivos:
- [`scripts/jarvis_tts.py`](../scripts/jarvis_tts.py): eSpeak NG produce un WAV temporal; `aplay` lo reproduce por `plughw:0,0`; se borra después. Procesos ejecutados con argumentos separados (sin shell), timeout y manejo de errores.
- [`scripts/zn_assistant_local.py`](../scripts/zn_assistant_local.py): `--voice` activa respuestas audibles. Sin parámetro, se conserva el modo texto. `--audio-device` permite seleccionar otro dispositivo ALSA.
- [`tests/test_jarvis_tts.py`](../tests/test_jarvis_tts.py): pruebas de flujo TTS simuladas, texto vacío, longitud excesiva y ausencia de dependencias; no requieren audio real.

### Actualización y pruebas

```bash
cd ~/zn-assistant
source .venv/bin/activate
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/scripts/zn_assistant_local.py -o scripts/zn_assistant_local.py
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/scripts/jarvis_tts.py -o scripts/jarvis_tts.py
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/tests/test_jarvis_tts.py -o tests/test_jarvis_tts.py
python -m py_compile scripts/zn_assistant_local.py scripts/jarvis_tts.py
python -m unittest discover -s tests -v
python scripts/zn_assistant_local.py --voice
```

Criterios de aceptación:
1. Responde por texto a `hola Jarvis` y reproduce el audio por audífonos.
2. Si falla la reproducción, informa el error y mantiene la sesión de texto.
3. Las pruebas unitarias muestran `OK`; con los dos tests del clima y los cuatro tests de TTS se esperan 12 pruebas en total.

El modo `--voice` **no reconoce voz**, pues aún no hay micrófono detectado; tampoco involucra OpenAI ni pagos. El motor de clima sí consulta HTTPS a Open-Meteo.

**Estado:** implementación subida a GitHub, pendiente de confirmación del operador en su Raspberry.


## Integración Jarvis → eSpeak NG → ALSA: validada (21 octubre 2026)

El primer intento con `--voice` no reprodujo audio: `grep -n "audio-device" scripts/zn_assistant_local.py` no encontró el argumento y la salida omitía `Salida hablada: activada`. Se diagnosticó que el archivo local era una revisión antigua.

**Corrección aplicada por el operador:** descarga directa de la revisión `1641f70e1b942522c51f06c42322ba0d72c04f4d` del archivo `scripts/zn_assistant_local.py`. El archivo actualizado se descargó con 5503 bytes y se verificaron:
- Línea 17: `from jarvis_tts import speak, AudioError`
- Línea 100: argumento `--audio-device`
- Línea 104: indicador `Salida hablada`

El usuario confirmó que **Jarvis reproduce audio correctamente** después de iniciar la versión actualizada con `python scripts/zn_assistant_local.py --voice`.

**Alcance de la evidencia:** integración salida por texto → eSpeak NG → salida analógica audible, sin micrófono ni STT. El usuario no adjuntó salida de la última batería de pruebas unitarias ni métricas de latencia, RAM o CPU; permanecen pendientes. Voz eSpeak NG provisional, no voz definitiva.

**Próximo hito recomendado:** medir el consumo y latencia, verificar `python -m unittest discover -s tests -v`, después evaluar Piper TTS con un modelo ligero en español.
