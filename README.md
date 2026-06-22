# Docker Panel

Local Docker control panel: Django API backend + Next.js frontend.

## Structure

```
server_ui/
├── backend/          # Django REST API + Docker service
├── frontend/         # Next.js UI
├── deploy/           # nginx + deploy script
└── docker-compose.yml
```

## Local development

### Backend (port 8000)

```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (port 3000)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

Set `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

## Server deploy (recommended)

### Server requirements

- Linux server (Kali Linux, Debian, Ubuntu, va hokazo)
- Docker Engine + Docker Compose plugin
- Mavjud :80 portdagi nginx ga faqat proxy qo'shiladi (band qilinmaydi)

See `deploy/DEPLOY.md` (Kali Linux) and `deploy/SERVER_IT_ZONE.md`.

### Quick deploy

```bash
git clone <your-repo> server_ui
cd server_ui
cp .env.example .env
nano .env   # set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Open **http://server.it-zone.uz** (see `deploy/SERVER_IT_ZONE.md` for domain setup).

### What runs in production

| Service | Role |
|---------|------|
| `docker-panel-nginx` | Public entry on port 80 |
| `docker-panel-frontend` | Next.js UI |
| `docker-panel-backend` | Django API + Gunicorn |
| `docker-panel-engine` | **Isolated** inner Docker (DinD) |

**Host Docker socket is NOT mounted.** The panel cannot start, stop, or delete containers that belong to other projects on the server.

Flow:

```
Browser → nginx:80 → /        → frontend
                    → /api/*  → backend → isolated docker-engine
```

Managed app containers are created inside `docker-engine` with the `panel-` name prefix.

### Environment variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Required. Long random string |
| `DJANGO_DEBUG` | `false` in production |
| `DJANGO_ALLOWED_HOSTS` | Server IP and/or domain |
| `HTTP_PORT` | Default `80` |
| `DOCKER_CONTAINER_PREFIX` | Default `panel-` |

Generate secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Useful commands

```bash
docker compose ps
docker compose logs -f
docker compose down
docker compose up -d --build
```

### Image build on server

When backend runs in Docker, use build path inside container:

```
/builds/my-project
```

Copy your project to the `build_context` volume on the host, or mount a folder in `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./host-builds:/builds
```

Then in UI use build path: `/builds/my-project` (must contain `Dockerfile`).

## Security warning

This panel has **no authentication**. Anyone who can open the URL can control containers **inside the isolated docker-engine**.

It does **not** control other containers on the host server (when deployed via `docker-compose.yml`).

Before exposing to the internet:

- Restrict access by firewall / VPN
- Or put nginx basic auth in front
- Do not expose port 8000 or 3000 directly; only use nginx on port 80

## API

Base URL in production: `/api`

- `GET /api/health/`
- `GET /api/dashboard/`
- `POST /api/containers/`
- `POST /api/images/`
