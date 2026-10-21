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


## Preparación de Python — observación inicial (21 octubre 2026)

- Python reportó `Python 3.13.5`.
- `python3 -m pip --version` reportó `No module named pip` en el intérprete del sistema.

### Procedimiento previsto, pendiente de validación en Raspberry

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
mkdir -p ~/zn-assistant
cd ~/zn-assistant
python3 -m venv .venv
source .venv/bin/activate
which python
python --version
python -m pip --version
python -m pip install --upgrade pip
```

Usar paquetes de aplicación solamente dentro de `.venv`. No usar `sudo pip` ni `--break-system-packages` sobre el Python administrado por Debian (PEP 668). El entorno virtual debe estar en `.gitignore` antes de sincronizar el directorio con Git.

**Estado:** se documentan versiones y ausencia de pip observadas; todavía no se recibió salida que confirme instalación de pip ni creación del entorno.
