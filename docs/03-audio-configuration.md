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


## Regresión y capacidad de memoria (observado 21 de octubre de 2026)

Pruebas ejecutadas por el operador: `python -m unittest discover -s tests -v` → **10 pruebas OK en 0.007 s**: 4 casos del sintetizador y 6 del motor de comandos locales.

**Diferencia con 12 casos esperados:** no aparecen `test_clima_despacha_sin_red` ni `test_clima_falla_con_gracia`. Esto indica que la copia local del archivo de pruebas de clima probablemente está desactualizada; **no se debe afirmar que las 12 pruebas están aprobadas**. Volver a descargar el archivo de pruebas desde una revisión GitHub fija y verificar su contenido, luego ejecutar la batería completa.

`free -h` reportado:

```text
Mem:  total 1.8Gi; used 247Mi; free 333Mi; buff/cache 1.4Gi; available 1.6Gi
Swap: total 1.8Gi; used 0B
```

Interpretación: Linux puede recuperar buena parte de la caché; la referencia útil es **available ≈1.6 GiB**, no free. No hay consumo de swap en el momento de la medida.

### Siguiente validación propuesta: compatibilidad Piper TTS

Piper es un motor local de voz neuronal que puede ejecutar la síntesis en CPU; comprobar primero si existen ruedas binarias compatibles con ARM64 y Python 3.13 para evitar compilaciones grandes en Raspberry Pi de 2 GB. Procedimiento sin instalación:

```bash
cd ~/zn-assistant
source .venv/bin/activate
python -m pip install --dry-run --only-binary=:all: piper-tts
```

El modo `--dry-run` resuelve dependencias sin instalarlas. No reemplazar eSpeak hasta validar Piper y medir recursos. Documentación oficial: https://github.com/OHF-Voice/piper1-gpl y voces https://huggingface.co/rhasspy/piper-voices.


## Piper TTS 1.8.0 — resolución binaria ARM64 verificada (21 octubre 2026)

El operador ejecutó `python -m pip install --dry-run --only-binary=:all: piper-tts` dentro de `.venv` (Python 3.13.5 ARM64). El resolvedor descargó metadatos y reportó únicamente dependencias binarias:

- `piper-tts==1.8.0`, rueda `cp39-abi3` para `aarch64`.
- `onnxruntime==1.31.0`, rueda `cp313` para `aarch64`.
- `numpy==2.5.4`, `pathvalidate==3.3.1`, `flatbuffers==25.12.19`, `packaging==26.3`, `protobuf==7.36.2`.

**Resultado:** compatibilidad de distribución **verificada por resolución dry-run**. No prueba todavía ejecución del motor, descarga de modelos ni calidad/latencia de síntesis.

### Fase siguiente: instalación y descubrimiento de voces

```bash
cd ~/zn-assistant
source .venv/bin/activate
python -m pip install --only-binary=:all: piper-tts==1.8.0
python -m pip show piper-tts
python -m pip show onnxruntime
python -m piper.download_voices | grep -E '^es_(ES|AR|MX)-'
```

Las voces disponibles deben confirmarse antes de escoger una. Al descargar un modelo, revisar su licencia individual `MODEL_CARD` si se planea redistribuirlo. Conservar `espeak-ng` como respaldo y medir primero RAM, swap y latencia de Piper. Consultar documentación oficial https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md y catálogo de voces https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md.


## Piper instalado; nueve voces españolas descubiertas — 21 octubre 2026

El operador confirmó:
- `piper-tts==1.8.0` instalado en `.venv`, GPL-3.0-or-later.
- `onnxruntime==1.31.0` instalado en `.venv`, licencia MIT.
- `python -m piper.download_voices | grep -E '^es_(ES|AR|MX)-'` devolvió nueve opciones: `es_AR-daniela-high`, `es_ES-carlfm-x_low`, `es_ES-davefx-medium`, `es_ES-mls_10246-low`, `es_ES-mls_9972-low`, `es_ES-sharvard-medium`, `es_MX-ald-medium`, `es_MX-ald-x_low`, `es_MX-claude-high`.

**Siguiente selección de prueba:** `es_MX-ald-medium`, calidad medium; modelo de aproximadamente 63 MB. No se ha evaluado todavía su calidad perceptual ni género de la voz. Modelo alternativo `es_ES-sharvard-medium` tiene dos perfiles de hablante identificados como M y F; valorar tras prueba.

### Procedimiento de referencia (aún pendiente de prueba)

```bash
cd ~/zn-assistant
source .venv/bin/activate
mkdir -p models/piper
python -m piper.download_voices --data-dir models/piper es_MX-ald-medium
ls -lh models/piper/
/usr/bin/time -v python -m piper --data-dir models/piper -m es_MX-ald-medium -f /tmp/jarvis-piper.wav -- "Hola, soy Jarvis. Mi nuevo motor de voz neuronal está funcionando correctamente."
aplay -D plughw:0,0 /tmp/jarvis-piper.wav
```

**Mediciones solicitadas:** calidad audible, duración del comando, tiempo de reloj (`Elapsed (wall clock)`), y `Maximum resident set size` de `/usr/bin/time -v`. Tener en cuenta que la primera ejecución incluye carga del modelo; posterior modo residente puede ofrecer mejores tiempos. No modificar `jarvis_tts.py` ni retirar eSpeak NG hasta verificar esta primera síntesis.

Referencias: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md ; catálogo https://huggingface.co/rhasspy/piper-voices/blob/main/voices.json


## Modelo Piper descargado; utilidad de benchmark ausente (21 octubre 2026)

El operador confirmó que `models/piper/` contiene:
- `es_MX-ald-medium.onnx` — 61 MB.
- `es_MX-ald-medium.onnx.json` — 4.8 KB.

El primer intento de ejecución de Piper utilizó `/usr/bin/time -v`, pero el sistema devolvió:

```text
-bash: /usr/bin/time: No such file or directory
```

**Diagnóstico:** el paquete `time` no está instalado. Como falló la resolución del ejecutable externo `time`, Piper **no llegó a ejecutarse**; no existe evidencia de error de Piper ni de un WAV generado por ese intento.

### Corrección y nueva prueba propuestas

```bash
sudo apt update
sudo apt install -y time
/usr/bin/time --version
cd ~/zn-assistant
source .venv/bin/activate
/usr/bin/time -v python -m piper \
  --data-dir models/piper \
  -m es_MX-ald-medium \
  -f /tmp/jarvis-piper.wav \
  -- "Hola, soy Jarvis. Mi nuevo motor de voz neuronal está funcionando correctamente."
ls -lh /tmp/jarvis-piper.wav
aplay -D plughw:0,0 /tmp/jarvis-piper.wav
```

Revisar salida de stderr de `time -v` para `Elapsed (wall clock) time` y `Maximum resident set size`; pedir confirmación auditiva y si se utilizó swap. **Pendiente de prueba real del motor neuronal.**


## Primera síntesis neuronal Piper reproducida y medida (21 octubre 2026)

**Evidencia del operador:** ejecución real de `es_MX-ald-medium` mediante `/usr/bin/time -v python -m piper --data-dir models/piper -m es_MX-ald-medium -f /tmp/jarvis-piper.wav -- "Hola, soy Jarvis. Mi nuevo motor de voz neuronal está funcionando correctamente."`. Se reprodujo correctamente con `aplay -D plughw:0,0 /tmp/jarvis-piper.wav`.

Mediciones registradas:

| Métrica | Valor |
|---|---|
| Tiempo de ejecución (wall clock) | 10.07 s |
| CPU user / system | 15.16 s / 0.46 s |
| CPU total promedio | 155 % |
| RSS máximo | 229644 KiB (~224.3 MiB) |
| Swaps | 0 |
| Código de salida | 0 |
| Archivo WAV | PCM signed 16-bit, mono, 22050 Hz |
| Modelo | es_MX-ald-medium, archivo ONNX de 61 MB |

**Interpretación:** el audio neuronal se genera y reproduce correctamente con memoria moderada y sin swap en esta prueba. Los 10.07 segundos incluyen inicialización/carga del modelo y síntesis; aún no se ha medido duración del WAV, latencia cálida ni factor de tiempo real. No declarar todavía aptitud para uso conversacional continuo. El operador todavía no ha calificado subjetivamente calidad o pronunciación.

**Próxima medición recomendada:** obtener duración del WAV mediante Python `wave` y comparar tiempo de síntesis con tiempo de reproducción; después evaluar motor Piper residente y secuencias de respuestas sin recargar modelo en cada interacción. Mantener eSpeak NG como respaldo.
