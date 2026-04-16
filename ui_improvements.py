#!/usr/bin/env python3
"""
UI Improvements
Add loading animations, buttons, and UI enhancements
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_loading_css():
    """Create loading animations CSS"""
    print("=== CREATING LOADING CSS ===")
    
    css_content = '''
/* Loading Animations */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.loading-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.loading-spinner-large {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

/* Enhanced Buttons */
.btn-enhanced {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.btn-enhanced:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-enhanced:active {
    transform: translateY(0);
}

.btn-gradient-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
}

.btn-gradient-success {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border: none;
    color: white;
}

.btn-gradient-warning {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border: none;
    color: white;
}

/* Enhanced Cards */
.card-enhanced {
    border: none;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.card-enhanced:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

/* Progress Bar Enhancements */
.progress-enhanced {
    height: 25px;
    border-radius: 15px;
    overflow: hidden;
    background: #f8f9fa;
}

.progress-bar-enhanced {
    border-radius: 15px;
    transition: width 0.6s ease;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Form Enhancements */
.form-control-enhanced {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 12px 15px;
    transition: all 0.3s ease;
}

.form-control-enhanced:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

/* Alert Enhancements */
.alert-enhanced {
    border: none;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 20px;
    animation: slideInDown 0.5s ease;
}

@keyframes slideInDown {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* Button Loading State */
.btn-loading {
    position: relative;
    pointer-events: none;
}

.btn-loading::after {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    top: 50%;
    left: 50%;
    margin-left: -8px;
    margin-top: -8px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* AI Chat Enhancements */
.ai-message {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
    border-left: 4px solid #667eea;
}

.ai-thinking {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 10px;
    margin-bottom: 10px;
}

.ai-thinking-dots {
    display: flex;
    gap: 5px;
}

.ai-thinking-dot {
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}

.ai-thinking-dot:nth-child(1) { animation-delay: -0.32s; }
.ai-thinking-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1.0);
    }
}

/* Test Enhancements */
.question-card {
    border: none;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    border-radius: 15px;
    margin-bottom: 20px;
    overflow: hidden;
}

.question-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
}

.option-card {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.option-card:hover {
    border-color: #667eea;
    background: #f8f9ff;
}

.option-card.selected {
    border-color: #667eea;
    background: #e7f3ff;
}

/* Certificate Enhancements */
.certificate-preview {
    border: 2px solid #gold;
    border-radius: 15px;
    padding: 30px;
    background: linear-gradient(135deg, #fff9e6 0%, #ffecb3 100%);
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.certificate-seal {
    width: 100px;
    height: 100px;
    border: 3px solid #gold;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 20px auto;
    background: white;
    font-weight: bold;
    color: #gold;
}

/* Responsive Enhancements */
@media (max-width: 768px) {
    .loading-content {
        margin: 20px;
        padding: 20px;
    }
    
    .btn-enhanced {
        padding: 12px 20px;
        font-size: 14px;
    }
    
    .card-enhanced {
        margin-bottom: 20px;
    }
}
'''
    
    try:
        os.makedirs('static/css', exist_ok=True)
        with open('static/css/enhanced_ui.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print("Loading CSS created!")
        return True
        
    except Exception as e:
        print(f"Error creating loading CSS: {e}")
        return False

def create_loading_js():
    """Create loading animations JavaScript"""
    print("=== CREATING LOADING JS ===")
    
    js_content = '''
// Loading and UI Enhancements

// Global loading functions
function showLoading(message = 'Yuklanmoqda...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner-large"></div>
            <h5>${message}</h5>
            <p class="text-muted">Iltimos, kuting...</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Button loading state
function setButtonLoading(button, loadingText = 'Yuborilmoqda...') {
    button.classList.add('btn-loading');
    button.disabled = true;
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = `${loadingText} <span class="loading-spinner"></span>`;
}

function resetButtonLoading(button) {
    button.classList.remove('btn-loading');
    button.disabled = false;
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
    }
}

// AI Chat typing effect
function showAIThinking() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'ai-thinking';
    thinkingDiv.innerHTML = `
        <div class="ai-thinking-dots">
            <div class="ai-thinking-dot"></div>
            <div class="ai-thinking-dot"></div>
            <div class="ai-thinking-dot"></div>
        </div>
        <span>AI javob berishmoqda...</span>
    `;
    return thinkingDiv;
}

// Form validation with visual feedback
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// Progress bar animation
function animateProgressBar(progressBar, targetWidth, duration = 1000) {
    const startWidth = 0;
    const startTime = Date.now();
    
    function updateProgress() {
        const currentTime = Date.now();
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentWidth = startWidth + (targetWidth - startWidth) * progress;
        progressBar.style.width = currentWidth + '%';
        progressBar.textContent = Math.round(currentWidth) + '%';
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

// Smooth scroll
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-enhanced position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

// Test timer
function startTestTimer(startTimeElement, durationElement) {
    const startTime = Date.now();
    
    setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        if (durationElement) {
            durationElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

// Certificate download animation
function downloadCertificate(certificateId) {
    const button = document.getElementById(`download-${certificateId}`);
    if (button) {
        setButtonLoading(button, 'Yuklanmoqda...');
        
        // Simulate download
        setTimeout(() => {
            resetButtonLoading(button);
            showNotification('Sertifikat muvaffaqiyatli yuklandi!', 'success');
        }, 2000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add loading classes to all buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.classList.add('btn-enhanced');
    });
    
    // Add enhanced classes to all cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('card-enhanced');
    });
    
    // Add enhanced classes to all form controls
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.classList.add('form-control-enhanced');
    });
    
    // Add enhanced classes to all progress bars
    const progressBars = document.querySelectorAll('.progress');
    progressBars.forEach(bar => {
        bar.classList.add('progress-enhanced');
        const progressBar = bar.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.classList.add('progress-bar-enhanced');
        }
    });
    
    // Add enhanced classes to all alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('alert-enhanced');
    });
});
'''
    
    try:
        os.makedirs('static/js', exist_ok=True)
        with open('static/js/enhanced_ui.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print("Loading JS created!")
        return True
        
    except Exception as e:
        print(f"Error creating loading JS: {e}")
        return False

def update_base_template():
    """Update base template with enhanced UI"""
    print("=== UPDATING BASE TEMPLATE ===")
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add enhanced CSS and JS
        if 'enhanced_ui.css' not in content:
            css_link = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/enhanced_ui.css\') }}">'
            
            # Find existing CSS links
            bootstrap_link = content.find('<link href="https://cdn.jsdelivr.net/npm/bootstrap')
            if bootstrap_link != -1:
                # Find end of bootstrap link
                end_of_bootstrap = content.find('>', bootstrap_link) + 1
                content = content[:end_of_bootstrap] + '\n' + css_link + '\n' + content[end_of_bootstrap:]
        
        if 'enhanced_ui.js' not in content:
            js_link = '    <script src="{{ url_for(\'static\', filename=\'js/enhanced_ui.js\') }}"></script>'
            
            # Find existing JS scripts
            bootstrap_js = content.find('<script src="https://cdn.jsdelivr.net/npm/bootstrap')
            if bootstrap_js != -1:
                # Find end of bootstrap JS
                end_of_bootstrap_js = content.find('</script>', bootstrap_js) + 9
                content = content[:end_of_bootstrap_js] + '\n' + js_link + '\n' + content[end_of_bootstrap_js:]
        
        # Add AI chat link to navigation
        if 'ai_chat' not in content:
            nav_link = '''                    <a href="{{ url_for('ai_chat') }}" class="nav-link">
                        <i class="fas fa-robot"></i> AI Chat
                    </a>'''
            
            # Find tests link and add AI chat after it
            tests_link = content.find('<a href="{{ url_for(\'tests\') }}"')
            if tests_link != -1:
                end_of_tests = content.find('</a>', tests_link) + 4
                next_li = content.find('</li>', end_of_tests)
                if next_li != -1:
                    content = content[:next_li] + '\n                    <li class="nav-item">' + nav_link + '</li>' + content[next_li:]
        
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Base template updated!")
        return True
        
    except Exception as e:
        print(f"Error updating base template: {e}")
        return False

def main():
    """Main UI improvements implementation"""
    print("STEP BY STEP EDUCATION PLATFORM - UI IMPROVEMENTS")
    print("Adding loading animations and UI enhancements...")
    
    success_steps = []
    
    if create_loading_css():
        success_steps.append("Loading CSS")
    else:
        print("Failed to create loading CSS")
        return False
    
    if create_loading_js():
        success_steps.append("Loading JS")
    else:
        print("Failed to create loading JS")
        return False
    
    if update_base_template():
        success_steps.append("Base Template")
    else:
        print("Failed to update base template")
        return False
    
    print(f"\n=== UI IMPROVEMENTS COMPLETE ===")
    print(f"Successfully implemented: {', '.join(success_steps)}")
    print("Loading animations and UI enhancements added!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
