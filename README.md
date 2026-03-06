# Diskiss

## Buenas practicas de Git

### 1. Flujo recomendado de ramas
- main: solo codigo estable y probado.
- feature/nombre-corto: nuevas funcionalidades.
- fix/nombre-corto: correcciones de bugs.
- chore/nombre-corto: tareas de mantenimiento (refactor, dependencias, etc.).

### 2. Commits pequenos y claros
- Haz commits por cambio logico (no mezclar varias cosas en uno).
- Usa mensajes descriptivos: feat, fix, chore.

### 3. Reglas antes de hacer push
- Ejecuta pruebas o validaciones minimas.
- Revisa cambios con git diff.
- Verifica archivos incluidos con git status.

### 4. Evitar subir archivos generados
Este repositorio ignora carpetas de build y cache en .gitignore, incluyendo:
- dist/
- build/
- __pycache__/ y archivos .pyc
- .venv/ y venv/

### 5. Comandos utiles del dia a dia
git checkout -b feature/mejora-descarga
git status
git add .
git commit -m "feat: mejora validacion de entradas"
git pull --rebase origin main
git push -u origin feature/mejora-descarga

## Descarga de ffmpeg y ffprobe

- Sitio oficial: https://ffmpeg.org/download.html
- Builds para Windows (recomendado): https://www.gyan.dev/ffmpeg/builds/

Despues de descargar, copia `ffmpeg.exe` y `ffprobe.exe` en la raiz del proyecto (mismo nivel que `app.py`).
