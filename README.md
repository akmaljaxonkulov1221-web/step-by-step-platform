# Ta'lim Platformasi

Ushbu platforma o'quvchilar uchun to'liq funktsional ta'lim tizimi bo'lib, ular uchun shaxsiy kabinet, testlar, dars jadvali va boshqa imkoniyatlarni taqdim etadi.

## Xususiyatlari

### O'quvchilar uchun:
- **Shaxsiy kabinet**: Ism, familiya, guruh, sertifikatlar va test natijalari
- **Fanlar va mavzular**: Har bir fan bo'yicha matnli va video darslar
- **Test tizimi**: Avtomatik baholash bilan testlar
- **Qiyin mavzular**: Tushunmagan mavzularni belgilash imkoniyati
- **Dars jadvali**: Guruhga oid dars jadvali
- **Guruh reytingi**: Guruhlar o'rtasida musobaqa va ballar tizimi

### Admin uchun:
- **O'quvchilar boshqaruvi**: Yangi o'quvchilarni qo'shish, tahrirlash
- **Guruhlar boshqaruvi**: Guruhlarni yaratish va boshqarish
- **Fanlar boshqaruvi**: Fanlar va mavzular qo'shish
- **Testlar boshqaruvi**: Testlar yaratish va savollar qo'shish
- **Jadval boshqaruvi**: Dars jadvalini tuzish

## O'rnatish

### Development muhitida:

1. **Klonlash**:
```bash
git clone <repository-url>
cd education_platform
```

2. **Virtual muhit yaratish**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Dependentsiyalarni o'rnatish**:
```bash
pip install -r requirements.txt
```

4. **Dasturni ishga tushirish**:
```bash
python app.py
```

### Production muhitida:

#### 1. Docker orqali:
```bash
# Build va run
docker-compose up --build

# Background mode
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f
```

#### 2. Gunicorn orqali:
```bash
# Environment sozlash
export FLASK_ENV=production
export DATABASE_URL=sqlite:///education_complete.db

# Gunicorn bilan ishga tushirish
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

#### 3. Render.com ga deployment:
1. **GitHub ga yuklash:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Render.com da:**
   - Yangi Web Service yarating
   - GitHub repository ni ulang
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app`
   - Environment variables:
     - `FLASK_ENV=production`
     - `SECRET_KEY=your-secret-key-here`

## Foydalanish

### Admin kirishi:
- Login: `admin`
- Parol: `admin123`

### O'quvchi qo'shish:
1. Admin paneliga kiring
2. "O'quvchilar" bo'limiga o'ting
3. "Yangi o'quvchi qo'shish" tugmasini bosing
4. Ma'lumotlarni to'ldiring

### Test yaratish:
1. "Fanlar" bo'limiga o'ting
2. Yangi fan qo'shing
3. "Testlar" bo'limiga o'ting
4. Yangi test yarating
5. Testga savollar qo'shing

## Texnologiyalar

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **Security**: bcrypt

## Ma'lumotlar bazasi tuzilmasi

### Asosiy jadvallar:
- `users`: O'quvchilar va adminlar
- `groups`: Guruhlar
- `subjects`: Fanlar
- `topics`: Mavzular
- `tests`: Testlar
- `questions`: Savollar
- `test_results': Test natijalari
- `schedule`: Dars jadvali
- `certificates`: Sertifikatlar
- `difficult_topics`: Qiyin mavzular

## Qo'shimcha imkoniyatlar

### Kundalik testlar:
- Har kuni avtomatik ravishda huquq fanidan test o'tkaziladi
- 80% dan yuqori natija ko'rsatgan o'quvchilar guruhiga ball qo'shadi
- Eng yaxshi 3 o'quvchi e'tirof etiladi

### Katta testlar:
- Har 5-7 kunda TDYU kirish fanlari bo'yicha test
- Barcha o'quvchilar natijalari chiqariladi
- Guruhlar reytingi yangilanadi

### Reyting tizimi:
- Guruhlar o'rtasida ballar bo'yicha musobaqa
- Real vaqt rejimida reyting ko'rish
- Oylik g'oliblarni e'tirof etish

## Rivojlanish

### Kelgusidagi imkoniyatlar:
- Mobil ilova
- Push bildirishnomalar
- Video konferensiya
- Avtomatik savol generatsiyasi
- AI asosida o'qitish

## Yordam

Agar sizda savollar yoki muammolar bo'lsa, iltimos, quyidagi manzilga murojaat qiling:
- Email: support@education.uz
- Telegram: @education_support

## Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.
