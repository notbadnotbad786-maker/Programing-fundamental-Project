# NEON DRIFT — Mobile-Controlled 3D Web Racing Game

## Folder layout
# 🏎️ NEON DRIFT — Mobile-Controlled 3D Web Racing Game

A browser-based 3D racing game with a cyberpunk anime aesthetic, steered in real time using
your phone's gyroscope. No app install required — everything runs in the browser.

Steer with your **phone** (like a real steering wheel), watch the race on your **laptop**,
connected live through a lightweight **Python WebSocket server**.

---

## ✨ What Makes This Project Interesting

- **Phone as a steering wheel** — tilt your phone left/right, the car turns left/right on your
  laptop screen, in real time (no lag).
- **Anime cel-shaded visuals** — toon-shaded 3D car with hand-drawn-style black ink outlines.
- **Cyberpunk neon world** — a winding night-time highway lined with glowing pink/cyan
  billboards and skyscrapers, rendered with real bloom post-processing.
- **Drift smoke & nitro flame** — custom particle systems react to how you're driving.
- **Zero installs on the phone** — the controller is just a web page, opened in any mobile browser.
- **Keyboard fallback** — you can also test-drive with WASD directly on the laptop, no phone needed.

---

## 🧩 How It Works — The Big Picture

This project has **three separate pieces** that talk to each other over WebSockets:

```
┌─────────────────────┐        ┌──────────────────────┐        ┌─────────────────────┐
│   MOBILE CONTROLLER  │ ──────▶│    BACKEND SERVER    │──────▶ │     LAPTOP GAME      │
│   controller.html    │  /ws/  │      server.py        │  /ws/  │     index.html       │
│                      │ mobile │                      │ laptop │                      │
│  Reads phone tilt    │        │  FastAPI WebSocket    │        │  Three.js 3D scene   │
│  (gyroscope) + touch │        │  bridge — relays      │        │  renders the car,    │
│  pedals, sends JSON  │        │  messages, nothing    │        │  track, and physics  │
│  ~25 times/second    │        │  else                 │        │  based on the data   │
└─────────────────────┘        └──────────────────────┘        └─────────────────────┘
```

**In one sentence:** the phone reads your tilt angle, packages it as a tiny JSON message,
the backend forwards that message untouched to the laptop, and the laptop's JavaScript
turns that number into an actual steering wheel movement on the 3D car.

The backend is intentionally "dumb" — it doesn't know anything about cars, physics, or
graphics. It's just a **relay**. All of the actual game logic lives in the browser.

---

## 📂 Project Structure

```
neon-drift/
├── backend/
│   └── server.py         # FastAPI WebSocket server (the bridge)
├── game/
│   └── index.html         # The 3D racing game — opens on your laptop
├── mobile/
│   └── controller.html    # The steering controller — opens on your phone
└── README.md
```

> Note: depending on how you set the project up, `server.py`, `index.html`, and
> `controller.html` may all sit in one flat folder instead of separate subfolders — both
> layouts work, just make sure the paths in `server.py` match where your files actually are.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn, WebSockets |
| 3D Rendering | Three.js (WebGL) |
| Steering Input | `DeviceOrientationEvent` (gyroscope) API |
| Visual Effects | Custom toon shaders, `UnrealBloomPass`, particle systems |
| Networking | WebSocket (`ws://` / `wss://`), optionally tunneled with `ngrok` |

---

## 🚀 Getting Started

### 1. Requirements

- Python 3.9+
- A modern browser on both your laptop and your phone (Chrome recommended)
- Both devices should ideally be on the same Wi-Fi network (or use `ngrok`, see below)

### 2. Install dependencies

```bash
pip install fastapi uvicorn websockets
```

### 3. Start the backend

```bash
cd backend
python server.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Keep this terminal running for the whole session.

### 4. Open the game on your laptop

Open `game/index.html` directly in your browser (double-click works fine — it loads
Three.js from a CDN, no build step needed).

In the on-screen panel, enter your backend address:

```
192.168.x.x:8000
```

(Find your local IP with `ipconfig` on Windows or `ifconfig` / `ip a` on Mac/Linux.)
Click **Connect**.

### 5. Open the controller on your phone

**Option A — Same Wi-Fi:**
Find your laptop's local IP as above, then serve the `mobile/` folder from a simple HTTP
server and open it on your phone's browser:

```bash
cd mobile
python -m http.server 5500
```

Then visit `http://192.168.x.x:5500/controller.html` on your phone.

**Option B — Different networks (recommended if Wi-Fi sharing is inconvenient):**
Use [ngrok](https://ngrok.com) to expose the backend publicly over HTTPS:

```bash
ngrok http 8000
```

Then open `https://<your-ngrok-domain>/controller.html` on your phone, and use the same
ngrok domain (no `https://` prefix) as the backend host on both the phone and the laptop.

> ⚠️ **Important:** if the controller page is loaded over `https://`, the backend
> connection must also be secure (`wss://`), not `ws://` — browsers block "mixed content"
> connections. This is why tunneling the backend through `ngrok` too (rather than just the
> controller page) is the most reliable setup.

### 6. Drive!

- Hold your phone **sideways (landscape)**, like a steering wheel.
- Tilt left/right to steer.
- Tap and hold the on-screen **GAS** / **BRAKE** buttons.
- Use the **Re-center Steering** button if the car drifts to one side while your phone is level.
- No phone handy? Use **WASD** / arrow keys directly on the laptop instead.

---

## 🧠 How Each Piece Works (In Detail)

### Backend (`server.py`)

The backend opens two WebSocket endpoints:

- **`/ws/laptop`** — the game connects here and just listens.
- **`/ws/mobile`** — the controller connects here and sends steering data.

Whenever a message arrives on `/ws/mobile`, the server checks if a laptop is currently
connected, and if so, forwards the message to it — untouched:

```python
while True:
    data = await websocket.receive_text()
    if laptop_client:
        await laptop_client.send_text(data)
```

That's the entire "brain" of the backend. It also serves `controller.html` and
`index.html` directly, so a single `ngrok` tunnel is enough to expose the whole project.

### Laptop Game (`index.html`)

Built with **Three.js**. Key systems:

- **Toon shading** — `MeshToonMaterial` with a 4-step gradient map for flat, anime-style
  lighting instead of realistic shading.
- **Ink outlines** — every visible part is cloned, scaled up ~6%, flipped inside-out
  (`BackSide`), and painted solid black — the classic "inverted hull" outline trick.
- **Bloom** — `UnrealBloomPass` makes bright neon colors genuinely glow.
- **Track** — a closed-loop winding road generated from a `CatmullRomCurve3`, with
  procedurally placed neon billboards and towers along both sides.
- **Particles** — hand-rolled point-based systems for drift smoke (white, triggered by
  sharp turns at speed) and nitro flame (blue, triggered while accelerating).
- **Physics** — simple arcade-style speed/steering model; no real-world physics engine.
- **Networking** — connects to the backend over WebSocket, applies whatever
  `{ steer, throttle, brake }` values arrive, with keyboard (WASD) as a fallback.

### Mobile Controller (`controller.html`)

- **Gyroscope steering** — listens to `deviceorientation` events, reads the `beta` (tilt)
  angle, and maps roughly ±55° of tilt to full left/right steering lock.
- **Touch pedals** — two large press-and-hold circles for **GAS** and **BRAKE**.
- **Manual steering arrows** — two on-screen arrow buttons that override the gyroscope on
  demand, useful on devices with an unreliable or absent gyroscope.
- **Calibration** — a "Re-center Steering" button captures the current tilt as the new
  zero point, so you don't have to hold the phone at a mathematically perfect angle.
- **Update loop** — sends the current `{ steer, throttle, brake }` state as JSON over
  WebSocket roughly 25 times per second.

---

## 🎨 Visual Style

The look is a deliberate mashup of two aesthetics:

1. **Anime cel-shading** — hard-edged toon lighting + black ink outlines, like a
   hand-drawn racing anime.
2. **Cyberpunk neon** — a dark, rain-slicked night city, with pink/cyan/purple billboards
   and skyscraper windows that genuinely bloom and glow thanks to post-processing.

---

## 🐛 Problems Solved Along the Way

Building this surfaced a few real-world web development gotchas worth knowing about:

- **Mixed content blocking:** a page loaded over `https://` cannot open an insecure
  `ws://` WebSocket — it has to be `wss://`. This broke the phone controller until the
  backend was also tunneled through `ngrok`.
- **Silent keyboard fallback failure:** an early version of the game only listened to the
  keyboard when *no* WebSocket was connected at all — meaning testing with WASD stopped
  working the moment the backend connection opened, even with no phone attached. Fixed by
  always combining both keyboard and network input.
- **Local IP changing:** switching Wi-Fi networks (or even reconnecting to the same one)
  can change a laptop's local IP address, silently breaking the "same Wi-Fi" connection
  method until it's re-checked with `ipconfig`.
- **ngrok free-tier limits:** the free plan only allows one tunnel domain online at a
  time — running two separate tunnels for the game and the controller caused a domain
  collision. Solved by having the backend serve both HTML pages itself, so only one
  tunnel is ever needed.
- **Steering direction ambiguity:** gyroscope tilt sign isn't consistent across every
  phone/orientation combination, so the steering logic exposes a single
  `DIRECTION_SIGN` constant to flip left/right without touching anything else.

---

## 🔮 Possible Future Improvements

- Lap timing and checkpoints
- Track-edge collision instead of free-roam driving
- Multiplayer (multiple phones racing the same track)
- Swappable car models / liveries
- Sound effects and background music
- Mobile-native haptic feedback on collisions

---

## 📄 License

This project was built as a personal / academic project. Feel free to fork it, learn
from it, or extend it for your own coursework.

---

## 🙌 Credits

Built by a Computer Science student as a hands-on project exploring real-time WebSocket
communication, Three.js 3D rendering, and mobile sensor APIs — combining a Python
Fundamentals lab-style project with a self-directed dive into game development on the web.
