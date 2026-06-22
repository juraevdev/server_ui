# Serverga deploy (Kali Linux / Debian)

## Xavfsizlik modeli

- Host `/var/run/docker.sock` **ulanmaydi**
- Alohida ichki Docker engine (`docker-engine`) ishlaydi
- Panel faqat ichki muhitdagi `panel-` containerlarni boshqaradi
- Host **:80** portni band qilmaydi — faqat `127.0.0.1:8080`

## 1. Kali Linux da Docker o'rnatish

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin curl
sudo systemctl enable docker --now
```

Root emas, oddiy user bilan ishlasangiz:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Tekshirish:

```bash
docker --version
docker compose version
```

## 2. Loyihani olish

```bash
git clone <repo-url> server_ui
cd server_ui
cp deploy/env.server.it-zone.uz.example .env
nano .env
```

`DJANGO_SECRET_KEY` yarating:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 3. Deploy

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Tekshirish:

```bash
curl http://127.0.0.1:8080/api/health/
```

## 4. Domen (server.it-zone.uz)

Mavjud host nginx ga proxy qo'shing (nginx ni o'chirmang):

```bash
sudo cp deploy/host-nginx.server.it-zone.uz.conf /etc/nginx/sites-available/server.it-zone.uz
sudo ln -sf /etc/nginx/sites-available/server.it-zone.uz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Brauzer: http://server.it-zone.uz

## 5. Firewall (Kali)

Kali da `ufw` bo'lmasligi mumkin. Band portlarga tegmang.

Agar `ufw` o'rnatilgan bo'lsa:

```bash
sudo ufw status
```

Agar `iptables`/`nftables` ishlatsangiz — faqat kerakli qoidalarni qo'shing, mavjudlarni o'zgartirmang.

## 6. Image build

Loyihani `host-builds/myapp/` ga qo'ying, UI da path: `/builds/myapp`

## 7. Yangilash

```bash
git pull
docker compose up -d --build
```

## Muammo bo'lsa

```bash
docker compose ps
docker compose logs docker-engine
docker compose logs backend
ss -tlnp | grep 8080
```

Port band bo'lsa `.env` da `HTTP_PORT=8081` qiling.
