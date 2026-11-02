"""Spotlight: self-hosted LAN music player (Python standard library)."""
import argparse
import json
import mimetypes
import os
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from spotlight.library import scan, safe_path
from spotlight.lyrics import parse_lrc

HERE = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    server_version = "Spotlight/1.0"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/library":
            return self.json(self.server.tracks)
        if path == "/api/refresh":
            self.server.tracks = scan(self.server.music_root)
            return self.json(self.server.tracks)
        if path.startswith("/api/lyrics/"):
            track = self.track(path.rsplit("/", 1)[-1])
            if not track or not track.get("lyrics"):
                return self.send_error(404, "No LRC file")
            try:
                data = safe_path(self.server.music_root, track["lyrics"]).read_text(encoding="utf-8-sig")
                return self.json(parse_lrc(data))
            except (OSError, ValueError):
                return self.send_error(404, "Lyrics unavailable")
        if path.startswith("/media/"):
            track = self.track(path.rsplit("/", 1)[-1])
            if not track:
                return self.send_error(404, "Unknown track")
            return self.file_response(track["path"], track["type"], False)
        if path.startswith("/art/"):
            track = self.track(path.rsplit("/", 1)[-1])
            if not track or not track.get("art"):
                return self.send_error(404, "No artwork")
            return self.file_response(track["art"], mimetypes.guess_type(track["art"])[0] or "application/octet-stream", False)
        if path.startswith("/download/"):
            track = self.track(path.rsplit("/", 1)[-1])
            if not track:
                return self.send_error(404, "Unknown track")
            return self.file_response(track["path"], track["type"], True)
        self.directory = str(HERE / "web")
        return super().do_GET()

    def track(self, ident):
            return next((row for row in self.server.tracks if row["id"] == ident), None)

    def json(self, value):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def file_response(self, relative, content_type, attachment):
        try:
            path = safe_path(self.server.music_root, relative)
            size = path.stat().st_size
            start, end, status = 0, size - 1, 200
            range_header = self.headers.get("Range")
            if range_header:
                unit, _, spec = range_header.partition("=")
                if unit != "bytes" or "," in spec:
                    return self.send_error(416, "Unsupported byte range")
                first, dash, last = spec.partition("-")
                if not dash:
                    return self.send_error(416, "Invalid byte range")
                if first:
                    start = int(first)
                    end = min(int(last), size - 1) if last else size - 1
                elif last:
                    start = max(0, size - int(last))
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", "bytes */%d" % size)
                    self.end_headers()
                    return
                status = 206
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            if status == 206:
                self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
            if attachment:
                self.send_header("Content-Disposition", "attachment; filename*=UTF-8''%s" % __import__("urllib.parse", fromlist=["quote"]).quote(Path(relative).name))
            self.end_headers()
            with path.open("rb") as stream:
                stream.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = stream.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (OSError, ValueError, OverflowError):
            self.send_error(404, "File unavailable")

def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(description="Host your music locally with Spotlight")
    parser.add_argument("--music", default=os.environ.get("SPOTLIGHT_MUSIC", str(HERE / "music")), help="Music library directory")
    parser.add_argument("--host", default="127.0.0.1", help="Bind to 0.0.0.0 to allow LAN devices")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(args.music).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.music_root = root
    server.tracks = scan(root)
    ip = lan_ip() if args.host == "0.0.0.0" else args.host
    print("Spotlight is serving %s" % root)
    print("On this laptop: http://127.0.0.1:%d" % args.port)
    print("On the same Wi-Fi: http://%s:%d" % (ip, args.port))
    print("Press Ctrl+C to stop. Use only on a trusted local network.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Spotlight...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
