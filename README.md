# 🪄 Gandalf Beat Sync

> A small local tool that makes Gandalf nod in time with your currently playing song.  
> Powered by Python + WebSockets + React. Developed for macOS with **BlackHole** audio routing.
> And don't worry, no aubio needed! Works out of the box without fiddling around with stuff you really not want to see.
> This setup skips it and uses scipy + numpy.
---

## 🛠 Prerequisites

### 📦 Python

- Python 3.11+
- Virtual environment recommended (`venv`)

### 📦 React & Vite

- Tested with Node 23.11 and npm 10.9, but should work with older versions

### 🎧 Audio Routing

- **BlackHole (2ch)** for macOS → https://existential.audio/blackhole/
  - Create an **Aggregated Device** (e.g. "BlackHole + <your-audio-device>")
  - In audio settings → select this aggregate as input source
  - Route audio from your system sources (e.g. Spotify, browser) there

---

## 📦 Installation

```bash
# Clone repository
git clone <repo-url>
cd gandalf-bpm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Start the Backend

```python backend/bpm_server.py```

Output looks like this

```
🎧 Starting stream and WebSocket on ws://<HOST>:<PORT>
Max value: 0.0094 | Peaks: 10
🎵 Detected BPM: 134.23
```


---

## 🎛 Start Frontend

Make sure [Node.js](https://nodejs.org/) and `npm` or `pnpm` is installed. Should work with bun too, haven't checked that.

```bash
cd frontend
npm install
npm run dev
```

Now Vite runs at `http://localhost:5173`:

- Gandalf nods
- Playbackrate is dynamicly adjusted via `WebSocket` and the submitted bpm result from the python backend

---

## 🧪 Debugging & Tipps

- 🎚 If no peaks are detected:
  - BlackHole too quiet? → Test with sound from YouTube and OBS recording
  - Threshold too high? → Dynamically set in code, but still adjustable
- 🎥 Video stuttering? Make sure:
  - `muted`, `autoplay`, `loop` are set in the `<video>` tag
- 🔊 No signal?
  - Check in the **Audio MIDI Setup** if BlackHole is really being used

---
