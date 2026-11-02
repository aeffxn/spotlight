# 🎧 Spotlight

![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square&logo=python&logoColor=black)
![Player](https://img.shields.io/badge/Player-HTML5%20Audio-black?style=flat-square)
![Lyrics](https://img.shields.io/badge/Lyrics-Synced%20LRC-orange?style=flat-square)
![Hosting](https://img.shields.io/badge/Hosting-Self--Hosted-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Early%20Build-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-black?style=flat-square)

Spotlight is a small, self-hosted music player for a laptop and the tablet on the same Wi-Fi. Your music stays on your computer; the browser streams it, reads local timed lyrics, and lets cover art set the room’s colour.

> Legacy-browser note: Spotlight is written with ES5 JavaScript and basic HTML/CSS, but it has **not** been physically tested on an original iPad mini running iOS 9.3.5. Use the compatibility probe and your own device before relying on it.

## Contents

- [✨ Features](#-features)
- [🎨 Dynamic Album-Art Themes](#-dynamic-album-art-themes)
- [🎤 Synchronized Lyrics](#-synchronized-lyrics)
- [📥 Streaming & Downloads](#-streaming--downloads)
- [🛠 Requirements](#-requirements)
- [📦 Installation](#-installation)
- [🚀 Running Spotlight](#-running-spotlight)
- [📱 Connecting from Another Device](#-connecting-from-another-device)
- [📂 Project Structure](#-project-structure)
- [⚙️ How It Works](#-how-it-works)
- [🎵 Supported Music Formats](#-supported-music-formats)
- [📝 LRC Lyrics Format](#-lrc-lyrics-format)
- [🔒 Security & Privacy](#-security--privacy)
- [🧪 Testing](#-testing)
- [🚧 Planned / Coming Soon](#-planned--coming-soon)
- [➕ Contributing](#-contributing)
- [License](#license)

## ✨ Features

- Browse, search, and stream tracks over your home network.
- Browse the collection by artist or album, and create browser-local playlists.
- Touch-friendly play, pause, previous, next, seek, shuffle, repeat, and volume controls.
- Queue tracks and save favourites in the browser.
- Load matching LRC files and follow lyrics as the song plays.
- Use nearby image files as artwork and derive an ambient accent locally in the browser.
- Serve progressive audio with HTTP byte-range responses for seeking.
- Download links use regular browser file handling; Spotlight does not claim managed offline storage.
- Python standard library server. `mutagen` is optional for richer tags and duration.

## 🎨 Dynamic Album-Art Themes

Place a `.jpg`, `.jpeg`, `.png`, or `.gif` image alongside a track. The first image in that folder is used for the folder’s tracks. The browser samples a small canvas copy and adjusts the ambient wash. If browser canvas access is blocked, the player keeps its warm default palette. Embedded image extraction is not implemented yet; use a sidecar image.

## 🎤 Synchronized Lyrics

Put an UTF-8 `.lrc` file beside the audio file, with the same base name (`Blue Hour.mp3` and `Blue Hour.lrc`). Timestamps and multiple timestamps on one line are supported. The current line follows audio time, including after seeks. Unsupported or malformed timestamps are skipped. Lyrics stay local; no lyrics service or bundled copyrighted text is used.

## 📥 Streaming & Downloads

Audio remains on the host and is sent in chunks. The server honors single HTTP byte ranges. Each track has a regular download URL with an attachment filename. Browser behavior depends on the browser and OS. iOS 9 Safari predates its download manager and support for the HTML `download` attribute (added to iOS Safari in iOS 13); it may open the audio instead of saving it. Spotlight cannot select a destination folder, guarantee permanent storage, or index downloaded files on iOS 9. Try the browser’s “Open In”/share action if offered. Test with your own iPad before depending on downloads.

## 🛠 Requirements

- Python 3.10 or newer recommended (the server itself uses the standard library).
- A music folder with MP3 recommended for old iOS Safari; AAC/M4A may also work.
- Laptop and playback device on the same trusted Wi-Fi network.
- For richer track metadata, install optional `mutagen` with `python -m pip install -r requirements.txt`.

Apple documents MP3, AAC-LC/HE-AAC, WAV, and AIFF audio for iOS Safari. Codec details within a file can still affect playback. Use the probe with your real files. See [Apple’s iOS media notes](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Device-SpecificConsiderations/Device-SpecificConsiderations.html).

## 📦 Installation

Download or clone the project. On Windows, optional metadata can be installed from PowerShell:

```powershell
py -3 -m pip install -r requirements.txt
```

Put music in `Spotlight/music/`, or select a directory with `--music`. Keep private music outside version control; the default `.gitignore` excludes the local `music/` folder.

## 🚀 Running Spotlight

On Windows, double-click `Start-Spotlight.bat`. On macOS/Linux:

```sh
python3 server.py --music "$HOME/Music"
```

The server CLI defaults to loopback only. The Windows launcher explicitly enables LAN access (`0.0.0.0`) at port 8765 for the iPad workflow. On macOS/Linux, add `--host 0.0.0.0` to enable LAN access. The terminal prints a loopback address and a likely LAN address. If the LAN address is wrong, find the laptop’s Wi-Fi IPv4 address in network settings and use that. Allow Python through the private-network firewall prompt.

First visit `/compat.html` and tap “Load sample from library”. Check connection, playback, seek, artwork, LRC loading, and download behavior before using the main player. The probe loads the first library track and its first lyric lines.

## 📱 Connecting from Another Device

Open `http://LAPTOP-IP:8765/` in Safari on the same Wi-Fi. Replace `LAPTOP-IP` with the address printed by the server. Use the compatibility page first. Playback starts only after a tap. Do not expose port 8765 to the public internet.

## 📂 Project Structure

```text
Spotlight/
├── README.md, LICENSE, requirements.txt, Start-Spotlight.bat
├── server.py
├── spotlight/        # library scanning and LRC parsing
├── web/              # ES5 UI, styles, artwork placeholder, probe
└── tests/            # Python unittest coverage
```

## ⚙️ How It Works

The Python server scans the configured music root at startup and on explicit refresh. Track IDs are derived from relative paths; browser requests address IDs, not arbitrary paths. Library metadata, audio, art, and lyrics are served from that root only. The web client uses one HTML audio element. Favourites persist in browser local storage; the queue and current playback are held in page memory.

## 🎵 Supported Music Formats

The library recognizes MP3, M4A, AAC, WAV, AIF, and AIFF. The old-device recommendation is MP3. Spotlight does not transcode: if the iPad cannot decode a file, it reports a playback error. Metadata comes from optional Mutagen when available; otherwise title is the filename and artist/album are “Unknown”. Embedded artwork is not extracted; sidecar images are supported.

## 📝 LRC Lyrics Format

```text
[ti:Example Song]
[ar:Example Artist]
[00:12.50]First line
[00:16.20][00:18.00]A line with two timings
```

No copyrighted sample lyrics are included.

## 🔒 Security & Privacy

The service exposes the configured music directory to anyone who can reach the listening port. Bind/firewall it to a trusted private network and do not port-forward it. The app rejects unknown track IDs, canonicalizes file paths, and supports only a configured library root. Local HTTP is not encrypted; other devices on an untrusted Wi-Fi network may observe requests and audio. There is no login or TLS layer.

## 🧪 Testing

Run `python -m unittest discover -s tests -v`. Tests cover LRC tags/timestamps, library scanning, sidecars, path traversal, library JSON, byte ranges, and download headers. `python -m py_compile server.py spotlight/*.py` checks Python syntax. The compatibility probe is available at `/compat.html`.

Desktop checks cannot establish iOS 9 behavior. No original iPad mini was available during this build, so physical playback, touch, and file-saving behavior remain unverified.

## 🚧 Planned / Coming Soon

- Embedded album-art extraction.
- Queue editing and previous-track history.
- More device-specific verification and a broader media test set.

## ➕ Contributing

Issues and focused pull requests are welcome. Please include the browser/OS and a reproduction for compatibility reports. Do not submit copyrighted music or lyrics.

## License

Spotlight is released under the MIT License. See [LICENSE](LICENSE).
