# 502 Bad Gateway — tuzatish

502 = host nginx panelga ulana olmayapti.

Zanjir:
```
server.it-zone.uz → host nginx (:80) → 127.0.0.1:8080 → docker-panel-nginx → frontend/backend
```

## 1. Tez tekshiruv

```bash
cd ~/server
chmod +x deploy/check.sh
./deploy/check.sh
```

## 2. Containerlar ishlayaptimi?

```bash
docker compose ps
```

Hammasi `Up` bo'lishi kerak:
- `docker-panel-nginx`
- `docker-panel-frontend`
- `docker-panel-backend`

Agar `Exit` yoki yo'q bo'lsa:

```bash
docker compose logs --tail=50 backend frontend nginx
```

## 3. Panel porti javob beradimi?

```bash
curl http://127.0.0.1:8080/api/health/
```

**Ishlamasa** — muammo docker-panel stackda (host nginx emas).

```bash
docker compose up -d --build
# yoki host mode:
docker compose -f docker-compose.yml -f docker-compose.host.yml up -d --build
```

`.env` da port:
```bash
grep HTTP_PORT .env
```

Host nginx ham shu portga qarashi kerak (`8080`).

## 4. Host nginx to'g'rimi?

```bash
grep -r "proxy_pass" /etc/nginx/sites-enabled/
```

`server.it-zone.uz` uchun:
```nginx
proxy_pass http://127.0.0.1:8080;
```

Certbot HTTPS qo'shgan bo'lsa:

```bash
sudo nginx -t
cat /etc/nginx/sites-enabled/server.it-zone.uz
```

`proxy_pass` hali ham `http://127.0.0.1:8080` bo'lishi kerak (https emas).

## 5. ALLOWED_HOSTS

`.env`:
```env
DJANGO_ALLOWED_HOSTS=server.it-zone.uz
```

```bash
docker compose restart backend
```

## 6. Qayta deploy

```bash
cd ~/server
git pull origin master
docker compose down
docker compose up -d --build
```

Host mode:
```bash
docker compose stop docker-engine
docker compose -f docker-compose.yml -f docker-compose.host.yml up -d --build
```

Kuting 1–2 daqiqa (frontend build va healthcheck).

```bash
curl http://127.0.0.1:8080/api/health/
curl http://server.it-zone.uz/api/health/
```
