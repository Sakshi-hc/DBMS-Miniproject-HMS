// dashboard.js - Scripts for dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get current date for dashboard display
    updateCurrentDate();
    
    // Initialize any charts if they exist on the page
    initializeCharts();
});

function updateCurrentDate() {
    const currentDateElement = document.getElementById('current-date');
    if (currentDateElement) {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        currentDateElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

function initializeCharts() {
    // This is just a placeholder - actual chart initialization occurs inline 
    // in the dashboard.html template for data access reasons
    
    // If there are additional charts beyond the main dashboard chart,
    // you could implement their initialization here
}

// Utility functions for dashboard stats (if needed)
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

function calculateGrowthPercentage(current, previous) {
    if (previous === 0) return 100;
    return Math.round(((current - previous) / previous) * 100);
}
