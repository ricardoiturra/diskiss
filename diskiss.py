import os
import sys
import subprocess
import yt_dlp
from rich.console import Console
import typer

def resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller."""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Ruta a ffmpeg y ffprobe (relativa al script)
ffmpeg_path = resource_path("ffmpeg.exe")
ffprobe_path = resource_path("ffprobe.exe")

# Verifica que los archivos existan
if not os.path.exists(ffmpeg_path):
    raise FileNotFoundError(f"ffmpeg.exe no encontrado en {ffmpeg_path}")
if not os.path.exists(ffprobe_path):
    raise FileNotFoundError(f"ffprobe.exe no encontrado en {ffprobe_path}")

# Usa ffmpeg o ffprobe en tu script
subprocess.run([ffmpeg_path, "-version"])
subprocess.run([ffprobe_path, "-version"])

app = typer.Typer()
console = Console()

# Crear carpetas si no existen
if not os.path.exists('mp3'):
    os.makedirs('mp3')
if not os.path.exists('mp4'):
    os.makedirs('mp4')

# Variable global para almacenar el nombre de la última canción descargada
ultima_cancion = ''

# Función para mostrar el mensaje de descarga solo una vez por canción
def mostrar_descarga(nombre_archivo):
    global ultima_cancion
    # Eliminar la extensión del archivo
    nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
    if nombre_sin_extension != ultima_cancion:
        console.print(f"[cyan][Descargando] {nombre_sin_extension}[/cyan]")
        ultima_cancion = nombre_sin_extension

# Configuración de yt-dlp para mostrar el progreso con un mensaje simple
class SimpleLogger:
    def __init__(self):
        pass

    def debug(self, msg):
        pass

    def warning(self, msg):
        console.print(f"[yellow]Warning: {msg}[/yellow]")

    def error(self, msg):
        console.print(f"[red]Error: {msg}[/red]")

    def info(self, msg):
        pass  # No usamos este método para mostrar el progreso

def download_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join('mp3', '%(title)s.%(ext)s'),
        'logger': SimpleLogger(),
        'progress_hooks': [lambda d: mostrar_descarga(d.get('filename', 'Archivo'))],
        'ffmpeg_location': ffmpeg_path,  # Especifica la ruta de ffmpeg
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        console.print(f"[red]Error al descargar: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")

def download_playlist_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join('mp3', '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
        'logger': SimpleLogger(),
        'progress_hooks': [lambda d: mostrar_descarga(d.get('filename', 'Archivo'))],
        'ffmpeg_location': ffmpeg_path,  # Especifica la ruta de ffmpeg
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        console.print(f"[red]Error al descargar: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")

def download_mp4(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join('mp4', '%(title)s.%(ext)s'),
        'logger': SimpleLogger(),
        'progress_hooks': [lambda d: mostrar_descarga(d.get('filename', 'Archivo'))],
        'ffmpeg_location': ffmpeg_path,  # Especifica la ruta de ffmpeg
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        console.print(f"[red]Error al descargar: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")

def download_playlist_mp4(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join('mp4', '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
        'logger': SimpleLogger(),
        'progress_hooks': [lambda d: mostrar_descarga(d.get('filename', 'Archivo'))],
        'ffmpeg_location': ffmpeg_path,  # Especifica la ruta de ffmpeg
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        console.print(f"[red]Error al descargar: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error inesperado: {e}[/red]")

@app.command()
def main():
    while True:
        console.print("[bold magenta]YouTube Downloader[/bold magenta]", justify="center")
        console.print("1) Descargar una canción (mp3)", style="bold cyan")
        console.print("2) Descargar toda una playlist (mp3)", style="bold cyan")
        console.print("3) Descargar un video (mp4)", style="bold cyan")
        console.print("4) Descargar toda una playlist (mp4)", style="bold cyan")
        console.print("5) Salir", style="bold red")
        choice = input("Selecciona una opción: ")

        if choice == '1':
            url = input("Introduce la URL de la canción: ")
            download_mp3(url)
        elif choice == '2':
            url = input("Introduce la URL de la playlist: ")
            download_playlist_mp3(url)
        elif choice == '3':
            url = input("Introduce la URL del video: ")
            download_mp4(url)
        elif choice == '4':
            url = input("Introduce la URL de la playlist: ")
            download_playlist_mp4(url)
        elif choice == '5':
            break
        else:
            console.print("Opción no válida. Inténtalo de nuevo.", style="bold red")

if __name__ == "__main__":
    app()