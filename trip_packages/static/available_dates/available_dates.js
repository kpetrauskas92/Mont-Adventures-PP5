var messageTimeout;

	document.body.addEventListener('htmx:afterOnLoad', function(event) {
		var xhr = event.detail.xhr;
		var messageDiv = document.getElementById('toast-messages');
		var messageHTML = '';

		// Clear any existing timeout
		clearTimeout(messageTimeout);

		if (xhr.getResponseHeader('HX-Item-Already-In-Cart') === 'true') {
			messageHTML = `
				<div class="inline-flex items-center justify-center flex-shrink-0 px-3 py-1 text-xs font-medium transition-colors border rounded-md h-9 hover:bg-gray-100 bg-red-100 focus:bg-red-100 focus:outline-none w-full">
					<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z">
						</path>
					</svg>
					<span>This date is already in your cart.</span>
				</div>`;
		} else if (xhr.getResponseHeader('HX-Item-Added') === 'true') {
			messageHTML = `
				<div class="inline-flex items-center justify-center flex-shrink-0 px-3 py-1 text-xs font-medium transition-colors border rounded-md h-9 hover:bg-gray-100 bg-green-100 focus:bg-green-100 focus:outline-none w-full">
					<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z">
						</path>
					</svg>
					<span>Trip added to cart.</span>
				</div>`;
		} else {
			return;
		}

		// Show the message
		messageDiv.style.display = 'block';
		messageDiv.innerHTML = messageHTML;

		// Hide the message after 5 seconds
		messageTimeout = setTimeout(function() {
			messageDiv.style.display = 'none';
		}, 3000);
	});