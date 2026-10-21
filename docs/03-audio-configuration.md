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
