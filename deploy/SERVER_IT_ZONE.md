# server.it-zone.uz — Kali Linux server

## Muhim

- Server: **Kali Linux** (Debian-asosli — `apt` ishlaydi)
- Panel **:80 / :443** band qilmaydi
- Faqat **127.0.0.1:8080** ishlatiladi
- Mavjud nginx va boshqa containerlar **o'zgarmaydi**

## 1. DNS

| Type | Name | Value |
|------|------|-------|
| A | server | SERVER_IP |

## 2. Docker (Kali)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable docker --now
```

## 3. Loyiha

```bash
cd server_ui
cp deploy/env.server.it-zone.uz.example .env
nano .env
```

Majburiy: `DJANGO_SECRET_KEY` ni almashtiring.

## 4. Deploy

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

```bash
curl http://127.0.0.1:8080/api/health/
```

## 5. Host nginx (mavjud :80 uchun)

```bash
sudo cp deploy/host-nginx.server.it-zone.uz.conf /etc/nginx/sites-available/server.it-zone.uz
sudo ln -sf /etc/nginx/sites-available/server.it-zone.uz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

> Kali da nginx bo'lmasa: `sudo apt install -y nginx`

## 6. Ochish

- http://server.it-zone.uz (hozirgi holat)
- HTTPS uchun: `deploy/HTTPS.md`

## Port band bo'lsa

```bash
ss -tlnp | grep 8080
docker compose down
# .env: HTTP_PORT=8081
# host-nginx conf ichida ham 8081 ga o'zgartiring
docker compose up -d --build
```

Batafsil: `deploy/DEPLOY.md`
