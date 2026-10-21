# LAB-05 — Integración IA y domótica

**Estado:** pendiente.

Utilizar credenciales API almacenadas fuera del repositorio. Distinguir consultas conversacionales de acciones físicas. Aplicar una lista explícita de acciones permitidas y confirmación adicional para acciones sensibles.

Medir costo por uso, latencia, errores y límites de solicitudes. La suscripción ChatGPT no incluye automáticamente créditos de API.


## Validación de conectividad API — 21 de octubre de 2026

Desde Raspberry Pi OS Lite se ejecutó:

```bash
curl -i --http1.1 --max-time 15 https://api.openai.com/v1/models
```

**Resultado observado:** `HTTP/1.1 401 Unauthorized`, encabezado `WWW-Authenticate: Bearer realm="OpenAI API"` y mensaje `Missing bearer authentication in header`.

**Interpretación:** conexión HTTPS, resolución de destino y respuesta del endpoint de OpenAI verificadas. La respuesta 401 es esperada al no suministrar token. Un intento anterior con `curl -I` usando HTTP/2 respondió 421; HTTP/1.1 permitió obtener la respuesta normal de autenticación.

**No validado todavía:** credenciales API, facturación/cuota, petición al modelo, tiempos de inferencia y robustez del cliente. No publicar tokens ni respuestas con datos privados.
