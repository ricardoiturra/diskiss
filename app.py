import os
import sys
import threading
import yt_dlp
import webview
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Función para obtener la ruta absoluta de los archivos cuando se empaquete con PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Rutas de ffmpeg y ffprobe
ffmpeg_path = resource_path("ffmpeg.exe")
ffprobe_path = resource_path("ffprobe.exe")

# Verificar que ffmpeg y ffprobe existen antes de continuar
if not os.path.exists(ffmpeg_path):
    raise FileNotFoundError(f"ffmpeg.exe no encontrado en {ffmpeg_path}")
if not os.path.exists(ffprobe_path):
    raise FileNotFoundError(f"ffprobe.exe no encontrado en {ffprobe_path}")

# Crear carpetas de descarga si no existen
os.makedirs("mp3", exist_ok=True)
os.makedirs("mp4", exist_ok=True)

class SimpleLogger:
    def debug(self, msg): pass
    def warning(self, msg): print(f"[WARNING] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")

class API:
    def __init__(self):
        self.download_thread = None
        self.cancel_requested = False
        self.status = {
            "state": "idle",
            "message": "",
            "current": 0,
            "total": 0,
        }
        self.current_files = set()
        self.current_title = ""

    def _extract_percent(self, d):
        try:
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes")
            if total and downloaded is not None:
                return f"{(downloaded / total) * 100:.1f}%"
        except Exception:
            pass

        percent_str = d.get("_percent_str") or ""
        percent_str = re.sub(r"\x1b\[[0-9;]*m", "", percent_str)
        match = re.search(r"(\d+(?:\.\d+)?)%", percent_str)
        if match:
            return f"{match.group(1)}%"
        return ""

    def download(self, request):
        parts = request.split("***")
        if len(parts) < 2:
            return "[ERROR] Formato de solicitud inválido"
        download_type = parts[0]
        url = parts[1]
        playlist_dir = parts[2].strip() if len(parts) > 2 else ""
        print(f"\n[INFO] Iniciando descarga: {download_type} - URL: {url}")

        if download_type == "mp3":
            return self.download_mp3(url)
        elif download_type == "playlist_mp3":
            return self.download_playlist_mp3(url, playlist_dir)
        elif download_type == "mp4":
            return self.download_mp4(url)
        elif download_type == "playlist_mp4":
            return self.download_playlist_mp4(url, playlist_dir)
        return "[ERROR] Tipo de descarga desconocido"

    def download_single(self, data):
        if self.download_thread and self.download_thread.is_alive():
            return "[ERROR] Ya hay una descarga en curso"

        download_type = data.get("format") or ""
        url = (data.get("url") or "").strip()
        if not url:
            return "[ERROR] URL inválida"
        if download_type not in ("mp3", "mp4"):
            return "[ERROR] Tipo de descarga inválido"

        self.cancel_requested = False
        self.status = {
            "state": "running",
            "message": "Iniciando...",
            "current": 1,
            "total": 1,
        }

        thread = threading.Thread(
            target=self._run_single_download,
            args=(download_type, url),
            daemon=True,
        )
        self.download_thread = thread
        thread.start()
        return "Descarga iniciada"

    def get_playlist_items(self, url):
        url = self._normalize_playlist_index(url)
        ydl_opts = {
            "extract_flat": "in_playlist",
            "skip_download": True,
            "quiet": True,
            "ignoreerrors": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if not info or "entries" not in info:
                return {"error": "No se pudo leer la playlist"}
            items = []
            for entry in info.get("entries", []):
                if not entry:
                    continue
                item_url = entry.get("url") or entry.get("webpage_url")
                item_id = entry.get("id") or ""
                title = entry.get("title") or "Sin titulo"
                if item_url and not item_url.startswith("http"):
                    item_url = f"https://www.youtube.com/watch?v={item_url}"
                items.append({
                    "id": item_id,
                    "title": title,
                    "url": item_url or "",
                })
            return {"title": info.get("title") or "", "items": items}
        except Exception as e:
            return {"error": f"Error al leer playlist: {e}"}

    def _normalize_playlist_index(self, url):
        try:
            parts = urlsplit(url)
            query = parse_qsl(parts.query, keep_blank_values=True)
            filtered = [(k, v) for (k, v) in query if k.lower() not in ("start_radio", "rv", "playnext", "t")]
            filtered = [(k, v) for (k, v) in filtered if k.lower() != "index"]
            filtered.append(("index", "1"))
            new_query = urlencode(filtered, doseq=True)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
        except Exception:
            return url


    def get_status(self):
        return self.status

    def cancel_download(self):
        self.cancel_requested = True
        return "OK"

    def download_selected(self, data):
        if self.download_thread and self.download_thread.is_alive():
            return "[ERROR] Ya hay una descarga en curso"

        items = data.get("items") or []
        download_type = data.get("format") or ""
        playlist_dir = (data.get("dir") or "").strip()

        if not items:
            return "[ERROR] No hay elementos seleccionados"
        items = [item for item in items if (item.get("url") or "").strip()]
        if not items:
            return "[ERROR] No hay URLs válidas en la selección"
        if download_type not in ("playlist_mp3", "playlist_mp4"):
            return "[ERROR] Tipo de descarga inválido"

        self.cancel_requested = False
        self.status = {
            "state": "running",
            "message": "Iniciando...",
            "current": 0,
            "total": len(items),
        }

        thread = threading.Thread(
            target=self._run_selected_downloads,
            args=(download_type, items, playlist_dir),
            daemon=True,
        )
        self.download_thread = thread
        thread.start()
        return "Descarga iniciada"

    def _run_selected_downloads(self, download_type, items, playlist_dir):
        folder = "mp3" if download_type == "playlist_mp3" else "mp4"
        base_dir = os.path.join(folder, playlist_dir) if playlist_dir else folder
        total_items = len(items)
        digits = len(str(total_items)) if total_items > 0 else 1
        attempted = 0
        downloaded = 0

        def track_file(path):
            if path:
                self.current_files.add(path)

        def cleanup_current_files():
            for path in list(self.current_files):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
            self.current_files.clear()

        def hook(d):
            filename = d.get("filename")
            tmpfilename = d.get("tmpfilename")
            if filename:
                track_file(filename)
            if tmpfilename:
                track_file(tmpfilename)

            if self.cancel_requested:
                cleanup_current_files()
                raise yt_dlp.utils.DownloadError("CANCEL_ALL")
            if d.get("status") == "downloading":
                percent = self._extract_percent(d)
                if percent:
                    self.status["message"] = f"{self.current_title} {percent}"
                else:
                    self.status["message"] = self.current_title

        def post_hook(d):
            filepath = d.get("filepath")
            track_file(filepath)

        base_opts = {
            "logger": SimpleLogger(),
            "ffmpeg_location": os.path.dirname(ffmpeg_path),
            "progress_hooks": [hook],
            "postprocessor_hooks": [post_hook],
            "outtmpl": {
                "default": os.path.join(base_dir, "%(title)s.%(ext)s")
            },
        }

        if download_type == "playlist_mp3":
            base_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
            })
        else:
            base_opts.update({
                "format": "bestvideo+bestaudio/best",
            })

        try:
            with yt_dlp.YoutubeDL(base_opts) as ydl:
                for idx, item in enumerate(items, start=1):
                    if self.cancel_requested:
                        break
                    self.current_files.clear()
                    title = item.get("title") or "Elemento"
                    url = item.get("url") or ""
                    self.current_title = f"{idx}/{len(items)} - {title}"
                    self.status["current"] = idx
                    self.status["message"] = self.current_title
                    if not url:
                        continue
                    attempted += 1
                    prefix = f"{idx:0{digits}d}- "
                    ydl.params["outtmpl"]["default"] = os.path.join(base_dir, f"{prefix}%(title)s.%(ext)s")
                    try:
                        ydl.download([url])
                        downloaded += 1
                    except yt_dlp.utils.DownloadError as e:
                        msg = str(e)
                        if "CANCEL_ALL" in msg:
                            self.cancel_requested = True
                            break
                        self.status["message"] = f"Error en '{title}': {e}"
                        continue
        finally:
            if self.cancel_requested:
                self.status["state"] = "cancelled"
                self.status["message"] = "Descarga cancelada"
            else:
                if attempted == 0:
                    self.status["state"] = "error"
                    self.status["message"] = "No se encontraron URLs válidas para descargar"
                elif downloaded == 0:
                    self.status["state"] = "error"
                    self.status["message"] = "No se pudo descargar ningún elemento"
                else:
                    self.status["state"] = "done"
                    self.status["message"] = "Descarga completada"

    def _run_single_download(self, download_type, url):
        folder = "mp3" if download_type == "mp3" else "mp4"

        def track_file(path):
            if path:
                self.current_files.add(path)

        def cleanup_current_files():
            for path in list(self.current_files):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
            self.current_files.clear()

        def hook(d):
            filename = d.get("filename")
            tmpfilename = d.get("tmpfilename")
            if filename:
                track_file(filename)
            if tmpfilename:
                track_file(tmpfilename)

            if self.cancel_requested:
                cleanup_current_files()
                raise yt_dlp.utils.DownloadError("CANCEL_ALL")
            if d.get("status") == "downloading":
                percent = self._extract_percent(d)
                if percent:
                    self.status["message"] = f"{self.current_title} {percent}"
                else:
                    self.status["message"] = self.current_title

        def post_hook(d):
            filepath = d.get("filepath")
            track_file(filepath)

        ydl_info_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "ignoreerrors": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            title = (info or {}).get("title") or "Descargando"
        except Exception:
            title = "Descargando"

        self.current_title = title
        self.status["message"] = title

        base_opts = {
            "logger": SimpleLogger(),
            "ffmpeg_location": os.path.dirname(ffmpeg_path),
            "progress_hooks": [hook],
            "postprocessor_hooks": [post_hook],
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "noplaylist": True,
        }

        if download_type == "mp3":
            base_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
            })
        else:
            base_opts.update({
                "format": "bestvideo+bestaudio/best",
            })

        try:
            with yt_dlp.YoutubeDL(base_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "CANCEL_ALL" in msg:
                self.cancel_requested = True
            else:
                self.status["message"] = f"Error: {e}"
        finally:
            if self.cancel_requested:
                self.status["state"] = "cancelled"
                self.status["message"] = "Descarga cancelada"
            else:
                if self.status["state"] != "cancelled":
                    self.status["state"] = "done"
                    if "Error" not in self.status["message"]:
                        self.status["message"] = "Descarga completada"
    def download_mp3(self, url):
        return self._download(url, 'mp3', {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }]
        })
    
    def download_playlist_mp3(self, url, playlist_dir=""):
        outtmpl = os.path.join('mp3', '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s')
        if playlist_dir:
            outtmpl = os.path.join('mp3', playlist_dir, '%(playlist_index)s - %(title)s.%(ext)s')
        return self._download(url, 'mp3', {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }],
            'outtmpl': outtmpl
        })
    
    def download_mp4(self, url):
        return self._download(url, 'mp4', {
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
        })
    
    def download_playlist_mp4(self, url, playlist_dir=""):
        outtmpl = os.path.join('mp4', '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s')
        if playlist_dir:
            outtmpl = os.path.join('mp4', playlist_dir, '%(playlist_index)s - %(title)s.%(ext)s')
        return self._download(url, 'mp4', {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': outtmpl
        })
    
    def _download(self, url, folder, options):
        log_path = "log.txt"

        if 'outtmpl' not in options:
            options['outtmpl'] = os.path.join(folder, '%(title)s.%(ext)s')
        options.update({
            'logger': SimpleLogger(),
            'ffmpeg_location': os.path.dirname(ffmpeg_path)
        })

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                with open(log_path, "w") as log_file:
                    sys.stdout = log_file  # Redirigir salida
                    sys.stderr = log_file
                    ydl.download([url])
                    sys.stdout = sys.__stdout__  # Restaurar salida
                    sys.stderr = sys.__stderr__

            return "Descarga completada"
        except yt_dlp.utils.DownloadError as e:
            return f"Error en la descarga (ver log.txt): {e}"
        except Exception as e:
            return f"Error inesperado (ver log.txt): {e}"


api = API()
html_path = resource_path(os.path.join("front", "index.html"))

if __name__ == "__main__":
    webview.create_window("Diskiss - Descarga música desde YouTube", html_path, js_api=api, width=1100, height=800)
    webview.start(debug=False)
