#!/usr/bin/env python3
"""
Add AI Features - Simple Implementation
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_ai_routes_simple():
    """Add AI routes to app.py"""
    print("=== ADDING AI ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple AI route
        ai_route = '''@app.route('/ai_chat', methods=['GET', 'POST'])
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
            # Mock AI response
            ai_response = "Bu savolga AI tomonidan avtomatik javob. Bu test versiyasi."
            
            # Save chat
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=topic_id,
                test_generated=generate_test
            )
            db.session.add(chat)
            db.session.commit()
            
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 last_question=user_question,
                                 last_answer=ai_response)
            
        except Exception as e:
            app.logger.error(f"AI chat error: {str(e)}")
            return render_template('ai_chat.html', error="Xatolik yuz berdi")
    
    return render_template('ai_chat.html', 
                         topics=Topic.query.all(),
                         chat_history=get_chat_history())

def get_chat_history():
    """Get user's chat history"""
    return AIChat.query.filter_by(user_id=session['user_id']).order_by(AIChat.created_at.desc()).limit(10).all()

'''
        
        # Add before last route
        last_route_pos = content.rfind('@app.route')
        if last_route_pos != -1:
            content = content[:last_route_pos] + ai_route + '\n' + content[last_route_pos:]
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("AI routes added!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_ai_template():
    """Create AI chat template"""
    print("=== CREATING AI TEMPLATE ===")
    
    template = '''{% extends "base.html" %}

{% block title %}AI Chatbot{% endblock %}

{% block page_title %}AI Chatbot{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-robot"></i> AI Chatbot</h5>
                </div>
                <div class="card-body">
                    {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    
                    {% if last_question and last_answer %}
                    <div class="mb-3">
                        <div class="alert alert-info">
                            <strong>Savol:</strong> {{ last_question }}
                        </div>
                        <div class="alert alert-success">
                            <strong>Javob:</strong> {{ last_answer }}
                        </div>
                    </div>
                    {% endif %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Savolingiz</label>
                            <textarea class="form-control" name="question" rows="3" 
                                      placeholder="Savolni yozing..." required></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Mavzu</label>
                            <select class="form-select" name="topic_id">
                                <option value="">Mavzuni tanlang</option>
                                {% for topic in topics %}
                                <option value="{{ topic.id }}">{{ topic.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="generate_test" id="generate_test">
                                <label class="form-check-label" for="generate_test">
                                    Test yaratish (20 savol)
                                </label>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-paper-plane"></i> Yuborish
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h6>Qo'llanma</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li><i class="fas fa-question text-primary"></i> Savol yozing</li>
                        <li><i class="fas fa-robot text-success"></i> AI javob beradi</li>
                        <li><i class="fas fa-file text-warning"></i> Test yaratish</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    try:
        with open('templates/ai_chat.html', 'w', encoding='utf-8') as f:
            f.write(template)
        print("AI template created!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("STEP BY STEP - AI FEATURES")
    
    if add_ai_routes_simple() and create_ai_template():
        print("AI features added successfully!")
        return True
    else:
        print("Failed to add AI features")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
