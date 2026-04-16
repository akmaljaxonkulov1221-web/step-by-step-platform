#!/usr/bin/env python3
"""
Create Sample Data - Simple Version
Create sample data without importing app
"""

import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_data_direct():
    """Create sample data directly in database"""
    print("=== CREATING SAMPLE DATA DIRECTLY ===")
    
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # 1. Create enhanced topics
        print("\n1. Creating Enhanced Topics")
        topics_data = [
            ('Ingliz tili grammatikasi', 'Ingliz tili grammatikasi', 'https://www.youtube.com/watch?v=dX3nQXkXGao', 'present_tense_grammar.pdf', 'Present tense vaqtidagi grammatik qoidalarini o\'rganing. Bu mavzuda oddiy vaqt, davomiy vaqt, mukammal vaqt shakllari ko\'rib chiqiladi.', 1),
            ('Ingliz tili - So\'zboylash', 'Ingliz tili So\'zboylash', 'https://www.youtube.com/watch?v=1kNQbHsS4ZE', 'vocabulary_builder.pdf', 'Ingliz tilida so\'zboylash usullari va yangi so\'zlarni esda saqlash texnikalari. Har kuni 5 ta yangi so\'z o\'rganing!', 1),
            ('Matematika - Kvadrat tenglamalar', 'Kvadrat Tenglamalar', 'https://www.youtube.com/watch?v=U0Yg--eJZ-U', 'quadratic_equations.pdf', 'Kvadrat tenglamalarni yechish usullari: diskriminant usuli, faktorizatsiya usuli, kvadrat ildiz formulasi.', 2),
            ('Fizika - Newton qonunlari', 'Newtonning Harakat Qonunlari', 'https://www.youtube.com/watch?v=KKMW5M-7fYY', 'newton_laws.pdf', 'Newtonning uchta harakat qonuni: birinchi qonun (inertsiya), ikkinchi qonun (F=ma), uchinchi qonun (harakat va reaktsiya).', 3)
        ]
        
        for topic in topics_data:
            cursor.execute('''
                INSERT OR IGNORE INTO topic (name, title, youtube_link, pdf_file, description, subject_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', topic)
            print(f"   Created topic: {topic[0]}")
        
        # 2. Create AI chats
        print("\n2. Creating AI Chats")
        # Get first user ID
        cursor.execute('SELECT id FROM user WHERE is_admin = 0 LIMIT 1')
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            
            # Get topic IDs
            cursor.execute('SELECT id, name FROM topic')
            topics = cursor.fetchall()
            
            ai_chats_data = [
                (user_id, 'Ingliz tili grammatikasida Present Tense qanday ishlatiladi?', 'Present Tense - bu hozirgi vaqtni ifodalovchi vaqt. U oddiy harakatlarni (I work - Men ishlayman), muntazam harakatlarni (He plays - U o\'ynaydi) va umumiy haqiqatlarni (Water boils - Suv qaynaydi) ifodalaydi. Present Continuous esa hozirgi vaqtda davom etayotgan harakatlarni ifodalaydi (I am working - Men hozir ishlamoqdaman).', topics[0][0] if topics else None, 0),
                (user_id, 'Kvadrat tenglamani qanday yechish mumkin?', 'Kvadrat tenglamani yechishning bir necha usuli bor: 1) Diskriminant usuli: D = b²-4ac formuladan foydalanib, x = (-b ± sqrt(D))/2a. 2) Faktorizatsiya usuli: Tenglama ko\'paytuvchilarga ajratiladi. 3) To\'la kvadrat usuli: (x + b/2a)² = (b²-4ac)/4a². Diskriminant usuli eng umumiy va ishonatli usul hisoblanadi.', topics[2][0] if len(topics) > 2 else None, 1),
                (user_id, 'Ingliz tilida so\'zboylashning eng samarali usuli nima?', 'Eng samarali so\'zboylash usullari: 1) Spaced repetition - so\'zlarni muntazam takrorlash (Anki, Quizlet kabi dasturlardan foydalaning). 2) Context learning - so\'zlarni gaplar ichida o\'rganing. 3) Active recall - eslab turishga harakat qiling. 4) Multiple exposure - so\'zni turli shakllarda ko\'ring (eshitib, o\'qib, yozib).', topics[1][0] if topics else None, 0)
            ]
            
            for chat in ai_chats_data:
                cursor.execute('''
                    INSERT OR IGNORE INTO ai_chat (user_id, question, answer, topic_id, test_generated, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', chat + (datetime.now(),))
                print(f"   Created AI chat: {chat[1][:50]}...")
        
        # 3. Create enhanced tests
        print("\n3. Creating Enhanced Tests")
        test_titles = [
            ('Ingliz tili Present Tense Testi', 1, 'ai_generated'),
            ('Matematika Kvadrat Tenglamalar Testi', 2, 'ai_generated')
        ]
        
        for title, subject_id, test_type in test_titles:
            # Create test
            cursor.execute('''
                INSERT OR IGNORE INTO test (title, subject_id, test_type, test_date)
                VALUES (?, ?, ?, ?)
            ''', (title, subject_id, test_type, datetime.now().date()))
            
            cursor.execute('SELECT id FROM test WHERE title = ?', (title,))
            test_result = cursor.fetchone()
            
            if test_result:
                test_id = test_result[0]
                
                # Create 20 questions
                for i in range(1, 21):
                    correct_answer = random.choice(['A', 'B', 'C', 'D'])
                    options = {
                        'A': f"Variant A - {title} bo'yicha {i}-javob varianti",
                        'B': f"Variant B - {title} bo'yicha {i}-javob varianti",
                        'C': f"Variant C - {title} bo'yicha {i}-javob varianti",
                        'D': f"Variant D - {title} bo'yicha {i}-javob varianti"
                    }
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO question (test_id, question, option_a, option_b, option_c, option_d, correct_answer)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (test_id, f"{title} - {i}-savol", options['A'], options['B'], options['C'], options['D'], correct_answer))
                
                print(f"   Created test: {title} (20 questions)")
        
        # 4. Create test results
        print("\n4. Creating Test Results")
        cursor.execute('SELECT id FROM user WHERE is_admin = 0 AND is_group_leader = 0 LIMIT 2')
        students = cursor.fetchall()
        
        cursor.execute('SELECT id FROM test WHERE test_type = \'ai_generated\' LIMIT 1')
        tests = cursor.fetchall()
        
        if students and tests:
            for student in students:
                for test in tests:
                    score = random.randint(12, 20)
                    percentage = (score / 20) * 100
                    
                    all_answers = list(range(1, 21))
                    correct_answers = random.sample(all_answers, score)
                    incorrect_answers = [a for a in all_answers if a not in correct_answers]
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO test_result 
                        (user_id, test_id, score, total_questions, percentage, correct_answers, incorrect_answers, total_time, taken_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (student[0], test[0], score, 20, percentage, 
                          ','.join(map(str, correct_answers)), 
                          ','.join(map(str, incorrect_answers)),
                          random.randint(600, 1800),
                          datetime.now() - timedelta(days=random.randint(1, 7))))
                    
                    print(f"   Created test result: Student {student[0]} - {score}/20")
        
        # 5. Create enhanced certificates
        print("\n5. Creating Enhanced Certificates")
        cursor.execute('SELECT id FROM user WHERE is_admin = 0 LIMIT 2')
        users = cursor.fetchall()
        
        cert_data = [
            ('Ingliz tili B1 Level', 'Ingliz tili bo\'yicha B1 darajasi sertifikati', 'B1', 'B1', 'achievement', 50, users[0][0] if users else None),
            ('Matematika Asoslari', 'Matematika asosiy kursini tugatgani uchun', 'Basic', 'Basic', 'completion', 30, users[1][0] if len(users) > 1 else users[0][0] if users else None)
        ]
        
        for cert in cert_data:
            cursor.execute('''
                INSERT OR IGNORE INTO certificate (title, description, level, subject_level, certificate_type, points, user_id, issued_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', cert + (datetime.now(),))
            print(f"   Created certificate: {cert[0]}")
        
        conn.commit()
        conn.close()
        
        # Display summary
        print("\n=== SAMPLE DATA SUMMARY ===")
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        counts = {
            'Topics': cursor.execute('SELECT COUNT(*) FROM topic').fetchone()[0],
            'AI Chats': cursor.execute('SELECT COUNT(*) FROM ai_chat').fetchone()[0],
            'Tests': cursor.execute('SELECT COUNT(*) FROM test').fetchone()[0],
            'Questions': cursor.execute('SELECT COUNT(*) FROM question').fetchone()[0],
            'Test Results': cursor.execute('SELECT COUNT(*) FROM test_result').fetchone()[0],
            'Certificates': cursor.execute('SELECT COUNT(*) FROM certificate').fetchone()[0]
        }
        
        for key, count in counts.items():
            print(f"{key}: {count}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - SAMPLE DATA CREATION")
    print("Creating comprehensive sample data...")
    
    if create_sample_data_direct():
        print("\n=== SAMPLE DATA CREATION COMPLETE ===")
        print("All sample data created successfully!")
        print("System is now ready for testing!")
        return True
    else:
        print("\nSample data creation failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
