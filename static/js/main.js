// Step by Step Education Platform - Main JavaScript

// Utility Functions
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize forms
    initializeForms();
    
    // Initialize tables
    initializeTables();
    
    // Initialize charts
    initializeCharts();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize animations
    initializeAnimations();
}

// Tooltips
function initializeTooltips() {
    const tooltips = $$('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.querySelector('.tooltiptext');
            if (tooltipText) {
                tooltipText.style.visibility = 'visible';
                tooltipText.style.opacity = '1';
            }
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltipText = this.querySelector('.tooltiptext');
            if (tooltipText) {
                tooltipText.style.visibility = 'hidden';
                tooltipText.style.opacity = '0';
            }
        });
    });
}

// Forms
function initializeForms() {
    // Password confirmation validation
    const passwordInputs = $$('input[type="password"]');
    const confirmPasswordInput = $('#confirm_password');
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            const password = $('#password') ? $('#password').value : '';
            const confirm = this.value;
            
            if (password !== confirm) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Form validation
    const forms = $$('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            
            // Add error message
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = 'This field is required';
            field.parentNode.appendChild(errorMsg);
        } else {
            field.classList.remove('error');
            const errorMsg = field.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

// Tables
function initializeTables() {
    const tables = $$('.table');
    tables.forEach(table => {
        // Add sorting functionality
        addTableSorting(table);
        
        // Add pagination if needed
        addTablePagination(table);
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(table, index);
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Try to sort as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }
        
        // Sort as strings
        return aValue.localeCompare(bValue);
    });
    
    // Clear and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

function addTablePagination(table) {
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    if (rows.length > 10) {
        // Add pagination controls
        const pagination = document.createElement('div');
        pagination.className = 'pagination';
        pagination.innerHTML = `
            <button class="btn btn-secondary" onclick="changePage(-1)">Previous</button>
            <span id="page-info">Page 1 of ${Math.ceil(rows.length / 10)}</span>
            <button class="btn btn-secondary" onclick="changePage(1)">Next</button>
        `;
        
        table.parentNode.insertBefore(pagination, table.nextSibling);
        
        // Initially show only first 10 rows
        showPage(1, table);
    }
}

let currentPage = 1;

function changePage(direction) {
    currentPage += direction;
    const table = $('.table');
    showPage(currentPage, table);
}

function showPage(pageNum, table) {
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    const rowsPerPage = 10;
    const startIndex = (pageNum - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    
    rows.forEach((row, index) => {
        row.style.display = (index >= startIndex && index < endIndex) ? '' : 'none';
    });
    
    // Update page info
    const pageInfo = $('#page-info');
    if (pageInfo) {
        const totalPages = Math.ceil(rows.length / rowsPerPage);
        pageInfo.textContent = `Page ${pageNum} of ${totalPages}`;
    }
}

// Charts
function initializeCharts() {
    const progressChart = $('#progressChart');
    if (progressChart) {
        drawProgressChart(progressChart);
    }
}

function drawProgressChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Sample data - replace with actual data
    const scores = [85, 90, 78, 92, 88, 95, 82, 91];
    const labels = ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5', 'Test 6', 'Test 7', 'Test 8'];
    
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw axes
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw grid lines
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 10; i++) {
        const y = padding + (height - 2 * padding) * i / 10;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Draw data
    if (scores.length > 0) {
        const xStep = (width - 2 * padding) / (scores.length - 1);
        const yScale = (height - 2 * padding) / 100;
        
        // Draw line
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        scores.forEach((score, index) => {
            const x = padding + index * xStep;
            const y = height - padding - (score * yScale);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Draw points
        scores.forEach((score, index) => {
            const x = padding + index * xStep;
            const y = height - padding - (score * yScale);
            
            ctx.fillStyle = '#667eea';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
            
            // Add value labels
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(score + '%', x, y - 10);
        });
        
        // Draw labels
        ctx.fillStyle = '#666';
        ctx.font = '12px Arial';
        labels.forEach((label, index) => {
            const x = padding + index * xStep;
            ctx.save();
            ctx.translate(x, height - padding + 20);
            ctx.rotate(-Math.PI / 4);
            ctx.textAlign = 'right';
            ctx.fillText(label, 0, 0);
            ctx.restore();
        });
    }
}

// Search functionality
function initializeSearch() {
    const searchInputs = $$('input[type="text"][placeholder*="search"], input[type="text"][placeholder*="Search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableId = this.getAttribute('data-table') || 'usersTable';
            const table = $('#' + tableId);
            
            if (table) {
                filterTable(table, searchTerm);
            }
        });
    });
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Navigation
function initializeNavigation() {
    // Mobile menu toggle
    const menuToggle = $('.menu-toggle');
    const navMenu = $('.nav');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = $$('.nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Animations
function initializeAnimations() {
    // Fade in elements
    const fadeElements = $$('.fade-in');
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Slide in elements
    const slideElements = $$('.slide-in');
    slideElements.forEach(element => {
        element.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            element.style.transition = 'transform 0.3s ease';
            element.style.transform = 'translateX(0)';
        }, 100);
    });
}

// Utility functions for AJAX requests
function ajaxRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => console.error('AJAX Error:', error));
}

function getCSRFToken() {
    const token = $('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = $('.container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
}

function hideLoading(element) {
    const spinner = element.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Export functions for global use
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.ajaxRequest = ajaxRequest;
window.changePage = changePage;
