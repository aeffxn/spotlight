import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from spotlight.library import scan, safe_path
from spotlight.lyrics import parse_lrc
from server import Handler

class LyricsTests(unittest.TestCase):
    def test_tags_multiple_timestamps_and_malformed(self):
        lines = parse_lrc("[ti:Song]\n[00:12.50][00:15.00]Line\n[00:99.2]bad\n[xx:yy]ignored")
        self.assertEqual([(x["time"], x["text"]) for x in lines], [(12.5, "Line"), (15.0, "Line")])

class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.root = Path(self.tmp.name)
        (self.root / "song.mp3").write_bytes(b"0123456789")
        (self.root / "song.lrc").write_text("[00:01.00]Hello", encoding="utf-8")
        (self.root / "cover.jpg").write_bytes(b"fake image")

    def tearDown(self): self.tmp.cleanup()

    def test_scan_lookup_and_associated_files(self):
        rows = scan(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "song")
        self.assertEqual(rows[0]["lyrics"], "song.lrc")
        self.assertEqual(rows[0]["art"], "cover.jpg")

    def test_safe_path_rejects_traversal(self):
        with self.assertRaises(ValueError): safe_path(self.root, "../outside")

class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.root = Path(self.tmp.name)
        (self.root / "song.mp3").write_bytes(b"0123456789")
        self.tracks = scan(self.root)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.music_root = self.root
        self.server.tracks = self.tracks
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.server.server_port

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.tmp.cleanup()

    def test_http_range_and_download_headers(self):
        ident = self.tracks[0]["id"]
        response = urlopen(Request(self.base + "/media/" + ident, headers={"Range": "bytes=2-5"}))
        self.assertEqual(response.status, 206)
        self.assertEqual(response.headers["Content-Range"], "bytes 2-5/10")
        self.assertEqual(response.read(), b"2345")
        response = urlopen(self.base + "/download/" + ident)
        self.assertIn("attachment", response.headers["Content-Disposition"])

    def test_unknown_track_cannot_reach_files(self):
        with self.assertRaises(HTTPError) as err: urlopen(self.base + "/media/../../server.py")
        self.assertEqual(err.exception.code, 404)

    def test_library_json(self):
        data = json.loads(urlopen(self.base + "/api/library").read().decode("utf-8"))
        self.assertEqual(data[0]["title"], "song")

if __name__ == "__main__": unittest.main()
