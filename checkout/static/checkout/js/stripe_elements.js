
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var isCardComplete = false; 
var cardErrors = '';

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


var card = elements.create('card', {style: style});
card.mount('#card-element');

function validateForm() {
    var errorDiv = document.getElementById('form-errors');
    var firstName = form.first_name.value.trim();
    var lastName = form.last_name.value.trim();
    var email = form.email.value.trim();
    var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    var errors = [];

    if (!firstName) {
        errors.push("First name is required.");
    } else if (firstName.length < 3) {
        errors.push("First name must be at least 3 characters long.");
    } else if (!/^[a-zA-Z]+$/.test(firstName)) {
        errors.push("First name should only contain letters.");
    }

    if (!lastName) {
        errors.push("Last name is required.");
    } else if (lastName.length < 3) {
        errors.push("Last name must be at least 3 characters long.");
    } else if (!/^[a-zA-Z]+$/.test(lastName)) {
        errors.push("Last name should only contain letters.");
    }

    if (!email) {
        errors.push("Email is required.");
    } else if (!emailPattern.test(email)) {
        errors.push("Invalid email format.");
    }

    if (errors.length > 0) {
        var html = errors.map(error => `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${error}</span><br>
        `).join('');
        $(errorDiv).html(html);
        return false;
    } else {
        errorDiv.textContent = '';
        return true;
    }
}


// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    isCardComplete = event.complete;
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        cardErrors = event.error.message;
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        cardErrors = '';
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();

    if (!validateForm() || !isCardComplete) {
        var errorDiv = document.getElementById('form-errors');
        if (!isCardComplete && !cardErrors) {
            cardErrors = "Card information is incomplete.";
        }
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${cardErrors}</span>
        `;
        $(errorDiv).html(html);
        return;
    }

    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
    };

    // Create a new payment intent
    $.ajax({
        url: '/checkout/create_payment_intent/',
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        data: postData,
        success: function(data) {
            // Use the new client secret
            var newClientSecret = data.client_secret;
            document.getElementsByName('client_secret')[0].value = newClientSecret;

            stripe.confirmCardPayment(newClientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: `${form.first_name.value} ${form.last_name.value}`,
                        email: $.trim(form.email.value),
                    }
                },
            }).then(function(result) {
                if (result.error) {
                    var errorDiv = document.getElementById('card-errors');
                    var html = `
                        <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                        </span>
                        <span>${result.error.message}</span>`;
                    $(errorDiv).html(html);
                    $('#payment-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    card.update({ 'disabled': false });
                    $('#submit-button').attr('disabled', false);
                } else {
                    if (result.paymentIntent.status === 'succeeded') {
                        form.submit();
                    }
                }
            });
        },
        error: function(error) {
            console.log("Error in creating payment intent: ", error);
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>Unable to process the payment. Please try again.</span>`;
            $(errorDiv).html(html);
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            card.update({ 'disabled': false });
            $('#submit-button').attr('disabled', false);
        }
    });
});
