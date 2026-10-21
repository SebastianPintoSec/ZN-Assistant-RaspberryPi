# LAB-04 — Pipeline de voz

**Estado:** diseño preliminar.

Flujo objetivo: palabra de activación local → captura de frase → speech-to-text → decisión/enrutamiento → respuesta → text-to-speech → reproducción.

Evaluar funciones de privacidad, falsos positivos, cancelación de eco y recuperación ante pérdida de conectividad. La palabra de activación personalizada debe probarse: no se asume que «Oye ZN» esté disponible de forma predeterminada.


## Identidad del asistente (21 octubre 2026)

**Nombre visible y hablado:** Jarvis. **Nombre técnico y repositorio:** ZN Assistant Raspberry Pi (se mantiene por compatibilidad y trazabilidad). El cambio de nombre se aplicó al saludo, textos de terminal y futuras instrucciones de personalidad en los prototipos local y OpenAI. **Palabra de activación prevista:** «Oye Jarvis»; todavía no existe módulo de wake word ni se ha probado una activación por voz. La voz eSpeak NG usada para la primera prueba era provisional; nombrar Jarvis no selecciona automáticamente otra voz.
