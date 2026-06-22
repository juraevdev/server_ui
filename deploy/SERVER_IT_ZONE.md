# server.it-zone.uz deploy

## 1. DNS sozlash

Domen panelida `A` yozuvi qo'shing:

| Type | Name | Value |
|------|------|-------|
| A | server | SERVER_IP_MANZILI |

Natija: `server.it-zone.uz` → serveringiz IP si

Tekshirish:

```bash
ping server.it-zone.uz
```

## 2. Serverda loyiha

```bash
git clone <repo-url> server_ui
cd server_ui
cp deploy/env.server.it-zone.uz.example .env
nano .env
```

`DJANGO_SECRET_KEY` ni o'zgartiring:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 3. Deploy

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 4. Tekshirish

- http://server.it-zone.uz
- http://server.it-zone.uz/api/health/

## 5. HTTPS (tavsiya etiladi)

Certbot bilan (serverda, docker tashqarisida yoki alohida nginx bo'lsa):

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d server.it-zone.uz
```

Keyin SSL nginx config qo'shish kerak bo'ladi. Hozircha HTTP (80-port) ishlaydi.

Agar **Cloudflare** ishlatsangiz:
- DNS proxy (orange cloud) yoqish mumkin
- SSL mode: Flexible yoki Full

## Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp   # HTTPS uchun
sudo ufw enable
```

## Yangilash

```bash
git pull
docker compose up -d --build
```
