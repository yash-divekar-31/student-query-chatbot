# Frontend

This folder contains the React/Vite student-query chat interface. For complete
installation, startup, API, and test instructions, see the
[project README](../README.md).

## Local frontend commands

Run these commands from this directory:

```powershell
npm ci
npm run dev -- --host 127.0.0.1
```

The Vite development server normally opens at `http://127.0.0.1:5173`. The
frontend reads `VITE_API_BASE_URL` from `.env`; the local value is
`http://127.0.0.1:8000`.

Run the frontend checks:

```powershell
npm test
npm run lint
npm run build
```
