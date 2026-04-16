
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
