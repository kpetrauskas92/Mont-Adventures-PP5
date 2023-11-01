// Initialize Stripe variables and elements
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();


// State variables for form validation
var isCardComplete = false; 
var cardErrors = '';


// Styles for Stripe card element
var style = {
    base: {
        color: '#333',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#333'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};


// Initialize interaction flags for form fields
if (typeof userInteracted === 'undefined') {
    var userInteracted = false;
}
if (typeof firstNameInteracted === 'undefined') {
    var firstNameInteracted = false;
}
if (typeof lastNameInteracted  === 'undefined') {
    var lastNameInteracted = false;
}
if (typeof emailInteracted === 'undefined') {
    var emailInteracted = false;
}


/**
 * Update the state of the submit button based on form validation.
 */
function updateSubmitButton() {
    var formValid = validateForm();
    var btn = document.getElementById('submit-button');
    btn.disabled = !(formValid && isCardComplete);
}


// Create and mount Stripe card element
var card = elements.create('card', {style: style});
card.mount('#card-element');


// Get form and form fields
var form = document.getElementById('payment-form')
var firstNameField = form.elements['first_name'];
var lastNameField = form.elements['last_name'];
var emailField = form.elements['email'];

// Add event listeners to form fields for real-time validation
firstNameField.addEventListener('keyup', function() {
    firstNameInteracted = true;
    validateForm();
    updateSubmitButton();
});
lastNameField.addEventListener('keyup', function() {
    lastNameInteracted = true;
    validateForm();
    updateSubmitButton();
});
emailField.addEventListener('keyup', function() {
    emailInteracted = true;
    validateForm();
    updateSubmitButton();
});


/**
 * Validate the form fields and display error messages if needed.
 */
function validateForm() {
    var firstNameErrorDiv = document.getElementById('first-name-error');
    var lastNameErrorDiv = document.getElementById('last-name-error');
    var emailErrorDiv = document.getElementById('email-error');
    var errorDiv = document.getElementById('form-errors');

    var firstName = form.first_name.value.trim();
    var lastName = form.last_name.value.trim();
    var email = form.email.value.trim();
    var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    var valid = true;


    
    
    if (firstNameInteracted) {
        if (!firstName) {
            firstNameErrorDiv.textContent = "First name is required.";
            valid = false;
        } else if (firstName.length < 3) {
            firstNameErrorDiv.textContent = "First name must be at least 3 characters long.";
            valid = false;
        } else if (!/^[a-zA-Z]+$/.test(firstName)) {
            firstNameErrorDiv.textContent = "First name should only contain letters.";
            valid = false;
        } else {
            firstNameErrorDiv.textContent = '';
        }
    }

    if (lastNameInteracted) {
        if (!lastName) {
            lastNameErrorDiv.textContent = "Last name is required.";
            valid = false;
        } else if (lastName.length < 3) {
            lastNameErrorDiv.textContent = "Last name must be at least 3 characters long.";
                valid = false;
        } else if (!/^[a-zA-Z]+$/.test(lastName)) {
            lastNameErrorDiv.textContent = "Last name should only contain letters.";
            valid = false;
        } else {
            lastNameErrorDiv.textContent = '';
        }
    }
    if (emailInteracted) {
        if (!email) {
            emailErrorDiv.textContent = "Email is required.";
            valid = false;
        } else if (!emailPattern.test(email)) {
            emailErrorDiv.textContent = "Invalid email format.";
            valid = false;
        } else {
            emailErrorDiv.textContent = '';
        }
    }

    return valid;
}


// Initial state update for submit button
updateSubmitButton();

// Listen for changes in the card element to display real-time validation errors
card.addEventListener('change', function (event) {
    isCardComplete = event.complete;
    updateSubmitButton();
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        cardErrors = event.error.message;
        var html = `
            <span class="icon" role="alert">
				<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
				</svg>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        cardErrors = '';
        errorDiv.textContent = '';
    }
});

var isPaymentSuccessful = false;

/**
 * Handle form submission and perform payment using Stripe.
 */
var form = document.getElementById('payment-form');

form.addEventListener('submit', async function(ev) {
    ev.preventDefault();

    document.getElementById('my_modal_3').close();
    document.getElementById('loading-overlay').style.display = 'flex';

    var formValid = validateForm();
    
    var errorDiv = document.getElementById('form-errors');
    var errors = [];

    if (!isCardComplete) {
		if (!cardErrors) {
			errors.push("Card information is incomplete.");
		}
	}
	
	if (cardErrors) {
		errors.push(cardErrors);
	}

    if (!formValid || errors.length > 0) {
        var existingErrors = $(errorDiv).html();
        var newErrors = errors.map(error => `
            <span role="alert">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                </svg>
            </span>
            <span>${error}</span><br>
        `).join('');
        $(errorDiv).html(newErrors);
        return;
    }

    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);

    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
    };

    try {
        const response = await fetch('/checkout/create_payment_intent/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(postData)
        });
        
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        
        const data = await response.json();
        var newClientSecret = data.client_secret;
        document.getElementsByName('client_secret')[0].value = newClientSecret;

        const result = await stripe.confirmCardPayment(newClientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: `${form.first_name.value} ${form.last_name.value}`,
                    email: $.trim(form.email.value),
                }
            },
        });

        if (result.error) {
            document.getElementById('my_modal_3').show();
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
				</svg>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                isPaymentSuccessful = true;
                form.submit();
            }
        }
    } catch (error) {
        document.getElementById('my_modal_3').show();
        console.log("Error in creating payment intent: ", error);
        var errorDiv = document.getElementById('card-errors');
        var html = `
            <span class="icon" role="alert">
				<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
				</svg>
            </span>
            <span>Unable to process the payment. Please try again.</span>`;
        $(errorDiv).html(html);
    } finally {
        document.getElementById('loading-overlay').style.display = 'none';
        
        if (!isPaymentSuccessful) {
            document.getElementById('my_modal_3').show();
        }
        
        card.update({ 'disabled': false });
        $('#submit-button').attr('disabled', false);
    }
});