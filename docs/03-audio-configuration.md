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
