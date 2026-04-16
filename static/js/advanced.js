// Advanced JavaScript for Excel-level Professional Functionality

// Global Configuration
const APP_CONFIG = {
    API_BASE_URL: '/api',
    WEBSOCKET_URL: '/ws',
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 300,
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
    TOAST_DURATION: 5000,
    CHART_COLORS: {
        primary: '#0ea5e9',
        success: '#22c55e',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6'
    }
};

// Advanced Utility Functions
class AdvancedUtils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static formatNumber(num) {
        return new Intl.NumberFormat('en-US').format(num);
    }

    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    static formatDate(date, options = {}) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            ...options
        }).format(new Date(date));
    }

    static generateId() {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    static deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    static isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static isValidPhone(phone) {
        const re = /^[\d\s\-\+\(\)]+$/;
        return re.test(phone);
    }

    static slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^\w\-]+/g, '')
            .replace(/\-\-+/g, '-')
            .replace(/^-+/, '')
            .replace(/-+$/, '');
    }

    static truncateText(text, length, suffix = '...') {
        if (text.length <= length) return text;
        return text.substring(0, length) + suffix;
    }

    static escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    static getContrastColor(hexColor) {
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }

    static hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    static rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    static calculateAge(birthDate) {
        const today = new Date();
        const birthDateObj = new Date(birthDate);
        let age = today.getFullYear() - birthDateObj.getFullYear();
        const monthDiff = today.getMonth() - birthDateObj.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDateObj.getDate())) {
            age--;
        }
        return age;
    }

    static getTimeAgo(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        
        let interval = Math.floor(seconds / 31536000);
        if (interval > 1) return interval + " years ago";
        
        interval = Math.floor(seconds / 2592000);
        if (interval > 1) return interval + " months ago";
        
        interval = Math.floor(seconds / 86400);
        if (interval > 1) return interval + " days ago";
        
        interval = Math.floor(seconds / 3600);
        if (interval > 1) return interval + " hours ago";
        
        interval = Math.floor(seconds / 60);
        if (interval > 1) return interval + " minutes ago";
        
        return Math.floor(seconds) + " seconds ago";
    }
}

// Advanced Cache System
class CacheManager {
    constructor() {
        this.cache = new Map();
        this.timestamps = new Map();
    }

    set(key, value, duration = APP_CONFIG.CACHE_DURATION) {
        this.cache.set(key, value);
        this.timestamps.set(key, Date.now() + duration);
    }

    get(key) {
        if (!this.cache.has(key)) return null;
        
        const expiry = this.timestamps.get(key);
        if (Date.now() > expiry) {
            this.delete(key);
            return null;
        }
        
        return this.cache.get(key);
    }

    delete(key) {
        this.cache.delete(key);
        this.timestamps.delete(key);
    }

    clear() {
        this.cache.clear();
        this.timestamps.clear();
    }

    size() {
        return this.cache.size;
    }

    keys() {
        return Array.from(this.cache.keys());
    }

    cleanup() {
        const now = Date.now();
        for (const [key, expiry] of this.timestamps.entries()) {
            if (now > expiry) {
                this.delete(key);
            }
        }
    }
}

// Advanced Event System
class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return this;
    }

    off(event, callback) {
        if (!this.events[event]) return this;
        
        const index = this.events[event].indexOf(callback);
        if (index > -1) {
            this.events[event].splice(index, 1);
        }
        return this;
    }

    emit(event, ...args) {
        if (!this.events[event]) return this;
        
        this.events[event].forEach(callback => {
            callback.apply(this, args);
        });
        return this;
    }

    once(event, callback) {
        const onceWrapper = (...args) => {
            callback.apply(this, args);
            this.off(event, onceWrapper);
        };
        return this.on(event, onceWrapper);
    }
}

// Advanced Toast Notification System
class ToastManager {
    constructor() {
        this.toasts = [];
        this.container = null;
        this.init();
    }

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = APP_CONFIG.TOAST_DURATION) {
        const toast = document.createElement('div');
        const id = AdvancedUtils.generateId();
        
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${this.getBackgroundColor(type)};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            min-width: 300px;
            max-width: 500px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
        `;
        
        toast.innerHTML = `
            <span>${this.getIcon(type)}</span>
            <span>${message}</span>
            <button onclick="toastManager.close('${id}')" style="
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                margin-left: auto;
            ">&times;</button>
        `;
        
        this.container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        const toastData = { id, element: toast };
        this.toasts.push(toastData);
        
        // Auto remove
        setTimeout(() => {
            this.close(id);
        }, duration);
        
        return id;
    }

    close(id) {
        const toastIndex = this.toasts.findIndex(t => t.id === id);
        if (toastIndex === -1) return;
        
        const toast = this.toasts[toastIndex];
        toast.element.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (toast.element.parentNode) {
                toast.element.parentNode.removeChild(toast.element);
            }
            this.toasts.splice(toastIndex, 1);
        }, 300);
    }

    getBackgroundColor(type) {
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }

    getIcon(type) {
        const icons = {
            success: '&#x2713;',
            error: '&#x2717;',
            warning: '&#x26a0;',
            info: '&#x2139;'
        };
        return icons[type] || icons.info;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Advanced Modal System
class ModalManager {
    constructor() {
        this.modals = new Map();
        this.activeModal = null;
        this.init();
    }

    init() {
        // Create modal container
        this.container = document.createElement('div');
        this.container.className = 'modal-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
        `;
        document.body.appendChild(this.container);
    }

    create(id, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            transform: scale(0.9);
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        modal.innerHTML = `
            <div class="modal-header" style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            ">
                <h2 style="margin: 0; color: #1f2937;">${options.title || 'Modal'}</h2>
                <button onclick="modalManager.close('${id}')" style="
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #6b7280;
                ">&times;</button>
            </div>
            <div class="modal-content">
                ${options.content || ''}
            </div>
            <div class="modal-footer" style="
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 20px;
            ">
                ${options.footer || ''}
            </div>
        `;
        
        this.container.appendChild(modal);
        this.modals.set(id, modal);
        
        return id;
    }

    show(id) {
        const modal = this.modals.get(id);
        if (!modal) return;
        
        this.container.style.display = 'flex';
        this.activeModal = id;
        
        setTimeout(() => {
            modal.style.transform = 'scale(1)';
            modal.style.opacity = '1';
        }, 10);
        
        // Close on background click
        this.container.onclick = (e) => {
            if (e.target === this.container) {
                this.close(id);
            }
        };
        
        // Close on escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                this.close(id);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    close(id) {
        const modal = this.modals.get(id);
        if (!modal) return;
        
        modal.style.transform = 'scale(0.9)';
        modal.style.opacity = '0';
        
        setTimeout(() => {
            this.container.style.display = 'none';
            this.activeModal = null;
        }, 300);
    }

    confirm(message, onConfirm, options = {}) {
        const id = AdvancedUtils.generateId();
        
        this.create(id, {
            title: options.title || 'Confirm',
            content: `<p>${message}</p>`,
            footer: `
                <button class="btn btn-secondary" onclick="modalManager.close('${id}')">Cancel</button>
                <button class="btn btn-danger" onclick="modalManager.handleConfirm('${id}')">Confirm</button>
            `
        });
        
        this.modals.get(id).onConfirm = onConfirm;
        this.show(id);
        
        return id;
    }

    handleConfirm(id) {
        const modal = this.modals.get(id);
        if (modal.onConfirm) {
            modal.onConfirm();
        }
        this.close(id);
    }

    alert(message, options = {}) {
        const id = AdvancedUtils.generateId();
        
        this.create(id, {
            title: options.title || 'Alert',
            content: `<p>${message}</p>`,
            footer: `
                <button class="btn btn-primary" onclick="modalManager.close('${id}')">OK</button>
            `
        });
        
        this.show(id);
        
        return id;
    }
}

// Advanced Chart System
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                    }
                },
                x: {
                    grid: {
                        display: false,
                    }
                }
            }
        };
    }

    createLineChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        const config = {
            type: 'line',
            data: data,
            options: { ...this.defaultOptions, ...options }
        };
        
        // Simple line chart implementation
        this.drawSimpleLineChart(ctx, data, options);
        
        const chartId = AdvancedUtils.generateId();
        this.charts.set(chartId, { canvas, ctx, config });
        
        return chartId;
    }

    drawSimpleLineChart(ctx, data, options) {
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw axes
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Draw data
        if (data.datasets && data.datasets.length > 0) {
            const dataset = data.datasets[0];
            const points = dataset.data;
            const labels = data.labels || [];
            
            if (points.length > 0) {
                const xStep = (width - 2 * padding) / (points.length - 1);
                const yMax = Math.max(...points);
                const yScale = (height - 2 * padding) / yMax;
                
                // Draw line
                ctx.strokeStyle = dataset.borderColor || APP_CONFIG.CHART_COLORS.primary;
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                points.forEach((point, index) => {
                    const x = padding + index * xStep;
                    const y = height - padding - (point * yScale);
                    
                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                
                ctx.stroke();
                
                // Draw points
                points.forEach((point, index) => {
                    const x = padding + index * xStep;
                    const y = height - padding - (point * yScale);
                    
                    ctx.fillStyle = dataset.borderColor || APP_CONFIG.CHART_COLORS.primary;
                    ctx.beginPath();
                    ctx.arc(x, y, 4, 0, 2 * Math.PI);
                    ctx.fill();
                });
                
                // Draw labels
                ctx.fillStyle = '#6b7280';
                ctx.font = '12px Inter, sans-serif';
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
    }

    createBarChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Simple bar chart implementation
        this.drawSimpleBarChart(ctx, data, options);
        
        const chartId = AdvancedUtils.generateId();
        this.charts.set(chartId, { canvas, ctx, data, options });
        
        return chartId;
    }

    drawSimpleBarChart(ctx, data, options) {
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw axes
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Draw data
        if (data.datasets && data.datasets.length > 0) {
            const dataset = data.datasets[0];
            const points = dataset.data;
            const labels = data.labels || [];
            
            if (points.length > 0) {
                const barWidth = (width - 2 * padding) / points.length * 0.6;
                const barSpacing = (width - 2 * padding) / points.length;
                const yMax = Math.max(...points);
                const yScale = (height - 2 * padding) / yMax;
                
                points.forEach((point, index) => {
                    const x = padding + index * barSpacing + barSpacing * 0.2;
                    const barHeight = point * yScale;
                    const y = height - padding - barHeight;
                    
                    // Draw bar
                    ctx.fillStyle = dataset.backgroundColor || APP_CONFIG.CHART_COLORS.primary;
                    ctx.fillRect(x, y, barWidth, barHeight);
                    
                    // Draw value on top
                    ctx.fillStyle = '#374151';
                    ctx.font = '12px Inter, sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(point, x + barWidth / 2, y - 5);
                    
                    // Draw label
                    if (labels[index]) {
                        ctx.save();
                        ctx.translate(x + barWidth / 2, height - padding + 20);
                        ctx.rotate(-Math.PI / 4);
                        ctx.textAlign = 'right';
                        ctx.fillText(labels[index], 0, 0);
                        ctx.restore();
                    }
                });
            }
        }
    }

    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        chart.data = newData;
        
        if (chart.config.type === 'line') {
            this.drawSimpleLineChart(chart.ctx, newData, chart.config.options);
        } else if (chart.config.type === 'bar') {
            this.drawSimpleBarChart(chart.ctx, newData, chart.config.options);
        }
    }

    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            const ctx = chart.ctx;
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            this.charts.delete(chartId);
        }
    }
}

// Advanced Form Validation
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.rules = new Map();
        this.errors = new Map();
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validate()) {
                e.preventDefault();
                e.stopPropagation();
            }
        });

        // Add real-time validation
        this.form.addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                this.validateField(e.target);
            }
        });
    }

    addRule(fieldName, rules) {
        this.rules.set(fieldName, rules);
        return this;
    }

    validate() {
        this.errors.clear();
        let isValid = true;

        for (const [fieldName, rules] of this.rules.entries()) {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field, rules)) {
                isValid = false;
            }
        }

        this.showErrors();
        return isValid;
    }

    validateField(field, customRules = null) {
        const rules = customRules || this.rules.get(field.name);
        if (!rules) return true;

        const value = field.value.trim();
        let isValid = true;
        let error = '';

        for (const rule of rules) {
            if (rule.required && !value) {
                error = rule.message || 'This field is required';
                isValid = false;
                break;
            }

            if (rule.minLength && value.length < rule.minLength) {
                error = rule.message || `Minimum length is ${rule.minLength}`;
                isValid = false;
                break;
            }

            if (rule.maxLength && value.length > rule.maxLength) {
                error = rule.message || `Maximum length is ${rule.maxLength}`;
                isValid = false;
                break;
            }

            if (rule.pattern && !rule.pattern.test(value)) {
                error = rule.message || 'Invalid format';
                isValid = false;
                break;
            }

            if (rule.email && !AdvancedUtils.isValidEmail(value)) {
                error = rule.message || 'Invalid email address';
                isValid = false;
                break;
            }

            if (rule.phone && !AdvancedUtils.isValidPhone(value)) {
                error = rule.message || 'Invalid phone number';
                isValid = false;
                break;
            }

            if (rule.custom && !rule.custom(value)) {
                error = rule.message || 'Invalid value';
                isValid = false;
                break;
            }
        }

        if (isValid) {
            this.removeFieldError(field);
        } else {
            this.errors.set(field.name, error);
            this.showFieldError(field, error);
        }

        return isValid;
    }

    showFieldError(field, error) {
        this.removeFieldError(field);

        field.classList.add('error');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = error;
        errorElement.style.cssText = `
            color: #ef4444;
            font-size: 0.875rem;
            margin-top: 4px;
            font-weight: 500;
        `;
        
        field.parentNode.appendChild(errorElement);
    }

    removeFieldError(field) {
        field.classList.remove('error');
        
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showErrors() {
        // Show summary error if any errors exist
        if (this.errors.size > 0) {
            const errorMessages = Array.from(this.errors.values());
            toastManager.error(`Please fix the following errors: ${errorMessages.join(', ')}`);
        }
    }

    getErrors() {
        return Array.from(this.errors.values());
    }

    hasErrors() {
        return this.errors.size > 0;
    }

    clearErrors() {
        this.errors.clear();
        
        const errorElements = this.form.querySelectorAll('.field-error');
        errorElements.forEach(el => el.remove());
        
        const fields = this.form.querySelectorAll('.error');
        fields.forEach(field => field.classList.remove('error'));
    }
}

// Advanced Data Table
class DataTable {
    constructor(tableElement, options = {}) {
        this.table = tableElement;
        this.options = {
            pageSize: 10,
            sortable: true,
            filterable: true,
            pagination: true,
            ...options
        };
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.init();
    }

    init() {
        this.extractData();
        this.createControls();
        this.render();
        this.bindEvents();
    }

    extractData() {
        const rows = this.table.querySelectorAll('tbody tr');
        this.data = Array.from(rows).map(row => {
            const cells = row.querySelectorAll('td');
            return Array.from(cells).map(cell => cell.textContent.trim());
        });
        this.filteredData = [...this.data];
    }

    createControls() {
        if (this.options.filterable) {
            this.createFilterControl();
        }
        
        if (this.options.pagination) {
            this.createPaginationControl();
        }
    }

    createFilterControl() {
        const filterContainer = document.createElement('div');
        filterContainer.className = 'table-filter';
        filterContainer.style.cssText = `
            margin-bottom: 16px;
            display: flex;
            gap: 12px;
            align-items: center;
        `;

        const filterInput = document.createElement('input');
        filterInput.type = 'text';
        filterInput.placeholder = 'Search...';
        filterInput.style.cssText = `
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            flex: 1;
            max-width: 300px;
        `;

        filterContainer.appendChild(filterInput);
        this.table.parentNode.insertBefore(filterContainer, this.table);
        
        this.filterInput = filterInput;
    }

    createPaginationControl() {
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'table-pagination';
        paginationContainer.style.cssText = `
            margin-top: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;

        const info = document.createElement('div');
        info.className = 'pagination-info';
        paginationContainer.appendChild(info);

        const controls = document.createElement('div');
        controls.className = 'pagination-controls';
        controls.style.cssText = `
            display: flex;
            gap: 8px;
        `;

        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.className = 'btn btn-secondary';
        prevBtn.disabled = true;

        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.className = 'btn btn-secondary';

        controls.appendChild(prevBtn);
        controls.appendChild(nextBtn);
        paginationContainer.appendChild(controls);

        this.table.parentNode.appendChild(paginationContainer);
        
        this.paginationContainer = paginationContainer;
        this.paginationInfo = info;
        this.prevBtn = prevBtn;
        this.nextBtn = nextBtn;
    }

    bindEvents() {
        if (this.filterInput) {
            this.filterInput.addEventListener('input', 
                AdvancedUtils.debounce(() => this.filter(), 300)
            );
        }

        if (this.options.sortable) {
            const headers = this.table.querySelectorAll('th');
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => this.sort(index));
            });
        }

        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.previousPage());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextPage());
        }
    }

    filter() {
        const searchTerm = this.filterInput.value.toLowerCase();
        
        if (!searchTerm) {
            this.filteredData = [...this.data];
        } else {
            this.filteredData = this.data.filter(row => 
                row.some(cell => cell.toLowerCase().includes(searchTerm))
            );
        }
        
        this.currentPage = 1;
        this.render();
    }

    sort(columnIndex) {
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnIndex;
            this.sortDirection = 'asc';
        }

        this.filteredData.sort((a, b) => {
            const aVal = a[columnIndex];
            const bVal = b[columnIndex];
            
            if (this.sortDirection === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        });

        this.render();
    }

    getPageData() {
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        return this.filteredData.slice(start, end);
    }

    render() {
        const tbody = this.table.querySelector('tbody');
        tbody.innerHTML = '';

        const pageData = this.getPageData();
        
        pageData.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        this.updatePaginationInfo();
        this.updatePaginationButtons();
    }

    updatePaginationInfo() {
        if (this.paginationInfo) {
            const start = (this.currentPage - 1) * this.options.pageSize + 1;
            const end = Math.min(this.currentPage * this.options.pageSize, this.filteredData.length);
            const total = this.filteredData.length;
            
            this.paginationInfo.textContent = `Showing ${start}-${end} of ${total} entries`;
        }
    }

    updatePaginationButtons() {
        if (this.prevBtn && this.nextBtn) {
            const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
            
            this.prevBtn.disabled = this.currentPage === 1;
            this.nextBtn.disabled = this.currentPage === totalPages;
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.render();
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.render();
        }
    }

    refresh() {
        this.extractData();
        this.filter();
    }

    setData(newData) {
        this.data = newData;
        this.filteredData = [...newData];
        this.currentPage = 1;
        this.render();
    }

    getData() {
        return [...this.data];
    }

    getFilteredData() {
        return [...this.filteredData];
    }
}

// Initialize global instances
const cacheManager = new CacheManager();
const eventEmitter = new EventEmitter();
const toastManager = new ToastManager();
const modalManager = new ModalManager();
const chartManager = new ChartManager();

// Auto-cleanup cache every 5 minutes
setInterval(() => {
    cacheManager.cleanup();
}, 5 * 60 * 1000);

// Export for global use
window.AdvancedUtils = AdvancedUtils;
window.cacheManager = cacheManager;
window.eventEmitter = eventEmitter;
window.toastManager = toastManager;
window.modalManager = modalManager;
window.chartManager = chartManager;
window.FormValidator = FormValidator;
window.DataTable = DataTable;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animations to elements
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('.tooltip');
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

    // Initialize data tables
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        new DataTable(table);
    });

    // Initialize form validators
    const forms = document.querySelectorAll('[data-validate]');
    forms.forEach(form => {
        const validator = new FormValidator(form);
        
        // Add common validation rules
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            validator.addRule(field.name, [
                { required: true, message: 'This field is required' }
            ]);
        });

        const emailFields = form.querySelectorAll('[type="email"]');
        emailFields.forEach(field => {
            validator.addRule(field.name, [
                { required: true, message: 'Email is required' },
                { email: true, message: 'Please enter a valid email address' }
            ]);
        });
    });

    // Show welcome toast
    if (window.location.pathname === '/admin_dashboard') {
        toastManager.success('Welcome to the Admin Dashboard!');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+K for search
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape' && modalManager.activeModal) {
        modalManager.close(modalManager.activeModal);
    }

    // Ctrl+Enter to submit forms
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.activeElement.form;
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
});

// Performance monitoring
if (window.performance && window.performance.mark) {
    window.performance.mark('app-start');
    
    window.addEventListener('load', function() {
        window.performance.mark('app-loaded');
        window.performance.measure('app-load-time', 'app-start', 'app-loaded');
        
        const measure = window.performance.getEntriesByName('app-load-time')[0];
        if (measure && measure.duration > 3000) {
            console.warn('App load time is slow:', measure.duration + 'ms');
        }
    });
}

// Service Worker registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    toastManager.error('An unexpected error occurred. Please try again.');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    toastManager.error('An unexpected error occurred. Please try again.');
});

console.log('Advanced JavaScript loaded successfully!');
