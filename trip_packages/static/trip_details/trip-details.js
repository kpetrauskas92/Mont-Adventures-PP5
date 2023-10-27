    // Function to activate and scroll to the Reviews tab
    function activateReviewsTab() {
        const reviewsTab = document.getElementById('reviewsTab');
        if (reviewsTab) {
            manageActiveTab(reviewsTab);
            reviewsTab.click();
            reviewsTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Function to manage tab active state
    function manageActiveTab(tabElement) {
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => tab.classList.remove('tab-active'));
        tabElement.classList.add('tab-active');
    }
    
    // Initialize when the DOM is fully loaded
    document.addEventListener("DOMContentLoaded", function() {
        // Handling tab clicks to toggle active state
        const tabs = document.querySelectorAll(".tab");
        tabs.forEach(tab => {
            tab.addEventListener("click", function() {
                manageActiveTab(this);
                document.body.setAttribute('data-initiating-tab', this.id);
            });
        });
    
        // Reviews link event
        const ReviewLink = document.getElementById('ReviewLink');
        if (ReviewLink) {
            ReviewLink.addEventListener("click", function() {
                activateReviewsTab();
                document.body.setAttribute('data-initiating-tab', 'reviewsTab');
            });
        }
    
        // Check URL parameters for specific tab
        const urlParams = new URLSearchParams(window.location.search);
        const tab = urlParams.get('tab');
        if (tab === 'reviews') {
            activateReviewsTab();
        }
    });
    
    // htmx specific event after DOM swap
    document.body.addEventListener('htmx:afterSwap', function(event) {
        const initiatingTabId = document.body.getAttribute('data-initiating-tab');
        if (initiatingTabId) {
            const tabElement = document.getElementById(initiatingTabId);
            if (tabElement) {
                manageActiveTab(tabElement);
                tabElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            // Clear the attribute so it doesn't affect other swaps
            document.body.removeAttribute('data-initiating-tab');
        }
    });