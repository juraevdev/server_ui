# Host mode — server containerlarini ko'rish

## Nima uchun bo'sh chiqadi?

Default **isolated** rejimda panel alohida ichki Docker ishlatadi.
`zarbdor_driver`, `docker-panel-*` va boshqa host containerlar **ko'rinmaydi**.

## Host rejimga o'tish

Serverda:

```bash
cd ~/server
git pull origin master
docker compose stop docker-engine
docker compose -f docker-compose.yml -f docker-compose.host.yml up -d --build
```

Tekshirish:

```bash
curl http://127.0.0.1:8080/api/health/
curl http://127.0.0.1:8080/api/dashboard/ | head -c 500
```

`docker_mode` qiymati `host` bo'lishi kerak.

## Xavfsizlik

| Container | Ko'rinish | Start/Stop/Delete |
|-----------|-----------|-------------------|
| `zarbdor_driver-*` | Ha | Yo'q (read-only) |
| `panel-*` | Ha | Ha |

Boshqa loyihalarga panel orqali zarar yetkazib bo'lmaydi.

## Isolated rejimga qaytish

```bash
docker compose down
docker compose up -d --build
```
