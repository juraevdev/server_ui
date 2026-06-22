# HTTPS — server.it-zone.uz

Hozir **http://server.it-zone.uz** ishlashi normal — SSL hali o'rnatilmagan.

## 1. Certbot o'rnatish (Kali)

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

## 2. SSL sertifikat olish

Host nginx allaqachon `server.it-zone.uz` uchun 80-portda ishlashi kerak.

```bash
sudo certbot --nginx -d server.it-zone.uz
```

Email kiriting, shartlarni qabul qiling. Certbot nginx configni avtomatik yangilaydi.

## 3. Tekshirish

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://server.it-zone.uz/api/health/
```

Brauzer: **https://server.it-zone.uz**

## 4. Django .env (server papkada)

```bash
cd ~/server
nano .env
```

```env
CSRF_TRUSTED_ORIGINS=https://server.it-zone.uz,http://server.it-zone.uz
```

```bash
docker compose restart backend
```

## 5. Avtomatik yangilanish

```bash
sudo certbot renew --dry-run
```

Certbot systemd timer o'rnatadi — sertifikat muddati tugashidan oldin yangilanadi.

## Cloudflare ishlatsangiz

- DNS da proxy (orange cloud) yoqilgan bo'lishi mumkin
- SSL/TLS mode: **Full** yoki **Full (strict)** (certbot dan keyin)
- Flexible ham HTTP bilan ishlaydi, lekin Full tavsiya etiladi

## Muammo

```bash
sudo certbot certificates
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

Port 80 tashqaridan ochiq bo'lishi kerak (Let's Encrypt tekshiruvi uchun).
