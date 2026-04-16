#!/usr/bin/env python3
"""
Clear SQLAlchemy Metadata Cache Script
Clears SQLAlchemy metadata cache and forces table reflection
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clear_sqlalchemy_cache():
    """Clear SQLAlchemy metadata cache"""
    print("=== CLEARING SQLALCHEMY CACHE ===")
    
    try:
        # Import app to clear metadata
        import app
        
        # Clear SQLAlchemy metadata
        app.db.metadata.clear()
        app.db.metadata.bind = None
        
        # Force table reflection
        with app.app.app_context():
            # Reflect database tables
            app.db.metadata.reflect(bind=app.db.engine)
            print("Database tables reflected!")
            
            # Test basic query
            try:
                groups = app.Group.query.limit(1).all()
                print("Basic query test: OK")
                return True
            except Exception as e:
                print(f"Query test failed: {e}")
                return False
                
    except Exception as e:
        print(f"Cache clearing error: {e}")
        return False

def test_after_cache_clear():
    """Test after clearing cache"""
    print("\n=== TESTING AFTER CACHE CLEAR ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test group query
            groups = app.Group.query.all()
            print(f"Groups query: {len(groups)} groups found")
            
            # Test user query
            users = app.User.query.limit(5).all()
            print(f"Users query: {len(users)} users found")
            
            # Test subject query
            subjects = app.Subject.query.all()
            print(f"Subjects query: {len(subjects)} subjects found")
            
            print("Post-cache-clear test: OK")
            return True
            
    except Exception as e:
        print(f"Post-cache-clear test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - SQLALCHEMY CACHE CLEAR")
    print("Clearing SQLAlchemy metadata cache...")
    
    if clear_sqlalchemy_cache():
        print("\nCache clearing successful!")
        
        if test_after_cache_clear():
            print("All tests passed!")
            return True
        else:
            print("Post-cache-clear tests failed!")
            return False
    else:
        print("Cache clearing failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
