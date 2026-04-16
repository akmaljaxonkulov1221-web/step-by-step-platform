import unittest
import requests
from app import app, db, User, Group

class TestEducationPlatform(unittest.TestCase):
    
    def setUp(self):
        """Test setup"""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Test cleanup"""
        with app.app_context():
            db.drop_all()
    
    def test_homepage(self):
        """Test homepage loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ta\'lim Platformasi', response.data)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_admin_login(self):
        """Test admin login"""
        # Create admin user
        with app.app_context():
            admin = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_group_leader=False
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Test login
        response = self.app.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        self.assertIn(b'Login successful', response.data)
    
    def test_user_creation(self):
        """Test user creation"""
        response = self.app.post('/admin/users/create', data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'test123',
            'is_admin': 'on'
        }, follow_redirects=True)
        
        # Check if user was created
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, 'Test')
    
    def test_group_creation(self):
        """Test group creation"""
        response = self.app.post('/admin/groups/create', data={
            'name': 'Test Group',
            'description': 'Test group description'
        }, follow_redirects=True)
        
        # Check if group was created
        with app.app_context():
            group = Group.query.filter_by(name='Test Group').first()
            self.assertIsNotNone(group)
            self.assertEqual(group.description, 'Test group description')

if __name__ == '__main__':
    unittest.main()
