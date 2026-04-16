# QADAM 8: Advanced Features & User Management

## MAQSAD:
Step by step platformiga advanced features qo'shish va full user management system yaratish

## QILINADIGAN ISHLAR:

### 1. User Management System
- User CRUD operatsiyalari
- Group management
- Subject management
- Role management

### 2. Advanced Dashboard
- Statistics va analytics
- User activity tracking
- Performance monitoring
- Report generation

### 3. Security Features
- Input validation
- CSRF protection
- Rate limiting
- Audit logging

## KOD:

### User Management Routes:

```python
@app.route('/admin/users')
def admin_users():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    users = User.query.all()
    groups = Group.query.all()
    
    return render_template('admin_users.html', users=users, groups=groups)

@app.route('/admin/users/create', methods=['POST'])
def admin_create_user():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    group_id = request.form.get('group_id', type=int)
    password = request.form.get('password', '').strip()
    is_admin = request.form.get('is_admin') == 'on'
    is_group_leader = request.form.get('is_group_leader') == 'on'
    
    # Validation
    if not all([username, first_name, last_name, password]):
        flash("Barcha maydonlarni to'ldiring!", "error")
        return redirect(url_for('admin_users'))
    
    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Bu username allaqachon mavjud!", "error")
        return redirect(url_for('admin_users'))
    
    # Create user
    new_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        group_id=group_id,
        is_admin=is_admin,
        is_group_leader=is_group_leader,
        needs_password_change=False
    )
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        flash("Foydalanuvchi muvaffaqiyatli yaratildi!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Xatolik: {str(e)}", "error")
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't delete admin
    if user.username == 'admin':
        flash("Admin foydalanuvchini o'chirib bo'lmaydi!", "error")
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash("Foydalanuvchi o'chirildi!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Xatolik: {str(e)}", "error")
    
    return redirect(url_for('admin_users'))
```

### Group Management:

```python
@app.route('/admin/groups')
def admin_groups():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    groups = Group.query.all()
    return render_template('admin_groups.html', groups=groups)

@app.route('/admin/groups/create', methods=['POST'])
def admin_create_group():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash("Guruh nomini kiriting!", "error")
        return redirect(url_for('admin_groups'))
    
    existing_group = Group.query.filter_by(name=name).first()
    if existing_group:
        flash("Bu guruh nomi allaqachon mavjud!", "error")
        return redirect(url_for('admin_groups'))
    
    new_group = Group(name=name, description=description)
    
    try:
        db.session.add(new_group)
        db.session.commit()
        flash("Guruh muvaffaqiyatli yaratildi!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Xatolik: {str(e)}", "error")
    
    return redirect(url_for('admin_groups'))
```

### Advanced Dashboard:

```python
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    # Basic statistics
    total_users = User.query.count()
    total_groups = Group.query.count()
    total_subjects = Subject.query.count()
    
    # User distribution
    admin_count = User.query.filter_by(is_admin=True).count()
    leader_count = User.query.filter_by(is_group_leader=True).count()
    student_count = User.query.filter_by(is_admin=False, is_group_leader=False).count()
    
    # Recent users
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Group statistics
    groups_with_users = db.session.query(Group, func.count(User.id)).join(User).group_by(Group.id).all()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_groups=total_groups,
                         total_subjects=total_subjects,
                         admin_count=admin_count,
                         leader_count=leader_count,
                         student_count=student_count,
                         recent_users=recent_users,
                         groups_with_users=groups_with_users)
```

## TEMPLATES:

### admin_users.html:

```html
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Foydalanuvchilar - Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .btn { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn-danger { background: #dc3545; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background: #f8f9fa; }
        .form { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .checkbox { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Foydalanuvchilar Boshqaruvi</h1>
            <a href="/admin/dashboard">Orqaga</a>
        </div>
        
        <div class="form">
            <h2>Yangi Foydalanuvchi Qo'shish</h2>
            <form method="post" action="/admin/users/create">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Ism:</label>
                    <input type="text" name="first_name" required>
                </div>
                <div class="form-group">
                    <label>Familiya:</label>
                    <input type="text" name="last_name" required>
                </div>
                <div class="form-group">
                    <label>Parol:</label>
                    <input type="password" name="password" required>
                </div>
                <div class="form-group">
                    <label>Guruh:</label>
                    <select name="group_id">
                        <option value="">Guruh tanlang</option>
                        {% for group in groups %}
                        <option value="{{ group.id }}">{{ group.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="checkbox">
                    <input type="checkbox" name="is_admin"> Admin
                </div>
                <div class="checkbox">
                    <input type="checkbox" name="is_group_leader"> Guruh rahbari
                </div>
                <button type="submit" class="btn">Qo'shish</button>
            </form>
        </div>
        
        <h2>Mavjud Foydalanuvchilar</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Ism</th>
                    <th>Familiya</th>
                    <th>Role</th>
                    <th>Guruh</th>
                    <th>Amallar</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.username }}</td>
                    <td>{{ user.first_name }}</td>
                    <td>{{ user.last_name }}</td>
                    <td>
                        {% if user.is_admin %}Admin{% endif %}
                        {% if user.is_group_leader %}Guruh rahbari{% endif %}
                        {% if not user.is_admin and not user.is_group_leader %}O'quvchi{% endif %}
                    </td>
                    <td>{{ user.group.name if user.group else '-' }}</td>
                    <td>
                        {% if user.username != 'admin' %}
                        <form method="post" action="/admin/users/{{ user.id }}/delete" style="display:inline;">
                            <button type="submit" class="btn btn-danger" onclick="return confirm('O\'chirishni istaysizmi?')">O'chirish</button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
```

## QO'SHISH JOYI:
app.py fayliga yangi routes qo'shish
templates papkasiga yangi shablonlar qo'shish

## NATIJA:
- Full user management system
- Advanced admin dashboard
- CRUD operatsiyalari
- Security features

## STATUS:
- [ ] User management routes qo'shiladi
- [ ] Group management routes qo'shiladi
- [ ] Advanced dashboard qo'shiladi
- [ ] Templates yaratiladi
- [ ] Security features qo'shiladi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Login ishlaydi
- [x] Basic admin dashboard ishlaydi
- [ ] Advanced features qo'shiladi

## KEYINGI QADAM:
QADAM 9: Testing & Production Deployment
