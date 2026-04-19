# GitHub va Render.com ga yuklash qo'llanmasi

## Tayyor holat:
- Git repository tayyor
- Barcha fayllar commit qilindi
- Deployment fayllari tayyor

## GitHub ga yuklash:

### 1. GitHub repozitoriyasini yarating:
1. GitHub.com ga kiring
2. "New repository" tugmasini bosing
3. Repository nomi: `education-platform` (yoki istalgan nom)
4. Public/Private tanlang (Public tavsiya etiladi)
5. "Create repository" tugmasini bosing

### 2. GitHub ga yuklash:
```bash
# GitHub repozitoriyasini qo'shing (URL ni o'zingizning repository bilan almashtiring)
git remote add origin https://github.com/USERNAME/education-platform.git

# Branch nomini main deb o'zgartiring (agar kerak bo'lsa)
git branch -M main

# GitHub ga yuklang
git push -u origin main
```

### 3. GitHub da tekshiring:
- GitHub repozitoriyasiga kiring
- Barcha fayllar ko'rinishi kerak
- `render.yaml` fayli borligini tekshiring

## Render.com ga deploy qilish:

### 1. Render.com ga kiring:
1. Render.com ga kiring
2. GitHub bilan ro'yxatdan o'ting

### 2. Yangi Web Service yarating:
1. Dashboardda "New +" tugmasini bosing
2. "Web Service" ni tanlang
3. GitHub repository ni tanlang
4. "Connect" tugmasini bosing

### 3. Konfiguratsiyani o'rnatish:
Render.com `render.yaml` faylidan avtomatik konfiguratsiyani o'qiydi:

**Build Command:** `pip install -r requirements.txt && python migrate_database_new_features.py`
**Start Command:** `gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app`

### 4. Environment Variables:
Environment Variables qo'shing:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
FLASK_APP=app.py
DATABASE_URL=sqlite:///education_complete.db
PYTHON_VERSION=3.12.0
```

### 5. Deploy tugmasini bosing:
- "Create Web Service" tugmasini bosing
- Deploy avtomatik boshlanadi (2-3 daqiqa)

### 6. Deploy ni tekshiring:
- Deploy tugagandan so'ng app URL ni oling
- `https://your-app-name.onrender.com` ga kiring
- Login sahifasi ochilishi kerak

## Post-deployment tekshirish:

### 1. Admin panelga kirish:
- URL: `https://your-app-name.onrender.com/login`
- Username: `admin`
- Password: `admin123`

### 2. PDF funksiyalarini tekshiring:
1. Fanlar bo'limiga kiring
2. Yangi fan qo'shing (PDF fayl bilan)
3. Mavzu qo'shing (PDF fayl bilan)
4. Test yarating (PDF fayl bilan)

### 3. Test sistemini tekshiring:
1. Studentlar bo'limiga kiring
2. Yangi student qo'shing
3. Testlar bo'limiga kiring
4. Haftalik jadvalni tekshiring

## Muammolar va yechimlari:

### Agar deploy ishlamasa:
1. **Build error**: Requirements.txt ni tekshiring
2. **Database error**: migrate_database_new_features.py ishlashi kerak
3. **Permission error**: uploads/pdfs papkasi bo'lishi kerak

### Loglarni tekshirish:
Render.com dashboardda "Logs" bo'limida xatoliklarni ko'rishingiz mumkin

### Qayta deploy qilish:
```bash
# O'zgarishlarni qo'shing
git add .
git commit -m "Update description"
git push origin main
```

## Muvaffaqiyatli deploy belgilari:
- [ ] Admin panel ochiladi
- [ ] PDF yuklash ishlamoqda
- [ ] Studentlar ro'yxatga olinmoqda
- [ ] Testlar jadvali ko'rinmoqda
- [ ] Haftalik testlar ishlamoqda

---

**Platform tayyor!** GitHub ga yuklab, Render.com ga deploy qiling!
