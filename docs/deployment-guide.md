# Deployment Guide

Hướng dẫn triển khai Photo Studio Capstone Backend.

---

## Yêu cầu

- Python 3.8+
- PostgreSQL (local hoặc Supabase)
- pip

---

## 1. Local Development

### Bước 1: Clone & Setup

```bash
cd photo-studio-capstone/src

# Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate  # Unix/macOS
# .venv\Scripts\activate   # Windows

# Cài dependencies
pip install -r requirements.txt
```

### Bước 2: Cấu hình .env

Tạo file `src/.env`:

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Supabase (PostgreSQL cloud)
POSTGREE_DATABASE_URL="postgresql+psycopg2://postgres.xxx:password@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

# Hoặc PostgreSQL local
# POSTGREE_DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/photo_studio"
```

### Bước 3: Chạy

```bash
python app.py
```

App khởi động tại `http://localhost:9999`

- Test GUI: http://localhost:9999/
- Swagger: http://localhost:9999/docs
- API JSON: http://localhost:9999/swagger.json

---

## 2. Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 9999

CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "9999:9999"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - POSTGREE_DATABASE_URL=${DATABASE_URL}
    volumes:
      - uploads:/app/uploads
    restart: unless-stopped

volumes:
  uploads:
```

### Chạy

```bash
echo "SECRET_KEY=your_secret" > .env
echo "DATABASE_URL=postgresql+psycopg2://..." >> .env
docker-compose up -d --build
```

---

## 3. Supabase (Database)

### Bước 1: Tạo Project

1. Đăng nhập https://supabase.com
2. Tạo project mới
3. Copy connection string: Settings → Database → Connection string → URI

### Bước 2: Cấu hình .env

```env
POSTGREE_DATABASE_URL="postgresql+psycopg2://postgres.[ref].[password]@aws-0-[region].pooler.supabase.com:5432/postgres"
```

### Bước 3: Tạo tables

Option 1: Auto-create khi chạy `init_db()` (app.py)

Option 2: Manual SQL trên Supabase Dashboard → SQL Editor

---

## 4. Render

1. Đăng nhập https://render.com
2. New → Web Service → Connect GitHub

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r src/requirements.txt` |
| Start Command | `cd src && python app.py` |
| Port | 9999 |

Environment Variables:
```
FLASK_ENV=production
SECRET_KEY=your_secret
POSTGREE_DATABASE_URL=postgresql+...
```

---

## 5. Railway

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=your_secret
railway variables set POSTGREE_DATABASE_URL="postgresql+..."
railway up
```

---

## 6. Heroku

Tạo file `Procfile`:
```
web: cd src && python app.py
```

Tạo file `runtime.txt`:
```
python-3.11.8
```

```bash
heroku create photo-studio-api
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your_secret
heroku config:set POSTGREE_DATABASE_URL="postgresql+..."
git push heroku main
```

---

## Environment Variables

| Variable | Required | Default | Mô tả |
|---|---|---|---|
| `FLASK_ENV` | No | `development` | `development` / `testing` / `production` |
| `SECRET_KEY` | Yes | - | Secret key cho JWT (HS256) |
| `POSTGREE_DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `DEBUG` | No | `False` | Bật debug mode |
| `TESTING` | No | `False` | Bật testing mode |

---

## Troubleshooting

### Database connection refused

```bash
# Kiểm tra PostgreSQL
pg_isready -h localhost -p 5432

# Kiểm tra .env
python -c "
from dotenv import load_dotenv
import os
load_dotenv('src/.env')
print(os.environ.get('POSTGREE_DATABASE_URL'))
"
```

### Port 9999 in use

```bash
lsof -i :9999        # macOS/Linux
netstat -ano | findstr :9999  # Windows
kill -9 <PID>
```

### Import errors

```bash
source .venv/bin/activate
pip install -r requirements.txt
```
