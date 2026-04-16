# QADAM 2: User Modelga Password Methods Qo'shish

## MAQSAD:
User modeliga password metodlarini qo'shish uchun login ishlashi

## QILINADIGAN ISHLAR:

### 1. set_password() method qo'shish
- Parolni hash qilish
- User modelga qo'shish

### 2. check_password() method qo'shish
- Parolni tekshirish
- User modelga qo'shish

## KOD:

```python
# User model class ichiga qo'shing
def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

## QO'SHISH JOYI:
User class ichida, relationships dan keyin

## NATIJA:
- Login ishlaydi
- Password hashing ishlaydi
- User authentication ishlaydi

## STATUS:
- [x] set_password() method qo'shildi
- [x] check_password() method qo'shildi
- [x] Password hashing ishlaydi
- [x] User authentication ishlaydi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Login ishlaydi
- [x] Admin panelga kirish mumkin

## KEYINGI QADAM:
QADAM 3: Login route ni to'liq ishlash
(QADAM 3-4-5 ham server uchun tayyor qilindi)
