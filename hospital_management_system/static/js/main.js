// main.js - Common scripts for the entire application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Handle flash messages auto-dismiss
    setupFlashMessages();
    
    // Add current year to footer if present
    updateFooterYear();
    
    // Handle form validation styles
    setupFormValidation();
});

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup auto-dismiss for flash messages after 5 seconds
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            const dismissButton = alert.querySelector('.btn-close');
            if (dismissButton) {
                dismissButton.click();
            }
        }, 5000);
    });
}

// Update footer with current year
function updateFooterYear() {
    const yearElement = document.querySelector('footer .text-muted');
    if (yearElement && yearElement.textContent.includes('{{ now.year }}')) {
        const currentYear = new Date().getFullYear();
        yearElement.textContent = yearElement.textContent.replace('{{ now.year }}', currentYear);
    }
}

// Setup form validation styles for required fields
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        // Add was-validated class on submit
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
        
        // Add visual indicators for required fields (asterisk)
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(function(field) {
            const label = field.previousElementSibling;
            if (label && label.classList.contains('form-label') && !label.querySelector('.required-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'required-indicator text-danger ms-1';
                indicator.textContent = '*';
                label.appendChild(indicator);
            }
        });
    });
}

// Utility function to format date strings
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility function to confirm dangerous actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}
