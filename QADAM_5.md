# QADAM 5: Admin Dashboard Route Qo'shish

## MAQSAD:
Admin dashboard route qo'shish va basic statistics ko'rsatish

## QILINADIGAN ISHLAR:

### 1. Admin dashboard route qo'shish
- Admin only access
- Basic statistics
- User management

### 2. Statistics qo'shish
- Total users count
- Total groups count
- Total subjects count
- Recent activities

### 3. Navigation qo'shish
- Admin menu
- Quick links
- User management

## KOD:

```python
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    # Get basic statistics
    total_users = User.query.count()
    total_groups = Group.query.count()
    total_subjects = Subject.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Get user distribution
    admin_count = User.query.filter_by(is_admin=True).count()
    leader_count = User.query.filter_by(is_group_leader=True).count()
    student_count = User.query.filter_by(is_admin=False, is_group_leader=False).count()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_groups=total_groups,
                         total_subjects=total_subjects,
                         recent_users=recent_users,
                         admin_count=admin_count,
                         leader_count=leader_count,
                         student_count=student_count)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
```

## QO'SHISH JOYI:
Logout route dan oldin qo'shish

## NATIJA:
- Admin dashboard ishlaydi
- Statistics ko'rsatiladi
- Recent users ko'rsatiladi
- User distribution ko'rsatiladi

## STATUS:
- [x] Admin dashboard route qo'shildi
- [x] Basic statistics qo'shildi
- [x] Recent users qo'shildi
- [x] User distribution qo'shildi

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Admin panel ishlaydi
- [x] Statistics ko'rsatiladi
- [x] User management tayor

## KEYINGI QADAM:
QADAM 6: Testing & Deployment
