# Fullstack quiz application
## Tech stack: python(fastapi), postgres, JavaScript(React)

This will be a quiz-maker application that allows a user to create an account and make quizzes for others to take. They will have a dashboard to show the status of each quiz they make and are able to share their quizzes by a unique link made for them. They will also get a leaderboard for each quiz that they made showing the users who have the best scores.

## Running locally

Backend, from `backend/` -- copy `.env-example` to `.env` and fill it in first:

```
pip install -r requirements-dev.txt
uvicorn main:app --reload
pytest
```

The tests run on their own in-memory sqlite database, so they never touch the real one.

Frontend, from `frontend/react-quiz-app/`:

```
npm install
npm run dev
```

## Deploying

### Backend (web service)

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

`--host 0.0.0.0` matters: uvicorn otherwise binds localhost only and the host can't route to it.

Environment:

| var | value |
| --- | --- |
| `DATABASE_URL` | the internal connection string for the postgres instance |
| `SESSION_SECRET` | a long random string |
| `ALLOWED_ORIGINS` | optional -- comma separated frontend origins. the deployed one is already the default |
| `COOKIE_SAMESITE` | optional -- defaults to `none` when it detects it's running on render |
| `COOKIE_SECURE` | optional -- defaults to `true` when it detects it's running on render |

Only `DATABASE_URL` and `SESSION_SECRET` have to be set. The cookie flags switch
themselves on from render's own `RENDER` env var, because a cross-site `SameSite=Lax`
cookie is dropped by the browser -- login looks like it works and then every
authenticated call comes back 401. Set any of them explicitly to override.

### Frontend (static site)

- Root Directory: `frontend/react-quiz-app`
- Build Command: `npm run render-build`
- Publish Directory: `dist`
- Rewrite rule: `/*` to `/index.html`

The chained install lives in that npm script because render's build command field only
accepts `[A-Za-z0-9-_./ ]`, which rules out `&&`.

Set `VITE_API_URL` to the deployed backend url. Vite inlines it at build time rather than
reading it at runtime, so it has to be set before the build runs -- adding it afterwards
does nothing until the next deploy.

The rewrite rule is what makes shared quiz links and page refreshes work; without it the
host looks for a file at `/take/<link>` and 404s. The build also drops a copy of
index.html at 404.html as a fallback for hosts that serve it on a miss, but the rewrite
is the real fix -- it returns 200 instead of a 404 status.
