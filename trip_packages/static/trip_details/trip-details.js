// Function to smoothly scroll to an element
function smoothScrollToElement(element, duration = 800) {
    const startY = window.scrollY;
    const endY = element.getBoundingClientRect().top + window.scrollY - 10;
    const distance = endY - startY;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const nextScrollY = ease(timeElapsed, startY, distance, duration);

        window.scrollTo(0, nextScrollY);

        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}

// Function to manage tab active state and scroll to the tab
function manageActiveTabAndScroll(tabElement) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('tab-active'));
    tabElement.classList.add('tab-active');

    // Smooth scroll to the tab element itself
    smoothScrollToElement(tabElement);
}

document.addEventListener("DOMContentLoaded", function() {
    const overviewTab = document.getElementById('overviewTab');
    const reviewsTab = document.getElementById('reviewsTab');
    const reviewLink = document.getElementById('reviewLink');

    overviewTab.addEventListener('click', function() {
        manageActiveTabAndScroll(this);
    });

    reviewsTab.addEventListener('click', function() {
        manageActiveTabAndScroll(this);
    });

    // Event listener for ReviewLink
    if (reviewLink) {
        reviewLink.addEventListener('click', function(event) {
            event.preventDefault();
            manageActiveTabAndScroll(reviewsTab);
        });
    }

    // Check for 'tab=reviews' URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('tab') === 'reviews') {
        manageActiveTabAndScroll(reviewsTab);
        reviewsTab.click();
    }
});
