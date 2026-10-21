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
