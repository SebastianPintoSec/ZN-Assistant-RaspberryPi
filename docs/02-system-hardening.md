# LAB-02 — Endurecimiento del sistema

**Estado:** en curso. Validación parcial del acceso SSH, 21 de octubre de 2026.

## Objetivos
Endurecer Raspberry Pi OS Lite sin perder el acceso de administración, priorizando SSH, actualizaciones, mínimos privilegios, servicios y firewall.

## Evidencia verificada — SSH con clave dedicada

El operador ejecutó exitosamente desde macOS:

```bash
ssh -o IdentitiesOnly=yes \
    -o PreferredAuthentications=publickey \
    -o PasswordAuthentication=no \
    -i ~/.ssh/id_ed25519_znassistant \
    znadmin@<IP_PRIVADA_RASPBERRY>
```

**Resultado:** sesión iniciada en `zn-assistant-rpi01`, sin contraseña de la cuenta de Linux. Se solicitó la frase de protección de la clave privada Ed25519. Esto valida la autenticación por clave pública y separación del material criptográfico por proyecto. **No demuestra que la autenticación por contraseña esté ya deshabilitada del lado del servidor.**

### Advertencia de configuración regional

Durante el inicio de sesión se observó:

```text
-bash: warning: setlocale: LC_CTYPE: cannot change locale (UTF-8)
```

Diagnóstico preliminar: el cliente macOS transmite una variable `LC_CTYPE=UTF-8` sin prefijo de idioma, que el servidor Debian no reconoce como locale válido. Pendiente de verificar `locale` y `locale -a` y corregir la variable transmitida. No se considera una falla de autenticación.

## Próximos controles
1. Diagnosticar y corregir variables de locale.
2. Comprobar configuración efectiva de sshd (`sshd -T`), y `authorized_keys`.
3. Deshabilitar acceso mediante contraseña **solo después** de probar clave en una segunda sesión, conservando acceso de recuperación.
4. Evaluar firewall según puertos y arquitectura real.
5. Revisar servicios activos, actualizaciones y logs.
6. Documentar rollback para cada cambio.

## Precauciones
No publicar claves privadas, passphrases, contenido de `authorized_keys` ni identificadores únicos. Mantener sesión SSH abierta y copia de seguridad de la configuración antes de modificar sshd.


## Diagnóstico confirmado — 21 de octubre de 2026

### Configuración efectiva SSH antes de endurecer
```text
permitrootlogin without-password
pubkeyauthentication yes
passwordauthentication yes
kbdinteractiveauthentication no
authenticationmethods any
```
Interpretación: clave pública habilitada y verificada; acceso mediante contraseña de usuario **todavía habilitado**; acceso root con contraseña prohibido pero root con clave pública no descartado. `without-password` es una forma histórica equivalente a prohibir contraseña para root, **no** equivale a `no`. `authenticationmethods any` significa que no se requiere combinación obligatoria de varios métodos.

### Locale
```text
LANG=en_GB.UTF-8
LC_CTYPE=UTF-8
LC_ALL=
locale -a: C, C.utf8, en_GB.utf8, POSIX
```
El locale `en_GB.UTF-8` está disponible y es válido. El valor `LC_CTYPE=UTF-8` es inválido en Debian y probablemente fue enviado por el cliente macOS durante SSH.

### Procedimiento propuesto (pendiente de validar)
1. Desde sesión Raspberry, ejecutar `env -u LC_CTYPE locale` para verificar el locale sin la variable inválida.
2. Desde Mac, probar `LC_CTYPE=en_GB.UTF-8 ssh -i ~/.ssh/id_ed25519_znassistant znadmin@<IP_PRIVADA>` para validar conexión sin advertencias.
3. Respaldar SSH: `sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.pre-znassistant`.
4. Aplicar una configuración explícita en el archivo de drop-in `/etc/ssh/sshd_config.d/00-znassistant-hardening.conf` **después de revisar precedencia**: `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no`.
5. Validar sintaxis con `sudo sshd -t`, y configuración efectiva mediante `sudo sshd -T` antes de recargar el servicio.
6. Conservar sesión abierta; ejecutar `sudo systemctl reload ssh`, y validar acceso **desde una segunda terminal** obligando clave pública y prohibiendo fallback a contraseña.
7. Si el acceso falla, revertir desde la sesión original; nunca cerrar el último acceso antes de la prueba.

**Nota:** pasos 3–7 todavía no realizados. Confirmar otros archivos `sshd_config.d` y reglas `Match` antes de aplicar la política.


## Diagnóstico adicional validado — 21 octubre 2026

### Prueba de locale corregida
Conexión exitosa desde macOS al utilizar `LC_CTYPE=en_GB.UTF-8` antes del comando SSH; desaparecieron las advertencias `setlocale`. La corrección persistente de la configuración del cliente sigue pendiente.

### Inspección de precedencia SSH
El operador creó respaldo de `/etc/ssh/sshd_config` mediante `sudo cp -a`. El directorio `/etc/ssh/sshd_config.d/` contenía únicamente `50-cloud-init.conf`; la inspección confirmó:

```text
/etc/ssh/sshd_config:12:Include /etc/ssh/sshd_config.d/*.conf
/etc/ssh/sshd_config:64:KbdInteractiveAuthentication no
/etc/ssh/sshd_config.d/50-cloud-init.conf:1:PasswordAuthentication yes
```

**Plan de cambio, todavía sin validación de ejecución:** crear `00-znassistant-hardening.conf` con `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no`. El nombre garantiza procesamiento anterior a `50-cloud-init.conf` en el include observado.

**Controles de seguridad del cambio:** mantener sesión original abierta; ejecutar `sudo sshd -t`, inspeccionar `sudo sshd -T` y recargar `sudo systemctl reload ssh` solo si coincide la política. Probar autenticación pública desde una segunda terminal y rechazo de contraseña. **No marcar como aplicado hasta recibir salidas de ejecución**.

**Rollback:** desde la sesión SSH que sigue abierta, ejecutar `sudo rm /etc/ssh/sshd_config.d/00-znassistant-hardening.conf && sudo sshd -t && sudo systemctl reload ssh`, solo si se necesita revertir el cambio; el respaldo previo del fichero principal se conserva. Evitar cerrar la sesión de recuperación.


## Evidencia posterior — rechazo de contraseña (21 octubre 2026)

Desde el cliente macOS se ejecutó una conexión forzando autenticación por contraseña, deshabilitando explícitamente clave pública e interacción:

```bash
ssh -o PubkeyAuthentication=no \
  -o PreferredAuthentications=password \
  -o KbdInteractiveAuthentication=no \
  znadmin@<IP_PRIVADA_RASPBERRY>
```

**Salida observada:**

```text
Permission denied (publickey).
```

**Interpretación:** el servidor no ofreció autenticación por contraseña a ese cliente en esta prueba. Es una evidencia positiva de que la contraseña ya no está disponible como método SSH para esa conexión. **Pendiente**: confirmar nueva sesión por clave pública después de aplicar la política, y verificar `sudo sshd -T` con `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no` y `PubkeyAuthentication yes`. La prohibición de root no está verificada todavía por esta prueba.

No se publicaron credenciales ni direcciones IP concretas.


## Validación definitiva de hardening SSH — 21 octubre 2026

**Estado: aprobado para los controles SSH evaluados.** El operador reconectó exitosamente desde macOS usando exclusivamente la clave Ed25519 dedicada a ZN Assistant, con `IdentitiesOnly=yes`, `PreferredAuthentications=publickey` y `PasswordAuthentication=no`. La clave privada pidió su passphrase local y la sesión SSH se inició correctamente.

Configuración efectiva consultada en Raspberry mediante `sudo sshd -T`:

```text
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no
kbdinteractiveauthentication no
```

La prueba anterior forzando autenticación por contraseña devolvió `Permission denied (publickey)`. En conjunto, se confirma acceso por clave, rechazo de contraseña, bloqueo de teclado interactivo y política de rechazo del acceso root directo, según la configuración efectiva.

**Locale:** conexión sin advertencias al iniciar SSH desde Mac con `LC_CTYPE=en_GB.UTF-8`. La corrección permanente en el cliente macOS no se ha aplicado o verificado.

**Pendiente dentro de LAB-02:** inventario de puertos y servicios, revisión de actualizaciones, firewall, registros y políticas de respaldo. Ninguno se considera validado todavía.


## Inventario de servicios y puertos — 21 de octubre de 2026

**Fuente:** salidas facilitadas desde la Raspberry Pi real: `sudo ss -tulpen`, `systemctl list-units --type=service --state=running --no-pager`, `sudo nft list ruleset`, `apt list --upgradable`.

| Elemento | Observación | Decisión |
|---|---|---|
| SSH | TCP/22 escucha en IPv4 `0.0.0.0` e IPv6 `[::]`; proceso `sshd` | Conservar, restringir por firewall |
| Avahi | UDP/5353 en IPv4/IPv6 y puertos UDP efímeros asociados | Conservar temporalmente para mDNS |
| Servicios running | 13: avahi-daemon, bluetooth, cron, dbus, getty@tty1, NetworkManager, ssh, systemd-journald, systemd-logind, systemd-timesyncd, systemd-udevd, user@1000, wpa_supplicant | No deshabilitar sin evaluación |
| nftables | `sudo nft list ruleset` no mostró reglas | Se requiere definir política de firewall |
| Actualizaciones | `apt list --upgradable` no mostró paquetes | Ninguno listado en ese momento; verificar frescura de índices |

**Advertencia:** los sockets en escucha no demuestran exposición externa, y la ausencia de reglas nftables no descarta filtrado upstream por el router. La política SSH ya fue validada; la política de firewall sigue pendiente de implementación.

### Próximo control de seguridad — firewall seguro para administración remota

1. Verificar interfaz y ruta predeterminada, disponibilidad de `ufw` e IPv6; confirmar red de origen de administración.
2. Mantener una sesión SSH por clave abierta.
3. Definir acceso entrante SSH únicamente desde la red administrativa autorizada, permitir tráfico establecido, permitir lo requerido para mDNS y dejar tráfico saliente necesario.
4. Habilitar el firewall solo después de revisar su configuración, y validar inmediatamente una **segunda conexión SSH** desde el Mac.
5. Guardar `ufw status verbose` y verificar SSH/mDNS. Documentar rollback mediante sesión abierta.

No considerar LAB-02 finalizado hasta validar firewall y política de actualización. No publicar identificadores únicos, credenciales o topología sensible.


## Preflight UFW — 21 octubre 2026 (observado)

- `ufw`: no instalado (`command -v ufw` sin resultado).
- Ruta por defecto: interfaz `eth0`, gateway LAN privado, dirección IPv4 privada en segmento `192.168.88.0/24`.
- Cliente SSH actual: equipo macOS de la misma subred.
- `/proc/sys/net/ipv6/conf/all/disable_ipv6` = `0`: IPv6 **habilitado**, por lo que las reglas de IPv6 también deben evaluarse.
- El puerto SSH sigue siendo TCP/22. La política SSH por clave ya fue verificada.

### Política inicial propuesta (no ejecutada)
- Instalar UFW y comprobar `IPV6=yes` en `/etc/default/ufw`.
- `ufw default deny incoming`, `ufw default allow outgoing`.
- Permitir TCP/22 en `eth0` desde `192.168.88.0/24` como alcance inicial de gestión; **esto autoriza a toda esa LAN, no solamente al Mac**. Reducir el permiso a IP fija o VLAN administrativa cuando se definan reservas DHCP y segmentación.
- Permitir mDNS UDP/5353 desde el segmento local únicamente si se requiere resolver `.local`; evitar interpretar eso como exposición pública.
- Revisar `ufw status numbered` antes de habilitarlo, mantener SSH actual abierto y probar segundo SSH después de activación.
- Con IPv6 habilitado, denegar nuevas conexiones entrantes IPv6 que no tengan permiso explícito.

**Advertencia:** la política debe validarse en el equipo antes de marcarse completada. No copiar direcciones de hosts específicos ni secretos a un repositorio público.


## Firewall UFW — regla preparada, activación pendiente (21 octubre 2026)

El operador confirmó mediante `sudo ufw show added` que se registró la regla de gestión:

```text
ufw allow in on eth0 from 192.168.88.0/24 to any port 22 proto tcp comment 'ZN-ASSISTANT SSH ADMIN'
Status: inactive
```

**Interpretación:** la excepción SSH está definida pero UFW sigue inactivo; por tanto todavía no se ha validado filtrado efectivo.

**Próxima ejecución controlada:** verificar `grep '^IPV6=' /etc/default/ufw` y `sudo ufw show added`; asegurar política deny incoming / allow outgoing; con la sesión SSH original abierta, ejecutar `sudo ufw enable` y verificar `sudo ufw status verbose`. Abrir una segunda sesión SSH por clave desde el Mac, revisar `sudo ufw status numbered` y `systemctl is-active ssh`. Si la nueva conexión falla, desde la sesión original ejecutar `sudo ufw disable`.

**Observación de alcance:** el permiso permite toda la subred administrativa 192.168.88.0/24 en `eth0`; no es una restricción a un único cliente. La aplicación del firewall no se considerará completada hasta tener evidencia de activación y nueva conexión exitosa.
