"""Small, defensive LRC parser."""
import re

STAMP = re.compile(r"\[(\d{1,3}):(\d{1,2})(?:\.(\d{1,3}))?\]")

def parse_lrc(text):
    lines = []
    for raw in (text or "").replace("\r", "").split("\n"):
        stamps = STAMP.findall(raw)
        if not stamps:
            continue
        lyric = STAMP.sub("", raw).strip()
        for minute, second, fraction in stamps:
            sec = int(second)
            if sec >= 60:
                continue
            frac = (fraction or "0")
            millis = int((frac + "00")[:2]) / 100.0
            lines.append({"time": int(minute) * 60 + sec + millis, "text": lyric})
    return sorted(lines, key=lambda row: row["time"])
