#!/usr/bin/env python3
"""
Upgrade Test System
Upgrade to 20 questions with 4 options each
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def upgrade_test_templates():
    """Upgrade test templates to show 20 questions"""
    print("=== UPGRADING TEST TEMPLATES ===")
    
    try:
        # Upgrade take_test.html
        take_test_content = '''{% extends "base.html" %}

{% block title %}{{ test.title }}{% endblock %}

{% block page_title %}{{ test.title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-file-alt"></i> {{ test.title }}
                    </h5>
                    <small class="text-muted">
                        Test turi: {{ test.test_type }} | 
                        Jami savollar: {{ questions|length }} ta
                    </small>
                </div>
                <div class="card-body">
                    {% if test_result %}
                    <div class="alert alert-success">
                        <h5>Test natijasi</h5>
                        <p><strong>Ball:</strong> {{ test_result.score }}/{{ test_result.total_questions }}</p>
                        <p><strong>Foiz:</strong> {{ "%.1f"|format(test_result.percentage) }}%</p>
                        
                        {% if test_result.correct_answers %}
                        <h6>To'g'ri javoblar:</h6>
                        <p>{{ test_result.correct_answers }}</p>
                        
                        <h6>Noto'g'ri javoblar:</h6>
                        <p>{{ test_result.incorrect_answers }}</p>
                        {% endif %}
                        
                        <div class="mt-3">
                            <a href="{{ url_for('tests') }}" class="btn btn-primary">
                                <i class="fas fa-arrow-left"></i> Testlarga qaytish
                            </a>
                        </div>
                    </div>
                    {% else %}
                    <form method="POST" id="testForm">
                        <input type="hidden" name="test_id" value="{{ test.id }}">
                        <input type="hidden" name="start_time" id="start_time">
                        
                        <div class="progress mb-3">
                            <div class="progress-bar" id="progressBar" style="width: 0%">0%</div>
                        </div>
                        
                        <div id="questionsContainer">
                            {% for question in questions %}
                            <div class="question-container mb-4" data-question="{{ loop.index }}" style="display: none;">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">
                                            Savol {{ loop.index }}/{{ questions|length }}
                                        </h6>
                                    </div>
                                    <div class="card-body">
                                        <p class="question-text">{{ question.question }}</p>
                                        
                                        <div class="options-container">
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" 
                                                       name="question_{{ question.id }}" 
                                                       value="A" id="q{{ question.id }}_a" required>
                                                <label class="form-check-label" for="q{{ question.id }}_a">
                                                    A. {{ question.option_a }}
                                                </label>
                                            </div>
                                            
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" 
                                                       name="question_{{ question.id }}" 
                                                       value="B" id="q{{ question.id }}_b">
                                                <label class="form-check-label" for="q{{ question.id }}_b">
                                                    B. {{ question.option_b }}
                                                </label>
                                            </div>
                                            
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" 
                                                       name="question_{{ question.id }}" 
                                                       value="C" id="q{{ question.id }}_c">
                                                <label class="form-check-label" for="q{{ question.id }}_c">
                                                    C. {{ question.option_c }}
                                                </label>
                                            </div>
                                            
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" 
                                                       name="question_{{ question.id }}" 
                                                       value="D" id="q{{ question.id }}_d">
                                                <label class="form-check-label" for="q{{ question.id }}_d">
                                                    D. {{ question.option_d }}
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div class="navigation-buttons mt-3">
                                            {% if loop.index > 1 %}
                                            <button type="button" class="btn btn-secondary" onclick="previousQuestion({{ loop.index - 1 }})">
                                                <i class="fas fa-arrow-left"></i> Oldingi
                                            </button>
                                            {% endif %}
                                            
                                            {% if loop.index < questions|length %}
                                            <button type="button" class="btn btn-primary" onclick="nextQuestion({{ loop.index + 1 }})">
                                                Keyingi <i class="fas fa-arrow-right"></i>
                                            </button>
                                            {% else %}
                                            <button type="submit" class="btn btn-success">
                                                <i class="fas fa-check"></i> Testni tugatish
                                            </button>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="text-center mt-4">
                            <button type="button" class="btn btn-primary" id="startTestBtn" onclick="startTest()">
                                <i class="fas fa-play"></i> Testni boshlash
                            </button>
                        </div>
                    </form>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let currentQuestion = 0;
let totalQuestions = {{ questions|length }};
let startTime = null;

function startTest() {
    document.getElementById('startTestBtn').style.display = 'none';
    document.getElementById('start_time').value = new Date().toISOString();
    startTime = new Date();
    
    // Show first question
    showQuestion(1);
}

function showQuestion(questionNum) {
    // Hide all questions
    document.querySelectorAll('.question-container').forEach(q => {
        q.style.display = 'none';
    });
    
    // Show current question
    const currentQ = document.querySelector(`[data-question="${questionNum}"]`);
    if (currentQ) {
        currentQ.style.display = 'block';
        currentQuestion = questionNum;
        
        // Update progress
        const progress = (questionNum / totalQuestions) * 100;
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';
    }
}

function nextQuestion(questionNum) {
    if (questionNum <= totalQuestions) {
        showQuestion(questionNum);
    }
}

function previousQuestion(questionNum) {
    if (questionNum >= 1) {
        showQuestion(questionNum);
    }
}

// Form validation
document.getElementById('testForm').addEventListener('submit', function(e) {
    const unansweredQuestions = [];
    
    {% for question in questions %}
    const answered{{ question.id }} = document.querySelector('input[name="question_{{ question.id }}"]:checked');
    if (!answered{{ question.id }}) {
        unansweredQuestions.push({{ loop.index }});
    }
    {% endfor %}
    
    if (unansweredQuestions.length > 0) {
        e.preventDefault();
        alert(`Iltimos, quyidagi savollarga javob bering: ${unansweredQuestions.join(', ')}`);
        return false;
    }
    
    // Calculate total time
    if (startTime) {
        const totalTime = Math.floor((new Date() - startTime) / 1000);
        const timeInput = document.createElement('input');
        timeInput.type = 'hidden';
        timeInput.name = 'total_time';
        timeInput.value = totalTime;
        this.appendChild(timeInput);
    }
    
    // Show loading
    const submitBtn = this.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Natijalar hisoblanmoqda...';
    submitBtn.disabled = true;
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    showQuestion(1);
});
</script>
{% endblock %}
'''
        
        with open('templates/take_test.html', 'w', encoding='utf-8') as f:
            f.write(take_test_content)
        
        print("Test templates upgraded!")
        return True
        
    except Exception as e:
        print(f"Error upgrading templates: {e}")
        return False

def upgrade_test_result_display():
    """Upgrade test result display"""
    print("=== UPGRADING TEST RESULT DISPLAY ===")
    
    try:
        # Upgrade test_result.html
        result_content = '''{% extends "base.html" %}

{% block title %}Test Natijasi{% endblock %}

{% block page_title %}Test Natijasi{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-chart-line"></i> Test Natijasi
                    </h5>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <h2>{{ test_result.score }}/{{ test_result.total_questions }}</h2>
                        <div class="progress mb-3" style="height: 25px;">
                            <div class="progress-bar {% if test_result.percentage >= 80 %}bg-success{% elif test_result.percentage >= 60 %}bg-warning{% else %}bg-danger{% endif %}" 
                                 style="width: {{ test_result.percentage }}%">
                                {{ "%.1f"|format(test_result.percentage) }}%
                            </div>
                        </div>
                        
                        {% if test_result.percentage >= 80 %}
                        <div class="alert alert-success">
                            <i class="fas fa-trophy"></i> A'lo! Testni muvaffaqiyatli tugatdingiz!
                        </div>
                        {% elif test_result.percentage >= 60 %}
                        <div class="alert alert-warning">
                            <i class="fas fa-thumbs-up"></i> Yaxshi! Biroz ko'proq tayyorlanish kerak.
                        </div>
                        {% else %}
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> Qayta urinib ko'ring!
                        </div>
                        {% endif %}
                    </div>
                    
                    {% if test_result.correct_answers %}
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card border-success">
                                <div class="card-header bg-success text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-check"></i> To'g'ri javoblar
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <p class="mb-0">{{ test_result.correct_answers }}</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card border-danger">
                                <div class="card-header bg-danger text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-times"></i> Noto'g'ri javoblar
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <p class="mb-0">{{ test_result.incorrect_answers }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="mt-4">
                        <h5>Barcha savollar va to'g'ri javoblar:</h5>
                        <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Savol</th>
                                        <th>Sizning javobingiz</th>
                                        <th>To'g'ri javob</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for question in questions %}
                                    <tr>
                                        <td>{{ loop.index }}. {{ question.question|truncatechars(50) }}</td>
                                        <td>
                                            {% if user_answers and user_answers[question.id] %}
                                                {{ user_answers[question.id] }}
                                            {% else %}
                                                -
                                            {% endif %}
                                        </td>
                                        <td class="fw-bold text-success">{{ question.correct_answer }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div class="mt-4 text-center">
                        <a href="{{ url_for('tests') }}" class="btn btn-primary me-2">
                            <i class="fas fa-arrow-left"></i> Testlarga qaytish
                        </a>
                        
                        <button type="button" class="btn btn-success" onclick="requestMoreQuestions()">
                            <i class="fas fa-plus"></i> Yana savol berish
                        </button>
                        
                        {% if test_result.percentage >= 80 %}
                        <a href="{{ url_for('upload_certificate') }}" class="btn btn-warning">
                            <i class="fas fa-certificate"></i> Sertifikat yuklash
                        </a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function requestMoreQuestions() {
    if (confirm('Ushbu mavzu bo\'yicha qo\'shimcha test yaratilsinmi?')) {
        // Redirect to AI chat with topic context
        window.location.href = '/ai_chat';
    }
}
</script>
{% endblock %}
'''
        
        with open('templates/test_result.html', 'w', encoding='utf-8') as f:
            f.write(result_content)
        
        print("Test result display upgraded!")
        return True
        
    except Exception as e:
        print(f"Error upgrading result display: {e}")
        return False

def main():
    """Main upgrade function"""
    print("STEP BY STEP EDUCATION PLATFORM - TEST SYSTEM UPGRADE")
    print("Upgrading to 20 questions with 4 options each...")
    
    success_steps = []
    
    if upgrade_test_templates():
        success_steps.append("Test Templates")
    else:
        print("Failed to upgrade test templates")
        return False
    
    if upgrade_test_result_display():
        success_steps.append("Result Display")
    else:
        print("Failed to upgrade result display")
        return False
    
    print(f"\n=== TEST SYSTEM UPGRADE COMPLETE ===")
    print(f"Successfully upgraded: {', '.join(success_steps)}")
    print("Test system now supports 20 questions with 4 options each!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
