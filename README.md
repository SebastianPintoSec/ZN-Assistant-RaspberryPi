# ZN Assistant — Raspberry Pi 4 Voice AI Lab

> **Estado:** planificación y preparación de plataforma. Las funcionalidades de voz y domótica aún no se han implementado ni validado.

## Objetivo
Diseñar, implementar, securizar y validar un asistente de voz independiente en Raspberry Pi 4: activación local por palabra clave, reconocimiento de voz, conversación a través de la API de OpenAI y ejecución controlada de acciones mediante Home Assistant.

## Alcance
- Raspberry Pi 4 como terminal de voz dedicado (Raspberry Pi OS Lite, 64 bits).
- Audio de entrada/salida con speakerphone USB compatible con Linux.
- Servidor Ubuntu 24.04 opcional para Home Assistant y servicios de procesamiento.
- Operación persistente, telemetría, pruebas reproducibles y seguridad por defecto.
- La API de OpenAI requiere credenciales y facturación independientes de ChatGPT.

## Arquitectura propuesta
```text
[Speakerphone USB] ⇄ [Raspberry Pi 4: wake word + audio]
                            ⇅ LAN (autenticada)
              [Servidor Ubuntu / Home Assistant]
                            ⇅
                   [OpenAI API]
```
El diagrama representa una arquitectura objetivo, no una instalación validada.

## Roadmap
- [ ] LAB-01: instalación de Raspberry Pi OS Lite 64-bit y conectividad por SSH
- [ ] LAB-02: endurecimiento de sistema, acceso SSH y actualizaciones
- [ ] LAB-03: detección y prueba de audio USB, captura y reproducción
- [ ] LAB-04: palabra de activación y pipeline STT/TTS
- [ ] LAB-05: integración con OpenAI API y gestión segura de secretos
- [ ] LAB-06: Home Assistant, permisos mínimos y acciones domóticas
- [ ] LAB-07: servicios systemd, observabilidad y pruebas de resiliencia

## Documentación
- [Instalación](docs/01-installation.md)
- [Seguridad](docs/02-system-hardening.md)
- [Audio](docs/03-audio-configuration.md)
- [Pipeline de voz](docs/04-voice-pipeline.md)
- [Integración de IA](docs/05-ai-integration.md)
- [Diagnóstico](docs/06-troubleshooting.md)

## Seguridad y publicación
No publicar contraseñas, tokens, claves de API, direcciones IP públicas, datos de ubicación precisa ni grabaciones con información personal. Usar configuraciones de ejemplo y datos redactados para evidencias.

## Licencia
MIT. Ver [LICENSE](LICENSE).
