"""Library scanning and safe ID mapping."""
import hashlib
import os
from pathlib import Path

AUDIO = {".mp3", ".m4a", ".aac", ".wav", ".aif", ".aiff"}
ART = {".jpg", ".jpeg", ".png", ".gif"}

def scan(root):
    base = Path(root).resolve()
    tracks = []
    if not base.is_dir():
        return tracks
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in AUDIO:
            continue
        rel = path.relative_to(base).as_posix()
        ident = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:16]
        title = path.stem
        artist = "Unknown Artist"
        album = "Unknown Album"
        duration = 0
        try:
            from mutagen import File as MutagenFile
            audio = MutagenFile(str(path), easy=True)
            if audio:
                title = (audio.get("title") or [title])[0]
                artist = (audio.get("artist") or [artist])[0]
                album = (audio.get("album") or [album])[0]
                duration = int(getattr(audio.info, "length", 0))
        except Exception:
            pass
        art = next((p for p in path.parent.iterdir() if p.is_file() and p.suffix.lower() in ART), None)
        lrc = path.with_suffix(".lrc")
        tracks.append({"id": ident, "title": str(title), "artist": str(artist), "album": str(album),
                       "duration": duration, "path": rel, "art": art.relative_to(base).as_posix() if art else None,
                       "lyrics": lrc.relative_to(base).as_posix() if lrc.is_file() else None,
                       "type": {".mp3":"audio/mpeg", ".m4a":"audio/mp4", ".aac":"audio/aac", ".wav":"audio/wav", ".aif":"audio/aiff", ".aiff":"audio/aiff"}[path.suffix.lower()]})
    return sorted(tracks, key=lambda t: (t["artist"].lower(), t["album"].lower(), t["title"].lower()))

def safe_path(root, relative):
    base = Path(root).resolve()
    candidate = (base / relative).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("Path outside library")
    if not candidate.is_file():
        raise FileNotFoundError(relative)
    return candidate
