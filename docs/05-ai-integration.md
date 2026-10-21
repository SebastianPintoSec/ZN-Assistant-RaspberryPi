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


## Entorno virtual Python — validación real (21 octubre 2026)

Comandos ejecutados desde `~/zn-assistant`:

```bash
python3 -m venv .venv
source .venv/bin/activate
which python
python --version
python -m pip --version
python -m pip install --upgrade pip
```

**Resultados observados:**
- Intérprete activo: `/home/znadmin/zn-assistant/.venv/bin/python`.
- Python: `3.13.5`.
- pip antes de actualizar: `25.1.1`.
- pip después de actualizar: `26.2.2`.
- Instalación de pip completada dentro de `.venv` sin errores.

**Estado:** aislamiento Python y gestor pip **validados**. SDK OpenAI, API key, petición autenticada y motor conversacional **aún pendientes**.

**Siguiente control:** instalar el paquete `openai` dentro del entorno virtual, guardar la versión y ejecutar una prueba de importación sin introducir secretos en comandos ni registros públicos.


## SDK instalado y probado — 21 octubre 2026

El operador confirmó:

```text
Name: openai
Version: 3.36.0
Location: /home/znadmin/zn-assistant/.venv/lib/python3.13/site-packages
OpenAI SDK: 3.36.0
```

Se ejecutó `python -m pip freeze > requirements.txt` dentro del entorno virtual. **La generación local del archivo se confirmó, pero todavía no se ha publicado ni inspeccionado su contenido en el repositorio**.

**Estado:** instalación e importación del SDK validadas. La llamada autenticada, las credenciales y la facturación permanecen pendientes.

## Control de costos previsto

La API de OpenAI factura separadamente del plan ChatGPT; para ZN Assistant, presupuestar texto (tokens entrada/salida), transcripción y voz sintetizada, y posibles búsquedas web. Ejemplos de tarifas: `gpt-6-luna` entrada US$0.10 / 1M tokens y salida US$0.50 / 1M tokens (precio estándar consultado 21 octubre 2026), `gpt-4o-mini-transcribe` ~US$0.003 / minuto; revisar página oficial antes de cada cambio de modelo: https://developers.openai.com/api/docs/pricing

Controles a implementar: límite mensual de gasto en la cuenta cuando esté disponible, alertas, cupos de uso por sesión, `max_output_tokens`, instrumentación de tokens y uso de respuesta compacta; no registrar secretos ni contenido sensible.


## Prototipo de texto v0.1 — código publicado (pendiente de validación en hardware)

Archivo: [`scripts/zn_assistant_text.py`](../scripts/zn_assistant_text.py). Este programa implementa:
- `OpenAI().responses.create` con `store=False` y modelo configurable mediante `ZN_MODEL` (predeterminado: `gpt-4.1-mini`).
- Entrada manual por consola; ninguna entrada/salida de audio ni automatización doméstica.
- Timeout 25 segundos, un reintento en el cliente, máximo 250 tokens de salida, máximo 1200 caracteres por entrada y retención de solo tres intercambios aproximados.
- Manejo de errores de autenticación, cuotas, tiempo de espera y errores HTTP.
- Visualización de latencia y tokens por sesión sin imprimir clave API. Las cifras de tokens no equivalen por sí solas a una factura.

### Instalación en Raspberry (pendiente de prueba)

```bash
cd ~/zn-assistant
source .venv/bin/activate
mkdir -p scripts
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/scripts/zn_assistant_text.py -o scripts/zn_assistant_text.py
python -m py_compile scripts/zn_assistant_text.py
```

**Clave para prueba temporal sin persistencia:**

```bash
read -rsp "Introduce tu OpenAI API key: " OPENAI_API_KEY
echo
export OPENAI_API_KEY
python scripts/zn_assistant_text.py
```

La clave será válida solo en la sesión actual de shell; jamás compartirla o incluirla en `requirements.txt`, GitHub, capturas o logs. Configurar facturación y límites de cuenta en OpenAI Platform. `gpt-4.1-mini` es un identificador publicado en la documentación de modelos de la API; su acceso depende del proyecto y cuenta. Si la API devuelve un error de modelo, diagnosticar primero antes de cambiar parámetros.

**Criterio de aceptación:** consulta con respuesta no vacía, error limpio al faltar credenciales, seguimiento contextual básico y contabilización de tokens. Aún sin pruebas reales en Raspberry.


## Ruta sin facturación: asistente local v0.1 — 21 octubre 2026

El usuario optó por continuar sin créditos de API mientras resuelve la aceptación del medio de pago. No se requieren clave API ni llamadas a OpenAI para esta fase.

Código publicado:
- [`scripts/zn_assistant_local.py`](../scripts/zn_assistant_local.py): CLI Python con normalización Unicode, reconocimiento determinista de intenciones (saludos, ayuda, hora local, estado, gracias) y respuesta segura ante acciones no admitidas.
- [`tests/test_zn_assistant_local.py`](../tests/test_zn_assistant_local.py): seis pruebas unitarias de normalización, órdenes soportadas y rechazo por defecto de una acción domótica.

Instalación y ejecución en Raspberry:

```bash
cd ~/zn-assistant
source .venv/bin/activate
mkdir -p scripts tests
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/scripts/zn_assistant_local.py -o scripts/zn_assistant_local.py
curl -fL https://raw.githubusercontent.com/SebastianPintoSec/ZN-Assistant-RaspberryPi/main/tests/test_zn_assistant_local.py -o tests/test_zn_assistant_local.py
python -m unittest discover -s tests -v
python scripts/zn_assistant_local.py
```

**Alcance:** no hay inteligencia generativa, STT, TTS, wake word ni ejecución de comandos del SO. La prueba de hora utiliza el reloj del sistema Raspberry. Esta fase valida únicamente el bucle conversacional, las intenciones definidas y las pruebas automatizadas. **Pendiente:** evidencia de ejecución real en Raspberry.
