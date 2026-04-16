# QADAM 6: Testing & Deployment

## MAQSAD:
Barcha funksiyalarni test qilish va deployment qilish

## QILINADIGAN ISHLAR:

### 1. Local testing
- Server start test
- Database creation test
- Login test
- Admin dashboard test

### 2. Error handling
- Try-catch bloklar qo'shish
- Error messages
- User feedback

### 3. GitHub deployment
- Commit qilish
- Push qilish
- Render deployment

## TEST QILISH:

### 1. Server Test:
```bash
python app.py
# Server ishlayotganini tekshir
# http://localhost:5000
```

### 2. Login Test:
- Username: admin
- Password: admin123
- Admin dashboardga kirish

### 3. Database Test:
- Database jadvallari yaratilishi
- Admin user yaratilishi
- Default groups/subjects yaratilishi

## DEPLOYMENT:

### 1. GitHub:
```bash
git add app.py
git commit -m "Complete education platform - all features working"
git push origin main
```

### 2. Render.com:
- Auto-deploy kutiladi
- Build status tekshiriladi
- Server test qilinadi

## NATIJA:
- Server ishlaydi
- Barcha funksiyalar ishlaydi
- Deployment muvaffaqiyatli
- Live URL ishlaydi

## STATUS:
- [x] Local testing qilindi
- [x] Error handling qo'shildi
- [x] GitHub push qilindi
- [x] Render deployment qilindi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Login ishlaydi
- [x] Admin panel ishlaydi
- [x] Barcha funksiyalar ishlaydi

## KEYINGI QADAM:
QADAM 7: Final Verification & Documentation
