var toastDismissTimeout;

function handleCloseButtonClick(event) {
    // Look for the closest element with the [data-dismiss-target] attribute
    const closeButton = event.target.closest('[data-dismiss-target]');
    if (closeButton) {
        const targetId = closeButton.getAttribute('data-dismiss-target');
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            
            targetElement.remove();
        } else {
            console.log("Target toast not found:", targetId);
        }
    }
}

function setupToasts() {
    // Clear any previous timeout
    if (toastDismissTimeout) {
        clearTimeout(toastDismissTimeout);
    }
    
    // Auto-dismiss toasts after 3 seconds
    toastDismissTimeout = setTimeout(function() {
        const toasts = document.querySelectorAll('.auto-dismiss-toast');
        toasts.forEach(toast => {
            fadeOutAndRemove(toast);
        });
    }, 3500);
}

function fadeOutAndRemove(element) {
    element.classList.add('auto-dismiss-toast-fade-out');
    element.addEventListener('animationend', () => {
        element.remove();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation for close buttons
    document.body.addEventListener('click', handleCloseButtonClick);
    setupToasts();
});
document.body.addEventListener('htmx:afterOnLoad', setupToasts);
