# CampoControl — aplicación web ganadera

Aplicación en español para registrar animales, fotos, salud y vacunas, reproducción, compras y ventas, peso, leche, finanzas y copias de seguridad.

## Antes de publicar

1. Abre `config.py`. Cambia `ADMIN_PASSWORD` por una contraseña larga y única. Puedes cambiar también `ADMIN_USERNAME`.
2. No publiques ni compartas `config.py`, porque contiene las credenciales y la clave de sesión.
3. Los registros se guardan en `data/ganado.json`; las fotos, en `fotos/`; y las copias, en `respaldos/`. En un alojamiento web, estas carpetas deben estar en almacenamiento persistente.
4. Haz copias de seguridad periódicas. Para fotos y datos reales, no uses una instalación sin proteger.

## Probar en tu computador

Necesitas Python 3.10 o posterior. Abre una terminal dentro de esta carpeta y ejecuta:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`. Usuario inicial: `admin`. Contraseña inicial: `CambiaEstaClave123!`. Cambia la contraseña en `config.py` antes de publicar.

## Publicar en PythonAnywhere (plan gratuito, sujeto a límites del proveedor)

1. Crea una cuenta en PythonAnywhere.
2. Sube la carpeta del proyecto a tu espacio de archivos. No subas datos reales a un repositorio público.
3. En la consola Bash de PythonAnywhere, entra en la carpeta y crea un entorno virtual:

   ```bash
   cd ~/CampoControl_Web
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

4. En la pestaña **Web**, crea una aplicación web manual con Flask y la versión de Python disponible. Configura el archivo WSGI para que cargue `app` desde la carpeta del proyecto. Un ejemplo de bloque WSGI es:

   ```python
   import os
   import sys
   os.environ['CAMPOCONTROL_HTTPS'] = '1'
   project = '/home/TU_USUARIO/CampoControl_Web'
   if project not in sys.path:
       sys.path.insert(0, project)
   activate_this = project + '/.venv/bin/activate_this.py'
   # Si ese archivo no existe en tu entorno, selecciona el virtualenv
   # en la pestaña Web en lugar de usar estas líneas.
   from app import app as application
   ```

   Reemplaza `TU_USUARIO` con tu nombre de usuario real. En la pestaña Web selecciona el virtualenv ` /home/TU_USUARIO/CampoControl_Web/.venv ` si la interfaz ofrece ese campo.

5. En la pestaña Web pulsa **Reload**. Abre el enlace público asignado por la plataforma e inicia sesión.
6. Prueba crear un animal de prueba, subir una foto, cerrar sesión y volver a entrar. Comprueba que ambos sigan allí. Luego elimina el registro de prueba.
7. No compartas tu enlace privado con otras personas sin revisar permisos y copias.

### Nota sobre alojamiento gratuito

Las condiciones, cuotas y funciones gratuitas de los proveedores cambian. Antes de guardar información real, confirma que tu plan mantiene los archivos entre reinicios y que el espacio disponible es suficiente. Si la cuenta gratuita no permite el almacenamiento persistente requerido, no cargues datos reales hasta elegir una opción adecuada.
