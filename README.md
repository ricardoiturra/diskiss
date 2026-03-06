# Diskiss

Diskiss es un descargador de YouTube para Windows con dos modos:
- Interfaz grafica (`app.py`) usando `pywebview`.
- Modo consola (`diskiss.py`) con menu interactivo.

Permite descargar:
- Video individual en MP3.
- Video individual en MP4.
- Playlist en MP3.
- Playlist en MP4.
- Seleccion parcial de elementos de una playlist (solo GUI).

## Requisitos

- Windows.
- Python 3.10+.
- `ffmpeg.exe` y `ffprobe.exe` en la raiz del proyecto.

## Descargar ffmpeg y ffprobe

- Sitio oficial: https://ffmpeg.org/download.html
- Builds para Windows (recomendado): https://www.gyan.dev/ffmpeg/builds/

Pasos:
1. Descarga y extrae el paquete.
2. Copia `ffmpeg.exe` y `ffprobe.exe` en la raiz del repo (junto a `app.py`).

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install yt-dlp pywebview typer rich
```

## Uso de la interfaz grafica

```powershell
python app.py
```

Flujo:
1. Elige tipo de descarga (MP3, MP4, playlist MP3 o playlist MP4).
2. Pega la URL.
3. Si es playlist, carga los items y marca los que quieras.
4. Inicia la descarga y revisa el estado.
5. Puedes cancelar durante el proceso.

Salidas:
- MP3: carpeta `mp3/`.
- MP4: carpeta `mp4/`.
- Playlists: subcarpetas dentro de `mp3/` o `mp4/`.

## Uso por consola

```powershell
python diskiss.py
```

El menu permite elegir descarga de audio/video individual o playlist completa.

## Estructura principal

- `app.py`: backend Python y API para la UI.
- `front/`: interfaz HTML/CSS/JS.
- `diskiss.py`: modo CLI.
- `mp3/` y `mp4/`: carpetas de salida (se crean automaticamente).

## Errores comunes

- `FileNotFoundError: ffmpeg.exe no encontrado...`
  - Falta `ffmpeg.exe` en la raiz del proyecto.
- `FileNotFoundError: ffprobe.exe no encontrado...`
  - Falta `ffprobe.exe` en la raiz del proyecto.
- Error al descargar contenido de YouTube:
  - Actualiza `yt-dlp`: `pip install -U yt-dlp`.
