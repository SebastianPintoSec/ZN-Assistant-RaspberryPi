# LAB-01 — Preparación de Raspberry Pi OS Lite

## Objetivo
Instalar una plataforma reproducible y verificable para el asistente.

## Equipo
- Raspberry Pi 4 y alimentación apropiada.
- microSD de al menos 32 GB recomendada.
- Ethernet recomendado para la instalación inicial.
- Equipo administrador con Raspberry Pi Imager.

## Instalación
1. Descargar Raspberry Pi Imager desde https://www.raspberrypi.com/software/.
2. Seleccionar **Raspberry Pi 4** y **Raspberry Pi OS Lite (64-bit)**.
3. Seleccionar con cuidado la microSD destino: **se borrará su contenido**.
4. Personalizar el hostname `zn-assistant-rpi01`, usuario `znadmin`, zona horaria `America/Santiago`.
5. Activar SSH; preferir autenticación por clave pública. Establecer credenciales seguras.
6. Grabar la imagen, arrancar la Raspberry y comprobar que obtiene conectividad.

## Comprobación inicial
Desde un terminal administrador:
```bash
ssh znadmin@zn-assistant-rpi01.local
```
Si mDNS no resuelve, usar la IP DHCP asignada por el router.

Una vez conectado:
```bash
hostnamectl
uname -m
cat /etc/os-release
free -h
df -h
ip -br addr
```
Esperado: arquitectura `aarch64`; hostname `zn-assistant-rpi01`; instalación Lite de 64 bits.

## Evidencias
Registrar fecha, versión de OS, arquitectura, modelo, cantidad de memoria, interfaz activa y conectividad. Redactar MAC, IP pública o datos personales antes de publicar.

## Riesgos y rollback
La escritura de imagen destruye los datos de la microSD seleccionada. Si el arranque falla, verificar fuente de alimentación, microSD y repetir el flasheo. No habilitar exposición pública de SSH.

## Estado
Instalación inicial y acceso SSH validados; pendiente de hardening y servicios de voz.


## Validación real — 21 de octubre de 2026

**Resultado:** plataforma inicial validada. La información procede de la salida de los comandos ejecutados en el equipo real; no acredita todavía el endurecimiento del sistema ni el funcionamiento del asistente.

| Control | Resultado observado | Estado |
|---|---|---|
| Hostname | `zn-assistant-rpi01` | OK |
| Hardware | Raspberry Pi 4 Model B Rev 1.5 | OK |
| SO | Debian GNU/Linux 13 (trixie), Debian 13.7 | OK |
| Kernel | `6.18.50+rpt-rpi-v8` | OK |
| Arquitectura | `arm64` / `aarch64` | OK |
| Memoria RAM | 1.8 GiB utilizables (modelo de ~2 GB) | OK |
| Swap | 1.8 GiB (sin uso en la observación) | Informativo |
| Partición raíz | 28 GB, 3.7 GB usados, 23 GB disponibles (14 %) | OK |
| Partición de arranque | 505 MB, 76 MB usados (15 %) | OK |
| Ethernet | `eth0` UP, IPv4 privada /24 asignada | OK |
| Wi-Fi | `wlan0` DOWN | Informativo |
| SSH | `active` | OK |

**Comandos de evidencia:** `hostnamectl`, `uname -m`, `cat /etc/os-release`, `cat /proc/device-tree/model`, `free -h`, `df -h`, `ip -br addr`, `systemctl is-active ssh`.

**Privacidad:** se omitieron Machine ID, Boot ID, dirección IPv4 exacta, direcciones IPv6 y datos del equipo administrador. No se publican contraseñas, claves ni tokens.

**Observaciones:**
- El sistema reporta Debian 13.7; Raspberry Pi OS Lite utiliza Debian como base. La imagen exacta debe confirmarse si se requiere reproducibilidad bit a bit.
- La conectividad SSH por IP fue confirmada por el operador.
- La salida no demuestra aún conectividad a Internet, actualizaciones recientes, configuración de firewall, autenticación por claves o salud de la microSD.

**Próxima fase:** LAB-02 — inventario de servicios, actualizaciones y endurecimiento SSH.
