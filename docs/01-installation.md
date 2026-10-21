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
Pendiente de ejecución y validación en equipo real.
