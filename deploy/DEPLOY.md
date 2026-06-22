# Serverga deploy qo'llanmasi

## Xavfsizlik modeli

Bu loyiha serverdagi **boshqa containerlarga tegmaydi**.

- Host `/var/run/docker.sock` **ulanmaydi**
- Alohida ichki Docker engine (`docker-engine`) ishlaydi
- Panel faqat shu izolyatsiya qilingan muhitdagi containerlarni boshqaradi
- Yaratilgan container nomlari avtomatik `panel-` prefiksi bilan boshlanadi

```
Server (host Docker — boshqa loyihalar)
  └── docker-panel stack (alohida)
        ├── docker-panel-engine   ← ichki Docker
        ├── docker-panel-backend  ← faqat engine ga ulanadi
        ├── docker-panel-frontend
        └── docker-panel-nginx    ← tashqariga faqat 80-port
```

## 1. Server tayyorlash

Ubuntu serverda:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

Firewall:

```bash
sudo ufw allow 80/tcp
sudo ufw enable
```

## 2. Loyihani serverga olish

```bash
git clone <repo-url> server_ui
cd server_ui
```

## 3. Sozlash

```bash
cp .env.example .env
nano .env
```

```env
DJANGO_SECRET_KEY=<uzun-random-kalit>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=123.45.67.89,yourdomain.com
HTTP_PORT=80
DOCKER_CONTAINER_PREFIX=panel-
```

## 4. Ishga tushirish

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Brauzer: `http://SERVER_IP`

Tekshirish: `http://SERVER_IP/api/health/`

## 5. Container yaratish

UI da nom yozsangiz: `my-nginx`

Aslida ichkarida yaratiladi: `panel-my-nginx`

Bu containerlar **faqat panel ichki Docker** da ishlaydi, serverdagi boshqa containerlar xavfsiz.

## 6. Image build

Loyihani `host-builds/myapp/` ga qo'ying, UI da path:

```
/builds/myapp
```

## 7. Yangilash

```bash
git pull
docker compose up -d --build
```

## Muhim eslatmalar

1. **Port mapping** (`8081:80`) ichki Docker ichida ishlaydi — host server porti emas.
2. **Auth yo'q** — panel URL ni himoya qiling (firewall/VPN).
3. Stackni to'liq o'chirish: `docker compose down` (ichki containerlar ham o'chadi).
4. Ichki Docker ma'lumotlari `docker_engine_data` volume da saqlanadi.

## Muammo bo'lsa

```bash
docker compose ps
docker compose logs docker-engine
docker compose logs backend
```
