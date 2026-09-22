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
| `ALLOWED_ORIGINS` | the deployed frontend's origin, comma separated if more than one |
| `COOKIE_SAMESITE` | `none` |
| `COOKIE_SECURE` | `true` |

The last two are required once the frontend is on a different origin than the api. A
`SameSite=Lax` cookie is not sent on cross-site requests, so login appears to succeed and
then every authenticated call comes back 401.

### Frontend (static site)

- Root Directory: `frontend/react-quiz-app`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Rewrite rule: `/*` to `/index.html`

Set `VITE_API_URL` to the deployed backend url. Vite inlines it at build time rather than
reading it at runtime, so it has to be set before the build runs -- adding it afterwards
does nothing until the next deploy.

The rewrite rule is what makes shared quiz links and page refreshes work; without it the
host looks for a file at `/take/<link>` and 404s.
