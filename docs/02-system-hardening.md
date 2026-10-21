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
