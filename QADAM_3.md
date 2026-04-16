# QADAM 3: Login Route To'g'rilash

## MAQSAD:
Login route ni to'g'rilash va duplicate code ni olib tashlash

## QILINADIGAN ISHLAR:

### 1. Duplicate code ni olib tashlash
- Login route ichidagi takroriy kodni tozalash
- Logic soddalashtirish

### 2. Admin user creation ni to'g'rilash
- Admin user avtomatik yaratilishi
- Password to'g'ri hash qilinishi

### 3. Session management ni to'g'rilash
- Session data to'g'ri saqlanishi
- Redirect logic to'g'ri ishlashi

## KOD:

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_group_leader=False,
                needs_password_change=False
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
        
        # Check login credentials
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session['is_group_leader'] = user.is_group_leader
            session['logged_in'] = True
            
            if user.needs_password_change:
                return redirect(url_for('change_password'))
            elif user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif user.is_group_leader:
                return redirect(url_for('group_leader_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        
        return render_template('login.html', error="Login yoki parol noto'g'ri!")
    
    return render_template('login.html')
```

## QO'SHISH JOYI:
Login route ni butunlay almashtirish

## NATIJA:
- Login ishlaydi
- Admin user yaratiladi
- Session management ishlaydi
- Redirect logic ishlaydi

## STATUS:
- [x] Duplicate code olib tashlandi
- [x] Login logic to'g'rilandi
- [x] Session management ishlaydi
- [x] Admin login ishlaydi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Login ishlaydi
- [x] Admin panelga kirish mumkin

## KEYINGI QADAM:
QADAM 4: Register route ni to'g'rilash
