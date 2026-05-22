# Desplegar Rethiner en Render

## 1. Subir el código a GitHub

Desde la carpeta del repositorio:

```bash
git add .
git commit -m "Configurar despliegue en Render"
git push origin main
```

Repositorio: `https://github.com/escob-2225/Trabajo-Final-Herramientas-Computacionales-`

## 2. Base de datos MySQL en la nube

Render no incluye MySQL gratis. Crea una base MySQL externa (por ejemplo en [Railway](https://railway.app), [Aiven](https://aiven.io) o [FreeSQLDatabase](https://freesqldatabase.com)) y anota:

- Host
- Puerto (normalmente `3306`)
- Usuario
- Contraseña
- Nombre de la base (`optica_db`)

Importa tu base local a la nube (phpMyAdmin, MySQL Workbench o `mysqldump`):

```bash
mysqldump -u root optica_db > backup.sql
mysql -h TU_HOST -u TU_USUARIO -p optica_db < backup.sql
```

Luego ejecuta también `setup_admin.sql` si hace falta.

## 3. Crear el servicio en Render

1. Entra a [render.com](https://render.com) e inicia sesión.
2. **New +** → **Blueprint** (si detecta `render.yaml`) o **Web Service**.
3. Conecta tu cuenta de GitHub y elige el repositorio del proyecto.
4. Configura:
   - **Root Directory:** `Rethiner_trabajo final`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

## 4. Variables de entorno en Render

En el panel del servicio → **Environment**:

| Variable | Valor |
|----------|--------|
| `SECRET_KEY` | Una clave larga y aleatoria |
| `MYSQL_HOST` | Host de tu MySQL en la nube |
| `MYSQL_USER` | Usuario de la base |
| `MYSQL_PASSWORD` | Contraseña |
| `MYSQL_DATABASE` | `optica_db` |
| `MYSQL_PORT` | `3306` |
| `MAIL_USERNAME` | Correo Gmail de la óptica |
| `MAIL_PASSWORD` | Contraseña de aplicación de Gmail |

## 5. Desplegar

Pulsa **Create Web Service** o **Deploy**. La primera compilación puede tardar varios minutos.

Tu sitio quedará en una URL como: `https://rethiner-optica.onrender.com`

## Notas

- El plan gratuito de Render **apaga** el servicio tras inactividad; la primera visita puede tardar ~1 minuto en responder.
- No subas contraseñas al repositorio; usa solo variables de entorno en Render.
- Si el build falla por MySQL, verifica que exista el archivo `apt.txt` en `Rethiner_trabajo final/`.
