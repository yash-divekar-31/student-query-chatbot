# Deployment Guide

The prepared free-tier deployment targets are Render for the FastAPI backend
and Vercel for the React/Vite frontend.

No account deployment is claimed until the platform URLs return successful
health/API responses.

## Backend: Render

1. Create a new Render web service from this repository.
2. Render can read the root `render.yaml` blueprint.
3. Set `CORS_ORIGINS` to the final Vercel frontend origin. Use a comma-separated
   list of origins and do not include `*`.
4. Keep `CONFIDENCE_THRESHOLD=0.065` unless the fallback behavior is deliberately
   changed and retested.
5. Deploy and verify `https://<backend-name>.onrender.com/health`.

The model and dataset directories are checked into the repository, so the
Render build does not need external model downloads. Render does not persist
local file changes; retraining must happen in source control or in the build
pipeline.

## Frontend: Vercel

1. Import this repository into Vercel.
2. Set the project root directory to `frontend`.
3. Set `VITE_API_BASE_URL` to the deployed Render backend origin, for example
   `https://student-query-chatbot-api.onrender.com`.
4. Use `npm ci` as the install command and `npm run build` as the build
   command. The output directory is `dist`.
5. Deploy and open the Vercel URL.

Update the Render `CORS_ORIGINS` value to the final Vercel origin. Redeploy
the backend after changing CORS configuration.

## Configuration files

- `render.yaml`: Render web service and health-check configuration.
- `vercel.json`: Vercel SPA fallback for the Vite application.
- `backend/.env.example`: backend environment variable template.
- `frontend/.env.example`: frontend environment variable template.

Do not commit real `.env` files or credentials.
