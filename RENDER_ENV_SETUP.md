# Render.com Environment Variables Setup

## QADAM: Environment Variables Konfiguratsiyasi

### Render.com da Environment Variables Qo'shish:

#### 1. Render.com Dashboard:
- **Web Service** ga kiring
- **Settings** -> **Environment** ga o'ting
- **Add Environment Variable** ni bosing

#### 2. Qo'shish Kerak Bo'lgan Variables:

```
FLASK_ENV=production
SECRET_KEY=super-secret-key-for-sessions-to-work-step-by-step-platform
DATABASE_URL=sqlite:///education_complete.db
SQLALCHEMY_DATABASE_URI=sqlite:///education_complete.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
PORT=5000
HOST=0.0.0.0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
APP_NAME=Step by Step Education Platform
APP_VERSION=1.0.0
DEBUG=False
SESSION_TIMEOUT=3600
PASSWORD_MIN_LENGTH=6
```

#### 3. Qo'shish Tartibi:

##### **Asosiy Configuration:**
- **NAME:** `FLASK_ENV`
- **VALUE:** `production`

- **NAME:** `SECRET_KEY`
- **VALUE:** `super-secret-key-for-sessions-to-work-step-by-step-platform`

##### **Database Configuration:**
- **NAME:** `SQLALCHEMY_DATABASE_URI`
- **VALUE:** `sqlite:///education_complete.db`

- **NAME:** `SQLALCHEMY_TRACK_MODIFICATIONS`
- **VALUE:** `False`

##### **Server Configuration:**
- **NAME:** `PORT`
- **VALUE:** `5000`

- **NAME:** `HOST`
- **VALUE:** `0.0.0.0`

##### **Admin Configuration:**
- **NAME:** `ADMIN_USERNAME`
- **VALUE:** `admin`

- **NAME:** `ADMIN_PASSWORD`
- **VALUE:** `admin123`

#### 4. Keyingi Qadam:
- **Save Environment Variables** ni bosing
- **Manual Deploy** ni bosing
- **Build** va **Deploy** kutiling

#### 5. Test Qilish:
- **URL:** https://step-by-step-platform.onrender.com
- **Login:** admin/admin123
- **Status:** Working bo'lishi kerak

---

## MUHIM ESLATMA:

### Environment Variables Nomi:
- **NAME:** Variable nomi (masalan: `FLASK_ENV`)
- **VALUE:** Variable qiymati (masalan: `production`)

### Security:
- **SECRET_KEY** ni o'zgartiring (unique bo'lishi kerak)
- **ADMIN_PASSWORD** ni o'zgartiring (production uchun)

### Production:
- **FLASK_ENV** `production` bo'lishi kerak
- **DEBUG** `False` bo'lishi kerak

---

## NATIJA:

### Environment Variables Muvaffaqiyatli Qo'shilgandan So'ng:
- [x] Server configuration to'g'ri ishlaydi
- [x] Database ulanadi
- [x] Security yaxshilandi
- [x] Production mode active

### Deploy Status:
- [x] Environment variables configured
- [x] Build successful
- [x] Deploy successful
- [x] Application live

---

## QO'SHIMCHA:

### .env Fayli:
- **Local development** uchun `.env` fayl yaratildi
- **Production** uchun Render.com environment variables ishlatiladi
- **Security** uchun .env fayl .gitignore ga qo'shildi

### Load Dotenv:
- **app.py** da `load_dotenv()` qo'shildi
- **Environment variables** avtomatik yuklanadi
- **Default values** beriladi

**ENDI RENDER.COM DA ENVIRONMENT VARIABLES QO'SHING!**
