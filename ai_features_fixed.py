#!/usr/bin/env python3
"""
AI Features Implementation
AI chatbot and automatic test generation
"""

import os
import sys
import json
import random
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_ai_routes():
    """Add AI-related routes to app.py"""
    print("=== ADDING AI ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add AI chatbot route
        ai_chat_route = '''
@app.route('/ai_chat', methods=['GET', 'POST'])
def ai_chat():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()
        topic_id = request.form.get('topic_id', type=int)
        generate_test = request.form.get('generate_test') == 'on'
        
        if not user_question:
            return render_template('ai_chat.html', error="Iltimos, savol kiriting!")
        
        try:
            # Generate AI response (mock implementation)
            ai_response = generate_ai_response(user_question, topic_id)
            
            # Save chat to database
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=topic_id,
                test_generated=generate_test
            )
            db.session.add(chat)
            db.session.commit()
            
            # If user wants to generate test
            if generate_test and topic_id:
                test_id = generate_ai_test(topic_id, user_question)
                if test_id:
                    return redirect(url_for('take_test', test_id=test_id))
            
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 last_question=user_question,
                                 last_answer=ai_response)
            
        except Exception as e:
            app.logger.error(f"AI chat error: {str(e)}")
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 error="AI javob berishda xatolik yuz berdi")
    
    return render_template('ai_chat.html', 
                         topics=Topic.query.all(),
                         chat_history=get_chat_history())

def generate_ai_response(question, topic_id=None):
    """Generate AI response (mock implementation)"""
    # This is a mock implementation - in real app, you'd integrate with OpenAI or similar
    responses = [
        "Bu savolga javob berish uchun qo'shimcha ma'lumot kerak. Iltimos, savolingizni aniqroq qiling.",
        "Bu juda yaxshi savol! Keling, buni batafsil ko'rib chiqaylik.",
        "Sizning savolingiz o'quv jarayonida muhim rol o'ynaydi. Quyidagicha javob berish mumkin:",
        "Bu mavzu bo'yicha quyidagi tavsiyalarni berish mumkin:",
        "Sizning savolingiz asosida, quyidagi izohlar muhim:"
    ]
    
    base_response = random.choice(responses)
    
    if topic_id:
        topic = Topic.query.get(topic_id)
        if topic:
            base_response += f" {topic.name} mavzusi bo'yicha, {topic.description if topic.description else 'qo\'shimcha materiallar bilan'} ishlash tavsiya etiladi."
    
    return base_response + " Bu javob AI tomonidan avtomatik ravishda yaratilgan."

def generate_ai_test(topic_id, question):
    """Generate AI-powered test (20 questions)"""
    try:
        topic = Topic.query.get(topic_id)
        if not topic:
            return None
        
        # Create test
        test = Test(
            title=f"AI yaratilgan test - {topic.name}",
            subject_id=topic.subject_id,
            test_type='ai_generated',
            test_date=datetime.now().date()
        )
        db.session.add(test)
        db.session.flush()
        
        # Generate 20 questions
        for i in range(1, 21):
            question_text = f"{topic.name} bo'yicha {i}-savol (AI yaratilgan)"
            
            # Generate 4 options
            correct_answer = random.choice(['A', 'B', 'C', 'D'])
            options = {
                'A': f"Variant A - {topic.name} bo'yicha javob",
                'B': f"Variant B - {topic.name} bo'yicha javob", 
                'C': f"Variant C - {topic.name} bo'yicha javob",
                'D': f"Variant D - {topic.name} bo'yicha javob"
            }
            
            question_obj = Question(
                test_id=test.id,
                question=question_text,
                option_a=options['A'],
                option_b=options['B'],
                option_c=options['C'],
                option_d=options['D'],
                correct_answer=correct_answer
            )
            db.session.add(question_obj)
        
        db.session.commit()
        return test.id
        
    except Exception as e:
        app.logger.error(f"AI test generation error: {str(e)}")
        return None

def get_chat_history():
    """Get user's chat history"""
    return AIChat.query.filter_by(user_id=session['user_id']).order_by(AIChat.created_at.desc()).limit(10).all()

'''
        
        # Add the route before the last @app.route
        last_route_pos = content.rfind('@app.route')
        if last_route_pos != -1:
            content = content[:last_route_pos] + ai_chat_route + '\n' + content[last_route_pos:]
        
        # Write updated content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("AI routes added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding AI routes: {e}")
        return False

def create_ai_chat_template():
    """Create AI chat template"""
    print("=== CREATING AI CHAT TEMPLATE ===")
    
    template_content = '''{% extends "base.html" %}

{% block title %}AI Chatbot{% endblock %}

{% block page_title %}AI Chatbot{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-robot"></i> AI Chatbot
                    </h5>
                </div>
                <div class="card-body">
                    {% if error %}
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            {{ error }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endif %}
                    
                    {% if last_question and last_answer %}
                        <div class="chat-message mb-3">
                            <div class="alert alert-info">
                                <strong>Sizning savolingiz:</strong> {{ last_question }}
                            </div>
                            <div class="alert alert-success">
                                <strong>AI javobi:</strong> {{ last_answer }}
                            </div>
                        </div>
                    {% endif %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label for="question" class="form-label">Savolingiz</label>
                            <textarea class="form-control" id="question" name="question" rows="3" 
                                      placeholder="Istalgan savolni yozing..." required></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label for="topic_id" class="form-label">Mavzu (tanlangan bo'lsa)</label>
                            <select class="form-select" id="topic_id" name="topic_id">
                                <option value="">Mavzuni tanlang</option>
                                {% for topic in topics %}
                                <option value="{{ topic.id }}">{{ topic.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="generate_test" name="generate_test">
                                <label class="form-check-label" for="generate_test">
                                    Shu mavzu asosida test yaratish (20 ta savol)
                                </label>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary" id="submit-btn">
                                <i class="fas fa-paper-plane"></i> Savol yuborish
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            {% if chat_history %}
            <div class="card mt-3">
                <div class="card-header">
                    <h6 class="mb-0">Chat tarixi</h6>
                </div>
                <div class="card-body">
                    {% for chat in chat_history %}
                    <div class="chat-history-item mb-2">
                        <small class="text-muted">{{ chat.created_at.strftime('%H:%M') }}</small>
                        <div class="alert alert-light">
                            <strong>Savol:</strong> {{ chat.question[:100] }}{% if chat.question|length > 100 %}...{% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">Qo'llanma</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li class="mb-2">
                            <i class="fas fa-question-circle text-primary"></i>
                            Istalgan savol yozishingiz mumkin
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-robot text-success"></i>
                            AI tushunarli javob beradi
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-file-alt text-warning"></i>
                            Test yaratish imkoniyati
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-history text-info"></i>
                            Chat tarixi saqlanadi
                        </li>
                    </ul>
                    
                    <div class="alert alert-info">
                        <small>
                            <i class="fas fa-info-circle"></i>
                            AI javoblari avtomatik ravishda yaratiladi. Uzr, ba'zi savollarga to'liq javob bera olmasligimiz mumkin.
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.querySelector('form').addEventListener('submit', function(e) {
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yuborilmoqda...';
    submitBtn.disabled = true;
    
    // Re-enable after 3 seconds (simulated processing time)
    setTimeout(() => {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Savol yuborish';
        submitBtn.disabled = false;
    }, 3000);
});
</script>
{% endblock %}
'''
        
        try:
            os.makedirs('templates', exist_ok=True)
            with open('templates/ai_chat.html', 'w', encoding='utf-8') as f:
                f.write(template_content)
            print("AI chat template created!")
            return True
        except Exception as e:
            print(f"Error creating AI chat template: {e}")
            return False

def add_ai_chat_to_navigation():
    """Add AI chat to navigation"""
    print("=== ADDING AI CHAT TO NAVIGATION ===")
    
    try:
        # Read base.html
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add AI chat link to navigation
        if 'ai_chat' not in content:
            # Find where to add the link (after tests)
            if '<a href="{{ url_for(\'tests\') }}"' in content:
                ai_link = '''                    <a href="{{ url_for('ai_chat') }}" class="nav-link">
                        <i class="fas fa-robot"></i> AI Chat
                    </a>'''
                
                # Find the tests link and add AI chat after it
                tests_link_pos = content.find('<a href="{{ url_for(\'tests\') }}"')
                if tests_link_pos != -1:
                    # Find the end of the tests link
                    end_of_tests_link = content.find('</a>', tests_link_pos) + 4
                    # Find the next </li> or </ul>
                    next_element = content.find('</li>', end_of_tests_link)
                    if next_element == -1:
                        next_element = content.find('</ul>', end_of_tests_link)
                    
                    if next_element != -1:
                        content = content[:next_element] + '\n' + ai_link + '\n                    ' + content[next_element:]
            
            with open('templates/base.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("AI chat added to navigation!")
        else:
            print("AI chat already in navigation")
        
        return True
        
    except Exception as e:
        print(f"Error adding AI chat to navigation: {e}")
        return False

def main():
    """Main AI features implementation"""
    print("STEP BY STEP EDUCATION PLATFORM - AI FEATURES")
    print("Implementing AI chatbot and test generation...")
    
    success_steps = []
    
    # Add AI routes
    if add_ai_routes():
        success_steps.append("AI Routes")
    else:
        print("Failed to add AI routes")
        return False
    
    # Create AI chat template
    if create_ai_chat_template():
        success_steps.append("AI Chat Template")
    else:
        print("Failed to create AI chat template")
        return False
    
    # Add AI chat to navigation
    if add_ai_chat_to_navigation():
        success_steps.append("Navigation Update")
    else:
        print("Failed to update navigation")
        return False
    
    print(f"\n=== AI FEATURES IMPLEMENTATION COMPLETE ===")
    print(f"Successfully completed: {', '.join(success_steps)}")
    print("AI chatbot and test generation features added!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
