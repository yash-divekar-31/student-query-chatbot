# Screenshot Capture Guide

Run the backend and frontend before capturing images.

```powershell
# Terminal 1
Set-Location .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2
Set-Location .\frontend
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173` and capture the following real application states:

1. `main-interface.png`: welcome message and four suggested questions.
2. `successful-response.png`: send `What is the admission process?` and include
   the user query and backend response.
3. `fallback-response.png`: send `xylophonic quasar blorptastic` and include
   the fallback label.
4. `mobile-interface.png`: use a 390-pixel-wide or smaller browser viewport.

Use a local screen-capture tool or browser screenshot feature. Do not create
mockups or add fabricated UI states. After genuine files exist, embed them in
the root README with relative paths.
