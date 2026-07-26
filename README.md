# NEON DRIFT — Mobile-Controlled 3D Web Racing Game

## Folder layout
```
D:\mobile-racing-project\
├── backend\server.py       (FastAPI WebSocket bridge)
├── game\index.html         (Three.js game — open on laptop)
└── mobile\controller.html  (Gyro steering + pedals — open on phone)
```

## 1. Run the backend
```powershell
cd D:\mobile-racing-project\backend
python -m pip install fastapi uvicorn websockets --break-system-packages
python server.py
```
It listens on `0.0.0.0:8000`.

## 2. Find your laptop's local IP
```powershell
ipconfig
```
Look for the `IPv4 Address` on your Wi-Fi adapter, e.g. `192.168.1.5`.
Phone and laptop must be on the **same Wi-Fi network** for this to work without ngrok.

## 3. Open the game on your laptop
Open `game\index.html` directly in Chrome/Edge (double-click works — it's a static file using CDN Three.js modules).
In the top-left panel, type your backend host, e.g.:
```
192.168.1.5:8000
```
Click **CONNECT**.

## 4. Serve the mobile controller to your phone
Phones can't open a `file://` HTML page and use the gyroscope reliably over plain HTTP on some browsers — easiest is ngrok, same pattern as your PF gun-game project:
```powershell
cd D:\mobile-racing-project\mobile
python -m http.server 5500
.\ngrok.exe http 5500
```
Open the printed `https://xxxx.ngrok-free.app` URL on your phone.

On the controller page, enter the **same backend host** (`192.168.1.5:8000` or the backend's own ngrok URL if you tunnel the backend too), tap **ENABLE MOTION + CONNECT**, allow the motion permission prompt (iOS), rotate to landscape, and hold the phone like a wheel.

## Controls
- **Steering:** tilt phone left/right (landscape "wheel" hold)
- **Gas / Brake:** big touch buttons, bottom-right / bottom-left
- **Laptop fallback (no phone needed for testing):** WASD or Arrow keys

## Notes / next steps
- The car currently drives freely rather than being hard-locked to the spline — the road is a full winding cyberpunk track for visuals and camera framing works well following it, but there's no wall collision yet. Natural next step: add track-edge collision or a lap/checkpoint system using the `trackCurve` already defined in `game/index.html`.
- Drift smoke triggers automatically at high steering + speed; nitro flame runs continuously while accelerating (no separate nitro button, per your control spec).
- Bloom, toon shading (`MeshToonMaterial` + inverted-hull black outlines), and the neon billboard/tower generation are all tunable — the relevant constants are near the top of each section in `index.html` (`ROAD_WIDTH`, `neonColors`, `bloomPass` params, `carState`).
