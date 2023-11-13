// Function to update all #max-price and #max-price-label elements
function syncMaxPrice(value) {
    var maxPriceInputs = document.querySelectorAll('.max-price');
    var maxPriceLabels = document.querySelectorAll('.max-price-label');
    
    maxPriceInputs.forEach(function(input) {
        input.value = value;
    });

    maxPriceLabels.forEach(function(label) {
        label.innerText = '€' + value;
    });
}

// Listen for changes on any #max-price element
document.body.addEventListener('input', function(event) {
    if (event.target.classList.contains('max-price')) {
        syncMaxPrice(event.target.value);
    }
});

//  Function for trip count
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('htmx:afterOnLoad', function() {
        var tripCountElement = document.getElementById('trip-count');
        var tripItems = document.querySelectorAll('#trip-package-list .trip-item').length;
        var expeditionText = tripItems === 1 ? ' Expedition' : ' Expeditions';
        tripCountElement.innerHTML = '<strong>' + tripItems + '</strong>' + expeditionText;
    });
});

// Listen for changes to checkboxes and price sliders in both the main form and mobile sidebar
document.addEventListener("DOMContentLoaded", function() {
    const inputs = document.querySelectorAll("input[type='checkbox'], input[type='range']");
    const resetButtons = document.querySelectorAll(".resetButton");

    inputs.forEach(input => {
        input.addEventListener("change", function() {
            // Find the closest form, or null if there isn't one
            const form = input.closest('form');
            
            // Proceed only if the input is inside a form
            if (form) {
                const defaultPrice = form.querySelector(".max-price").getAttribute('max');
                const anyCheckedOrAdjusted = Array.from(inputs).some(
                    input => (input.type === 'checkbox' && input.checked) || 
                            (input.type === 'range' && input.value !== defaultPrice)
                );
                resetButtons.forEach(resetButton => {
                    resetButton.classList.toggle("hidden", !anyCheckedOrAdjusted);
                });
            }
        });
    });
});


// Reset all filters
// eslint-disable-next-line no-unused-vars
function resetFilters() {
    // Main filter form and mobile drawer form
    const filterForms = document.querySelectorAll("[id^='filterForm-']");

    filterForms.forEach(filterForm => {
        const checkboxes = filterForm.querySelectorAll("input[type='checkbox']");
        const priceSlider = filterForm.querySelector("input[type='range']");
        const priceLabel = filterForm.querySelector(".max-price-label");

        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        // Reset price slider to its default position
        const defaultPrice = priceSlider.getAttribute('max');
        priceSlider.value = defaultPrice;

        // Update displayed maximum price
        priceLabel.innerText = '€' + defaultPrice;

        // Hide the reset button
        const resetButton = filterForm.querySelector(".resetButton");
        resetButton.classList.add("hidden");
    });

    // Trigger a change event to refresh the filter results
    filterForms[0].dispatchEvent(new Event('submit', { bubbles: true }));
}