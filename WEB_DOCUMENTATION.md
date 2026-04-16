# Step by Step Education Platform - Web Documentation

## **Platform Overview**

### **Project Description**
Step by Step Education Platform - Uzbek tilida to'liq ta'lim platformasi. O'quvchilar, guruh rahbarlari va adminlar uchun to'liq funksionallik.

### **Live URL**
- **Asosiy URL:** https://step-by-step-platform.onrender.com
- **Login:** admin/admin123
- **Status:** 24/7 Live

---

## **Technical Architecture**

### **Backend Technology**
- **Framework:** Flask 2.3.3
- **Database:** SQLite (Flask-SQLAlchemy 2.5.1)
- **Authentication:** Werkzeug Security
- **Deployment:** Render.com Cloud Platform

### **Frontend Technology**
- **Templates:** Jinja2
- **Styling:** Bootstrap 5.3
- **Icons:** FontAwesome 6.0
- **Language:** Uzbek (complete localization)

### **Deployment Configuration**
- **Platform:** Render.com
- **Auto-deploy:** GitHub integration
- **Database:** SQLite cloud storage
- **Availability:** 24/7

---

## **User Roles & Permissions**

### **Admin Role**
- **Full Access:** Barcha funktsiyalar
- **User Management:** O'quvchilar va guruh rahbarlari
- **Test Management:** Testlar yaratish va tahrir qilish
- **Schedule Management:** Dars jadvali
- **Subject Management:** Fanlar
- **Groups Management:** Guruhlar
- **Analytics:** Reytinglar va statistika

### **Group Leader Role**
- **Group Access:** O'z guruhidagi o'quvchilar
- **Test Management:** Guruh testlari
- **Schedule View:** Guruh jadvali
- **Basic Reports:** Guruh statistikasi

### **Student Role**
- **Personal Dashboard:** Shaxsiy kabinet
- **Test Taking:** Testlarni topshirish
- **Results View:** Natijalar
- **Schedule View:** Dars jadvali
- **Certificate Upload:** Sertifikatlar

---

## **Core Features**

### **Authentication System**
- **Login:** username/password
- **Session Management:** Xavfsiz sessiyalar
- **Role-based Access:** Rolga asoslangan kirish
- **Password Security:** Hashlangan parollar

### **Test System**
- **Test Creation:** Testlar yaratish
- **Question Types:** Multiple choice
- **Test Types:** DTM va Kundalik testlar
- **Schedule:** Vaqta asoslangan testlar
- **Results:** Avtomatik baholash
- **Statistics:** Test natijalari

### **User Management**
- **Student Registration:** O'quvchi qo'shish
- **Group Assignment:** Guruhga biriktirish
- **Leader Assignment:** Guruh rahbari
- **Password Reset:** Parolni tiklash
- **Profile Management:** Profil tahriri

### **Schedule System**
- **Weekly Schedule:** Haftalik jadval
- **Class Management:** Dars vaqtlari
- **Teacher Assignment:** O'qituvchilar
- **Room Management:** Xonalar
- **Conflict Detection:** Vaqt ziddiyatlari

### **Rating System**
- **Overall Rating:** Umumiy reyting
- **Group Rating:** Guruh reytingi
- **Subject Rating:** Fan bo'yicha reyting
- **Test Results:** Test natijalari
- **Progress Tracking:** Progress monitoring

---

## **Database Schema**

### **User Model**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_group_leader = db.Column(db.Boolean, default=False)
    needs_password_change = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
```

### **Group Model**
```python
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_score = db.Column(db.Integer, default=0)
```

### **Subject Model**
```python
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
```

### **Test Model**
```python
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    test_type = db.Column(db.String(20), default='daily')
    test_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    duration_minutes = db.Column(db.Integer)
```

---

## **API Endpoints**

### **Authentication**
- `GET /login` - Login sahifasi
- `POST /login` - Login amali
- `GET /logout` - Logout

### **Admin Panel**
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/students` - O'quvchilar ro'yxati
- `GET /admin/groups` - Guruhlar ro'yxati
- `GET /admin/tests` - Testlar ro'yxati
- `GET /admin/subjects` - Fanlar ro'yxati
- `GET /admin/schedule` - Jadval

### **Student Panel**
- `GET /student/dashboard` - Student dashboard
- `GET /tests` - Testlar
- `GET /subjects` - Fanlar
- `GET /schedule` - Jadval
- `GET /test_results` - Natijalar

### **Public Pages**
- `GET /` - Bosh sahifa
- `GET /overall_rating` - Umumiy reyting
- `GET /group_rating` - Guruh reytingi

---

## **Deployment Instructions**

### **Local Development**
```bash
# Clone repository
git clone https://github.com/akmaljaxonkulov1221-web/step-by-step-platform.git
cd step-by-step

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### **Production Deployment**
```bash
# Push to GitHub
git add .
git commit -m "Update production"
git push origin main

# Render.com auto-deploys from main branch
```

### **Environment Variables**
- `FLASK_ENV`: production
- `PORT`: 5000
- `SECRET_KEY`: Auto-generated
- `DATABASE_URL`: sqlite:///education_complete.db

---

## **Security Features**

### **Authentication Security**
- **Password Hashing:** Werkzeug security
- **Session Management:** Flask sessions
- **CSRF Protection:** Flask-WTF
- **Role Validation:** Route-based access control

### **Data Security**
- **SQL Injection Protection:** SQLAlchemy ORM
- **XSS Protection:** Jinja2 auto-escaping
- **Input Validation:** WTForms validation
- **Secure Headers:** Flask security headers

---

## **Backup & Recovery**

### **Database Backup**
- **Automated Backup:** Backup script
- **Manual Backup:** Backup button
- **Recovery:** Restore functionality
- **Data Integrity:** Validation checks

### **File Backup**
- **Database File:** SQLite backup
- **Configuration Files:** Git version control
- **Static Files:** Render.com storage
- **Logs:** Application logs

---

## **Maintenance**

### **Regular Tasks**
- **Database Optimization:** Weekly cleanup
- **Log Review:** Error monitoring
- **Security Updates:** Dependency updates
- **Performance Monitoring:** Load testing

### **Troubleshooting**
- **Common Issues:** Error fix script
- **Database Issues:** Database repair
- **Performance Issues:** Optimization
- **Deployment Issues:** Render.com logs

---

## **User Guide**

### **For Admins**
1. **Login:** admin/admin123
2. **Dashboard:** Overview of system
3. **Users:** Add/edit students and leaders
4. **Tests:** Create and manage tests
5. **Schedule:** Manage class schedule
6. **Reports:** View statistics

### **For Students**
1. **Login:** Use assigned credentials
2. **Dashboard:** View personal progress
3. **Tests:** Take available tests
4. **Results:** View test results
5. **Schedule:** View class schedule

### **For Group Leaders**
1. **Login:** Use assigned credentials
2. **Group Management:** Manage group students
3. **Tests:** Create group tests
4. **Reports:** View group statistics

---

## **Support & Contact**

### **Technical Support**
- **Repository:** https://github.com/akmaljaxonkulov1221-web/step-by-step-platform
- **Issues:** GitHub issues
- **Documentation:** This file

### **Platform Access**
- **URL:** https://step-by-step-platform.onrender.com
- **Admin Login:** admin/admin123
- **Status:** 24/7 Available

---

## **Version History**

### **Current Version: 1.0.0**
- **Release Date:** April 2026
- **Features:** Complete education platform
- **Language:** Uzbek localization
- **Deployment:** Render.com cloud hosting

### **Previous Versions**
- **Development:** Multiple iterations
- **Testing:** Comprehensive testing
- **Feedback:** User-driven improvements

---

## **Future Enhancements**

### **Planned Features**
- **Mobile App:** Native mobile application
- **Advanced Analytics:** Detailed reporting
- **Integration APIs:** Third-party integrations
- **Multi-language:** Additional language support

### **Technical Improvements**
- **Database Migration:** PostgreSQL migration
- **Performance Optimization:** Caching implementation
- **Security Enhancements:** Advanced security features
- **Scalability:** Load balancing

---

## **Conclusion**

Step by Step Education Platform - Uzbek tilida to'liq funksionallikga ega ta'lim platformasi. 24/7 availability, xavfsiz authentication, va comprehensive user management bilan ta'minlangan.

**Platform Status:** Production Ready
**Availability:** 24/7 Live
**Support:** Active maintenance
**Future:** Continuous improvement
