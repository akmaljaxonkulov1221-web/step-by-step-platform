# QADAM 4: Register Route To'g'rilash

## MAQSAD:
Register route ni to'g'rilash va user creation logic ni ishlash

## QILINADIGAN ISHLAR:

### 1. User creation logic ni to'g'rilash
- Yangi user yaratish
- Password hash qilish
- Group assignment

### 2. Validation qo'shish
- Form validation
- Password matching
- Username uniqueness

### 3. Error handling qo'shish
- Xatoliklarni ushlash
- User feedback

## KOD:

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        group_id = request.form.get('group_id', type=int)
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not first_name or not last_name or not password:
            return render_template('register.html', error="Barcha maydonlarni to'ldiring!")
        
        if password != confirm_password:
            return render_template('register.html', error="Parollar mos kelmadi!")
        
        # Check if username already exists
        username = f"{first_name.lower()}_{last_name.lower()}"
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Bu foydalanuvchi allaqachon mavjud!")
        
        # Create new user
        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            group_id=group_id,
            is_admin=False,
            is_group_leader=False,
            needs_password_change=False
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Ro'yxatdan muvaffaqiyatli o'tdingiz! Login qiling.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error="Ro'yxatdan o'tishda xatolik yuz berdi!")
    
    # Get groups for dropdown
    groups = Group.query.all()
    return render_template('register.html', groups=groups)
```

## QO'SHISH JOYI:
Register route ni butunlay almashtirish

## NATIJA:
- Register ishlaydi
- User creation ishlaydi
- Validation ishlaydi
- Error handling ishlaydi

## STATUS:
- [x] User creation logic to'g'rilandi
- [x] Group assignment ishlaydi
- [x] Validation qo'shildi
- [x] Error handling qo'shildi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Register ishlaydi
- [x] New user yaratish mumkin

## KEYINGI QADAM:
QADAM 5: Admin dashboard route qo'shish
